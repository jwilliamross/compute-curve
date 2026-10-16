"""Claim 10 runs: exploration screen, one-shot confirmation, nightly lab (docs/modern_plan.md).

No orders anywhere. Reports carry percentages and statistics only (D29).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from compute_curve.config import Config, StatArbConfig
from compute_curve.statarb import modern as mx
from compute_curve.statarb.engine import Costs, book_returns
from compute_curve.statarb.pipeline import REGIONS_6C, Prices, _clean

PLAN = "docs/modern_plan.md"


@dataclass(frozen=True)
class Book:
    weights: np.ndarray
    n_trades: int
    ridge: mx.RidgeOut | None = None
    base: np.ndarray | None = None  # MX1: the unmanaged SA2-M weights


def volume_wide(bars: pd.DataFrame, closes: pd.DataFrame) -> pd.DataFrame:
    """Volume pivoted like the closes, NaN wherever the close is masked."""
    b = bars.copy()
    b["session"] = pd.to_datetime(b["session"])
    v = b.pivot_table(index="session", columns="symbol", values="volume", aggfunc="last")
    v = v.reindex(index=closes.index, columns=closes.columns)
    return v.where(closes.notna())


def build_books(
    prices: Prices, volume: pd.DataFrame, sa: StatArbConfig, costs: Costs
) -> dict[str, Book]:
    """Every MX book on data through the last session of ``prices`` (nothing later exists)."""
    lp, n = prices.signal_logp, len(prices.closes)
    hi = n - 1
    region = REGIONS_6C["SA2-M"]
    etf_scores = mx.memo(mx.etf_scorer())
    w0, n0 = mx.region_weights(lp, sa, region, hi, etf_scores)
    symbols = list(prices.closes.columns)
    o, c = prices.opens.to_numpy(float), prices.closes.to_numpy(float)
    r0 = book_returns(w0, o, c, costs, symbols)
    scale = mx.vol_scale(r0, w0)
    books = {"SA2-M": Book(w0, n0), "MX1": Book(w0 * scale[:, None], n0, base=w0)}
    av = mx.abnormal_volume(volume)
    eligible = lp.notna()
    for name, loud in (("MX2a", False), ("MX2b", True)):
        gate = mx.volume_gate(av, eligible, loud)
        w, k = mx.region_weights(lp, sa, region, hi, etf_scores, gate)
        books[name] = Book(w, k)
    for k in mx.PCA_KS:
        w, nt = mx.region_weights(lp, sa, region, hi, mx.memo(mx.pca_scorer(k)))
        books[f"MX3-k{k}"] = Book(w, nt)
    rid = mx.ridge_book(lp, prices.opens, volume, hi, sa.max_positions)
    books["MX4"] = Book(rid.weights, rid.n_trades, ridge=rid)
    return books


def evaluate_books(
    books: dict[str, Book],
    prices: Prices,
    costs: tuple[Costs, Costs, Costs],
    window: tuple[date, date],
    sa: StatArbConfig,
    seed: int,
) -> list[mx.MxResult]:
    """Each strategy's test on ``window`` (SA2-M is the reference row, not a variant)."""
    rows: list[mx.MxResult] = []
    base_r: np.ndarray | None = None
    for name in ("SA2-M", *mx.STRATEGIES):
        b = books[name]
        res, r = mx.summarize(
            name,
            b.weights,
            prices.opens,
            prices.closes,
            costs,
            window,
            b.n_trades,
            sa.hac_lag,
            seed,
            sa.boot_block,
        )
        if name == "SA2-M":
            base_r = r
            res.test = "reference (SA2-M, frozen; not a claim-10 variant)"
        elif name == "MX1" and base_r is not None:
            a, p = mx.mm_alpha_p(r, base_r, sa.hac_lag)
            res.test, res.p = "Moreira-Muir alpha > 0 (HAC)", p
            res.extra["alpha_daily"] = a
        elif name == "MX4" and b.ridge is not None:
            res.extra.update(ic_stats(b.ridge, prices.closes.index, window))
            res.test = "net mean > 0 (HAC); gate: IC(ridge) - IC(baseline) > 0"
        rows.append(res)
    return rows


def ic_stats(
    rid: mx.RidgeOut, index: pd.DatetimeIndex, window: tuple[date, date]
) -> dict[str, float]:
    inside = mx.window_mask(index, window)
    keep = [i for i, t in enumerate(rid.forecast_dates) if inside[t]]
    m = np.array([rid.ic_model[i] for i in keep], float)
    b = np.array([rid.ic_base[i] for i in keep], float)
    ok = np.isfinite(m) & np.isfinite(b)
    m, b = m[ok], b[ok]
    from compute_curve.statarb import evaluate as ev  # noqa: PLC0415

    return {
        "ic_days": float(m.size),
        "ic_model": float(m.mean()) if m.size else float("nan"),
        "ic_baseline": float(b.mean()) if b.size else float("nan"),
        "ic_p": ev.hac_p_one_sided(m - b, mx.IC_LAG) if m.size > 3 * mx.IC_LAG else float("nan"),
    }


def render(title: str, rows: list[mx.MxResult], note: str, verdicts: dict[str, str]) -> str:
    out = [
        f"# {title}",
        "",
        note,
        "",
        "| Strategy | Sessions | Trades | Mean (bps/day) | Sharpe (ann.) | 95% CI Sharpe |"
        " Test p | Stress mean (bps) | Avg gross | Verdict |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        m = r.moments
        out.append(
            f"| {r.strategy} | {r.n_sessions} | {r.n_trades} | {m['mean'] * 1e4:+.2f} | "
            f"{m['sr_annual']:+.2f} | [{r.ci_sharpe[0]:+.2f}, {r.ci_sharpe[1]:+.2f}] | "
            f"{r.p:.3f} | {r.stress_mean * 1e4:+.2f} | {r.gross_mean:.2f} | "
            f"{verdicts.get(r.strategy, '')} |"
        )
    out += ["", "Tests:", ""]
    out += [f"- {r.strategy}: {r.test}" + _extra(r) for r in rows]
    return "\n".join(out) + "\n"


def _extra(r: mx.MxResult) -> str:
    if not r.extra:
        return ""
    return " (" + ", ".join(f"{k} {v:.4g}" for k, v in r.extra.items()) + ")"


COST_NOTE = (
    "Costs (ASSUMPTIONS): per symbol, half the median quoted spread + 2 bps per side "
    "(reports/statarb/claim6c_spreads.json); sell fee 1 bp; borrow 3%/yr. Stress: all x2, "
    "borrow 10%/yr. Books are pooled weights, entries from the first eligible session, data "
    "truncated at the window end. Simulation only; no orders. Plan: " + PLAN + "."
)


# ---------------------------------------------------------------------------
# Entry points (read local data)
# ---------------------------------------------------------------------------
def _sa(cfg: Config) -> StatArbConfig:
    if cfg.statarb is None:
        raise RuntimeError("[statarb] config is required")
    return cfg.statarb


def _dir(cfg: Config) -> Path:
    d = cfg.path("reports") / "statarb" / "modern"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _inputs(
    cfg: Config,
) -> tuple[Prices, pd.DataFrame, tuple[Costs, Costs, Costs]]:  # pragma: no cover
    from compute_curve.claim5.pipeline import claim5_cfg  # noqa: PLC0415
    from compute_curve.statarb.pipeline import load_bars, quoted_costs, wide_prices  # noqa: PLC0415

    sa, c4 = cfg.statarb, cfg.claim4
    if sa is None or c4 is None:
        raise RuntimeError("[statarb] and [claim4] config are required")
    bars = load_bars(cfg)
    symbols = [*c4.universe.members(), c4.benchmark]
    prices = wide_prices(bars, symbols, dict(claim5_cfg(cfg).member_start), sa.min_history)
    spreads = pd.Series(
        json.loads((cfg.path("reports") / "statarb" / "claim6c_spreads.json").read_text())[
            "median_quoted_spread"
        ],
        dtype=float,
    )
    return prices, volume_wide(bars, prices.closes), quoted_costs(sa, spreads)


def _truncate(prices: Prices, volume: pd.DataFrame, end: date) -> tuple[Prices, pd.DataFrame]:
    p = prices.until(end)
    return p, volume.loc[p.closes.index]


def run_explore(cfg: Config) -> Path:  # pragma: no cover - reads local data
    sa = _sa(cfg)
    d = _dir(cfg)
    if (d / "frozen.json").exists():
        raise RuntimeError("claim 10 exploration is frozen")
    prices, volume, costs = _inputs(cfg)
    p, v = _truncate(prices, volume, sa.explore[1])
    rows = evaluate_books(
        build_books(p, v, sa, costs[0]), p, costs, sa.explore, sa, cfg.project.seed
    )
    survivors = [r.strategy for r in rows if r.strategy != "SA2-M" and mx.screen(r)]
    verdicts = {
        r.strategy: ("survives the screen" if r.strategy in survivors else "stops here")
        for r in rows
        if r.strategy != "SA2-M"
    }
    (d / "exploration.json").write_text(json.dumps(_clean([asdict(r) for r in rows]), indent=2))
    (d / "frozen.json").write_text(json.dumps({"survivors": survivors}, indent=2))
    md = render(
        f"Claim 10 exploration, {sa.explore[0]} to {sa.explore[1]}",
        rows,
        COST_NOTE + f" Screen: test p <= {mx.SCREEN_P}, mean > 0, effective N >= "
        f"{mx.MIN_EFFECTIVE_N} (MX4 also IC gate p <= {mx.SCREEN_P}).",
        verdicts,
    )
    (d / "exploration.md").write_text(md)
    return d / "exploration.md"


def run_confirm(cfg: Config) -> Path:  # pragma: no cover - reads local data
    sa = _sa(cfg)
    d = _dir(cfg)
    if (d / "confirmation.json").exists():
        raise RuntimeError("claim 10 confirmation runs once")
    survivors = json.loads((d / "frozen.json").read_text())["survivors"]
    prices, volume, costs = _inputs(cfg)
    p, v = _truncate(prices, volume, sa.confirm[1])
    rows = evaluate_books(
        build_books(p, v, sa, costs[0]), p, costs, sa.confirm, sa, cfg.project.seed
    )
    conf = mx.confirm([r for r in rows if r.strategy in survivors], sa.alpha)
    verdicts = {str(c["strategy"]): str(c["verdict"]) for c in conf}
    for r in rows:
        if r.strategy != "SA2-M" and r.strategy not in survivors:
            verdicts[r.strategy] = "descriptive (did not survive the screen)"
    (d / "confirmation.json").write_text(
        json.dumps(_clean({"rows": [asdict(r) for r in rows], "decisions": conf}), indent=2)
    )
    md = render(
        f"Claim 10 confirmation (one shot), {sa.confirm[0]} to {sa.confirm[1]}",
        rows,
        COST_NOTE + " Holm across the survivors, alpha 0.05. This window was already used for "
        "SA2-M, so it is not blind for reversal; the forward shadow decides.",
        verdicts,
    )
    (d / "confirmation.md").write_text(md)
    return d / "confirmation.md"


def lab_lines(
    books: dict[str, Book], prices: Prices, costs: Costs, start: date
) -> list[tuple[str, int, float, float]]:
    """(strategy, sessions, cumulative net return, today's gross) from ``start``."""
    symbols = list(prices.closes.columns)
    o, c = prices.opens.to_numpy(float), prices.closes.to_numpy(float)
    mask = np.asarray(prices.closes.index >= pd.Timestamp(start))
    etf = symbols.index(mx.ETF)
    out = []
    for name, b in books.items():
        r = book_returns(b.weights, o, c, costs, symbols)[mask]
        gross = float(np.abs(np.delete(b.weights[-1], etf)).sum()) if len(b.weights) else 0.0
        out.append((name, int(mask.sum()), float(np.prod(1 + r) - 1) if r.size else 0.0, gross))
    return out


def run_lab(cfg: Config) -> Path:  # pragma: no cover - calls Alpaca data
    """Nightly: forward shadow P&L of every MX book next to SA2-M; evaluates once at 60."""
    from compute_curve.statarb.pipeline import quoted_costs  # noqa: PLC0415
    from compute_curve.statarb.signals import latest_bars  # noqa: PLC0415

    sa = _sa(cfg)
    d = _dir(cfg)
    prices, bars = latest_bars(cfg)
    volume = volume_wide(bars, prices.closes)
    spreads = pd.Series(
        json.loads((cfg.path("reports") / "statarb" / "claim6c_spreads.json").read_text())[
            "median_quoted_spread"
        ],
        dtype=float,
    )
    costs = quoted_costs(sa, spreads)
    books = build_books(prices, volume, sa, costs[0])
    fwd = [t.date() for t in prices.closes.index if t.date() >= mx.FORWARD_START]
    asof = str(prices.closes.index[-1].date())
    lines = [
        f"# Strategy lab: forward shadow, data through {asof}",
        "",
        "Shadow only: these books are simulated next to the SA2-M paper account and never "
        f"send orders. Forward window starts {mx.FORWARD_START}; {len(fwd)} of "
        f"{mx.FORWARD_SESSIONS} sessions so far. Plan: {PLAN}. Until 60 sessions exist "
        "these numbers are descriptive and decide nothing.",
        "",
        "| Strategy | Forward sessions | Net return since start | Gross stock exposure now |",
        "|---|---|---|---|",
    ]
    for name, n, cum, gross in lab_lines(books, prices, costs[0], mx.FORWARD_START):
        lines.append(f"| {name} | {n} | {cum * 100:+.2f}% | {gross:.2f} |")
    if len(fwd) >= mx.FORWARD_SESSIONS and not (d / "forward.json").exists():
        win = (fwd[0], fwd[mx.FORWARD_SESSIONS - 1])
        p, v = _truncate(prices, volume, win[1])
        rows = evaluate_books(build_books(p, v, sa, costs[0]), p, costs, win, sa, cfg.project.seed)
        conf_p = d / "confirmation.json"
        confirmed = (
            [
                str(c["strategy"])
                for c in json.loads(conf_p.read_text())["decisions"]
                if c["confirmed"]
            ]
            if conf_p.exists()
            else []
        )
        dec = mx.confirm([r for r in rows if r.strategy in confirmed], sa.alpha)
        (d / "forward.json").write_text(
            json.dumps(
                _clean(
                    {
                        "window": [str(w) for w in win],
                        "rows": [asdict(r) for r in rows],
                        "decisions": dec,
                    }
                ),
                indent=2,
            )
        )
        verdicts = {
            str(c["strategy"]): ("forward test passed" if c["confirmed"] else "forward test failed")
            for c in dec
        }
        (d / "forward.md").write_text(
            render(f"Claim 10 forward shadow, {win[0]} to {win[1]}", rows, COST_NOTE, verdicts)
        )
        lines += ["", "The 60-session forward evaluation ran: see forward.md."]
    out = cfg.path("reports") / "statarb" / "lab"
    out.mkdir(parents=True, exist_ok=True)
    (out / "latest.md").write_text("\n".join(lines) + "\n")
    return out / "latest.md"
