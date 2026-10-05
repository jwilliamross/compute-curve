"""Trading signals wired to the paper engine, gated by out-of-sample validation.

Each signal computes a prediction every trading day. It contributes target
positions only if it is listed in ``signals.trade`` *and* present in the
validated set loaded from ``var/validation.json``. Otherwise it is in shadow
mode: the prediction is returned for logging, and the target is flat.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from compute_curve.config import Config
from compute_curve.contracts import parse_month
from compute_curve.models import nowcast as nc
from compute_curve.models import relative_value as rv
from compute_curve.paper.engine import AccountState, Key, Strategy
from compute_curve.paper.market import MarketView


@dataclass
class SignalBook:
    """Collects shadow predictions made during a run for the ledger."""

    rows: list[dict[str, object]] = field(default_factory=list)

    def record(self, **kw: object) -> None:
        self.rows.append(kw)


def load_validated(path: Path) -> set[str]:
    """Names of signals that passed their out-of-sample test. Empty if no file."""
    if not path.exists():
        return set()
    data = json.loads(path.read_text())
    return {k for k, v in data.get("signals", {}).items() if v.get("validated") is True}


def round_trip_cost_per_gpu_hour(cfg: Config, product: str) -> float:
    spec = cfg.contracts[product]
    c = cfg.costs
    per_side = (c.half_spread_ticks + c.slippage_ticks) * spec.tick_size
    fee = spec.exchange_fee_per_contract + c.broker_clearing_fee_per_contract
    per_side += fee / spec.gpu_hours_per_contract
    return 2 * per_side


def front_month(view: MarketView, product: str) -> str | None:
    settles = view.latest_settles()
    months = sorted(m for p, m in settles if p == product)
    return months[0] if months else None


def nowcast_targets(
    view: MarketView, cfg: Config, book: SignalBook, active: bool
) -> dict[Key, int]:
    targets: dict[Key, int] = {}
    settles = view.latest_settles()
    for product, spec in cfg.contracts.items():
        cm = front_month(view, product)
        if cm is None:
            continue
        month = parse_month(cm)
        preds = nc.nowcast_all(view, spec, spec.gpu_model, month)
        settle = settles[(product, cm)]
        model = preds.get("own_bridge")
        threshold = cfg.signals.nowcast_edge_multiple * round_trip_cost_per_gpu_hour(cfg, product)
        edge = (model - settle) if model is not None else None
        side = 0
        if edge is not None and abs(edge) > threshold:
            side = 1 if edge > 0 else -1
        book.record(
            signal="nowcast",
            decision_date=view.as_of.date(),
            product=product,
            contract_month=cm,
            settle=settle,
            prediction=model,
            baseline_last_value=preds.get("last_value"),
            baseline_mtd_carry=preds.get("mtd_carry"),
            edge=edge,
            threshold=threshold,
            side=side,
            active=active,
        )
        if active and side != 0:
            targets[(product, cm)] = side * cfg.signals.nowcast_size
    return targets


def _settle_history(view: MarketView, product: str, offset: int) -> dict[date, tuple[str, float]]:
    """Per trade date, the (month, settle) of the ``offset``-th listed contract."""
    s = view.settlements()
    out: dict[date, tuple[str, float]] = {}
    if s.empty:
        return out
    for d, grp in s.loc[s["product"] == product].groupby("trade_date"):
        g = grp.sort_values("contract_month")
        if len(g) > offset:
            r = g.iloc[offset]
            out[d] = (str(r["contract_month"]), float(r["settle_price"]))
    return out


def rv_targets(
    view: MarketView,
    cfg: Config,
    state: AccountState,
    book: SignalBook,
    active: bool,
) -> dict[Key, int]:
    rc = cfg.relative_value
    off = cfg.signals.rv_contract_offset
    h1 = _settle_history(view, "GPU1", off)
    h2 = _settle_history(view, "GPU2", off)
    common = sorted(set(h1) & set(h2))
    if len(common) < rc.zscore_window_days + 1:
        book.record(
            signal="relative_value",
            decision_date=view.as_of.date(),
            status="insufficient_history",
            n=len(common),
            active=active,
        )
        return {}
    p1 = pd.Series({d: h1[d][1] for d in common})
    p2 = pd.Series({d: h2[d][1] for d in common})
    spread = rv.log_spread(p2, p1, rc.perf_ratio_b200_over_h100)
    z = float(rv.rolling_z(spread, rc.zscore_window_days).iloc[-1])
    m1, m2 = h1[common[-1]][0], h2[common[-1]][0]
    cur = state.net_position(("GPU2", m2))
    cur_side = int(np.sign(cur))
    side = rv.fade_signal(z, rc.entry_z, rc.exit_z, cur_side)
    book.record(
        signal="relative_value",
        decision_date=view.as_of.date(),
        product="GPU2/GPU1",
        contract_month=m2,
        prediction=z,
        side=side,
        active=active,
    )
    if not active or side == 0:
        return {}
    n2 = cfg.signals.rv_size_gpu2
    n1 = rv.hedge_contracts(n2, float(p2.iloc[-1]), float(p1.iloc[-1]))
    return {("GPU2", m2): side * n2, ("GPU1", m1): -side * n1}


def make_strategy(cfg: Config, validated: set[str], book: SignalBook) -> Strategy:
    """Combined strategy; each component trades only if listed and validated."""
    trade = set(cfg.signals.trade)

    def strategy(view: MarketView, state: AccountState) -> dict[Key, int]:
        targets: dict[Key, int] = {}
        for k, q in nowcast_targets(view, cfg, book, "nowcast" in trade & validated).items():
            targets[k] = targets.get(k, 0) + q
        for k, q in rv_targets(
            view, cfg, state, book, "relative_value" in trade & validated
        ).items():
            targets[k] = targets.get(k, 0) + q
        return {k: q for k, q in targets.items() if q != 0}

    return strategy
