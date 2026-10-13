"""Round 6: trading-relevant tests on archived list prices (docs/exploration_round6_plan.md).

Runs once. Month-end prices exactly as round 5; stock months from the
cached Alpaca closes (claim 6). Holm over R6-01..R6-03.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import scipy.stats as st

from compute_curve.claim4 import stats as cs
from compute_curve.explore import round5 as r5

MIN_OBS = 10
MIN_PRIOR = 3
MIN_TRAIN = 12
ALPHA = 0.05


def median_log(panel: pd.DataFrame) -> pd.Series:
    return np.log(panel.astype(float)).median(axis=1, skipna=True)


def ratio_series(h100: pd.DataFrame, b200: pd.DataFrame) -> pd.Series:
    """L(m): median over providers with both of ln(B200/H100); NaN if none."""
    lr = np.log(b200.astype(float)) - np.log(h100.astype(float))
    return lr.median(axis=1, skipna=True)


def ols_slope_test(x: np.ndarray, y: np.ndarray, lag: int, sign: int) -> dict[str, Any]:
    """Slope of y on x with Newey-West SE; one-sided p in the direction ``sign``."""
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    res: dict[str, Any] = {"n": int(x.size)}
    if x.size < MIN_OBS or np.ptp(x) == 0:
        res["verdict"] = "too little history to conclude"
        return res
    xc = x - x.mean()
    b = float(xc @ (y - y.mean()) / (xc @ xc))
    e = (y - y.mean()) - b * xc
    # Newey-West variance of the slope: sum of weighted autocovariances of xc*e.
    u = xc * e
    s = float(u @ u)
    for k in range(1, min(lag, u.size - 1) + 1):
        s += 2 * (1 - k / (lag + 1)) * float(u[k:] @ u[:-k])
    se = float(np.sqrt(s) / (xc @ xc))
    t = b / se if se > 0 else float("nan")
    p = float(st.t.sf(sign * t, df=x.size - 2)) if np.isfinite(t) else float("nan")
    res |= {
        "slope": b,
        "se": se,
        "t": float(t),
        "p_one_sided": p,
        "corr": float(np.corrcoef(x, y)[0, 1]),
    }
    return res


def r601(ratio: pd.Series) -> dict[str, Any]:
    L = ratio.dropna()
    d, out = [], []
    vals = L.to_numpy(float)
    idx = L.index
    for i in range(len(L)):
        if i < MIN_PRIOR:
            continue
        target = idx[i] + pd.DateOffset(months=3)
        fut = L.loc[(L.index.year == target.year) & (L.index.month == target.month)]
        if fut.empty:
            continue
        d.append(vals[i] - vals[:i].mean())
        out.append(float(fut.iloc[0]) - vals[i])
    return ols_slope_test(np.asarray(d), np.asarray(out), lag=3, sign=-1)


def monthly_stock_excess(closes: pd.DataFrame, members: list[str], bench: str) -> pd.Series:
    """Equal-weight member return minus benchmark return per calendar month (month-end index)."""
    me = closes.groupby(closes.index.to_period("M")).last()
    ret = me / me.shift(1) - 1
    eq = ret[[m for m in members if m in ret.columns]].mean(axis=1, skipna=True)
    ex = eq - ret[bench]
    ex.index = ex.index.to_timestamp("M")
    return ex.dropna()


def r602(h100_med: pd.Series, excess: pd.Series) -> dict[str, Any]:
    dp = h100_med.diff()
    dp.index = dp.index.tz_localize(None).normalize().to_period("M")
    ex = excess.copy()
    ex.index = ex.index.to_period("M")
    x, y = [], []
    for m, v in dp.items():
        nxt = m + 1
        if np.isfinite(v) and nxt in ex.index:
            x.append(float(v))
            y.append(float(ex.loc[nxt]))
    return ols_slope_test(np.asarray(x), np.asarray(y), lag=1, sign=1)


def r603(h100_med: pd.Series) -> dict[str, Any]:
    dp = h100_med.diff().to_numpy(float)
    actual, model = [], []
    for t in range(len(dp) - 1):
        hist = dp[: t + 1]
        hist = hist[np.isfinite(hist)]
        if hist.size < MIN_TRAIN + 1 or not np.isfinite(dp[t + 1]):
            continue
        x0, x1 = hist[:-1], hist[1:]
        if np.ptp(x0) == 0:
            fc = 0.0
        else:
            b = float(np.polyfit(x0, x1, 1)[0])
            a = float(x1.mean() - b * x0.mean())
            fc = a + b * hist[-1]
        actual.append(dp[t + 1])
        model.append(fc)
    y, m = np.asarray(actual), np.asarray(model)
    res: dict[str, Any] = {"n": int(y.size)}
    if y.size < MIN_OBS:
        res["verdict"] = "too little history to conclude"
        return res
    cw = cs.clark_west(y, m, np.zeros_like(y), lag=1)
    if cw is None:
        res["verdict"] = "too little history to conclude"
        return res
    res |= {
        "cw_stat": cw.stat,
        "p_one_sided": cw.p_value,
        "mse_model": float(np.mean((y - m) ** 2)),
        "mse_random_walk": float(np.mean(y**2)),
    }
    return res


def descriptive(panel: pd.DataFrame) -> dict[str, float]:
    med = median_log(panel).diff().dropna()
    lp = np.log(panel.astype(float))
    ch = lp.diff()
    present = ch.notna()
    changed = (ch.abs() > 1e-9) & present
    return {
        "vol_annual": float(med.std(ddof=1) * np.sqrt(12)) if med.size > 2 else float("nan"),
        "n_months": int(med.size),
        "change_share": float(changed.sum().sum() / max(int(present.sum().sum()), 1)),
    }


def finish(tests: dict[str, dict[str, Any]]) -> None:
    names = [k for k in tests if "p_one_sided" in tests[k]]
    ps = [tests[k]["p_one_sided"] if np.isfinite(tests[k]["p_one_sided"]) else 1.0 for k in names]
    # Holm over all three declared tests (a test that could not run counts as p = 1).
    full = ps + [1.0] * (3 - len(ps))
    order = np.argsort(full)
    adj = np.empty(3)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (3 - rank) * full[i]))
        adj[i] = running
    for k, a in zip(names, adj[: len(names)], strict=True):
        tests[k]["p_holm"] = float(a)
        tests[k]["verdict"] = "pass" if a <= ALPHA else "not confirmed"


def render(r: dict[str, Any]) -> str:
    t = r["tests"]
    lines = [
        "# Round 6: archived list prices, trading-relevant tests (one-shot)",
        "",
        "Plan: docs/exploration_round6_plan.md. Holm over 3 tests at 5%. Research only.",
        "",
        "| Test | n | Estimate | One-sided p | Holm p | Verdict |",
        "|---|---|---|---|---|---|",
    ]
    labels = {
        "R6-01": "B200/H100 ratio mean reversion (slope)",
        "R6-02": "H100 price change -> next-month stock excess (slope)",
        "R6-03": "AR(1) vs random walk for monthly H100 change (Clark-West)",
    }
    for k, lab in labels.items():
        v = t[k]
        est = v.get("slope", v.get("cw_stat", float("nan")))
        lines.append(
            f"| {k} {lab} | {v['n']} | {est:.3f} | {v.get('p_one_sided', float('nan')):.3f} | "
            f"{v.get('p_holm', float('nan')):.3f} | {v['verdict']} |"
        )
    d = r["descriptive"]
    lines += [
        "",
        "## Descriptive",
        "",
        f"- H100 median list price: annualised volatility of monthly log changes "
        f"{d['H100']['vol_annual']:.3f}; share of provider-months with a price change "
        f"{d['H100']['change_share']:.2f} ({d['H100']['n_months']} months).",
        f"- B200: volatility {d['B200']['vol_annual']:.3f}; change share "
        f"{d['B200']['change_share']:.2f} ({d['B200']['n_months']} months).",
    ]
    return "\n".join(lines) + "\n"


def run_round6(cfg: Any) -> Path:  # pragma: no cover - reads committed and cached local data
    import json  # noqa: PLC0415

    from compute_curve.statarb.pipeline import ETF, load_prices  # noqa: PLC0415

    out = cfg.path("reports") / "exploration"
    out.mkdir(parents=True, exist_ok=True)
    done = out / "round6.json"
    if done.exists():
        raise RuntimeError(f"{done} exists; round 6 runs once")
    rows = r5.load_archive(cfg.path("data"))
    first, last = date(2023, 1, 1), date(2026, 9, 30)
    panels = {}
    for gpu in ("H100", "B200"):
        caps = r5.capture_prices(rows, gpu)
        caps = caps.loc[caps["ts"] <= pd.Timestamp(last, tz="UTC") + pd.Timedelta(days=1)]
        panels[gpu] = r5.month_end_panel(caps, first, last)
    h100_med = median_log(panels["H100"])
    ratio = ratio_series(panels["H100"], panels["B200"])
    prices = load_prices(cfg)
    members = cfg.claim4.universe.members()
    excess = monthly_stock_excess(prices.closes, members, ETF)
    excess = excess.loc[(excess.index >= "2024-10-01") & (excess.index <= "2026-09-30")]
    tests = {"R6-01": r601(ratio), "R6-02": r602(h100_med, excess), "R6-03": r603(h100_med)}
    finish(tests)
    res = {
        "tests": tests,
        "descriptive": {g: descriptive(p) for g, p in panels.items()},
        "stock_months": [str(excess.index.min().date()), str(excess.index.max().date())],
    }
    done.write_text(json.dumps(res, indent=2, default=float))
    path = out / "round6.md"
    path.write_text(render(res))
    return path
