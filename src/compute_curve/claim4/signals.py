"""Index-derived signals for claim 4, aligned to US equity sessions without look-ahead.

Pre-registered in ``docs/claim4_plan.md`` section 4. For each GPU model the
fixed provider panel (frozen in ``config/default.toml`` ``[claim4]``) gives,
per index day ``d``:

* ``level``: the history-panel index value (provider-weighted median,
  identical to ``build_history_index``);
* ``dispersion``: the interquartile range, across panel providers present on
  ``d``, of the log of each provider's median eligible price;
* ``n_listings``: the number of eligible panel listings (the availability
  proxy, because sources rarely flag availability);
* ``ts_available``: when the day's snapshot was observed;
* ``ts_usable``: when claim 4 may first act on it, the later of
  ``ts_available + margin`` (60 minutes) and the daily cutoff (23:30 UTC on
  ``d``), which is when the live cycle runs. A backtest therefore sees
  exactly what the scheduled live cycle would have seen (decision D31).

A session ``t`` with official open ``O_t`` sees index day ``d*(t)``, the
latest day with full coverage and ``ts_usable <= O_t - buffer``. The
signals for session ``t`` are the changes between ``d*(t)`` and ``d*(t-1)``:

* ``level_<gpu>  = ln level[d*(t)] - ln level[d*(t-1)]``
* ``disp_<gpu>   = dispersion[d*(t)] - dispersion[d*(t-1)]``
* ``avail_<gpu>  = ln n_listings[d*(t)] - ln n_listings[d*(t-1)]``

If no new index day arrived between the two opens the change is 0.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd

from compute_curve.config import IndexConfig
from compute_curve.index.own_index import (
    aggregate,
    eligible_listings,
    latest_snapshot_per_source_day,
    prefer_sources,
)

GPU_MODELS = ("H100", "B200")
SIGNAL_KINDS = ("level", "disp", "avail")
SIGNAL_NAMES = tuple(f"{k}_{g.lower()}" for g in GPU_MODELS for k in SIGNAL_KINDS)

FEATURE_COLUMNS = (
    "as_of_date",
    "gpu_model",
    "level",
    "dispersion",
    "n_listings",
    "n_providers",
    "meets_coverage",
    "ts_available",
    "ts_usable",
)

DEFAULT_MARGIN_MINUTES = 60
DEFAULT_DAILY_CUTOFF_UTC = "23:30"


def iqr_log_provider_prices(prices: np.ndarray, providers: Sequence[str]) -> float:
    """IQR of ln(provider median price): one value per provider, linear interpolation."""
    s = pd.Series(np.asarray(prices, dtype=float)).groupby(list(providers)).median()
    logs = np.log(s.to_numpy(dtype=float))
    if logs.size < 2:
        return float("nan")
    q75, q25 = np.percentile(logs, [75, 25])
    return float(q75 - q25)


def usable_time(
    ts_available: pd.Series,
    as_of_date: pd.Series,
    margin_minutes: int = DEFAULT_MARGIN_MINUTES,
    daily_cutoff_utc: str = DEFAULT_DAILY_CUTOFF_UTC,
) -> pd.Series:
    """Later of ``ts_available + margin`` and ``daily_cutoff_utc`` on ``as_of_date``."""
    avail = pd.to_datetime(ts_available, utc=True) + pd.Timedelta(minutes=margin_minutes)
    hh, mm = (int(x) for x in daily_cutoff_utc.split(":"))
    days = pd.to_datetime(pd.Series(as_of_date, index=avail.index)).dt.tz_localize("UTC")
    cutoff = days + pd.Timedelta(hours=hh, minutes=mm)
    return avail.where(avail >= cutoff, cutoff)


def panel_features(
    obs: pd.DataFrame,
    cfg: IndexConfig,
    gpu_model: str,
    panel: Sequence[str],
    margin_minutes: int = DEFAULT_MARGIN_MINUTES,
    daily_cutoff_utc: str = DEFAULT_DAILY_CUTOFF_UTC,
) -> pd.DataFrame:
    """Daily level, dispersion and listing count for one GPU model's fixed panel."""
    if obs.empty or not panel:
        return pd.DataFrame(columns=list(FEATURE_COLUMNS))
    hist = obs.loc[obs["source"].isin(cfg.history_sources)]
    daily = latest_snapshot_per_source_day(hist)
    elig = prefer_sources(eligible_listings(daily, cfg, gpu_model), cfg.source_priority)
    elig = elig.loc[elig["provider"].isin(list(panel))]
    rows: list[dict[str, object]] = []
    for day, grp in elig.groupby("as_of_date", sort=True):
        prices = grp["price_usd_per_gpu_hour"].to_numpy(dtype=float)
        providers = grp["provider"].astype(str).tolist()
        n_prov = len(set(providers))
        rows.append(
            {
                "as_of_date": day,
                "gpu_model": gpu_model,
                "level": aggregate(prices, providers, cfg.method, cfg.trim_fraction),
                "dispersion": iqr_log_provider_prices(prices, providers),
                "n_listings": len(prices),
                "n_providers": n_prov,
                "meets_coverage": bool(
                    n_prov >= cfg.min_providers and len(prices) >= cfg.min_listings
                ),
                "ts_available": grp["ts_snapshot"].max(),
            }
        )
    out = pd.DataFrame(rows, columns=[c for c in FEATURE_COLUMNS if c != "ts_usable"])
    if out.empty:
        return out.assign(ts_usable=pd.Series(dtype="datetime64[ns, UTC]"))
    out["ts_usable"] = usable_time(
        out["ts_available"], out["as_of_date"], margin_minutes, daily_cutoff_utc
    )
    return out


def align_to_sessions(
    features: pd.DataFrame, sessions: pd.DataFrame, buffer_minutes: int = 5
) -> pd.DataFrame:
    """For each session, the latest covered index day usable before its open.

    ``sessions`` has columns ``session`` (date) and ``open_utc``. Returns one
    row per session with ``as_of_date`` (``d*``), ``level``, ``dispersion``,
    ``n_listings`` and ``ts_usable`` of that day; NaN before any day is
    usable.
    """
    cols = ["session", "open_utc", "as_of_date", "level", "dispersion", "n_listings", "ts_usable"]
    s = sessions[["session", "open_utc"]].sort_values("open_utc").reset_index(drop=True)
    f = features.loc[features["meets_coverage"].astype(bool)].copy()
    if f.empty:
        out = s.assign(as_of_date=None, level=np.nan, dispersion=np.nan, n_listings=np.nan)
        return out.assign(ts_usable=pd.NaT)[cols]
    f["ts_usable"] = pd.to_datetime(f["ts_usable"], utc=True)
    f = f.sort_values(["ts_usable", "as_of_date"])
    # A late snapshot of an earlier day must not replace a newer day: keep only
    # rows that raise the running maximum as_of_date among days usable so far.
    f["_ord"] = pd.to_datetime(f["as_of_date"])
    f = f.loc[f["_ord"] >= f["_ord"].cummax()]
    cutoff = pd.to_datetime(s["open_utc"], utc=True) - pd.Timedelta(minutes=buffer_minutes)
    left = pd.DataFrame({"_i": s.index, "_cut": cutoff}).sort_values("_cut")
    merged = pd.merge_asof(
        left,
        f[["ts_usable", "as_of_date", "level", "dispersion", "n_listings"]],
        left_on="_cut",
        right_on="ts_usable",
        direction="backward",
        allow_exact_matches=True,
    ).sort_values("_i")
    out = s.copy()
    for c in ("as_of_date", "level", "dispersion", "n_listings", "ts_usable"):
        out[c] = merged[c].to_numpy()
    return out[cols]


def session_signals(aligned: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Six signals per session from per-GPU aligned frames (keys ``H100``, ``B200``)."""
    out: pd.DataFrame | None = None
    for gpu in GPU_MODELS:
        a = aligned[gpu].sort_values("open_utc").reset_index(drop=True)
        lvl = np.log(a["level"].astype(float))
        cnt = np.log(a["n_listings"].astype(float))
        frame = pd.DataFrame(
            {
                "session": a["session"],
                "open_utc": a["open_utc"],
                f"asof_{gpu.lower()}": a["as_of_date"],
                f"level_{gpu.lower()}": lvl.diff(),
                f"disp_{gpu.lower()}": a["dispersion"].astype(float).diff(),
                f"avail_{gpu.lower()}": cnt.diff(),
            }
        )
        out = frame if out is None else out.merge(frame, on=["session", "open_utc"], how="outer")
    if out is None:
        raise ValueError("no GPU models to build signals from")
    return out.sort_values("open_utc").reset_index(drop=True)


def build_signals(
    obs: pd.DataFrame,
    cfg: IndexConfig,
    panels: dict[str, Sequence[str]],
    sessions: pd.DataFrame,
    buffer_minutes: int = 5,
    margin_minutes: int = DEFAULT_MARGIN_MINUTES,
    daily_cutoff_utc: str = DEFAULT_DAILY_CUTOFF_UTC,
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    """Session signals plus the per-GPU daily features they came from."""
    feats = {
        g: panel_features(obs, cfg, g, panels.get(g, []), margin_minutes, daily_cutoff_utc)
        for g in GPU_MODELS
    }
    aligned = {g: align_to_sessions(feats[g], sessions, buffer_minutes) for g in GPU_MODELS}
    return session_signals(aligned), feats
