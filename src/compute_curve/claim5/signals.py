"""Claim-5 signals from AWS GPU spot prices, aligned to US equity sessions.

Pre-registered in docs/claim5_plan.md section 3. For GPU class ``g`` and
session ``t``:

* ``d*(t)``: the latest price day whose value is usable before the open,
  where day ``d``'s value (the price in effect at 23:30 UTC) is usable from
  23:30 UTC + 60 minutes, the timing of claim 4 (D31). Because the data
  cover every calendar day, ``d*(t)`` must be the calendar day before the
  session (``max_age_days = 1``); otherwise the session has no signal,
  which marks the dataset's 2026-03 to 2026-06 gap and its end.
* Matched pools: pools (availability zone x instance type) priced on both
  ``d*(t-1)`` and ``d*(t)``. At least ``min_pools`` are required.
* ``level_g = median over matched pools of ln p(d*(t)) - ln p(d*(t-1))``:
  a price change free of composition effects when pools enter or leave.
* ``disp_g = IQR(ln p(d*(t))) - IQR(ln p(d*(t-1)))`` over the matched pools.

There is no availability signal: within a month a pool can only appear,
never disappear, so a pool count would mostly mark month starts (D37).
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd

from compute_curve.config import Claim5Config


def _iqr(x: np.ndarray) -> float:
    if x.size < 2:
        return float("nan")
    q75, q25 = np.percentile(x, [75, 25])
    return float(q75 - q25)


def session_days(
    days: Sequence[object],
    sessions: pd.DataFrame,
    cutoff_utc: str,
    margin_minutes: int,
    buffer_minutes: int,
    max_age_days: int,
) -> pd.Series:
    """``d*(t)`` per session (index aligned with ``sessions``); None when stale or absent."""
    hh, mm = (int(x) for x in cutoff_utc.split(":"))
    d = pd.Series(sorted(set(days)))
    if d.empty:
        return pd.Series([None] * len(sessions), index=sessions.index, dtype=object)
    usable = (
        pd.to_datetime(d).dt.tz_localize("UTC")
        + pd.Timedelta(hours=hh, minutes=mm)
        + pd.Timedelta(minutes=margin_minutes)
    )
    right = pd.DataFrame({"usable": usable, "day": d}).sort_values("usable")
    cut = pd.to_datetime(sessions["open_utc"], utc=True) - pd.Timedelta(minutes=buffer_minutes)
    left = pd.DataFrame({"_i": sessions.index, "cut": cut}).sort_values("cut")
    m = pd.merge_asof(left, right, left_on="cut", right_on="usable", direction="backward")
    m = m.sort_values("_i").set_index("_i")
    out = []
    for i, row in m.iterrows():
        day = row["day"]
        if day is None or pd.isna(day):
            out.append(None)
            continue
        age = (sessions.loc[i, "session"] - day).days
        out.append(day if age <= max_age_days else None)
    return pd.Series(out, index=sessions.index, dtype=object)


def class_signals(
    pools: pd.DataFrame, gpu: str, sessions: pd.DataFrame, c5: Claim5Config, buffer_minutes: int
) -> pd.DataFrame:
    """Level and dispersion signals for one GPU class."""
    g = gpu.lower()
    sess = sessions.sort_values("open_utc").reset_index(drop=True)
    pg = pools.loc[pools["gpu"] == gpu]
    out = sess[["session", "open_utc"]].copy()
    out[f"asof_{g}"] = None
    out[f"level_{g}"] = np.nan
    out[f"disp_{g}"] = np.nan
    if pg.empty:
        return out
    wide = np.log(
        pg.assign(pool=pg["az_id"] + "|" + pg["instance_type"]).pivot_table(
            index="day", columns="pool", values="price_per_gpu_hour", aggfunc="first"
        )
    )
    dstar = session_days(
        list(wide.index),
        sess,
        c5.cutoff_utc,
        c5.availability_margin_minutes,
        buffer_minutes,
        c5.max_age_days,
    )
    out[f"asof_{g}"] = dstar.to_numpy()
    for i in range(1, len(sess)):
        d0, d1 = dstar.iloc[i - 1], dstar.iloc[i]
        if d0 is None or d1 is None:
            continue
        a, b = wide.loc[d0], wide.loc[d1]
        both = a.notna() & b.notna()
        if int(both.sum()) < c5.min_pools:
            continue
        out.loc[i, f"level_{g}"] = float(np.median(b[both] - a[both]))
        out.loc[i, f"disp_{g}"] = _iqr(b[both].to_numpy()) - _iqr(a[both].to_numpy())
    return out


def build_signals(
    pools: pd.DataFrame, sessions: pd.DataFrame, c5: Claim5Config, buffer_minutes: int = 5
) -> pd.DataFrame:
    """All claim-5 signals per session (``session``, ``open_utc``, ``asof_*``, signals)."""
    frames = [class_signals(pools, gpu, sessions, c5, buffer_minutes) for gpu in c5.gpu_classes]
    out = frames[0]
    for f in frames[1:]:
        out = out.merge(f, on=["session", "open_utc"], how="outer")
    return out.sort_values("open_utc").reset_index(drop=True)
