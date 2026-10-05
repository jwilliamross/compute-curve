"""Tearsheet statistics with uncertainty and explicit cost assumptions.

Daily PnL is the change in equity on each processed calendar day; Sharpe
uses trading days only and annualizes by sqrt(252). Confidence intervals
use the circular block bootstrap. Capacity is a rough upper bound:
``participation x average daily volume`` contracts, with volume taken from
settlement data when present; otherwise it is reported as unknown.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
import pandas as pd

from compute_curve.backtest import variants
from compute_curve.backtest.bootstrap import block_bootstrap_ci
from compute_curve.config import Config
from compute_curve.paper.runner import RunResult
from compute_curve.reporting import frame_to_md

TRADING_DAYS = 252


def sharpe(x: np.ndarray) -> float:
    x = np.asarray(x, float)
    sd = x.std(ddof=1) if x.size > 1 else 0.0
    return float(np.sqrt(TRADING_DAYS) * x.mean() / sd) if sd > 0 else float("nan")


def max_drawdown(equity: np.ndarray) -> float:
    e = np.asarray(equity, float)
    if e.size == 0:
        return 0.0
    return float(np.max(np.maximum.accumulate(e) - e))


@dataclass(frozen=True)
class Tearsheet:
    run_id: str
    is_synthetic: bool
    cost_multiplier: float
    n_days: int
    n_trading_days: int
    total_pnl: float
    sharpe: float
    sharpe_ci: tuple[float, float]
    mean_daily_pnl_ci: tuple[float, float]
    max_drawdown: float
    contracts_traded: int
    turnover_per_day: float
    total_costs: float
    capacity_contracts: float | None
    variants_tried: int


def tearsheet(
    r: RunResult,
    cfg: Config,
    avg_daily_volume: float | None = None,
    participation: float = 0.05,
) -> Tearsheet:
    acct = r.account
    eq = acct["equity"].to_numpy(float)
    trading = acct.loc[acct["trading_day"].astype(bool)]
    daily = trading["day_pnl"].to_numpy(float)
    b = cfg.bootstrap
    if daily.size >= 10:
        s_ci = block_bootstrap_ci(
            daily, sharpe, b.n_boot, b.block_length, b.confidence, cfg.project.seed
        )
        m_ci = block_bootstrap_ci(
            daily, np.mean, b.n_boot, b.block_length, b.confidence, cfg.project.seed
        )
    else:
        s_ci = m_ci = (float("nan"), float("nan"))
    traded = int(r.fills["qty"].abs().sum()) if not r.fills.empty else 0
    costs = r.cash_flows.loc[r.cash_flows["kind"].isin(["fees", "spread_slippage"]), "amount"]
    return Tearsheet(
        run_id=r.run_id,
        is_synthetic=r.is_synthetic,
        cost_multiplier=r.cost_multiplier,
        n_days=len(acct),
        n_trading_days=len(trading),
        total_pnl=float(eq[-1] - cfg.risk.starting_cash) if eq.size else 0.0,
        sharpe=sharpe(daily) if daily.size > 1 else float("nan"),
        sharpe_ci=s_ci,
        mean_daily_pnl_ci=m_ci,
        max_drawdown=max_drawdown(eq),
        contracts_traded=traded,
        turnover_per_day=traded / max(len(trading), 1),
        total_costs=float(-costs.sum()) if not costs.empty else 0.0,
        capacity_contracts=participation * avg_daily_volume if avg_daily_volume else None,
        variants_tried=variants.count(),
    )


def cost_sensitivity(run: Callable[[float], RunResult], cfg: Config) -> pd.DataFrame:
    """Re-run the same backtest at each cost multiplier in config."""
    rows = []
    for m in cfg.costs.sensitivity_multipliers:
        ts = tearsheet(run(m), cfg)
        rows.append(
            {
                "cost_multiplier": m,
                "total_pnl": ts.total_pnl,
                "sharpe": ts.sharpe,
                "sharpe_ci_low": ts.sharpe_ci[0],
                "sharpe_ci_high": ts.sharpe_ci[1],
                "total_costs": ts.total_costs,
            }
        )
    return pd.DataFrame(rows)


def cost_assumptions_md(cfg: Config) -> str:
    c = cfg.costs
    lines = [
        "| Assumption | Value | Status |",
        "|---|---|---|",
        f"| Half-spread | {c.half_spread_ticks} ticks per side | assumption |",
        f"| Slippage | {c.slippage_ticks} ticks per side | assumption |",
        f"| All-in fee | USD {c.fee_per_contract:.2f} per contract per side | assumption |",
    ]
    for k, s in cfg.contracts.items():
        lines.append(
            f"| {k} tick | USD {s.tick_size}/GPU-h = USD {s.tick_value:.2f}/contract | "
            f"{'verified' if s.verified else 'unverified'} |"
        )
        lines.append(
            f"| {k} contract size | {s.gpu_hours_per_contract:g} GPU-hours | "
            f"{'verified' if s.verified else 'unverified'} |"
        )
    return "\n".join(lines)


def tearsheet_md(ts: Tearsheet, cfg: Config, sensitivity: pd.DataFrame | None = None) -> str:
    banner = (
        "> **SYNTHETIC DATA - ENGINE VALIDATION ONLY - NOT A RESULT.**\n\n"
        if ts.is_synthetic
        else ""
    )
    cap = (
        f"{ts.capacity_contracts:.1f} contracts/day"
        if ts.capacity_contracts
        else "unknown (no volume data)"
    )
    lo_m, hi_m = ts.mean_daily_pnl_ci
    lo_s, hi_s = ts.sharpe_ci
    out = [
        f"# Tearsheet: {ts.run_id}",
        "",
        banner
        + f"Cost multiplier: {ts.cost_multiplier}. "
        + f"Variants tried project-wide: {ts.variants_tried}.",
        "",
        "| Metric | Value | 95% CI |",
        "|---|---|---|",
        f"| Days processed (trading) | {ts.n_days} ({ts.n_trading_days}) | |",
        f"| Total PnL (USD) | {ts.total_pnl:,.0f} | |",
        f"| Mean daily PnL (USD) | | [{lo_m:,.1f}, {hi_m:,.1f}] |",
        f"| Sharpe (annualized) | {ts.sharpe:.2f} | [{lo_s:.2f}, {hi_s:.2f}] |",
        f"| Max drawdown (USD) | {ts.max_drawdown:,.0f} | |",
        f"| Contracts traded | {ts.contracts_traded} | |",
        f"| Turnover (contracts/trading day) | {ts.turnover_per_day:.2f} | |",
        f"| Total costs (USD) | {ts.total_costs:,.0f} | |",
        f"| Capacity estimate | {cap} | |",
        "",
        "## Cost assumptions",
        "",
        cost_assumptions_md(cfg),
    ]
    if sensitivity is not None and not sensitivity.empty:
        out += ["", "## Sensitivity to costs", "", frame_to_md(sensitivity, 2)]
    return "\n".join(out) + "\n"
