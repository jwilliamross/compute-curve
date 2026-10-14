"""Round 7 post-hoc analysis (exploratory, labelled; docs/exploration_round7.md).

Run after the one-shot round 7. Nothing here is a confirmed test:
- robustness variants of the two confirmed tests (R7-01, R7-04);
- index-construction choices on the same provider data (basis risk);
- monthly-average settlement risk, as for a power-market monthly contract.

Writes aggregates only (D60).
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from compute_curve.claim4 import stats as cs
from compute_curve.collectors.getdeploying_api import EXCLUDED
from compute_curve.explore import round7 as r7

HYPERSCALERS = frozenset({"aws", "google-cloud", "microsoft-azure", "oracle-cloud"})
DAILY_FROM = "2026-07-30"
SPLIT = "2025-10-06"


def fm_slope(
    panel: pd.DataFrame,
    *,
    lag_premium: int = 0,
    drop: Iterable[str] = (),
    horizon: int = r7.H,
    start: str | None = None,
    end: str | None = None,
) -> dict[str, float]:
    """R7-01's Fama-MacBeth mean slope under one variation; Newey-West t at lag 6."""
    p = panel.drop(columns=[c for c in drop if c in panel.columns])
    slopes = []
    for i in range(lag_premium, len(p) - horizon):
        t = p.index[i]
        if (start and t < pd.Timestamp(start)) or (end and t >= pd.Timestamp(end)):
            continue
        base, now, fut = p.iloc[i - lag_premium], p.iloc[i], p.iloc[i + horizon]
        ok = base.notna() & now.notna() & fut.notna()
        if int(ok.sum()) < r7.MIN_CS:
            continue
        s = (base - base.median(skipna=True))[ok].to_numpy(float)
        c = (fut - now)[ok].to_numpy(float)
        if np.ptp(s) > 1e-12:
            slopes.append(float(np.polyfit(s, c, 1)[0]))
    x = np.asarray(slopes)
    if x.size < 3:
        return {"n": float(x.size)}
    se = cs.hac_mean_se(x, r7.LAG)
    return {"n": float(x.size), "mean": float(x.mean()), "t": float(x.mean() / se) if se else 0.0}


def balanced_ratio(h100: pd.DataFrame, b200: pd.DataFrame, min_share: float = 0.6) -> pd.Series:
    """R7-04 ratio over providers priced for both GPUs on >= ``min_share`` of weeks."""
    both = b200.notna() & h100.reindex(index=b200.index, columns=b200.columns).notna()
    keep = both.columns[both.mean() >= min_share]
    return r7.ratio_series(h100[keep.intersection(h100.columns)], b200[keep])


def on_demand(hist: pd.DataFrame, gpu: str) -> pd.DataFrame:
    h = hist.loc[
        (hist["gpu_model"] == gpu)
        & (hist["billing_type"] == "ON_DEMAND")
        & hist["reservation_months"].isna()
        & ~hist["provider"].isin(EXCLUDED)
    ].copy()
    h["price"] = pd.to_numeric(h["median_price"], errors="coerce")
    h["weight"] = pd.to_numeric(h["offering_count"], errors="coerce").fillna(1.0)
    h["date"] = pd.to_datetime(h["date"])
    return h.loc[h["price"] > 0]


def weighted_median(values: np.ndarray, weights: np.ndarray) -> float:
    o = np.argsort(values)
    v, w = values[o], weights[o]
    c = np.cumsum(w)
    return float(v[np.searchsorted(c, c[-1] / 2)])


def trimmed_mean(s: pd.Series, cut: float = 0.2) -> float:
    v = np.sort(s.to_numpy(float))
    k = int(len(v) * cut)
    return float(v[k : max(len(v) - k, k + 1)].mean())


def index_methods(h: pd.DataFrame) -> pd.DataFrame:
    """One value per day for four index constructions on the same provider rows."""
    g = h.groupby("date")
    out = pd.DataFrame(
        {
            "provider_median": g["price"].median(),
            "offering_weighted_median": g[["price", "weight"]].apply(
                lambda x: weighted_median(x["price"].to_numpy(), x["weight"].to_numpy())
            ),
            "provider_median_ex_hyperscalers": h.loc[~h["provider"].isin(HYPERSCALERS)]
            .groupby("date")["price"]
            .median(),
            "trimmed_mean_20": g["price"].apply(trimmed_mean),
            "n_providers": g["provider"].nunique(),
        }
    )
    return out


def settlement_risk(h: pd.DataFrame) -> dict[str, float]:
    """Monthly average of the Monday provider median vs its first Monday (power-style BOM risk)."""
    w = h.groupby("date")["price"].median()
    w = w.loc[w.index.dayofweek == 0]
    rows = [(s.iloc[0], s.mean()) for _, s in w.groupby(w.index.to_period("M")) if len(s) >= 3]
    r = pd.DataFrame(rows, columns=["first", "avg"])
    if len(r) < 3:
        return {"n_months": float(len(r))}
    dev = np.log(r["avg"] / r["first"]).abs()
    mom = np.log(r["avg"]).diff().dropna()
    return {
        "n_months": float(len(r)),
        "avg_vs_first_median": float(dev.median()),
        "avg_vs_first_max": float(dev.max()),
        "mom_sd": float(mom.std(ddof=1)),
        "mom_max_abs": float(mom.abs().max()),
        "zero_change_share": float((mom.abs() < 1e-9).mean()),
    }


def run(hist: pd.DataFrame) -> dict[str, Any]:
    h100 = r7.trim_start(r7.weekly_panel(hist, "nvidia-h100"))
    b200 = r7.weekly_panel(hist, "nvidia-b200")
    robust = {
        "main": fm_slope(h100),
        "lagged_premium": fm_slope(h100, lag_premium=1),
        "ex_hyperscalers": fm_slope(h100, drop=HYPERSCALERS),
        "before_split": fm_slope(h100, end=SPLIT),
        "from_split": fm_slope(h100, start=SPLIT),
        "horizon_13w": fm_slope(h100, horizon=13),
        "b200": fm_slope(r7.trim_start(b200)),
    }
    ratio = r7.ratio_series(h100, b200).dropna()
    r704b = r7.r704(balanced_ratio(h100, b200))
    methods: dict[str, Any] = {}
    risk: dict[str, Any] = {}
    for gpu in ("nvidia-h100", "nvidia-b200"):
        h = on_demand(hist, gpu)
        m = index_methods(h.loc[h["date"] >= DAILY_FROM])
        vals = m.drop(columns="n_providers")
        moves = np.log(vals).diff().abs() > 0.001
        methods[gpu] = {
            "days": len(m),
            "providers_per_day": float(m["n_providers"].median()),
            "mean": vals.mean().round(4).to_dict(),
            "latest": vals.iloc[-1].round(4).to_dict(),
            "latest_date": str(m.index.max().date()),
            "share_days_moving": moves.iloc[1:].mean().round(4).to_dict(),
        }
        risk[gpu] = settlement_risk(h)
    return {
        "r701_variants": robust,
        "r704_balanced": {
            k: v for k, v in r704b.items() if k in ("n", "slope", "t", "p_one_sided")
        },
        "ratio_first_last": [float(ratio.iloc[0]), float(ratio.iloc[-1])],
        "index_methods": methods,
        "settlement_risk": risk,
    }


def run_posthoc(cfg: Any) -> Path:  # pragma: no cover - reads git-ignored API data
    import json  # noqa: PLC0415

    from compute_curve.collectors import getdeploying_api as gd  # noqa: PLC0415

    vint = gd.latest_vintage(cfg.path("var") / "getdeploying_api")
    if vint is None:
        raise RuntimeError("no GetDeploying API download in var/getdeploying_api/")
    res = run(gd.load_history(vint)) | {"vintage": vint.name}
    out = cfg.path("reports") / "exploration" / "round7_posthoc.json"
    out.write_text(json.dumps(res, indent=2, default=float))
    return out
