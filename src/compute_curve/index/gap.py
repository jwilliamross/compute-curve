"""Claim 1b: does the gap between our index and Silicon Data's predict SD's next move?

Pre-registered in docs/index_gap_plan.md. Needs licensed SD history in
``data/manual/published_index/`` (B7, D59); until then the runner only
reports that it is waiting.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from compute_curve.claim4 import stats as cs
from compute_curve.statarb.power import holm

H = 5
MIN_PRIOR_GAP = 20
MIN_TRAIN = 40
MIN_OOS = 60
HAC_LAG = 4
BREAK_PAD = 2 * H
SD_BREAKS = (date(2025, 12, 4), date(2026, 4, 6), date(2026, 7, 15), date(2026, 9, 25))
INDEX_NAMES = {"H100": "SDH100RT", "B200": "SDB200RT"}
MODELS = {"GAP-1": ("dJ", "dI"), "GAP-2": ("dJ", "dI", "dev")}


def align(sd: pd.Series, own: pd.Series) -> pd.DataFrame:
    """Business days on which both indices have a value; log levels."""
    df = pd.concat({"I": sd, "J": own}, axis=1).dropna()
    df.index = pd.to_datetime(df.index)
    df = df.loc[df.index.dayofweek < 5].sort_index()
    return pd.DataFrame({"lnI": np.log(df["I"]), "lnJ": np.log(df["J"])}, index=df.index)


def near_break(days: pd.DatetimeIndex, breaks: Sequence[date], pad: int = BREAK_PAD) -> np.ndarray:
    """True where a day is within ``pad`` business days of a known SD break."""
    d = days.to_numpy("datetime64[D]")
    out = np.zeros(d.size, dtype=bool)
    for b in breaks:
        bb = np.datetime64(b, "D")
        lo = np.busday_count(np.minimum(d, bb), np.maximum(d, bb))
        out |= lo <= pad
    return out


def features(df: pd.DataFrame, breaks: Sequence[date] = SD_BREAKS) -> pd.DataFrame:
    g = df["lnJ"] - df["lnI"]
    prior_mean = g.expanding().mean().shift(1)
    prior_n = g.expanding().count().shift(1)
    out = pd.DataFrame(
        {
            "y": df["lnI"].shift(-H) - df["lnI"],
            "dJ": df["lnJ"] - df["lnJ"].shift(H),
            "dI": df["lnI"] - df["lnI"].shift(H),
            "dev": (g - prior_mean).where(prior_n >= MIN_PRIOR_GAP),
            "target_day": pd.Series(df.index, index=df.index).shift(-H),
        },
        index=df.index,
    )
    out["excluded"] = near_break(out.index, breaks)
    return out


def walk_forward(feat: pd.DataFrame, cols: Sequence[str]) -> tuple[np.ndarray, np.ndarray]:
    """Out-of-sample (actual, prediction); each fit uses rows whose target was known by t."""
    ok = feat.dropna(subset=["y", *cols]).loc[lambda d: ~d["excluded"]]
    actual, pred = [], []
    for t, row in ok.iterrows():
        train = ok.loc[ok["target_day"] <= t]
        if len(train) < MIN_TRAIN:
            continue
        x = np.column_stack([np.ones(len(train)), train[list(cols)].to_numpy(float)])
        beta, *_ = np.linalg.lstsq(x, train["y"].to_numpy(float), rcond=None)
        xt = np.r_[1.0, row[list(cols)].to_numpy(float)]
        actual.append(float(row["y"]))
        pred.append(float(xt @ beta))
    return np.asarray(actual), np.asarray(pred)


def evaluate(pooled: dict[str, tuple[np.ndarray, np.ndarray]]) -> dict[str, Any]:
    res: dict[str, Any] = {}
    ps = []
    for name, (y, m) in pooled.items():
        r: dict[str, Any] = {"n_oos": int(y.size)}
        if y.size < MIN_OOS:
            r["verdict"] = "waiting: fewer than 60 out-of-sample predictions"
            ps.append(1.0)
            res[name] = r
            continue
        cw = cs.clark_west(y, m, np.zeros_like(y), HAC_LAG)
        p = cw.p_value if cw is not None and np.isfinite(cw.p_value) else 1.0
        r |= {
            "clark_west": None if cw is None else cw.stat,
            "p_one_sided": p,
            "mse_model": float(np.mean((y - m) ** 2)),
            "mse_random_walk": float(np.mean(y**2)),
            "mae_gain_log": float(np.mean(np.abs(y)) - np.mean(np.abs(y - m))),
        }
        ps.append(p)
        res[name] = r
    for (_name, r), pa in zip(res.items(), holm(ps), strict=True):
        if "p_one_sided" in r:
            r["p_holm"] = float(pa)
            r["verdict"] = "pass" if pa <= 0.05 else "not confirmed"
    return res


def run_gap(cfg: Any) -> Path:  # pragma: no cover - reads git-ignored licensed data
    from compute_curve.pipeline import paths as ppaths  # noqa: PLC0415
    from compute_curve.storage import warehouse as wh  # noqa: PLC0415

    out = cfg.path("reports") / "index_gap"
    out.mkdir(parents=True, exist_ok=True)
    md = out / "status.md"
    pub = wh.load_published_index_csvs(
        ppaths(cfg)["manual_index"], cfg.nowcast.publication_lag_days
    )
    if pub.empty:
        md.write_text(
            "# Claim 1b index gap\n\nWaiting for licensed Silicon Data history in "
            "data/manual/published_index/ (B7). Nothing computed.\n"
        )
        return md
    own = pd.read_csv(cfg.path("reports") / "own_index.csv")
    own = own.loc[(own["series"] == "history_panel") & own["meets_coverage"].astype(bool)]
    pooled: dict[str, tuple[list[float], list[float]]] = {k: ([], []) for k in MODELS}
    for gpu, name in INDEX_NAMES.items():
        sd = pub.loc[pub["index_name"] == name].set_index("as_of_date")["value"]
        j = own.loc[own["gpu_model"] == gpu].set_index("as_of_date")["value"]
        if sd.empty or j.empty:
            continue
        feat = features(align(sd, j))
        for k, cols in MODELS.items():
            y, m = walk_forward(feat, cols)
            pooled[k][0].extend(y)
            pooled[k][1].extend(m)
    res = evaluate({k: (np.asarray(a), np.asarray(b)) for k, (a, b) in pooled.items()})
    done = out / "claim1b_result.json"
    if all("p_one_sided" in r for r in res.values()) and not done.exists():
        done.write_text(json.dumps(res, indent=2, default=float))
    lines = ["# Claim 1b index gap", "", "Derived numbers only (D59)."]
    lines += [
        f"- {k}: {r['n_oos']} out-of-sample predictions; {r['verdict']}." for k, r in res.items()
    ]
    md.write_text("\n".join(lines) + "\n")
    return md
