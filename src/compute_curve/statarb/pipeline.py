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
from compute_curve.statarb.engine import TRADING_DAYS, Costs, Trade, run_book, run_book_shares
from compute_curve.statarb.spreads import median_spreads
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
    costs: tuple[Costs, Costs, Costs] | None = None,
    label: str | None = None,
) -> tuple[StrategyResult, dict[tuple[int, int], pd.Series], dict[tuple[int, int], list[Trade]]]:
    """Map the grid, pool the region and run the checks on the exploration set.

    ``costs`` is (base, free, stress); by default claim 6's flat costs. With
    measured costs the break-even is reported as a multiple of the base costs.
    """
    p = prices.until(sa.explore[1])
    lo, hi = set_bounds(p, sa.explore[0])
    ax1, ax2 = grid_axes(sa, strategy)
    if costs is None:
        base, free_c = costs_of(sa), costs_of(sa, 0.0)
        stress = costs_of(sa, sa.stress_multiplier, sa.stress_borrow_annual)
        base_bps = sa.stock_side_bps
    else:
        base, free_c, stress = costs
        base_bps = 1.0
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
        label or strategy,
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
        [in_set(run_book(trades[c], p.opens, p.closes, free_c), sa.explore[0]) for c in cells]
    )
    res.breakeven_bps = ev.cost_breakeven(free.to_numpy(), pooled.to_numpy(), base_bps)
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
    costs: tuple[Costs, Costs, Costs] | None = None,
    window: tuple[date, date] | None = None,
    accounting: str = "weights",
) -> dict[str, Any]:
    """Frozen region on a window. ``accounting``: "weights" (engine default) or "shares" (D56)."""
    book = run_book_shares if accounting == "shares" else run_book
    start, end = window or sa.confirm
    p = prices.until(end)
    lo, hi = set_bounds(p, start)
    if costs is None:
        base, stress = costs_of(sa), costs_of(sa, sa.stress_multiplier, sa.stress_borrow_annual)
    else:
        base, _, stress = costs
    base_series, stress_series, n_trades = [], [], 0
    for a, b in region:
        tr = cell_trades(p, sa, groups, strategy, a, b, lo, hi)
        n_trades += len(tr)
        base_series.append(in_set(book(tr, p.opens, p.closes, base), start))
        stress_series.append(in_set(book(tr, p.opens, p.closes, stress), start))
    pooled, pooled_stress = ev.pool(base_series), ev.pool(stress_series)
    m = ev.moments(pooled.to_numpy())
    return {
        "strategy": strategy,
        "accounting": accounting,
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


# ---------------------------------------------------------------------------
# Claim 6b: residual reversal with measured costs (docs/statarb_plan2.md)
# ---------------------------------------------------------------------------
SLIPPAGE_6B = 0.0002  # ASSUMPTION: 2 bps per side on top of the half-spread
N_LIQUID = 10


def measured_costs(sa: StatArbConfig, spreads: pd.Series) -> tuple[Costs, Costs, Costs]:
    """(base, free, stress): half the Corwin-Schultz spread + slippage per side, per stock."""
    per = tuple((s, float(v) / 2 + SLIPPAGE_6B) for s, v in spreads.items() if s != ETF)
    base = Costs(
        sa.stock_side_bps / 1e4,
        sa.etf_side_bps / 1e4,
        sa.sell_fee_bps / 1e4,
        sa.borrow_annual,
        ETF,
        per,
    )
    free = base.scaled(0.0, sa.borrow_annual)
    stress = base.scaled(sa.stress_multiplier, sa.stress_borrow_annual)
    return base, free, stress


def subset(prices: Prices, names: list[str]) -> Prices:
    cols = [c for c in prices.closes.columns if c in names or c == ETF]
    return Prices(prices.opens[cols], prices.closes[cols], prices.signal_logp[cols])


def liquid_names(spreads: pd.Series, n: int = N_LIQUID) -> list[str]:
    return [s for s in spreads.sort_values().index if s != ETF][:n]


def prior_cell_srs(cfg: Config) -> list[float]:  # pragma: no cover - reads local data
    """Daily Sharpe of claim 6's 21 cells (from its frozen exploration report)."""
    data = json.loads(paths(cfg)["exploration"].read_text())
    out = []
    for r in data["results"]:
        for row in r["grid_sr_annual"]:
            out += [float(v) / np.sqrt(TRADING_DAYS) for v in row if v is not None]
    return out


def load_bars(cfg: Config) -> pd.DataFrame:  # pragma: no cover - reads local data
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
    return _read_duckdb(path)


def run_claim6b(cfg: Config) -> Path:  # pragma: no cover - reads local data
    """Exploration of SA2-M and SA2-L with measured costs; then the one-shot confirmation."""
    from compute_curve.statarb.report import (  # noqa: PLC0415
        render_confirmation,
        render_exploration,
    )

    sa, c4 = cfg.statarb, cfg.claim4
    if sa is None or c4 is None:
        raise RuntimeError("[statarb] and [claim4] config are required")
    d = paths(cfg)["dir"]
    frozen_p, conf_p = d / "claim6b_frozen.json", d / "claim6b_confirmation.json"
    bars = load_bars(cfg)
    spreads = median_spreads(bars, sa.explore[0], sa.explore[1])
    costs = measured_costs(sa, spreads)
    liquid = liquid_names(spreads)
    prices = load_prices(cfg)
    groups = c4.universe.buckets()
    variants = {"SA2-M": prices, "SA2-L": subset(prices, liquid)}
    if frozen_p.exists():
        raise RuntimeError(f"{frozen_p} exists; claim 6b exploration is frozen")
    all_srs = prior_cell_srs(cfg)
    results = [
        explore_strategy(p, sa, groups, "SA2", all_srs, cfg.project.seed, costs, label)[0]
        for label, p in variants.items()
    ]
    finish_exploration(results, all_srs, sa)
    lines = [
        render_exploration(results, sa, len(all_srs)).replace(
            "# Claim 6: statistical arbitrage, exploration set",
            "# Claim 6b: residual reversal with measured costs, exploration set",
        ),
        "## Measured costs (Corwin-Schultz, exploration set only)",
        "",
        "Per-side cost = half the median spread + 2 bps slippage (ASSUMPTION). With measured "
        "costs the 'break-even stock cost' row is the multiple of these costs at which the "
        "mean net return reaches zero.",
        "",
        "| Symbol | Median spread (bps) | Per-side cost (bps) | Liquid 10 |",
        "|---|---|---|---|",
    ]
    for sym, s in spreads.items():
        if sym == ETF:
            continue
        lines.append(
            f"| {sym} | {s * 1e4:.1f} | {(s / 2 + SLIPPAGE_6B) * 1e4:.1f} | "
            f"{'yes' if sym in liquid else ''} |"
        )
    (d / "claim6b_exploration.md").write_text("\n".join(lines) + "\n")
    survivors = [{"strategy": r.strategy, "region": r.region} for r in results if r.survives]
    frozen_p.write_text(
        json.dumps(
            {"survivors": survivors, "spreads": spreads.to_dict(), "liquid": liquid}, indent=2
        )
    )
    rows = []
    for s in survivors:
        p = variants[s["strategy"]]
        row = confirm_strategy(p, sa, groups, "SA2", s["region"], costs)
        row["strategy"] = s["strategy"]
        rows.append(row)
    if rows:
        finish_confirmation(rows, sa.alpha)
        conf_p.write_text(json.dumps(_clean({"rows": rows}), indent=2))
    (d / "claim6b_confirmation.md").write_text(render_confirmation(rows, sa))
    return d / "claim6b_exploration.md"


# ---------------------------------------------------------------------------
# Claim 6c: quoted-spread costs, straight to one-shot confirmation (docs/statarb_plan3.md)
# ---------------------------------------------------------------------------
QUOTED_COST_NOTE = (
    "Costs: per-symbol quoted-spread costs (half the median NBBO spread + 2 bps slippage, "
    "ASSUMPTION; reports/statarb/claim6c_spreads.json), sell fee 1 bp, borrow 3%/yr on shorts. "
    "Stress: all costs x2, borrow 10%/yr."
)


def _costs_line(sa: StatArbConfig) -> str:
    from compute_curve.statarb.report import _costs  # noqa: PLC0415

    return _costs(sa)


LIQUID_6C = ["MU", "TSM", "VRT", "AMD", "CRWV", "AVGO", "SMCI", "NVDA", "TLN", "VST"]
REGIONS_6C: dict[str, list[list[float]]] = {
    "SA2-M": [[w, e] for w in (40.0, 60.0, 90.0) for e in (1.0, 1.25, 1.5, 2.0)],
    "SA2-L": [[w, e] for w in (60.0, 90.0) for e in (1.0, 1.25, 1.5, 2.0)],
}


def quoted_costs(sa: StatArbConfig, spreads: pd.Series) -> tuple[Costs, Costs, Costs]:
    """Half the median quoted spread + 2 bps per side for every symbol, XLK included."""
    per = tuple((s, float(v) / 2 + SLIPPAGE_6B) for s, v in spreads.items())
    etf = float(spreads.get(ETF, sa.etf_side_bps / 1e4 * 2)) / 2 + SLIPPAGE_6B
    base = Costs(sa.stock_side_bps / 1e4, etf, sa.sell_fee_bps / 1e4, sa.borrow_annual, ETF, per)
    return (
        base,
        base.scaled(0.0, sa.borrow_annual),
        base.scaled(sa.stress_multiplier, sa.stress_borrow_annual),
    )


def fetch_quoted_spreads(
    cfg: Config, sessions: list[date], symbols: list[str]
) -> pd.Series:  # pragma: no cover
    """Median quoted spread per symbol over the sampled points (Alpaca data API, read-only)."""
    from compute_curve.claim4.alpaca import AlpacaDataClient  # noqa: PLC0415
    from compute_curve.statarb.spreads import (  # noqa: PLC0415
        first_valid_spread,
        median_quoted_spreads,
        sample_points,
    )

    samples: dict[str, list[float]] = {s: [] for s in symbols}
    with AlpacaDataClient() as client:
        for start, end in sample_points(sessions):
            quotes = client.quotes_window(symbols, start, end)
            for sym in symbols:
                v = first_valid_spread(quotes.get(sym, []))
                if v is not None:
                    samples[sym].append(v)
    return median_quoted_spreads(samples)


def run_claim6c(cfg: Config) -> Path:  # pragma: no cover - reads local data, calls Alpaca data
    from compute_curve.statarb.report import render_confirmation  # noqa: PLC0415

    sa, c4 = cfg.statarb, cfg.claim4
    if sa is None or c4 is None:
        raise RuntimeError("[statarb] and [claim4] config are required")
    d = paths(cfg)["dir"]
    sp_path, conf_p = d / "claim6c_spreads.json", d / "claim6c_confirmation.json"
    if conf_p.exists():
        raise RuntimeError(f"{conf_p} exists; claim 6c runs once")
    prices = load_prices(cfg)
    symbols = [*c4.universe.members(), ETF]
    if sp_path.exists():
        spreads = pd.Series(json.loads(sp_path.read_text())["median_quoted_spread"], dtype=float)
    else:
        idx = prices.closes.index
        sessions = [
            t.date() for t in idx if pd.Timestamp(sa.explore[0]) <= t <= pd.Timestamp(sa.explore[1])
        ]
        spreads = fetch_quoted_spreads(cfg, sessions, symbols)
        sp_path.write_text(
            json.dumps(
                {"median_quoted_spread": spreads.to_dict(), "note": "derived medians only (D29)"},
                indent=2,
            )
        )
    costs = quoted_costs(sa, spreads)
    groups = c4.universe.buckets()
    variants = {"SA2-M": prices, "SA2-L": subset(prices, LIQUID_6C)}
    rows = []
    for name, p in variants.items():
        row = confirm_strategy(p, sa, groups, "SA2", REGIONS_6C[name], costs)
        row["strategy"] = name
        rows.append(row)
    finish_confirmation(rows, sa.alpha)
    conf_p.write_text(json.dumps(_clean({"rows": rows}), indent=2))
    lines = [
        render_confirmation(rows, sa)
        .replace(
            "# Claim 6: statistical arbitrage, one-shot confirmation",
            "# Claim 6c: residual reversal with quoted-spread costs, one-shot confirmation",
        )
        .replace(_costs_line(sa), QUOTED_COST_NOTE),
        "## Quoted spreads (Alpaca NBBO, sampled exploration sessions)",
        "",
        "Per-side cost = half the median quoted spread + 2 bps (ASSUMPTION).",
        "",
        "| Symbol | Median quoted spread (bps) | Per-side cost (bps) |",
        "|---|---|---|",
        *[
            f"| {s} | {v * 1e4:.2f} | {(v / 2 + SLIPPAGE_6B) * 1e4:.2f} |"
            for s, v in spreads.sort_values().items()
        ],
    ]
    out = d / "claim6c_confirmation.md"
    out.write_text("\n".join(lines) + "\n")
    return out


# ---------------------------------------------------------------------------
# Claim 6c forward shadow test (docs/statarb_plan3.md section 6)
# ---------------------------------------------------------------------------
FORWARD_START = date(2026, 10, 6)
FORWARD_SESSIONS = 60
EXTENDED_SESSIONS = 250  # D57: SA2-M only, docs/statarb_forward_power.md
EXTENDED_STRATEGY = "SA2-M"


def forward_window(
    sessions: pd.DatetimeIndex, n: int = FORWARD_SESSIONS
) -> tuple[date, date] | None:
    """(first, n-th) session on or after FORWARD_START, or None while fewer exist."""
    fwd = [t.date() for t in sessions if t.date() >= FORWARD_START]
    if len(fwd) < n:
        return None
    return fwd[0], fwd[n - 1]


def run_forward(
    cfg: Config, n_sessions: int = FORWARD_SESSIONS
) -> Path:  # pragma: no cover - calls Alpaca data, reads local data
    """Count forward sessions daily; evaluate once when ``n_sessions`` exist. Never orders.

    ``n_sessions`` is 60 for the declared test (statarb_plan3.md sections 6 and 7) or
    ``EXTENDED_SESSIONS`` for the extension (D57), whose verdict counts for SA2-M only.
    """
    from datetime import timedelta  # noqa: PLC0415

    from compute_curve.claim4.alpaca import AlpacaDataClient  # noqa: PLC0415
    from compute_curve.claim4.market_data import fetch_bars_cached  # noqa: PLC0415
    from compute_curve.claim5.pipeline import claim5_cfg  # noqa: PLC0415
    from compute_curve.statarb.report import render_confirmation  # noqa: PLC0415
    from compute_curve.timeutil import utc_now  # noqa: PLC0415

    sa, c4, c5 = cfg.statarb, cfg.claim4, claim5_cfg(cfg)
    if sa is None or c4 is None:
        raise RuntimeError("[statarb] and [claim4] config are required")
    d = paths(cfg)["dir"]
    extended = n_sessions != FORWARD_SESSIONS
    stem = f"claim6c_forward{n_sessions}" if extended else "claim6c_forward"
    title = f"Claim 6c {'extended ' if extended else ''}forward test"
    out_json, out_md = d / f"{stem}.json", d / f"{stem}.md"
    if out_json.exists():
        out_md.write_text(f"# {title}\n\nDone earlier; see {stem}.json.\n")
        return out_md
    symbols = [*c4.universe.members(), c4.benchmark]
    last = utc_now().date() - timedelta(days=1)
    with AlpacaDataClient() as client:
        bars = fetch_bars_cached(
            client,
            symbols,
            c5.bars_start.isoformat(),
            last.isoformat(),
            cfg.path("var") / "market_data",
            feed=c4.feed,
            end_param=f"{last.isoformat()}T23:59:00Z",
        )
    prices = wide_prices(bars, symbols, dict(c5.member_start), sa.min_history)
    win = forward_window(prices.closes.index, n_sessions)
    n_fwd = int((prices.closes.index.date >= FORWARD_START).sum())
    if win is None:
        out_md.write_text(
            f"# {title}\n\n"
            f"Forward sessions so far: {n_fwd} of {n_sessions} (from {FORWARD_START}). "
            f"No statistic is computed until all {n_sessions} exist. No orders.\n"
        )
        return out_md
    spreads = pd.Series(
        json.loads((d / "claim6c_spreads.json").read_text())["median_quoted_spread"], dtype=float
    )
    costs = quoted_costs(sa, spreads)
    groups = c4.universe.buckets()
    rows = []
    for accounting in ("weights", "shares"):
        block = []
        for name, p in {"SA2-M": prices, "SA2-L": subset(prices, LIQUID_6C)}.items():
            row = confirm_strategy(p, sa, groups, "SA2", REGIONS_6C[name], costs, win, accounting)
            row["strategy"] = f"{name} ({accounting})"
            block.append(row)
        finish_confirmation(block, sa.alpha)
        rows += block
    for r in rows:  # D56: a strategy passes only if it passes under both accountings
        name = r["strategy"].split(" ")[0]
        both = [x for x in rows if x["strategy"].startswith(name + " ")]
        r["confirmed_both"] = all(x["confirmed"] for x in both)
        r["verdict"] = "forward test passed" if r["confirmed_both"] else "forward test failed"
        if extended and name != EXTENDED_STRATEGY:
            r["verdict"] = "descriptive only (the extension's verdict is for SA2-M, D57)"
    out_json.write_text(
        json.dumps(_clean({"window": [str(w) for w in win], "rows": rows}), indent=2)
    )
    out_md.write_text(
        render_confirmation(rows, sa)
        .replace(
            "# Claim 6: statistical arbitrage, one-shot confirmation",
            f"# {title} (shadow), sessions {win[0]} to {win[1]}",
        )
        .replace(_costs_line(sa), QUOTED_COST_NOTE)
    )
    return out_md


# ---------------------------------------------------------------------------
# Claim 6d: out-of-universe replication of frozen SA2-M (docs/statarb_plan4.md)
# ---------------------------------------------------------------------------
UNIVERSE_6D = [
    "AAPL", "MSFT", "ORCL", "CRM", "ADBE", "CSCO", "INTC", "QCOM", "TXN", "AMAT",
    "LRCX", "KLAC", "ADI", "NXPI", "ON", "MCHP", "IBM", "NOW", "INTU", "PANW",
]  # fmt: skip
WINDOW_6D = (date(2024, 9, 3), date(2026, 10, 5))


def run_claim6d(cfg: Config) -> Path:  # pragma: no cover - calls Alpaca data, reads local data
    """Frozen SA2-M on universe B, one shot, under both accountings."""
    from compute_curve.claim4.alpaca import AlpacaDataClient  # noqa: PLC0415
    from compute_curve.claim4.market_data import fetch_bars_cached  # noqa: PLC0415
    from compute_curve.claim5.pipeline import claim5_cfg  # noqa: PLC0415

    sa, c4, c5 = cfg.statarb, cfg.claim4, claim5_cfg(cfg)
    if sa is None or c4 is None:
        raise RuntimeError("[statarb] and [claim4] config are required")
    d = paths(cfg)["dir"]
    out_json, sp_path = d / "claim6d.json", d / "claim6d_spreads.json"
    if out_json.exists():
        raise RuntimeError(f"{out_json} exists; claim 6d runs once")
    symbols = [*UNIVERSE_6D, ETF]
    with AlpacaDataClient() as client:
        bars = fetch_bars_cached(
            client,
            symbols,
            c5.bars_start.isoformat(),
            WINDOW_6D[1].isoformat(),
            cfg.path("var") / "market_data",
            feed=c4.feed,
            end_param=f"{WINDOW_6D[1].isoformat()}T23:59:00Z",
        )
    prices = wide_prices(bars, symbols, {}, sa.min_history)
    if sp_path.exists():
        spreads = pd.Series(json.loads(sp_path.read_text())["median_quoted_spread"], dtype=float)
    else:
        idx = prices.closes.index
        sessions = [
            t.date() for t in idx if pd.Timestamp(sa.explore[0]) <= t <= pd.Timestamp(sa.explore[1])
        ]
        spreads = fetch_quoted_spreads(cfg, sessions, symbols)
        sp_path.write_text(
            json.dumps(
                {"median_quoted_spread": spreads.to_dict(), "note": "derived medians only (D29)"},
                indent=2,
            )
        )
    costs = quoted_costs(sa, spreads)
    groups = {"B": UNIVERSE_6D}
    rows = []
    for accounting in ("weights", "shares"):
        row = confirm_strategy(
            prices, sa, groups, "SA2", REGIONS_6C["SA2-M"], costs, WINDOW_6D, accounting
        )
        row["strategy"] = f"SA2-M on universe B ({accounting})"
        row["p_holm"] = row["hac_p_one_sided"]  # a single test per accounting
        row["c1"] = bool(row["hac_p_one_sided"] <= sa.alpha and row["moments"]["mean"] > 0)
        row["confirmed"] = row["c1"] and row["c2"]
        rows.append(row)
    replicates = all(r["confirmed"] for r in rows)
    for r in rows:
        r["verdict"] = "replicates" if replicates else "does not replicate"
    out_json.write_text(json.dumps(_clean({"rows": rows, "replicates": replicates}), indent=2))
    from compute_curve.statarb.report import render_confirmation  # noqa: PLC0415

    md = (
        render_confirmation(rows, sa)
        .replace(
            "# Claim 6: statistical arbitrage, one-shot confirmation",
            "# Claim 6d: frozen SA2-M on out-of-universe stocks (universe B), one shot",
        )
        .replace(_costs_line(sa), QUOTED_COST_NOTE)
        .replace(
            f"Sessions {sa.confirm[0]} to {sa.confirm[1]}",
            f"Sessions {WINDOW_6D[0]} to {WINDOW_6D[1]}",
        )
    )
    lines = [
        md,
        "## Quoted spreads, universe B (Alpaca NBBO, sampled sessions)",
        "",
        "| Symbol | Median quoted spread (bps) |",
        "|---|---|",
        *[f"| {s} | {v * 1e4:.2f} |" for s, v in spreads.sort_values().items()],
    ]
    out = d / "claim6d.md"
    out.write_text("\n".join(lines) + "\n")
    return out
