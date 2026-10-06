"""Claim-4 paper strategy: pair weights, cohort targets, hard limits, orders.

Pure functions only; the Alpaca client is called from ``claim4.pipeline``.
Rules are pre-registered in docs/claim4_plan.md section 9.

* A pair is the category-balanced basket against XLK. Direction +1 is long
  the basket and short XLK; -1 is the reverse.
* Each session's decision is a cohort held for ``h`` sessions with weight
  ``1/h``; the target for a session sums the active cohorts.
* Targets are scaled down proportionally, both legs together, until every
  symbol is within ``max_position_usd`` and gross exposure is within
  ``max_gross_exposure_usd``.
* Positions that would flip from long to short (or back) are only closed in
  that run; the opposite side opens on the next run. This avoids Alpaca's
  wash-trade rejections and is logged.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

from compute_curve.config import Claim4Config

CLIENT_PREFIX = "c4"
MIN_ORDER_USD = 25.0


def pair_weights(
    direction: int, cfg: Claim4Config, shortable: Mapping[str, bool] | None = None
) -> dict[str, float]:
    """Signed weights per unit of pair notional per leg.

    Basket weights sum to ``direction``; the benchmark gets ``-direction``.
    When the basket is short, names not shortable are dropped and the rest of
    the basket is re-weighted (a bucket with no shortable name loses its
    third, which goes to the other buckets).
    """
    if direction == 0:
        return {}
    buckets = cfg.universe.buckets()
    if direction < 0 and shortable is not None:
        buckets = {k: [s for s in v if shortable.get(s, False)] for k, v in buckets.items()}
    live = {k: v for k, v in buckets.items() if v}
    if not live:
        return {}
    w: dict[str, float] = {}
    for members in live.values():
        for s in members:
            w[s] = direction * (1.0 / len(live)) / len(members)
    w[cfg.benchmark] = -float(direction)
    return w


def cohort_target(
    directions: Sequence[int],
    horizon: int,
    cfg: Claim4Config,
    shortable: Mapping[str, bool] | None = None,
) -> dict[str, float]:
    """Target USD notional per symbol from the active cohorts' directions.

    ``directions`` holds the decisions of the last ``horizon`` sessions,
    including the one being decided (older first; missing ones are 0).
    """
    per_cohort = cfg.risk.pair_notional_usd / horizon
    target: dict[str, float] = {}
    for d in list(directions)[-horizon:]:
        for sym, wt in pair_weights(int(d), cfg, shortable).items():
            target[sym] = target.get(sym, 0.0) + wt * per_cohort
    return {k: v for k, v in target.items() if abs(v) > 1e-9}


@dataclass
class Scaled:
    target: dict[str, float]
    factor: float
    notes: list[str] = field(default_factory=list)


def apply_limits(target: Mapping[str, float], cfg: Claim4Config) -> Scaled:
    """Scale all targets by one factor so every hard limit holds."""
    r = cfg.risk
    if not target:
        return Scaled({}, 1.0)
    biggest = max(abs(v) for v in target.values())
    gross = sum(abs(v) for v in target.values())
    factor = 1.0
    notes = []
    if biggest > r.max_position_usd:
        factor = min(factor, r.max_position_usd / biggest)
        notes.append(f"scaled for max position (largest {biggest:,.0f} USD)")
    if gross > r.max_gross_exposure_usd:
        factor = min(factor, r.max_gross_exposure_usd / gross)
        notes.append(f"scaled for max gross exposure ({gross:,.0f} USD)")
    return Scaled({k: v * factor for k, v in target.items()}, factor, notes)


@dataclass(frozen=True)
class Order:
    symbol: str
    side: str  # "buy" or "sell"
    qty: float
    reason: str

    def payload(self, session: str, run_stamp: str) -> dict[str, str]:
        return {
            "symbol": self.symbol,
            "qty": _fmt_qty(self.qty),
            "side": self.side,
            "type": "market",
            "time_in_force": "day",
            "client_order_id": f"{CLIENT_PREFIX}-{session}-{self.symbol}-{run_stamp}",
        }


def _fmt_qty(q: float) -> str:
    return f"{q:.6f}".rstrip("0").rstrip(".") if q != int(q) else str(int(q))


def orders_for_targets(
    target_usd: Mapping[str, float],
    current_qty: Mapping[str, float],
    price: Mapping[str, float],
    fractionable: Mapping[str, bool],
    managed: Sequence[str],
) -> tuple[list[Order], list[str]]:
    """Orders that move managed symbols from ``current_qty`` toward the targets.

    Long targets in fractionable names use fractional quantities; short
    targets and non-fractionable names use whole shares (rounded toward
    zero). A position whose sign would flip is only closed this run.
    Symbols outside ``managed`` are never touched.
    """
    orders: list[Order] = []
    notes: list[str] = []
    for sym in sorted(set(managed)):
        cur = float(current_qty.get(sym, 0.0))
        tgt_usd = float(target_usd.get(sym, 0.0))
        px = price.get(sym)
        if tgt_usd != 0.0 and (px is None or not px > 0):
            notes.append(f"{sym}: no price; skipped")
            continue
        tgt = 0.0 if tgt_usd == 0.0 else tgt_usd / float(px)  # type: ignore[arg-type]
        if tgt > 0 and fractionable.get(sym, False):
            tgt = math.floor(tgt * 1e6) / 1e6
        else:
            tgt = float(math.trunc(tgt))
        if cur != 0.0 and tgt != 0.0 and math.copysign(1, cur) != math.copysign(1, tgt):
            notes.append(f"{sym}: direction flips; closing only this run")
            tgt = 0.0
        delta = tgt - cur
        if abs(delta) < 1e-9:
            continue
        notional = abs(delta) * float(px) if px else float("inf")
        if tgt != 0.0 and notional < MIN_ORDER_USD:
            continue  # too small to be worth an order; closing orders always go
        orders.append(Order(sym, "buy" if delta > 0 else "sell", abs(delta), "rebalance"))
    return orders, notes


def flatten_orders(current_qty: Mapping[str, float], managed: Sequence[str]) -> list[Order]:
    """Close every managed position."""
    out = []
    for sym in sorted(set(managed)):
        q = float(current_qty.get(sym, 0.0))
        if q != 0.0:
            out.append(Order(sym, "sell" if q > 0 else "buy", abs(q), "flatten"))
    return out
