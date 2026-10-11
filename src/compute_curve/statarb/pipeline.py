"""Claim 6 pipeline: exploration (surface, region, pool), freeze, one-shot confirmation."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from compute_curve.backtest.bootstrap import block_bootstrap_ci
from compute_curve.claim4 import stats as cs
from compute_curve.config import Config, StatArbConfig
from compute_curve.statarb import evaluate as ev
from compute_curve.statarb.engine import TRADING_DAYS, Costs, Trade, run_book
from compute_curve.statarb.strategies import pairs_trades, residual_trades

ETF = "XLK"
STRATEGIES = ("SA1", "SA2")


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Prices:
    opens: pd.DataFrame  # sessions x symbols
    closes: pd.DataFrame
    signal_logp: pd.DataFrame  # log closes, NaN until a name is eligible

    def until(self, end: date) -> Prices:
        keep = self.closes.index <= pd.Timestamp(end)
        return Prices(self.opens[keep], self.closes[keep], self.signal_logp[keep])


def wide_prices(
    bars: pd.DataFrame, symbols: list[str], member_start: dict[str, date], min_history: int
) -> Prices:
    """Open/close frames and eligibility-masked log closes (plan section 2)."""
    b = bars.loc[bars["symbol"].isin(symbols)].copy()
    b["session"] = pd.to_datetime(b["session"])
    opens = b.pivot_table(
        index="session", columns="symbol", values="open", aggfunc="last"
    ).sort_index()
    closes = b.pivot_table(
        index="session", columns="symbol", values="close", aggfunc="last"
    ).sort_index()
    cols = [s for s in symbols if s in closes.columns]
    opens, closes = opens[cols], closes[cols]
    for sym, d in member_start.items():
        if sym in closes.columns:
            early = closes.index < pd.Timestamp(d)
            opens.loc[early, sym] = np.nan
            closes.loc[early, sym] = np.nan
    logp = np.log(closes)
    seen = logp.notna().cumsum()
    signal = logp.where(seen > min_history)
    return Prices(opens, closes, signal)


def costs_of(sa: StatArbConfig, scale: float = 1.0, borrow: float | None = None) -> Costs:
    return Costs(
        sa.stock_side_bps / 1e4 * scale,
        sa.etf_side_bps / 1e4 * scale,
        sa.sell_fee_bps / 1e4 * scale,
        sa.borrow_annual if borrow is None else borrow,
        ETF,
    )


# ---------------------------------------------------------------------------
# Cells
# ---------------------------------------------------------------------------
def grid_axes(sa: StatArbConfig, strategy: str) -> tuple[list[float], list[float]]:
    if strategy == "SA1":
        return [float(x) for x in sa.pairs.lookbacks], list(sa.pairs.entries)
    return [float(x) for x in sa.residual.windows], list(sa.residual.entries)


def cell_trades(
    prices: Prices,
    sa: StatArbConfig,
    groups: dict[str, list[str]],
    strategy: str,
    p1: float,
    p2: float,
    entry_lo: int,
    entry_hi: int,
) -> list[Trade]:
    if strategy == "SA1":
        return pairs_trades(
            prices.signal_logp,
            groups,
            int(p1),
            p2,
            sa.pairs,
            sa.max_positions,
            sa.max_hold,
            entry_lo,
            entry_hi,
        )
    return residual_trades(
        prices.signal_logp,
        ETF,
        int(p1),
        p2,
        sa.residual,
        sa.max_positions,
        sa.max_hold,
        entry_lo,
        entry_hi,
    )


def set_bounds(prices: Prices, start: date) -> tuple[int, int]:
    idx = prices.closes.index
    lo = int(np.searchsorted(idx, pd.Timestamp(start)))
    return lo, len(idx) - 1


def _mean(x: np.ndarray) -> float:
    return float(np.mean(x))


def _sharpe(x: np.ndarray) -> float:
    sd = float(np.std(x, ddof=1))
    return float(np.mean(x) / sd * np.sqrt(TRADING_DAYS)) if sd > 0 else float("nan")


def boot_ci(
    x: np.ndarray, block: int, seed: int, stat: Callable[[np.ndarray], float]
) -> tuple[float, float]:
    """Circular-block bootstrap 95% CI (2,000 draws)."""
    if x.size < 2 * block:
        return (float("nan"), float("nan"))
    return block_bootstrap_ci(x, stat, n_boot=2000, block_length=block, seed=seed)


def in_set(r: pd.Series, start: date) -> pd.Series:
    return r.loc[r.index >= pd.Timestamp(start)]


# ---------------------------------------------------------------------------
# Exploration
# ---------------------------------------------------------------------------
@dataclass
class StrategyResult:
    strategy: str
    axes: tuple[list[float], list[float]]
    grid_sr_annual: list[list[float]]
    region: list[tuple[float, float]]
    pooled: dict[str, float] = field(default_factory=dict)
    dsr: float = float("nan")
    hac_p: float = float("nan")
    ci_mean: tuple[float, float] = (float("nan"), float("nan"))
    ci_sharpe: tuple[float, float] = (float("nan"), float("nan"))
    null_percentile: float = float("nan")
    drawdown_95: float = float("nan")
    breakeven_bps: float = float("nan")
    stress_mean: float = float("nan")
    n_trades: int = 0
    survives: bool = False
    notes: list[str] = field(default_factory=list)


def random_entry_null(
    trades_by_cell: list[list[Trade]],
    prices: Prices,
    costs: Costs,
    lo: int,
    hi: int,
    start: date,
    n_sims: int,
    seed: int,
    tries: int = 50,
) -> np.ndarray:
    """Pooled Sharpe when every trade keeps its legs and length but starts at a random session.

    A random start is redrawn (up to ``tries`` times) until every leg has prices
    over the whole holding period, so no null trade sits before a listing (D53).
    """
    rng = np.random.default_rng(seed)
    valid = prices.closes.notna().to_numpy()
    col = {s: j for j, s in enumerate(prices.closes.columns)}

    def placeable(s: int, length: int, legs: dict[str, float]) -> bool:
        return all(valid[s : s + length, col[k]].all() for k in legs)

    out = np.empty(n_sims)
    for k in range(n_sims):
        series = []
        for trades in trades_by_cell:
            moved = []
            for t in trades:
                length = t.end - t.start
                top = max(hi + 1 - length, lo + 1)
                s = int(rng.integers(lo + 1, top + 1))
                for _ in range(tries):
                    if placeable(s, length, t.weights):
                        break
                    s = int(rng.integers(lo + 1, top + 1))
                moved.append(Trade(s, s + length, t.weights))
            series.append(in_set(run_book(moved, prices.opens, prices.closes, costs), start))
        out[k] = ev.moments(ev.pool(series).to_numpy()).sr
    return out


def explore_strategy(
    prices: Prices,
    sa: StatArbConfig,
    groups: dict[str, list[str]],
    strategy: str,
    all_cell_srs: list[float],
    seed: int,
) -> tuple[StrategyResult, dict[tuple[int, int], pd.Series], dict[tuple[int, int], list[Trade]]]:
    p = prices.until(sa.explore[1])
    lo, hi = set_bounds(p, sa.explore[0])
    ax1, ax2 = grid_axes(sa, strategy)
    base = costs_of(sa)
    grid = np.full((len(ax1), len(ax2)), np.nan)
    rets: dict[tuple[int, int], pd.Series] = {}
    trades: dict[tuple[int, int], list[Trade]] = {}
    for i, a in enumerate(ax1):
        for j, b in enumerate(ax2):
            tr = cell_trades(p, sa, groups, strategy, a, b, lo, hi)
            r = in_set(run_book(tr, p.opens, p.closes, base), sa.explore[0])
            rets[(i, j)], trades[(i, j)] = r, tr
            m = ev.moments(r.to_numpy())
            grid[i, j] = m.sr_annual
            all_cell_srs.append(m.sr)
    years = len(next(iter(rets.values()))) / TRADING_DAYS if rets else 0.0
    cells = ev.region(grid, years)
    res = StrategyResult(
        strategy,
        (ax1, ax2),
        np.where(np.isfinite(grid), grid, np.nan).tolist(),
        [(ax1[i], ax2[j]) for i, j in cells],
    )
    if not cells:
        res.notes.append("no finite cell")
        return res, rets, trades
    pooled = ev.pool([rets[c] for c in cells])
    m = ev.moments(pooled.to_numpy())
    res.pooled = {k: float(v) for k, v in asdict(m).items()}
    res.n_trades = sum(len(trades[c]) for c in cells)
    res.hac_p = ev.hac_p_one_sided(pooled.to_numpy(), sa.hac_lag)
    res.ci_mean = boot_ci(pooled.to_numpy(), sa.boot_block, seed, _mean)
    res.ci_sharpe = boot_ci(pooled.to_numpy(), sa.boot_block, seed, _sharpe)
    res.drawdown_95 = ev.drawdown_tail(pooled.to_numpy(), sa.n_boot_paths, sa.boot_block, seed)
    free = ev.pool(
        [
            in_set(run_book(trades[c], p.opens, p.closes, costs_of(sa, 0.0)), sa.explore[0])
            for c in cells
        ]
    )
    res.breakeven_bps = ev.cost_breakeven(free.to_numpy(), pooled.to_numpy(), sa.stock_side_bps)
    stress = costs_of(sa, sa.stress_multiplier, sa.stress_borrow_annual)
    res.stress_mean = float(
        ev.pool(
            [in_set(run_book(trades[c], p.opens, p.closes, stress), sa.explore[0]) for c in cells]
        ).mean()
    )
    null = random_entry_null(
        [trades[c] for c in cells], p, base, lo, hi, sa.explore[0], sa.n_null, seed
    )
    res.null_percentile = ev.null_percentile(m.sr, null)
    return res, rets, trades


def finish_exploration(
    results: list[StrategyResult], all_cell_srs: list[float], sa: StatArbConfig
) -> None:
    """Deflated Sharpe against all 21 cells, then the survival rules (plan section 5)."""
    for r in results:
        if not r.pooled:
            continue
        p = r.pooled
        r.dsr = ev.deflated_sharpe(
            p["sr"], all_cell_srs, int(p["n"]), p["skew"], p["kurt"], p["rho"]
        )
        checks = {
            "pooled net Sharpe > 0": p["sr_annual"] > 0,
            f"deflated Sharpe >= {sa.dsr_min}": np.isfinite(r.dsr) and r.dsr >= sa.dsr_min,
            f"effective N >= {sa.min_effective_n}": p["effective_n"] >= sa.min_effective_n,
            "region has >= 2 cells": len(r.region) >= 2,
        }
        r.survives = all(checks.values())
        r.notes += [f"fails: {k}" for k, ok in checks.items() if not ok]


# ---------------------------------------------------------------------------
# Confirmation (one shot)
# ---------------------------------------------------------------------------
def confirm_strategy(
    prices: Prices,
    sa: StatArbConfig,
    groups: dict[str, list[str]],
    strategy: str,
    region: list[list[float]],
) -> dict[str, Any]:
    p = prices.until(sa.confirm[1])
    lo, hi = set_bounds(p, sa.confirm[0])
    base, stress = costs_of(sa), costs_of(sa, sa.stress_multiplier, sa.stress_borrow_annual)
    base_series, stress_series, n_trades = [], [], 0
    for a, b in region:
        tr = cell_trades(p, sa, groups, strategy, a, b, lo, hi)
        n_trades += len(tr)
        base_series.append(in_set(run_book(tr, p.opens, p.closes, base), sa.confirm[0]))
        stress_series.append(in_set(run_book(tr, p.opens, p.closes, stress), sa.confirm[0]))
    pooled, pooled_stress = ev.pool(base_series), ev.pool(stress_series)
    m = ev.moments(pooled.to_numpy())
    return {
        "strategy": strategy,
        "n_sessions": int(m.n),
        "n_trades": n_trades,
        "moments": {k: float(v) for k, v in asdict(m).items()},
        "hac_p_one_sided": ev.hac_p_one_sided(pooled.to_numpy(), sa.hac_lag),
        "ci_mean": list(boot_ci(pooled.to_numpy(), sa.boot_block, 1, _mean)),
        "ci_sharpe": list(boot_ci(pooled.to_numpy(), sa.boot_block, 1, _sharpe)),
        "stress_mean": float(pooled_stress.mean()),
        "c2": bool(pooled_stress.mean() > 0),
    }


def finish_confirmation(rows: list[dict[str, Any]], alpha: float) -> None:
    ps = [r["hac_p_one_sided"] if np.isfinite(r["hac_p_one_sided"]) else 1.0 for r in rows]
    for r, pa in zip(rows, cs.holm(ps), strict=True):
        r["p_holm"] = float(pa)
        r["c1"] = bool(pa <= alpha and r["moments"]["mean"] > 0)
        r["confirmed"] = r["c1"] and r["c2"]
        r["verdict"] = "confirmed: forward shadow test next" if r["confirmed"] else "not confirmed"


# ---------------------------------------------------------------------------
# Entry points (read local data)
# ---------------------------------------------------------------------------
def paths(cfg: Config) -> dict[str, Path]:
    d = cfg.path("reports") / "statarb"
    d.mkdir(parents=True, exist_ok=True)
    return {
        "dir": d,
        "exploration": d / "exploration.json",
        "exploration_md": d / "exploration.md",
        "frozen": d / "frozen.json",
        "confirmation": d / "confirmation.json",
        "confirmation_md": d / "confirmation.md",
    }


def _clean(v: Any) -> Any:
    if isinstance(v, float) and not np.isfinite(v):
        return None
    if isinstance(v, dict):
        return {str(k): _clean(x) for k, x in v.items()}
    if isinstance(v, list | tuple):
        return [_clean(x) for x in v]
    return v


def load_prices(cfg: Config) -> Prices:  # pragma: no cover - reads local data
    from compute_curve.claim4.market_data import _read_duckdb, cache_path  # noqa: PLC0415
    from compute_curve.claim5.pipeline import claim5_cfg  # noqa: PLC0415

    c4, sa, c5 = cfg.claim4, cfg.statarb, claim5_cfg(cfg)
    if c4 is None or sa is None:
        raise RuntimeError("[claim4] and [statarb] config are required")
    symbols = [*c4.universe.members(), c4.benchmark]
    path = cache_path(
        cfg.path("var") / "market_data",
        symbols,
        c5.bars_start.isoformat(),
        str(sa.confirm[1]),
        c4.feed,
    )
    if not path.exists():
        raise FileNotFoundError(f"cached bars not found: {path}")
    return wide_prices(_read_duckdb(path), symbols, dict(c5.member_start), sa.min_history)


def run_exploration(cfg: Config) -> Path:  # pragma: no cover - reads local data
    from compute_curve.statarb.report import render_exploration  # noqa: PLC0415

    sa, c4 = cfg.statarb, cfg.claim4
    if sa is None or c4 is None:
        raise RuntimeError("[statarb] and [claim4] config are required")
    p = paths(cfg)
    if p["frozen"].exists():
        raise RuntimeError(f"{p['frozen']} exists; the exploration is frozen")
    prices = load_prices(cfg)
    groups = c4.universe.buckets()
    all_srs: list[float] = []
    results = [
        explore_strategy(prices, sa, groups, s, all_srs, cfg.project.seed)[0] for s in STRATEGIES
    ]
    finish_exploration(results, all_srs, sa)
    data = {"results": [asdict(r) for r in results], "n_cells": len(all_srs)}
    p["exploration"].write_text(json.dumps(_clean(data), indent=2))
    frozen = [{"strategy": r.strategy, "region": r.region} for r in results if r.survives]
    p["frozen"].write_text(json.dumps({"survivors": frozen}, indent=2))
    p["exploration_md"].write_text(render_exploration(results, sa, len(all_srs)))
    return p["exploration_md"]


def run_confirmation(cfg: Config) -> Path:  # pragma: no cover - reads local data
    from compute_curve.statarb.report import render_confirmation  # noqa: PLC0415

    sa, c4 = cfg.statarb, cfg.claim4
    if sa is None or c4 is None:
        raise RuntimeError("[statarb] and [claim4] config are required")
    p = paths(cfg)
    if p["confirmation"].exists():
        raise RuntimeError(f"{p['confirmation']} exists; the confirmation runs once")
    survivors = json.loads(p["frozen"].read_text())["survivors"]
    prices = load_prices(cfg)
    rows = [
        confirm_strategy(prices, sa, c4.universe.buckets(), s["strategy"], s["region"])
        for s in survivors
    ]
    finish_confirmation(rows, sa.alpha)
    p["confirmation"].write_text(json.dumps(_clean({"rows": rows}), indent=2))
    p["confirmation_md"].write_text(render_confirmation(rows, sa))
    return p["confirmation_md"]
