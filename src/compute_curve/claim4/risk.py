"""Account-level hard limits for the claim-4 paper account (docs/claim4_plan.md 9-10).

Stateless by design: the CI runner keeps nothing between runs, so every
check is recomputed from Alpaca's own account and portfolio history.

* Kill switch: ``claim4.risk.kill_switch = true`` in config, or the
  environment variable ``COMPUTE_CURVE_KILL_SWITCH=1``.
* Drawdown latch (K2): if equity has ever been ``max_drawdown_usd`` or more
  below its running peak since ``paper_start``, the latch is on. Because the
  breach stays in the history, the latch persists until the owner changes
  ``paper_start`` or the limit.
* Daily loss halt (K3): today's P&L at or below ``-daily_loss_limit_usd``,
  or a breach within the last ``halt_sessions_after_daily_breach`` sessions.

Reports show percentages only (decision D29).
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from typing import Any

import numpy as np

from compute_curve.config import Claim4Config

KILL_ENV = "COMPUTE_CURVE_KILL_SWITCH"


@dataclass
class RiskState:
    kill_switch: bool = False
    drawdown_latched: bool = False
    daily_breach_today: bool = False
    halted_after_breach: bool = False
    daily_pnl_pct: float = float("nan")
    drawdown_pct: float = float("nan")
    notes: list[str] = field(default_factory=list)

    @property
    def blocks_new_positions(self) -> bool:
        return (
            self.kill_switch
            or self.drawdown_latched
            or self.daily_breach_today
            or self.halted_after_breach
        )

    @property
    def requires_flatten(self) -> bool:
        return self.kill_switch or self.drawdown_latched or self.daily_breach_today


def _f(v: Any) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return float("nan")


def equity_series(history: Mapping[str, Any], since: date) -> tuple[np.ndarray, np.ndarray]:
    """(equity, profit_loss) arrays from Alpaca portfolio history, from ``since`` on."""
    ts = history.get("timestamp") or []
    eq = history.get("equity") or []
    pl = history.get("profit_loss") or [None] * len(ts)
    keep_e, keep_p = [], []
    for t, e, p in zip(ts, eq, pl, strict=False):
        day = datetime.fromtimestamp(int(t), tz=UTC).date()
        if day < since or e is None or not _f(e) > 0:
            continue
        keep_e.append(_f(e))
        keep_p.append(_f(p))
    return np.asarray(keep_e, dtype=float), np.asarray(keep_p, dtype=float)


def evaluate_risk(
    account: Mapping[str, Any],
    history: Mapping[str, Any],
    cfg: Claim4Config,
    env: Mapping[str, str] | None = None,
) -> RiskState:
    e = os.environ if env is None else env
    r = cfg.risk
    st = RiskState()
    if r.kill_switch:
        st.kill_switch = True
        st.notes.append("kill switch set in config")
    if e.get(KILL_ENV, "") == "1":
        st.kill_switch = True
        st.notes.append(f"kill switch set by {KILL_ENV}")

    equity, last_equity = _f(account.get("equity")), _f(account.get("last_equity"))
    if np.isfinite(equity) and np.isfinite(last_equity) and last_equity > 0:
        pnl = equity - last_equity
        st.daily_pnl_pct = 100.0 * pnl / last_equity
        if pnl <= -r.daily_loss_limit_usd:
            st.daily_breach_today = True
            st.notes.append("daily loss limit breached today")

    eq, pl = equity_series(history, cfg.paper_start)
    if np.isfinite(equity) and equity > 0:
        eq = np.append(eq, equity)
    if eq.size:
        peak = np.maximum.accumulate(eq)
        dd = peak - eq
        st.drawdown_pct = float(100.0 * dd[-1] / peak[-1]) if peak[-1] > 0 else float("nan")
        if np.any(dd >= r.max_drawdown_usd):
            st.drawdown_latched = True
            st.notes.append("maximum drawdown breached since paper_start; latched")

    n = r.halt_sessions_after_daily_breach
    recent = pl[-n:] if n > 0 and pl.size else np.array([])
    if recent.size and np.any(recent[np.isfinite(recent)] <= -r.daily_loss_limit_usd):
        st.halted_after_breach = True
        st.notes.append(f"daily loss breach within the last {n} session(s); no new entries")
    return st
