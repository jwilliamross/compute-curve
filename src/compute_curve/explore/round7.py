"""Round 7: per-provider price history from the GetDeploying API.

Plan: docs/exploration_round7_plan.md, committed before any API row was
downloaded. Runs once. Reports aggregates and test statistics only (D60).
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import scipy.stats as st

from compute_curve.backtest.bootstrap import circular_block_indices
from compute_curve.claim4 import stats as cs
from compute_curve.collectors.getdeploying_api import EXCLUDED
from compute_curve.explore.round6 import ols_slope_test
from compute_curve.statarb.power import holm

LAST_MONDAY = date(2026, 10, 12)
MIN_CS = 8
H = 4
MIN_SECTIONS = 26
LAG = 6
MOVE = 0.005
MIN_TRAIN = 26
RATIO_MIN = 3
RATIO_PRIOR = 8
RATIO_H = 8
RATIO_LAG = 10
RATIO_MIN_OBS = 20
BLOCK = 8
N_BOOT = 2000
ALPHA = 0.05
BACKFILL_SPLIT = date(2025, 10, 6)


def weekly_panel(hist: pd.DataFrame, gpu: str, last: date = LAST_MONDAY) -> pd.DataFrame:
    """Rows: Mondays up to ``last``; columns: providers; values: log on-demand median price."""
    h = hist.loc[
        (hist["gpu_model"] == gpu)
        & (hist["billing_type"] == "ON_DEMAND")
        & hist["reservation_months"].isna()
        & ~hist["provider"].isin(EXCLUDED)
    ].copy()
    h["price"] = pd.to_numeric(h["median_price"], errors="coerce")
    h = h.loc[h["price"] > 0]
    d = pd.to_datetime(h["date"])
    h = h.loc[(d.dt.dayofweek == 0) & (d.dt.date <= last)].assign(date=d)
    if h.empty:
        return pd.DataFrame()
    p = h.pivot_table(index="date", columns="provider", values="price", aggfunc="median")
    full = pd.date_range(p.index.min(), p.index.max(), freq="W-MON")
    return np.log(p.reindex(full).astype(float))


def trim_start(panel: pd.DataFrame, min_cs: int = MIN_CS) -> pd.DataFrame:
    """From the first Monday with at least ``min_cs`` providers priced."""
    ok = panel.notna().sum(axis=1) >= min_cs
    return panel.loc[ok.idxmax() :] if ok.any() else panel.iloc[0:0]


def _mean_ci(x: np.ndarray, seed: int) -> list[float]:
    rng = np.random.default_rng(seed)
    b = [x[circular_block_indices(x.size, BLOCK, rng)].mean() for _ in range(N_BOOT)]
    return [float(v) for v in np.quantile(b, [0.025, 0.975])]


def _slope_ci(x: np.ndarray, y: np.ndarray, seed: int) -> list[float]:
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(N_BOOT):
        i = circular_block_indices(x.size, BLOCK, rng)
        if np.ptp(x[i]) > 0:
            out.append(float(np.polyfit(x[i], y[i], 1)[0]))
    return [float(v) for v in np.quantile(out, [0.025, 0.975])]


def r701(panel: pd.DataFrame, seed: int) -> dict[str, Any]:
    slopes = []
    for i in range(len(panel) - H):
        now, fut = panel.iloc[i], panel.iloc[i + H]
        ok = now.notna() & fut.notna()
        if int(ok.sum()) < MIN_CS:
            continue
        s = (now - now.median(skipna=True))[ok].to_numpy(float)
        c = (fut - now)[ok].to_numpy(float)
        if np.ptp(s) > 1e-12:
            slopes.append(float(np.polyfit(s, c, 1)[0]))
    x = np.asarray(slopes)
    res: dict[str, Any] = {"n": int(x.size)}
    if x.size < MIN_SECTIONS:
        res["verdict"] = "too little history to conclude"
        return res
    se = cs.hac_mean_se(x, LAG)
    t = float(x.mean() / se) if se > 0 else float("nan")
    p = float(st.t.cdf(t, df=x.size - 1)) if np.isfinite(t) else 1.0
    return res | {
        "estimate": float(x.mean()),
        "se": float(se),
        "p_one_sided": p,
        "ci95": _mean_ci(x, seed),
    }


def breadth(panel: pd.DataFrame) -> pd.DataFrame:
    """x(t): net share of providers moving up over the past H weeks; y(t): next-H median move."""
    rows = []
    for i in range(H, len(panel) - H):
        past, now, fut = panel.iloc[i - H], panel.iloc[i], panel.iloc[i + H]
        a = past.notna() & now.notna()
        b = now.notna() & fut.notna()
        if int(a.sum()) < MIN_CS or int(b.sum()) < MIN_CS:
            continue
        ch = (now - past)[a]
        x = (int((ch > MOVE).sum()) - int((ch < -MOVE).sum())) / int(a.sum())
        rows.append({"t": panel.index[i], "x": x, "y": float((fut - now)[b].median())})
    return pd.DataFrame(rows, columns=["t", "x", "y"])


def r702(panel: pd.DataFrame, seed: int) -> dict[str, Any]:
    b = breadth(panel)
    x, y = b["x"].to_numpy(float), b["y"].to_numpy(float)
    res = ols_slope_test(x, y, lag=LAG, sign=1)
    if x.size < MIN_SECTIONS:
        return {"n": int(x.size), "verdict": "too little history to conclude"}
    if "slope" in res:
        res |= {"estimate": res["slope"], "ci95": _slope_ci(x, y, seed)}
    return res


def market_moves(panel: pd.DataFrame) -> pd.Series:
    """d(t): median one-week log change over providers priced in both weeks."""
    ch = panel.diff()
    both = panel.notna() & panel.shift(1).notna()
    return ch.where(both).median(axis=1, skipna=True).iloc[1:]


def r703(panel: pd.DataFrame) -> dict[str, Any]:
    d = market_moves(panel).dropna().to_numpy(float)
    actual, model = [], []
    for t in range(MIN_TRAIN, d.size - 1):
        hist = d[: t + 1]
        x0, x1 = hist[:-1], hist[1:]
        if np.ptp(x0) == 0:
            fc = float(x1.mean())
        else:
            b = float(np.polyfit(x0, x1, 1)[0])
            fc = float(x1.mean() - b * x0.mean() + b * hist[-1])
        actual.append(d[t + 1])
        model.append(fc)
    y, m = np.asarray(actual), np.asarray(model)
    res: dict[str, Any] = {"n": int(y.size)}
    if y.size < MIN_TRAIN:
        res["verdict"] = "too little history to conclude"
        return res
    cw = cs.clark_west(y, m, np.zeros_like(y), 1)
    if cw is None or not np.isfinite(cw.p_value):
        res["verdict"] = "too little history to conclude"
        return res
    return res | {
        "estimate": float(cw.stat),
        "p_one_sided": float(cw.p_value),
        "mse_model": float(np.mean((y - m) ** 2)),
        "mse_random_walk": float(np.mean(y**2)),
    }


def ratio_series(h100: pd.DataFrame, b200: pd.DataFrame) -> pd.Series:
    idx = h100.index.union(b200.index)
    cols = h100.columns.intersection(b200.columns)
    lr = b200.reindex(index=idx, columns=cols) - h100.reindex(index=idx, columns=cols)
    n = lr.notna().sum(axis=1)
    return lr.median(axis=1, skipna=True).where(n >= RATIO_MIN)


def r704(ratio: pd.Series) -> dict[str, Any]:
    vals = ratio.to_numpy(float)
    x, y = [], []
    for i in range(len(vals) - RATIO_H):
        prior = vals[:i][np.isfinite(vals[:i])]
        if prior.size < RATIO_PRIOR or not np.isfinite(vals[i]):
            continue
        if not np.isfinite(vals[i + RATIO_H]):
            continue
        x.append(vals[i] - prior.mean())
        y.append(vals[i + RATIO_H] - vals[i])
    res = ols_slope_test(np.asarray(x), np.asarray(y), lag=RATIO_LAG, sign=-1)
    if res["n"] < RATIO_MIN_OBS:
        return {"n": res["n"], "verdict": "too little history to conclude"}
    if "slope" in res:
        res["estimate"] = res["slope"]
    return res


def finish(tests: dict[str, dict[str, Any]], signs: dict[str, int]) -> None:
    """Holm over all four declared tests; one that could not run counts as p = 1."""
    names = list(tests)
    ps = [float(tests[k].get("p_one_sided", 1.0)) for k in names]
    ps = [p if np.isfinite(p) else 1.0 for p in ps]
    for k, pa in zip(names, holm(ps), strict=True):
        t = tests[k]
        if "p_one_sided" not in t:
            continue
        t["p_holm"] = float(pa)
        sign_ok = np.sign(t.get("estimate", 0.0)) == signs[k] if k != "R7-03" else True
        t["verdict"] = "confirmed" if pa <= ALPHA and sign_ok else "not confirmed"


def descriptive(panel: pd.DataFrame) -> dict[str, Any]:
    if panel.empty:
        return {"n_mondays": 0}
    ch = panel.diff()
    present = ch.notna()
    moved = (ch.abs() > MOVE) & present
    exact = (ch.abs() < 1e-12) & present
    before = pd.Series(panel.index.date < BACKFILL_SPLIT, index=panel.index)
    d = market_moves(panel).dropna()

    def share(mask: pd.DataFrame, rows: pd.Series) -> float | None:
        n = int(present.loc[rows].sum().sum())
        return float(mask.loc[rows].sum().sum() / n) if n else None

    counts = panel.notna().sum(axis=1)
    return {
        "first_monday": str(panel.index.min().date()),
        "last_monday": str(panel.index.max().date()),
        "n_mondays": len(panel),
        "n_providers_ever": int(panel.notna().any().sum()),
        "providers_per_monday_median": float(counts.median()),
        "providers_per_monday_max": int(counts.max()),
        "change_share": share(moved, before | ~before),
        "vol_annual": float(d.std(ddof=1) * np.sqrt(52)) if d.size > 2 else None,
        "unchanged_share_before_2025_10_06": share(exact, before),
        "unchanged_share_after": share(exact, ~before),
    }


LABELS = {
    "R7-01": "Provider gaps close (mean 4-week Fama-MacBeth slope < 0)",
    "R7-02": "Breadth of past cuts predicts next 4-week market move (slope > 0)",
    "R7-03": "AR(1) beats random walk for the weekly market move (Clark-West)",
    "R7-04": "B200/H100 ratio mean-reverts over 8 weeks (slope < 0)",
}
SIGNS = {"R7-01": -1, "R7-02": 1, "R7-03": 1, "R7-04": -1}


def run_tests(hist: pd.DataFrame, seed: int) -> dict[str, Any]:
    h100 = trim_start(weekly_panel(hist, "nvidia-h100"))
    b200 = weekly_panel(hist, "nvidia-b200")
    h200 = weekly_panel(hist, "nvidia-h200")
    tests = {
        "R7-01": r701(h100, seed),
        "R7-02": r702(h100, seed),
        "R7-03": r703(h100),
        "R7-04": r704(ratio_series(h100, b200)),
    }
    finish(tests, SIGNS)
    return {
        "tests": tests,
        "descriptive": {
            "H100": descriptive(h100),
            "B200": descriptive(b200),
            "H200": descriptive(h200),
        },
    }


def _fmt(v: Any, nd: int = 3) -> str:
    return f"{v:.{nd}f}" if isinstance(v, (int, float)) and np.isfinite(v) else "n/a"


def render(r: dict[str, Any], vintage: str) -> str:
    lines = [
        "# Round 7: GetDeploying per-provider price history (one-shot)",
        "",
        "Plan: docs/exploration_round7_plan.md (committed before the download). Holm over 4 "
        "tests at 5%. Mondays up to 2026-10-12, on-demand, Vast.ai, RunPod and Together "
        "excluded. No trade is simulated, so no cost assumption applies. Variants: 6 "
        "(project total 315).",
        "",
        f"Data: GetDeploying API, research access (vintage {vintage}). Source credit: "
        "GetDeploying, getdeploying.com. Aggregates only; no provider price rows are published.",
        "",
        "| Test | n | Estimate | 95% CI | One-sided p | Holm p | Verdict |",
        "|---|---|---|---|---|---|---|",
    ]
    for k, lab in LABELS.items():
        t = r["tests"][k]
        ci = t.get("ci95")
        ci_s = f"[{ci[0]:+.3f}, {ci[1]:+.3f}]" if ci else "n/a"
        lines.append(
            f"| {k} {lab} | {t['n']} | {_fmt(t.get('estimate'))} | {ci_s} | "
            f"{_fmt(t.get('p_one_sided'))} | {_fmt(t.get('p_holm'))} | {t['verdict']} |"
        )
    lines += ["", "## Descriptive", ""]
    for g, d in r["descriptive"].items():
        if not d.get("n_mondays"):
            lines.append(f"- {g}: no data.")
            continue
        lines.append(
            f"- {g}: {d['n_mondays']} Mondays ({d['first_monday']} to {d['last_monday']}), "
            f"{d['n_providers_ever']} providers ever, median {d['providers_per_monday_median']:.0f}"
            f" a week; share of provider-weeks with a move > 0.5%: {_fmt(d['change_share'], 2)}; "
            f"weekly market move volatility {_fmt(d['vol_annual'])} a year; exactly unchanged "
            f"before 2025-10-06 {_fmt(d['unchanged_share_before_2025_10_06'], 2)} vs after "
            f"{_fmt(d['unchanged_share_after'], 2)}."
        )
    return "\n".join(lines) + "\n"


def run_round7(cfg: Any) -> Path:  # pragma: no cover - reads git-ignored API data, runs once
    import json  # noqa: PLC0415

    from compute_curve.collectors import getdeploying_api as gd  # noqa: PLC0415

    out = cfg.path("reports") / "exploration"
    out.mkdir(parents=True, exist_ok=True)
    done = out / "round7.json"
    if done.exists():
        raise RuntimeError(f"{done} exists; round 7 runs once")
    vint = gd.latest_vintage(cfg.path("var") / "getdeploying_api")
    if vint is None:
        raise RuntimeError("no GetDeploying API download in var/getdeploying_api/")
    res = run_tests(gd.load_history(vint), cfg.project.seed)
    res["vintage"] = vint.name
    done.write_text(json.dumps(res, indent=2, default=float))
    path = out / "round7.md"
    path.write_text(render(res, vint.name))
    return path
