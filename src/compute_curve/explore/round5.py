"""Round 5: provider gaps and list-price trend in archived pages.

Plan: docs/exploration_round5_plan.md.

Runs once, on the verified Wayback rows (D58). Everything here follows the
plan committed before any archived row was read.
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

PROVIDERS = ("lambda", "coreweave", "nebius", "hyperstack", "verda")
MAX_AGE_DAYS = 92
HORIZON = 3
MIN_CS = 4
MIN_SECTIONS = 12
HAC_LAG = 3
TREND_MIN_PROVIDERS = 3
TREND_BLOCK = 6


def capture_prices(rows: pd.DataFrame) -> pd.DataFrame:
    """One price per (provider, capture): the median verified H100 on-demand per-GPU price."""
    r = rows.loc[
        (rows["gpu_model"] == "H100")
        & (rows["term"] == "on_demand")
        & rows["provider"].isin(PROVIDERS)
        & ~rows.get("is_synthetic", pd.Series(False, index=rows.index)).astype(bool)
    ]
    if r.empty:
        return pd.DataFrame(columns=["provider", "ts", "price"])
    ts = pd.to_datetime(r["ts_observed"], utc=True)
    g = r.assign(ts=ts).groupby(["provider", "ts"])["price_usd_per_gpu_hour"].median()
    return g.rename("price").reset_index()


def month_end_panel(caps: pd.DataFrame, first: date, last: date) -> pd.DataFrame:
    """Rows: month ends; columns: providers; value: latest capture price at most 92 days old."""
    ends = pd.date_range(pd.Timestamp(first), pd.Timestamp(last), freq="ME", tz="UTC")
    ends = ends + pd.Timedelta(hours=23, minutes=59, seconds=59)
    out = pd.DataFrame(index=ends, columns=list(PROVIDERS), dtype=float)
    for p, grp in caps.groupby("provider"):
        g = grp.sort_values("ts")
        for m in ends:
            prior = g.loc[g["ts"] <= m]
            if prior.empty:
                continue
            last_cap = prior.iloc[-1]
            if (m - last_cap["ts"]).days <= MAX_AGE_DAYS:
                out.loc[m, p] = float(last_cap["price"])
    return out


def cross_sections(panel: pd.DataFrame) -> list[tuple[pd.Timestamp, np.ndarray, np.ndarray]]:
    """(month, premium, 3-month outcome) for months with at least MIN_CS complete providers."""
    logp = np.log(panel.astype(float))
    out = []
    for i in range(len(logp) - HORIZON):
        now, fut = logp.iloc[i], logp.iloc[i + HORIZON]
        prem = now - now.median(skipna=True)
        ok = now.notna() & fut.notna()
        if int(ok.sum()) >= MIN_CS:
            out.append((logp.index[i], prem[ok].to_numpy(), (fut - now)[ok].to_numpy()))
    return out


def fm_slopes(sections: list[tuple[pd.Timestamp, np.ndarray, np.ndarray]]) -> np.ndarray:
    """Per-month OLS slopes; a month with no premium variation gives no slope."""
    slopes = []
    for _, s, c in sections:
        if np.ptp(s) > 1e-12:
            slopes.append(float(np.polyfit(s, c, 1)[0]))
    return np.asarray(slopes, dtype=float)


def r501(panel: pd.DataFrame) -> dict[str, Any]:
    slopes = fm_slopes(cross_sections(panel))
    res: dict[str, Any] = {"n_sections": int(slopes.size)}
    if slopes.size < MIN_SECTIONS:
        res["verdict"] = "too little history to conclude"
        return res
    se = cs.hac_mean_se(slopes, HAC_LAG)
    t = float(slopes.mean() / se) if se > 0 else float("nan")
    p = float(st.t.cdf(t, df=slopes.size - 1)) if np.isfinite(t) else float("nan")
    res |= {
        "mean_slope": float(slopes.mean()),
        "hac_se": float(se),
        "p_one_sided": p,
        "verdict": "pass" if np.isfinite(p) and p <= 0.05 else "not confirmed",
    }
    return res


def r502(panel: pd.DataFrame, seed: int, n_boot: int = 2000) -> dict[str, Any]:
    count = panel.notna().sum(axis=1)
    med = np.log(panel.astype(float)).median(axis=1, skipna=True)[count >= TREND_MIN_PROVIDERS]
    if med.size < 6:
        return {"n_months": int(med.size), "verdict": "too little history to conclude"}
    years = ((med.index - med.index[0]).days / 365.25).to_numpy(float)
    y = med.to_numpy(float)
    slope = float(np.polyfit(years, y, 1)[0])
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(n_boot):
        idx = circular_block_indices(y.size, TREND_BLOCK, rng)
        if np.ptp(years[idx]) > 0:
            boots.append(float(np.polyfit(years[idx], y[idx], 1)[0]))
    lo, hi = np.quantile(boots, [0.025, 0.975])
    return {
        "n_months": int(y.size),
        "slope_per_year": slope,
        "ci95": [float(lo), float(hi)],
        "first_month": str(med.index[0].date()),
        "last_month": str(med.index[-1].date()),
    }


def load_archive(data_dir: Path) -> pd.DataFrame:  # pragma: no cover - reads committed data
    import duckdb  # noqa: PLC0415

    folder = data_dir / "raw" / "archive"
    if not any(folder.glob("wayback_*/**/*.parquet")):
        return pd.DataFrame()
    pattern = (folder / "wayback_*" / "**" / "*.parquet").as_posix()
    return duckdb.read_parquet(pattern, union_by_name=True).df()


def render(r: dict[str, Any]) -> str:
    a, b = r["r501"], r["r502"]
    lines = [
        "# Round 5: archived list prices (one-shot; docs/exploration_round5_plan.md)",
        "",
        f"Verified Wayback rows (D58): {r['n_rows']} rows, {r['n_captures']} provider "
        f"captures, months {r['first']} to {r['last']}. Research-only data.",
        "",
        "## R5-01: do provider gaps close? (monthly Fama-MacBeth, 3-month outcome)",
        "",
        f"- Cross-sections with at least {MIN_CS} providers: {a['n_sections']}.",
    ]
    if "mean_slope" in a:
        lines.append(
            f"- Mean slope {a['mean_slope']:.3f} (Newey-West SE {a['hac_se']:.3f}, lag "
            f"{HAC_LAG}); one-sided p {a['p_one_sided']:.3f}. Verdict: **{a['verdict']}**."
        )
    else:
        lines.append(f"- Verdict: **{a['verdict']}** (at least {MIN_SECTIONS} needed).")
    lines += ["", "## R5-02: list-price trend (descriptive, not a test)", ""]
    if "slope_per_year" in b:
        lines.append(
            f"- Median H100 on-demand list price: {b['slope_per_year']:+.3f} log points a year, "
            f"95% block-bootstrap CI [{b['ci95'][0]:+.3f}, {b['ci95'][1]:+.3f}], "
            f"{b['n_months']} months ({b['first_month']} to {b['last_month']}). "
            "GetDeploying drift for comparison: +0.135 (CI [-0.33, 0.60], D55)."
        )
    else:
        lines.append(f"- {b['verdict']} ({b['n_months']} months).")
    lines += [
        "",
        "Variants: 2 (project total 299). List prices only: no discounts, contracts or "
        "spot prices; captures are irregular.",
    ]
    return "\n".join(lines) + "\n"


def run_round5(cfg: Any) -> Path:  # pragma: no cover - reads committed data, runs once
    import json  # noqa: PLC0415

    out = cfg.path("reports") / "exploration"
    out.mkdir(parents=True, exist_ok=True)
    done = out / "round5.json"
    if done.exists():
        raise RuntimeError(f"{done} exists; round 5 runs once")
    rows = load_archive(cfg.path("data"))
    caps = capture_prices(rows)
    if caps.empty:
        raise RuntimeError("no verified archived H100 rows yet")
    first = date(2023, 1, 1)
    last_ts = caps["ts"].max()
    last = (last_ts.replace(day=1) - pd.Timedelta(days=1)).date()  # last complete month
    caps = caps.loc[caps["ts"] <= pd.Timestamp(last, tz="UTC") + pd.Timedelta(days=1)]
    panel = month_end_panel(caps, first, last)
    res = {
        "n_rows": len(rows),
        "n_captures": len(caps),
        "first": str(first),
        "last": str(last),
        "r501": r501(panel),
        "r502": r502(panel, cfg.project.seed),
    }
    done.write_text(json.dumps(res, indent=2))
    path = out / "round5.md"
    path.write_text(render(res))
    return path
