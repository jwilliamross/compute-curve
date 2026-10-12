"""Power of the claim-6c forward shadow test (docs/statarb_forward_power.md).

A design calculation on already-spent confirmation returns. It tests no
hypothesis. The confirmation's daily net series are resampled jointly in
circular blocks, each shifted so its true mean is ``theta`` times the
observed mean, and the frozen forward rule (statarb_plan3.md sections 6 and
7) is applied to each resample: one-sided Newey-West p, Holm over the two
strategies within each accounting, mean > 0, stress mean > 0, and a pass
under both accountings.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from compute_curve.backtest.bootstrap import circular_block_indices
from compute_curve.claim4 import stats as cs
from compute_curve.config import Config
from compute_curve.statarb import evaluate as ev
from compute_curve.statarb.engine import run_book, run_book_shares

ACCOUNTINGS = ("weights", "shares")


@dataclass(frozen=True)
class Series:
    """Aligned daily net returns of one strategy under one accounting."""

    strategy: str
    accounting: str
    base: np.ndarray
    stress: np.ndarray


def holm(pvalues: Sequence[float]) -> list[float]:
    """Holm step-down adjusted p-values (same values as ``claim4.stats.holm`` for finite p).

    Local because statsmodels' ``multipletests`` runs ``gc.collect`` on each
    call, which makes thousands of resamples take hours.
    """
    p = np.asarray(pvalues, dtype=float)
    m = p.size
    adj = np.empty(m)
    running = 0.0
    for rank, i in enumerate(np.argsort(p)):
        running = max(running, min(1.0, (m - rank) * p[i]))
        adj[i] = running
    return adj.tolist()


def _passes(base: np.ndarray, stress: np.ndarray, lag: int) -> tuple[float, bool]:
    p = ev.hac_p_one_sided(base, lag)
    ok = bool(base.mean() > 0 and stress.mean() > 0)
    return (p if np.isfinite(p) else 1.0), ok


def forward_rule(samples: Sequence[Series], lag: int, alpha: float) -> dict[str, bool]:
    """The frozen forward rule on one sample: strategy -> passed under both accountings."""
    passed: dict[str, list[bool]] = {}
    for acc in ACCOUNTINGS:
        block = [s for s in samples if s.accounting == acc]
        stats = [_passes(s.base, s.stress, lag) for s in block]
        adj = holm([p for p, _ in stats])
        for s, (_, ok), pa in zip(block, stats, adj, strict=True):
            passed.setdefault(s.strategy, []).append(bool(pa <= alpha and ok))
    return {k: all(v) for k, v in passed.items()}


def pass_probability(
    series: Sequence[Series],
    n_sessions: int,
    theta: float,
    n_sims: int,
    block: int,
    lag: int,
    alpha: float,
    seed: int,
) -> dict[str, float]:
    """P(forward pass) per strategy if each true mean is ``theta`` x its observed mean.

    The shift keeps each series' volatility, autocorrelation and cross-correlation
    (joint block resampling); the stress series gets the same shift as its base
    series, so the base-minus-stress cost gap is unchanged.
    """
    lengths = {s.base.size for s in series} | {s.stress.size for s in series}
    if len(lengths) != 1:
        raise ValueError("series must be aligned")
    n = lengths.pop()
    shift = {id(s): (theta - 1.0) * s.base.mean() for s in series}
    rng = np.random.default_rng(seed)
    wins: dict[str, int] = {}
    for _ in range(n_sims):
        idx = np.concatenate(
            [circular_block_indices(n, block, rng) for _ in range(int(np.ceil(n_sessions / n)))]
        )[:n_sessions]
        sample = [
            Series(
                s.strategy,
                s.accounting,
                s.base[idx] + shift[id(s)],
                s.stress[idx] + shift[id(s)],
            )
            for s in series
        ]
        for k, v in forward_rule(sample, lag, alpha).items():
            wins[k] = wins.get(k, 0) + int(v)
    return {k: v / n_sims for k, v in wins.items()}


# ---------------------------------------------------------------------------
# Runner (reads local cached bars; spent confirmation window only)
# ---------------------------------------------------------------------------
THETAS = (0.0, 0.25, 0.5, 0.75, 1.0)
LENGTHS = (60, 120, 250)


def confirmation_series(cfg: Config) -> list[Series]:  # pragma: no cover - reads local data
    """Rebuild claim 6c's pooled daily series exactly as ``confirm_strategy`` pools them."""
    from compute_curve.statarb import pipeline as sp  # noqa: PLC0415

    sa, c4 = cfg.statarb, cfg.claim4
    if sa is None or c4 is None:
        raise RuntimeError("[statarb] and [claim4] config are required")
    d = sp.paths(cfg)["dir"]
    spreads = pd.Series(
        json.loads((d / "claim6c_spreads.json").read_text())["median_quoted_spread"], dtype=float
    )
    base_c, _, stress_c = sp.quoted_costs(sa, spreads)
    prices = sp.load_prices(cfg)
    groups = c4.universe.buckets()
    start, end = sa.confirm
    out = []
    for name, p0 in {"SA2-M": prices, "SA2-L": sp.subset(prices, sp.LIQUID_6C)}.items():
        p = p0.until(end)
        lo, hi = sp.set_bounds(p, start)
        trades = [
            sp.cell_trades(p, sa, groups, "SA2", a, b, lo, hi) for a, b in sp.REGIONS_6C[name]
        ]
        for acc, book in (("weights", run_book), ("shares", run_book_shares)):
            base = ev.pool([sp.in_set(book(t, p.opens, p.closes, base_c), start) for t in trades])
            stress = ev.pool(
                [sp.in_set(book(t, p.opens, p.closes, stress_c), start) for t in trades]
            )
            out.append(Series(name, acc, base.to_numpy(float), stress.to_numpy(float)))
    return out


def dependence(x: np.ndarray, lag: int) -> dict[str, float]:
    """t of the mean (iid, Newey-West, block means) and the sum of autocorrelations 1..lag."""
    e = x - x.mean()
    ac = [float(e[k:] @ e[:-k] / (e @ e)) for k in range(1, lag + 1)]
    t_iid = float(x.mean() / (x.std(ddof=0) / np.sqrt(x.size)))
    t_hac = float(x.mean() / cs.hac_mean_se(x, lag))
    out = {"t_iid": t_iid, "t_hac": t_hac, "sum_autocorr": float(sum(ac))}
    for b in (5, 10, 20):  # t of the mean of non-overlapping block means
        m = x[: x.size // b * b].reshape(-1, b).mean(axis=1)
        out[f"t_block{b}"] = float(x.mean() / (m.std(ddof=1) / np.sqrt(m.size)))
    return out


def run_power(cfg: Config, n_sims: int = 2000) -> dict[str, Any]:  # pragma: no cover
    sa = cfg.statarb
    if sa is None:
        raise RuntimeError("[statarb] config is required")
    series = confirmation_series(cfg)
    observed = {
        f"{s.strategy} ({s.accounting})": {
            "n": int(s.base.size),
            "mean_bps": float(s.base.mean() * 1e4),
            "sharpe_daily": float(s.base.mean() / s.base.std(ddof=1)),
        }
        | dependence(s.base, sa.hac_lag)
        for s in series
    }
    grid: dict[str, dict[str, dict[str, float]]] = {}
    for n in LENGTHS:
        for th in THETAS:
            grid.setdefault(str(n), {})[f"{th:g}"] = pass_probability(
                series, n, th, n_sims, sa.boot_block, sa.hac_lag, sa.alpha, cfg.project.seed
            )
    return {
        "observed": observed,
        "pass_probability": grid,
        "n_sims": n_sims,
        "block": sa.boot_block,
        "seed": cfg.project.seed,
    }


def render_power(r: dict[str, Any]) -> str:
    lines = [
        "# Claim 6c forward test: power (design calculation, no test)",
        "",
        f"Joint circular block bootstrap (block {r['block']}, {r['n_sims']} resamples, seed "
        f"{r['seed']}) of the spent confirmation series, each shifted to theta x its observed "
        "mean; the frozen forward rule is applied to each resample. Method: "
        "docs/statarb_forward_power.md.",
        "",
        "| Series | Mean (bps/day) | Daily Sharpe | t (iid) | t (Newey-West) | "
        "t (5/10/20-day block means) | Sum of autocorrelations, lags 1-10 |",
        "|---|---|---|---|---|---|---|",
    ]
    for k, v in r["observed"].items():
        blocks = "/".join(f"{v[f't_block{b}']:.2f}" for b in (5, 10, 20))
        lines.append(
            f"| {k} | {v['mean_bps']:.2f} | {v['sharpe_daily']:.3f} | {v['t_iid']:.2f} | "
            f"{v['t_hac']:.2f} | {blocks} | {v['sum_autocorr']:.2f} |"
        )
    lines += ["", "## P(forward pass under both accountings)", ""]
    thetas = list(next(iter(r["pass_probability"].values())))
    lines += [
        "| Sessions | Strategy | " + " | ".join(f"theta = {t}" for t in thetas) + " |",
        "|---|---|" + "---|" * len(thetas),
    ]
    for n, by_theta in r["pass_probability"].items():
        for strat in ("SA2-M", "SA2-L"):
            cells = " | ".join(f"{by_theta[t][strat]:.3f}" for t in thetas)
            lines.append(f"| {n} | {strat} | {cells} |")
    lines += [
        "",
        "theta = 0 is the false-pass rate if there is no edge; theta = 1 assumes the "
        "confirmation's edge persists in full.",
    ]
    return "\n".join(lines) + "\n"


def write_power(cfg: Config) -> Path:  # pragma: no cover - reads local data
    from compute_curve.statarb.pipeline import paths  # noqa: PLC0415

    r = run_power(cfg)
    d = paths(cfg)["dir"]
    (d / "forward_power.json").write_text(json.dumps(r, indent=2))
    out = d / "forward_power.md"
    out.write_text(render_power(r))
    return out
