"""Claim 12: out-of-sample replications that decide the final candidate (docs/replication_plan.md).

R12-A: frozen SA2-M on 2019-01-02..2024-08-30 (never fetched before). R12-B: the
claim-11 rates effect (MD-4) on AWS spot GPU prices. Simulation only: no orders.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from compute_curve.macro import asof_friday, level_change, md_test
from compute_curve.statarb import evaluate as ev
from compute_curve.statarb.engine import run_book
from compute_curve.statarb.pipeline import (
    REGIONS_6C,
    Prices,
    _clean,
    cell_trades,
    in_set,
    set_bounds,
)
from compute_curve.statarb.power import holm

WINDOW_A = (date(2019, 1, 2), date(2024, 8, 30))
BARS_START_A = date(2018, 6, 1)
NEVER = date(2100, 1, 1)
MEMBER_START_A: dict[str, date] = {
    "VRT": date(2020, 2, 7),
    "IREN": date(2021, 11, 17),
    "CIFR": date(2021, 8, 30),
    "WULF": date(2021, 12, 14),
    "CEG": date(2022, 2, 2),
    "APLD": date(2022, 4, 13),
    "CORZ": date(2024, 1, 24),
    "TLN": date(2024, 7, 10),
    "NBIS": NEVER,
    "CRWV": NEVER,
    "WYFI": NEVER,
}
MIN_POOLS = 5
H = 4
ALPHA = 0.05
CLASSES_B = ("H100", "A100")


# ---------------------------------------------------------------------------
# R12-A helpers
# ---------------------------------------------------------------------------
def pooled_series(prices: Prices, sa: Any, window: tuple[date, date], costs: Any) -> pd.Series:
    """SA2-M pooled net daily returns (weights accounting) inside ``window``."""
    p = prices.until(window[1])
    lo, hi = set_bounds(p, window[0])
    series = []
    for a, b in REGIONS_6C["SA2-M"]:
        tr = cell_trades(p, sa, {}, "SA2", a, b, lo, hi)
        series.append(in_set(run_book(tr, p.opens, p.closes, costs), window[0]))
    return ev.pool(series)


def by_year(r: pd.Series) -> list[dict[str, float]]:
    out = []
    for y, g in r.groupby(r.index.year):
        m = ev.moments(g.to_numpy(float))
        out.append({"year": int(y), "n": int(m.n), "mean_bps": m.mean * 1e4, "sharpe": m.sr_annual})
    return out


def eligible_by_year(prices: Prices) -> dict[int, int]:
    ok = prices.signal_logp.drop(columns=["XLK"], errors="ignore").notna()
    return {int(y): int(g.any().sum()) for y, g in ok.groupby(ok.index.year)}


def verdict_a(rows: list[dict[str, Any]]) -> bool:
    """Plan section 2: C1, C2 and the mean CI not entirely below 0, under both accountings."""
    return all(
        r["hac_p_one_sided"] <= ALPHA
        and r["moments"]["mean"] > 0
        and r["c2"]
        and np.isfinite(r["ci_mean"][1])
        and r["ci_mean"][1] > 0
        for r in rows
    )


# ---------------------------------------------------------------------------
# R12-B helpers
# ---------------------------------------------------------------------------
def pool_monday_panel(pools: pd.DataFrame, gpu: str) -> pd.DataFrame:
    """Rows: Mondays; columns: pools; value: log price at the last observation in the 7 days."""
    g = pools.loc[pools["gpu"] == gpu].copy()
    if g.empty:
        return pd.DataFrame()
    g["day"] = pd.to_datetime(g["day"])
    g["pool"] = g["az_id"].astype(str) + "|" + g["instance_type"].astype(str)
    daily = g.pivot_table(
        index="day", columns="pool", values="price_per_gpu_hour", aggfunc="median"
    )
    days = pd.date_range(daily.index.min(), daily.index.max(), freq="D")
    filled = daily.reindex(days).ffill(limit=6)
    mondays = days[days.dayofweek == 0]
    return np.log(filled.loc[mondays].astype(float))


def pool_forward_change(panel: pd.DataFrame, h: int = H, min_pools: int = MIN_POOLS) -> pd.Series:
    fut = panel.shift(-h)
    both = panel.notna() & fut.notna()
    return (fut - panel).where(both).mean(axis=1).where(both.sum(axis=1) >= min_pools)


def r12b(pools: pd.DataFrame, dgs2: pd.Series, seed: int) -> dict[str, Any]:
    tests: dict[str, dict[str, Any]] = {}
    for gpu in CLASSES_B:
        panel = pool_monday_panel(pools, gpu)
        y = pool_forward_change(panel)
        x = asof_friday(level_change(dgs2), panel.index)
        tests[gpu] = md_test(x, y, seed)
        tests[gpu]["weeks"] = [str(panel.index[0].date()), str(panel.index[-1].date())]
    ids = [k for k in CLASSES_B if "p_one_sided" in tests[k]]
    for k, p in zip(ids, holm([tests[k]["p_one_sided"] for k in ids]), strict=True):
        tests[k]["p_holm"] = float(p)
        tests[k]["pass"] = bool(p <= ALPHA and tests[k]["slope"] > 0)
    return tests


# ---------------------------------------------------------------------------
# Rendering and the one-shot run
# ---------------------------------------------------------------------------
def render(res: dict[str, Any]) -> str:
    a, b = res["r12a"], res["r12b"]
    lines = [
        "# Claim 12 results: out-of-sample replications",
        "",
        "Plan: docs/replication_plan.md. One shot. Simulation only; no orders.",
        "",
        f"## R12-A: frozen SA2-M, {WINDOW_A[0]} to {WINDOW_A[1]} (never used before)",
        "",
        "Costs (ASSUMPTIONS): claim-6c per-symbol quoted-spread costs (half the median "
        "NBBO spread + 2 bps), sell fee 1 bp, borrow 3%/yr; stress x2 and 10%/yr.",
        "",
        "| Accounting | Sessions | Trades | Mean (bps/day) | 95% CI | Sharpe | 95% CI Sharpe |"
        " HAC p | Stress mean (bps) |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in a["rows"]:
        m = r["moments"]
        lines.append(
            f"| {r['accounting']} | {r['n_sessions']} | {r['n_trades']} | {m['mean'] * 1e4:+.2f} | "
            f"[{r['ci_mean'][0] * 1e4:+.2f}, {r['ci_mean'][1] * 1e4:+.2f}] | "
            f"{m['sr_annual']:+.2f} | [{r['ci_sharpe'][0]:+.2f}, {r['ci_sharpe'][1]:+.2f}] | "
            f"{r['hac_p_one_sided']:.3f} | {r['stress_mean'] * 1e4:+.2f} |"
        )
    lines += [
        "",
        f"**Verdict: {'passes' if a['passes'] else 'fails'}.**",
        "",
        "By year (weights accounting, descriptive):",
        "",
        "| Year | Names eligible | Sessions | Mean (bps/day) | Sharpe |",
        "|---|---|---|---|---|",
    ]
    elig = {str(k): v for k, v in a["eligible"].items()}
    for y in a["by_year"]:
        lines.append(
            f"| {y['year']} | {elig.get(str(y['year']), '')} "
            f"| {y['n']} | {y['mean_bps']:+.2f} | {y['sharpe']:+.2f} |"
        )
    lines += [
        "",
        "## R12-B: rates (20-session DGS2 change) vs AWS spot 4-week change",
        "",
        "| Class | Weeks | n | Slope | 95% CI | corr | HAC p | Holm p | Pass |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for k in CLASSES_B:
        t = b[k]
        ci = t.get("ci95", [float("nan")] * 2)
        slope = t.get("slope", float("nan"))
        lines.append(
            f"| {k} | {t['weeks'][0]} to {t['weeks'][1]} | {t['n']} | {slope:+.4f}"
            f" | [{ci[0]:+.4f}, {ci[1]:+.4f}] | {t.get('corr', float('nan')):+.2f} | "
            f"{t.get('p_one_sided', float('nan')):.3f} | {t.get('p_holm', float('nan')):.3f} | "
            f"{t.get('pass', False)} |"
        )
    return "\n".join(lines) + "\n"


def run_claim12(cfg: Any) -> Path:  # pragma: no cover - fetches Alpaca data, reads var/
    from compute_curve.claim4.alpaca import AlpacaDataClient  # noqa: PLC0415
    from compute_curve.claim4.market_data import fetch_bars_cached  # noqa: PLC0415
    from compute_curve.claim5.pipeline import read_pool_daily  # noqa: PLC0415
    from compute_curve.macro import fetch_dgs2  # noqa: PLC0415
    from compute_curve.statarb.pipeline import (  # noqa: PLC0415
        confirm_strategy,
        quoted_costs,
        wide_prices,
    )

    out = cfg.path("reports") / "replication"
    out.mkdir(parents=True, exist_ok=True)
    done = out / "claim12.json"
    if done.exists():
        raise RuntimeError(f"{done} exists; claim 12 runs once")
    sa, c4 = cfg.statarb, cfg.claim4
    symbols = [*c4.universe.members(), c4.benchmark]
    with AlpacaDataClient() as client:
        bars = fetch_bars_cached(
            client,
            symbols,
            BARS_START_A.isoformat(),
            WINDOW_A[1].isoformat(),
            cfg.path("var") / "market_data",
            feed=c4.feed,
            end_param=f"{WINDOW_A[1].isoformat()}T23:59:00Z",
        )
    prices = wide_prices(bars, symbols, MEMBER_START_A, sa.min_history)
    spreads = pd.Series(
        json.loads((cfg.path("reports") / "statarb" / "claim6c_spreads.json").read_text())[
            "median_quoted_spread"
        ],
        dtype=float,
    )
    costs = quoted_costs(sa, spreads)
    rows = []
    for accounting in ("weights", "shares"):
        r = confirm_strategy(
            prices, sa, {}, "SA2", REGIONS_6C["SA2-M"], costs, WINDOW_A, accounting
        )
        rows.append(r)
    series = pooled_series(prices, sa, WINDOW_A, costs[0])
    r12a = {
        "rows": rows,
        "passes": verdict_a(rows),
        "by_year": by_year(series),
        "eligible": eligible_by_year(prices.until(WINDOW_A[1])),
    }
    pools = read_pool_daily(cfg.path("var") / "aws_spot" / "pool_daily.parquet")
    dgs2 = fetch_dgs2(cfg, cfg.path("var") / "fred" / "DGS2.csv")
    res = {"r12a": r12a, "r12b": r12b(pools, dgs2, cfg.project.seed)}
    done.write_text(json.dumps(_clean(res), indent=2, default=float))
    path = out / "claim12.md"
    path.write_text(render(res))
    return path
