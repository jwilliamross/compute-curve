"""Markdown reports for claim 6 (every number with costs, variants and intervals)."""

from __future__ import annotations

from typing import Any

import numpy as np

from compute_curve.config import StatArbConfig

LABEL = {
    "SA1": ("pairs (cointegration)", "lookback L", "entry |z|"),
    "SA2": ("residual reversal vs XLK (Avellaneda-Lee)", "window W", "entry |s|"),
    "SA2-M": ("residual reversal, all names, measured costs", "window W", "entry |s|"),
    "SA2-L": ("residual reversal, 10 lowest-spread names, measured costs", "window W", "entry |s|"),
}


def _f(v: Any, nd: int = 2) -> str:
    try:
        x = float(v)
    except (TypeError, ValueError):
        return "n/a"
    return "n/a" if not np.isfinite(x) else f"{x:.{nd}f}"


def _costs(sa: StatArbConfig) -> str:
    return (
        f"Costs (ASSUMPTIONS): stocks {sa.stock_side_bps:g} bps per side, XLK "
        f"{sa.etf_side_bps:g} bps, sell fee {sa.sell_fee_bps:g} bp, borrow "
        f"{sa.borrow_annual:.0%}/yr on shorts. Stress: costs x{sa.stress_multiplier:g}, "
        f"borrow {sa.stress_borrow_annual:.0%}/yr."
    )


def render_exploration(results: list[Any], sa: StatArbConfig, n_cells: int) -> str:
    lines = [
        "# Claim 6: statistical arbitrage, exploration set",
        "",
        f"Sessions {sa.explore[0]} to {sa.explore[1]}. Plan: docs/statarb_plan.md. "
        f"Variants: {n_cells} grid cells (project total 255). Simulation only.",
        "",
        _costs(sa),
        "",
        "The universe was chosen in 2026 for its AI exposure (survivorship and "
        "selection, disclosed). Equity returns were used before in claims 4 and 5 "
        "with GPU signals; no stat-arb signal had been computed.",
        "",
    ]
    for r in results:
        name, a1, a2 = LABEL[r.strategy]
        ax1, ax2 = r.axes
        lines += [
            f"## {r.strategy}: {name}",
            "",
            f"Annualized net Sharpe by cell ({a1} down, {a2} across):",
            "",
            "| | " + " | ".join(f"{x:g}" for x in ax2) + " |",
            "|---" * (len(ax2) + 1) + "|",
        ]
        for i, x in enumerate(ax1):
            lines.append(f"| {x:g} | " + " | ".join(_f(v) for v in r.grid_sr_annual[i]) + " |")
        reg = ", ".join(f"({a:g}, {b:g})" for a, b in r.region) or "none"
        p = r.pooled
        lines += [
            "",
            f"Region (within one SE of the best smoothed cell): {reg}. "
            "The pooled candidate is the equal-weight average of these cells.",
            "",
            "| Pooled candidate | Value |",
            "|---|---|",
            f"| Sessions / trades | {int(p.get('n', 0))} / {r.n_trades} |",
            f"| Mean daily net return | {_f(p.get('mean', np.nan) * 1e4, 2)} bps |",
            f"| 95% block-bootstrap CI of the mean | [{_f(r.ci_mean[0] * 1e4)}, "
            f"{_f(r.ci_mean[1] * 1e4)}] bps |",
            f"| Annualized net Sharpe (non-IID SE) | {_f(p.get('sr_annual'))} "
            f"({_f(p.get('sr_annual_se'))}) |",
            f"| 95% block-bootstrap CI of the Sharpe | [{_f(r.ci_sharpe[0])}, "
            f"{_f(r.ci_sharpe[1])}] |",
            f"| Deflated Sharpe (K = {n_cells}) | {_f(r.dsr, 3)} |",
            f"| One-sided Newey-West p (descriptive here) | {_f(r.hac_p, 3)} |",
            f"| Skew / kurtosis / lag-1 autocorrelation | {_f(p.get('skew'))} / "
            f"{_f(p.get('kurt'))} / {_f(p.get('rho'))} |",
            f"| Effective observations | {_f(p.get('effective_n'), 0)} |",
            f"| Random-entry Monte Carlo: share of {sa.n_null} null Sharpes below the real one "
            f"| {_f(r.null_percentile, 3)} |",
            f"| Max drawdown, 95th percentile of {sa.n_boot_paths} bootstrap paths "
            f"| {_f(r.drawdown_95 * 100, 1)}% |",
            f"| Break-even stock cost per side | {_f(r.breakeven_bps, 1)} bps |",
            f"| Mean daily return at stress costs | {_f(r.stress_mean * 1e4)} bps |",
            "",
            f"**{'Survives' if r.survives else 'Does not survive'}.** "
            + ("; ".join(r.notes) if r.notes else "All survival rules pass."),
            "",
        ]
    return "\n".join(lines) + "\n"


def render_confirmation(rows: list[dict[str, Any]], sa: StatArbConfig) -> str:
    lines = [
        "# Claim 6: statistical arbitrage, one-shot confirmation",
        "",
        f"Sessions {sa.confirm[0]} to {sa.confirm[1]}, frozen pooled regions. {_costs(sa)}",
        "",
    ]
    if not rows:
        lines.append("No strategy survived the exploration, so nothing was confirmed.")
    for r in rows:
        m = r["moments"]
        lines += [
            f"## {r['strategy']}",
            "",
            f"- Sessions / trades: {r['n_sessions']} / {r['n_trades']}",
            f"- Mean daily net return {_f(m['mean'] * 1e4)} bps, 95% CI "
            f"[{_f(r['ci_mean'][0] * 1e4)}, {_f(r['ci_mean'][1] * 1e4)}] bps",
            f"- Annualized net Sharpe {_f(m['sr_annual'])} (SE {_f(m['sr_annual_se'])}), "
            f"bootstrap CI [{_f(r['ci_sharpe'][0])}, {_f(r['ci_sharpe'][1])}]",
            f"- C1: one-sided Newey-West p {_f(r['hac_p_one_sided'], 3)}, Holm "
            f"{_f(r['p_holm'], 3)}: {'pass' if r['c1'] else 'fail'}",
            f"- C2: mean at stress costs {_f(r['stress_mean'] * 1e4)} bps: "
            f"{'pass' if r['c2'] else 'fail'}",
            f"- **Verdict: {r['verdict']}.**",
            "",
        ]
    return "\n".join(lines) + "\n"
