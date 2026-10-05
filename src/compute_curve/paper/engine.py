"""Local paper trading engine. Simulation only: no broker, no order routing.

Daily cycle for calendar day ``d`` (identical in backtest and forward mode):

1. **Mark** existing positions to the settlement of ``d`` (variation margin).
2. **Fill** orders decided on earlier days at the settlement of ``d``,
   adjusted by half-spread and slippage, plus fees.
3. **Expire**: contracts past their last trading day cash-settle at the
   month-average index once it is published.
4. **Risk**: update equity, peak and drawdown. A daily loss breach flattens
   and halts; a drawdown breach flattens and stops trading for good.
5. **Decide**: if ``d`` is a trading day and trading is allowed, the strategy
   sees a point-in-time view at 23:59:59 UTC on ``d`` and returns target
   positions. The difference becomes orders that fill at the *next*
   settlement. A price known at decision time is never a fill price.

Accounting: futures are marked to settlement daily, so equity equals cash.
Contract value = price (USD/GPU-hour) x GPU-hours per contract.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from datetime import date, timedelta

from compute_curve.config import Config, ContractSpec
from compute_curve.contracts import final_settlement, last_trading_day, parse_month
from compute_curve.paper.market import MarketData, MarketView
from compute_curve.timeutil import end_of_day_utc

Key = tuple[str, str]  # (product, contract_month 'YYYY-MM')
Strategy = Callable[[MarketView, "AccountState"], dict[Key, int]]


@dataclass(frozen=True)
class CostModel:
    """Trading costs. ``multiplier`` scales every component (sensitivity runs)."""

    half_spread_ticks: float
    slippage_ticks: float
    fee_per_contract: float  # per side, all-in
    multiplier: float = 1.0
    product_fees: dict[str, float] = field(default_factory=dict)
    settlement_fees: dict[str, float] = field(default_factory=dict)

    @staticmethod
    def from_config(cfg: Config, multiplier: float = 1.0) -> CostModel:
        c = cfg.costs
        broker = c.broker_clearing_fee_per_contract
        return CostModel(
            half_spread_ticks=c.half_spread_ticks,
            slippage_ticks=c.slippage_ticks,
            fee_per_contract=broker,
            multiplier=multiplier,
            product_fees={
                k: s.exchange_fee_per_contract + broker for k, s in cfg.contracts.items()
            },
            settlement_fees={
                k: s.cash_settlement_fee_per_contract for k, s in cfg.contracts.items()
            },
        )

    def fill_price(self, settle: float, qty: int, tick: float) -> float:
        """Settlement worsened by half-spread plus slippage in the trade direction."""
        adj = (self.half_spread_ticks + self.slippage_ticks) * tick * self.multiplier
        return settle + math.copysign(adj, qty)

    def fees(self, qty: int, product: str | None = None) -> float:
        per = (
            self.product_fees.get(product, self.fee_per_contract)
            if product
            else self.fee_per_contract
        )
        return abs(qty) * per * self.multiplier

    def settlement_fee(self, qty: int, product: str) -> float:
        return abs(qty) * self.settlement_fees.get(product, 0.0) * self.multiplier


@dataclass
class Position:
    qty: int
    mark: float


@dataclass(frozen=True)
class Order:
    order_id: str
    decision_date: date
    product: str
    contract_month: str
    qty: int
    reason: str

    @property
    def key(self) -> Key:
        return (self.product, self.contract_month)


@dataclass
class AccountState:
    cash: float
    peak_equity: float
    positions: dict[Key, Position] = field(default_factory=dict)
    pending: list[Order] = field(default_factory=list)
    halted_until: date | None = None
    killed: bool = False
    last_date: date | None = None
    order_seq: int = 0

    @property
    def equity(self) -> float:
        return self.cash

    def gross_contracts(self) -> int:
        return sum(abs(p.qty) for p in self.positions.values())

    def net_position(self, key: Key) -> int:
        pos = self.positions.get(key)
        return pos.qty if pos else 0


@dataclass
class DayRecord:
    """Everything that happened on one day; the ledger persists these rows."""

    day: date
    cash_flows: list[dict[str, object]] = field(default_factory=list)
    fills: list[dict[str, object]] = field(default_factory=list)
    orders: list[dict[str, object]] = field(default_factory=list)
    events: list[dict[str, object]] = field(default_factory=list)
    account: dict[str, object] = field(default_factory=dict)
    positions: list[dict[str, object]] = field(default_factory=list)


def new_account(cfg: Config) -> AccountState:
    cash = cfg.risk.starting_cash
    return AccountState(cash=cash, peak_equity=cash)


def _spec(cfg: Config, product: str) -> ContractSpec:
    return cfg.contracts[product]


def _tradable(day: date, contract_month: str) -> bool:
    return day <= last_trading_day(parse_month(contract_month))


# ----------------------------------------------------------------------------
# Steps
# ----------------------------------------------------------------------------
def mark_to_market(
    state: AccountState, settles: dict[Key, float], cfg: Config, rec: DayRecord
) -> None:
    for key, pos in state.positions.items():
        if key not in settles or pos.qty == 0:
            continue
        mult = _spec(cfg, key[0]).gpu_hours_per_contract
        vm = pos.qty * (settles[key] - pos.mark) * mult
        state.cash += vm
        pos.mark = settles[key]
        rec.cash_flows.append(
            {"kind": "variation_margin", "product": key[0], "contract_month": key[1], "amount": vm}
        )


def fill_pending(
    state: AccountState,
    settles: dict[Key, float],
    day: date,
    cfg: Config,
    costs: CostModel,
    rec: DayRecord,
) -> None:
    still_pending: list[Order] = []
    for order in state.pending:
        key = order.key
        if not _tradable(day, order.contract_month):
            rec.events.append(
                {"kind": "order_cancelled_expired", "detail": f"{order.order_id} {key}"}
            )
            rec.orders.append({**_order_row(order), "status": "cancelled", "fill_date": None})
            continue
        if key not in settles:
            still_pending.append(order)
            continue
        spec = _spec(cfg, order.product)
        settle = settles[key]
        px = costs.fill_price(settle, order.qty, spec.tick_size)
        mult = spec.gpu_hours_per_contract
        spread_cost = order.qty * (settle - px) * mult  # always <= 0
        fee = costs.fees(order.qty, order.product)
        state.cash += spread_cost - fee
        pos = state.positions.get(key)
        if pos is None:
            state.positions[key] = Position(order.qty, settle)
        else:
            pos.qty += order.qty
            pos.mark = settle
        if state.positions[key].qty == 0:
            del state.positions[key]
        rec.fills.append(
            {
                "order_id": order.order_id,
                "product": order.product,
                "contract_month": order.contract_month,
                "qty": order.qty,
                "settle_price": settle,
                "fill_price": px,
                "spread_slippage_cost": spread_cost,
                "fees": fee,
            }
        )
        rec.cash_flows.append(
            {
                "kind": "spread_slippage",
                "product": key[0],
                "contract_month": key[1],
                "amount": spread_cost,
            }
        )
        rec.cash_flows.append(
            {"kind": "fees", "product": key[0], "contract_month": key[1], "amount": -fee}
        )
        rec.orders.append({**_order_row(order), "status": "filled", "fill_date": day})
    state.pending = still_pending


def settle_expiries(
    state: AccountState,
    view: MarketView,
    day: date,
    cfg: Config,
    rec: DayRecord,
    costs: CostModel | None = None,
) -> None:
    for key in list(state.positions):
        product, cm = key
        if _tradable(day, cm):
            continue
        spec = _spec(cfg, product)
        idx = view.published_index(spec.underlying_index)
        final = final_settlement(idx, spec, parse_month(cm))
        if final is None:
            continue
        pos = state.positions.pop(key)
        amt = pos.qty * (final - pos.mark) * spec.gpu_hours_per_contract
        state.cash += amt
        rec.cash_flows.append(
            {"kind": "final_settlement", "product": product, "contract_month": cm, "amount": amt}
        )
        if costs is not None:
            sfee = costs.settlement_fee(pos.qty, product)
            if sfee:
                state.cash -= sfee
                rec.cash_flows.append(
                    {"kind": "fees", "product": product, "contract_month": cm, "amount": -sfee}
                )
        rec.events.append(
            {"kind": "expired", "detail": f"{product} {cm} qty={pos.qty} final={final:.4f}"}
        )


def risk_check(state: AccountState, day_pnl: float, day: date, cfg: Config, rec: DayRecord) -> bool:
    """Update peak; return True if positions must be flattened now."""
    r = cfg.risk
    state.peak_equity = max(state.peak_equity, state.equity)
    flatten = False
    if day_pnl <= -r.daily_loss_limit:
        state.halted_until = day + timedelta(days=r.halt_days_after_daily_breach + 1)
        rec.events.append({"kind": "daily_loss_breach", "detail": f"pnl={day_pnl:.2f}"})
        flatten = True
    if state.peak_equity - state.equity >= r.max_drawdown and not state.killed:
        state.killed = True
        rec.events.append(
            {"kind": "max_drawdown_breach", "detail": f"dd={state.peak_equity - state.equity:.2f}"}
        )
        flatten = True
    return flatten


def clip_targets(targets: dict[Key, int], cfg: Config, rec: DayRecord) -> dict[Key, int]:
    """Enforce per-month and gross position limits by scaling toward zero."""
    r = cfg.risk
    out: dict[Key, int] = {}
    for k, q in targets.items():
        c = max(-r.max_contracts_per_month, min(r.max_contracts_per_month, int(q)))
        if c != q:
            rec.events.append({"kind": "limit_clip_month", "detail": f"{k} {q}->{c}"})
        if c != 0:
            out[k] = c
    gross = sum(abs(q) for q in out.values())
    if gross > r.max_gross_contracts:
        scale = r.max_gross_contracts / gross
        scaled = {k: math.trunc(q * scale) for k, q in out.items()}
        rec.events.append(
            {"kind": "limit_clip_gross", "detail": f"{gross}->{sum(map(abs, scaled.values()))}"}
        )
        out = {k: q for k, q in scaled.items() if q != 0}
    return out


def margin_ok(state: AccountState, targets: dict[Key, int], cfg: Config) -> bool:
    req = sum(abs(q) * _spec(cfg, k[0]).initial_margin_per_contract for k, q in targets.items())
    return req <= state.equity


def risk_reducing_only(state: AccountState, targets: dict[Key, int]) -> dict[Key, int]:
    """Keep only target changes that shrink or close existing positions."""
    out: dict[Key, int] = {}
    for key in set(targets) | set(state.positions):
        cur = state.net_position(key)
        tgt = targets.get(key, 0)
        reduces = abs(tgt) <= abs(cur) and (tgt == 0 or (tgt > 0) == (cur > 0))
        q = tgt if reduces else cur
        if q != 0:
            out[key] = q
    return out


def _order_row(o: Order) -> dict[str, object]:
    return {
        "order_id": o.order_id,
        "decision_date": o.decision_date,
        "product": o.product,
        "contract_month": o.contract_month,
        "qty": o.qty,
        "reason": o.reason,
    }


def orders_for_targets(
    state: AccountState, targets: dict[Key, int], day: date, reason: str
) -> list[Order]:
    """Orders that move current positions to ``targets``; replaces pending orders."""
    keys = set(targets) | set(state.positions)
    orders: list[Order] = []
    for key in sorted(keys):
        if not _tradable(day, key[1]):
            continue
        delta = targets.get(key, 0) - state.net_position(key)
        if delta != 0:
            state.order_seq += 1
            orders.append(Order(f"o{state.order_seq:07d}", day, key[0], key[1], delta, reason))
    return orders


# ----------------------------------------------------------------------------
# Daily cycle
# ----------------------------------------------------------------------------
def run_day(
    state: AccountState,
    day: date,
    market: MarketData,
    strategy: Strategy,
    cfg: Config,
    costs: CostModel,
) -> DayRecord:
    """Advance ``state`` through calendar day ``day``. Mutates ``state``."""
    if state.last_date is not None and day <= state.last_date:
        raise ValueError(f"day {day} already processed (last {state.last_date})")
    rec = DayRecord(day=day)
    equity_open = state.equity
    settles = market.settlement_on(day)
    view = market.view(end_of_day_utc(day))

    if settles:
        mark_to_market(state, settles, cfg, rec)
        fill_pending(state, settles, day, cfg, costs, rec)
    settle_expiries(state, view, day, cfg, rec, costs)

    day_pnl = state.equity - equity_open
    must_flatten = risk_check(state, day_pnl, day, cfg, rec)
    halted = state.killed or (state.halted_until is not None and day < state.halted_until)

    if settles:
        if must_flatten or halted:
            for o in state.pending:
                rec.orders.append({**_order_row(o), "status": "cancelled", "fill_date": None})
            state.pending = orders_for_targets(state, {}, day, "risk_flatten")
        else:
            targets = clip_targets(strategy(view, copy_state(state)), cfg, rec)
            if not margin_ok(state, targets, cfg):
                rec.events.append({"kind": "margin_reject", "detail": str(targets)})
                targets = risk_reducing_only(state, targets)
            for o in state.pending:
                rec.orders.append({**_order_row(o), "status": "replaced", "fill_date": None})
            state.pending = orders_for_targets(state, targets, day, "strategy")
        for o in state.pending:
            rec.orders.append({**_order_row(o), "status": "pending", "fill_date": None})

    state.last_date = day
    rec.account = {
        "cash": state.cash,
        "equity": state.equity,
        "peak_equity": state.peak_equity,
        "drawdown": state.peak_equity - state.equity,
        "day_pnl": day_pnl,
        "gross_contracts": state.gross_contracts(),
        "n_pending": len(state.pending),
        "halted": bool(halted),
        "killed": state.killed,
        "trading_day": bool(settles),
    }
    rec.positions = [
        {"product": k[0], "contract_month": k[1], "qty": p.qty, "mark": p.mark}
        for k, p in sorted(state.positions.items())
    ]
    return rec


def flat_strategy(view: MarketView, state: AccountState) -> dict[Key, int]:
    """Baseline strategy: hold nothing."""
    del view, state
    return {}


def copy_state(state: AccountState) -> AccountState:
    return replace(
        state,
        positions={k: Position(p.qty, p.mark) for k, p in state.positions.items()},
        pending=list(state.pending),
    )
