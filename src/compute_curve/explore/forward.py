"""Shadow forward test of round-1 candidates (docs/exploration_plan.md section 9).

Candidate H05: the CGI H100 index's past 6-hour change forecasts the next
6-hour change with the frozen coefficients (a reversal). This module only
logs forecasts and outcomes. It sends no order and touches no account.

Point in time:

* each CGI value is taken from the first vintage in which it was observed,
  so a later revision never changes a logged number;
* a value CGI generated more than ``max_publish_lag_minutes`` after its
  stamp is excluded (in the exploration and confirmation data the largest
  lag was about 8 minutes);
* a forecast row, once logged, is never rewritten; only its outcome is
  filled in when it becomes known;
* the decision time is 10 minutes after each hourly stamp, after the value
  stamped there is published.

The test itself is evaluated once, after the last decision point's outcome
is known, on forward data only, with the confirmation rules C1 and C2.
"""

from __future__ import annotations

import json
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats as st

from compute_curve.claim4 import stats as cs
from compute_curve.config import ExplorationConfig, ForwardConfig
from compute_curve.explore.hypotheses import SPECS, cgi_hourly

LOG_COLUMNS = ["tau", "decided_at", "x", "forecast", "known_at", "y", "logged_at"]
DECISION_DELAY = pd.Timedelta(minutes=10)
HORIZON = pd.Timedelta(hours=6)


def point_in_time(rows: pd.DataFrame, gpu: str, max_lag_minutes: int) -> tuple[pd.DataFrame, dict]:
    """First-observed CGI value per stamp, published on time; plus revision counts.

    ``rows`` has ``as_of``, ``gpu_model``, ``value``, ``ts_observed`` and
    ``raw_json`` (with ``generated_at``).
    """
    r = rows.loc[rows["gpu_model"] == gpu].copy()
    if r.empty:
        return pd.DataFrame(columns=["as_of", "gpu_model", "value"]), {"revised": 0, "late": 0}
    r["as_of"] = pd.to_datetime(r["as_of"], utc=True)
    r["ts_observed"] = pd.to_datetime(r["ts_observed"], utc=True)
    gen = r["raw_json"].map(lambda s: json.loads(s).get("generated_at") if s else None)
    r["generated_at"] = pd.to_datetime(gen, utc=True)
    r = r.sort_values(["as_of", "ts_observed"])
    first = r.drop_duplicates("as_of", keep="first")
    later = r.merge(first[["as_of", "value"]], on="as_of", suffixes=("", "_first"))
    revised = int(
        later.loc[(later["value"] - later["value_first"]).abs() > 1e-9, "as_of"].nunique()
    )
    lag = first["generated_at"] - first["as_of"]
    ok = lag.notna() & (lag <= pd.Timedelta(minutes=max_lag_minutes))
    out = first.loc[ok, ["as_of", "gpu_model", "value"]].reset_index(drop=True)
    return out, {"revised": revised, "late": int((~ok).sum())}


def decision_points(fwd: ForwardConfig) -> pd.DatetimeIndex:
    """Hourly stamps whose signal window and outcome window both lie in the forward window."""
    start = pd.Timestamp(fwd.start).tz_convert("UTC").ceil("h") + HORIZON
    end = (pd.Timestamp(fwd.end).tz_convert("UTC") - HORIZON).floor("h")
    return pd.date_range(start, end, freq="h")


def shadow_rows(
    values: pd.DataFrame,
    frozen: dict[str, Any],
    fwd: ForwardConfig,
    now: pd.Timestamp,
    max_age_minutes: int,
) -> pd.DataFrame:
    """Frozen forecasts for every decision point decided by ``now``, outcomes where known."""
    pts = decision_points(fwd)
    pts = pts[pts + DECISION_DELAY <= now]
    if pts.empty or values.empty:
        return pd.DataFrame(columns=LOG_COLUMNS)
    start = pd.Timestamp(fwd.start).tz_convert("UTC")
    v = cgi_hourly(values.loc[values["as_of"] >= start], "H100", max_age_minutes).asfreq("h")
    x = (v - v.shift(6)).reindex(pts)
    y = (v.shift(-6) - v).reindex(pts)
    known_at = pts + HORIZON + DECISION_DELAY
    y = y.where(known_at <= now)
    a, b = float(frozen["intercept"]), float(frozen["slope"])
    out = pd.DataFrame(
        {
            "tau": pts,
            "decided_at": pts + DECISION_DELAY,
            "x": x.to_numpy(),
            "forecast": a + b * x.to_numpy(),
            "known_at": known_at,
            "y": y.to_numpy(),
            "logged_at": now,
        }
    )
    return out.dropna(subset=["x"]).reset_index(drop=True)


def merge_log(old: pd.DataFrame | None, new: pd.DataFrame) -> pd.DataFrame:
    """Append new decision points; fill missing outcomes; never rewrite a forecast."""
    if old is None or old.empty:
        return new[LOG_COLUMNS].sort_values("tau").reset_index(drop=True)
    old = old[LOG_COLUMNS].copy()
    for c in ("tau", "decided_at", "known_at", "logged_at"):
        old[c] = pd.to_datetime(old[c], utc=True)
    fill = new.set_index("tau")["y"]
    missing = old["y"].isna() & old["tau"].isin(fill.index)
    old.loc[missing, "y"] = fill.reindex(old.loc[missing, "tau"]).to_numpy()
    fresh = new.loc[~new["tau"].isin(old["tau"])]
    return (
        pd.concat([old, fresh[LOG_COLUMNS]], ignore_index=True)
        .sort_values("tau")
        .reset_index(drop=True)
    )


def window_complete(log: pd.DataFrame, fwd: ForwardConfig, now: pd.Timestamp) -> bool:
    last = decision_points(fwd)[-1]
    return bool(now >= last + HORIZON + DECISION_DELAY)


def evaluate_forward(
    log: pd.DataFrame, frozen: dict[str, Any], ecfg: ExplorationConfig, n_candidates: int
) -> dict[str, Any]:
    """C1 (one-sided Newey-West, Holm across live candidates) and C2 on forward data only."""
    spec = SPECS[frozen["hid"]]
    d = log.dropna(subset=["x", "y"])
    x, y = d["x"].to_numpy(float), d["y"].to_numpy(float)
    sign = int(frozen["direction"])
    out: dict[str, Any] = {"hid": frozen["hid"], "n": int(x.size)}
    fit = cs.ols_hac(x, y, spec.lag)
    p1 = float(st.t.sf(sign * fit.t_stat, df=x.size - 2)) if fit is not None else float("nan")
    p_holm = min(1.0, p1 * n_candidates) if np.isfinite(p1) else float("nan")
    pred = d["forecast"].to_numpy(float)

    def r2(base: np.ndarray) -> float:
        den = float(np.sum((y - base) ** 2))
        return float(1.0 - np.sum((y - pred) ** 2) / den) if den > 0 else float("nan")

    r2_zero = r2(np.zeros_like(y)) if y.size else float("nan")
    r2_mean = r2(np.full_like(y, float(frozen["y_mean_explore"]))) if y.size else float("nan")
    c1 = bool(np.isfinite(p_holm) and p_holm <= ecfg.confirm_alpha)
    c2 = bool(np.isfinite(r2_zero) and np.isfinite(r2_mean) and r2_zero > 0 and r2_mean > 0)
    out.update(
        {
            "slope": fit.slope if fit is not None else float("nan"),
            "p_one_sided": p1,
            "p_holm": p_holm,
            "oos_r2_zero": r2_zero,
            "oos_r2_mean": r2_mean,
            "c1": c1,
            "c2": c2,
            "passed": c1 and c2,
        }
    )
    return out
