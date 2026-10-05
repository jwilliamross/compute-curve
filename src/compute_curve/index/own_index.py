"""Our own H100 / B200 on-demand rental index from collected listings.

Methodology (derived in ``docs/index_methodology.md``):

1. Date each listing by its effective observation time (the source's own
   timestamp for aggregators, ours otherwise). For each source and date keep
   only the latest snapshot.
2. Keep listings with term in ``index.terms``, availability not
   ``unavailable``, an allowed form-factor variant, a non-excluded provider
   (hyperscalers are excluded), and a region that is US/North America or
   unknown (the contracts reference "Geography: United States").
3. When several sources report the same provider on the same day, keep only
   the highest-priority source (direct provider pages before aggregators).
4. Price unit is USD per GPU-hour.
5. Aggregate with the pre-registered primary method,
   ``provider_weighted_median``: every provider carries total weight 1, split
   equally across its listings, and the index is the weighted median. This
   stops a marketplace with hundreds of listings from outvoting a provider
   that publishes one list price.

Alternatives (``pooled_median``, ``trimmed_mean``) exist only as declared
robustness variants and are counted in ``docs/variants_log.md`` when used.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd

from compute_curve.config import IndexConfig

INDEX_COLUMNS = (
    "as_of_date",
    "gpu_model",
    "value",
    "method",
    "n_listings",
    "n_providers",
    "meets_coverage",
    "ts_available",
)


def weighted_median(
    values: Sequence[float] | np.ndarray, weights: Sequence[float] | np.ndarray
) -> float:
    """Lower weighted median: smallest v with cumulative weight >= half the total.

    When the cumulative weight hits exactly one half at a value, the midpoint
    of that value and the next one is returned, which reduces to the ordinary
    median for equal weights.
    """
    v = np.asarray(values, dtype=float)
    w = np.asarray(weights, dtype=float)
    if v.size == 0 or v.size != w.size:
        raise ValueError("values and weights must be non-empty and equal length")
    if np.any(w < 0) or w.sum() <= 0:
        raise ValueError("weights must be non-negative with positive sum")
    order = np.argsort(v, kind="mergesort")
    v, w = v[order], w[order]
    cw = np.cumsum(w)
    half = 0.5 * cw[-1]
    idx = int(np.searchsorted(cw, half, side="left"))
    if np.isclose(cw[idx], half) and idx + 1 < v.size:
        return float(0.5 * (v[idx] + v[idx + 1]))
    return float(v[idx])


def trimmed_mean(values: Sequence[float] | np.ndarray, trim_fraction: float) -> float:
    """Symmetric trimmed mean dropping ``floor(n * trim_fraction)`` from each tail."""
    v = np.sort(np.asarray(values, dtype=float))
    if v.size == 0:
        raise ValueError("empty input")
    k = int(np.floor(v.size * trim_fraction))
    core = v[k : v.size - k] if v.size - 2 * k > 0 else v
    return float(core.mean())


def provider_weights(providers: Sequence[str]) -> np.ndarray:
    """Weight 1/n_p for each of the n_p listings of provider p."""
    s = pd.Series(list(providers))
    counts = s.map(s.value_counts())
    return (1.0 / counts.to_numpy(dtype=float)).astype(float)


def aggregate(prices: np.ndarray, providers: Sequence[str], method: str, trim: float) -> float:
    if method == "provider_weighted_median":
        return weighted_median(prices, provider_weights(providers))
    if method == "pooled_median":
        return float(np.median(prices))
    if method == "trimmed_mean":
        return trimmed_mean(prices, trim)
    raise ValueError(f"unknown method {method}")


def eligible_listings(obs: pd.DataFrame, cfg: IndexConfig, gpu_model: str) -> pd.DataFrame:
    """Filter observations to those that enter the index for ``gpu_model``."""
    if obs.empty:
        return obs
    allowed_variants = set(cfg.variants.get(gpu_model, []))
    region = obs["region"] if "region" in obs.columns else pd.Series(None, index=obs.index)
    region_ok = region.isin(cfg.allowed_regions)
    if cfg.include_unknown_region:
        region_ok |= region.isna()
    mask = (
        (obs["gpu_model"] == gpu_model)
        & obs["term"].isin(cfg.terms)
        & (obs["availability"] != "unavailable")
        & obs["gpu_variant"].isin(allowed_variants)
        & ~obs["provider"].isin(cfg.exclude_providers)
        & (obs["price_usd_per_gpu_hour"] > 0)
        & region_ok
    )
    if "is_synthetic" in obs.columns:
        mask &= ~obs["is_synthetic"].fillna(False).astype(bool)
    return obs.loc[mask]


def effective_time(obs: pd.DataFrame) -> pd.Series:
    """When the price was observed: the source's own time if given, else ours."""
    ours = pd.to_datetime(obs["ts_observed"], utc=True)
    if "ts_source" not in obs.columns:
        return ours
    theirs = pd.to_datetime(obs["ts_source"], utc=True)
    return theirs.fillna(ours)


def latest_snapshot_per_source_day(obs: pd.DataFrame) -> pd.DataFrame:
    """Keep, for each (source, snapshot date), only rows from the latest snapshot.

    A snapshot is dated by its own time: the latest effective observation time
    among its rows (for our own fetches that is when we received it; for an
    aggregator's archived daily file it is when the publisher last refreshed
    it). Every row of a snapshot takes that date, including stale rows the
    publisher carried forward, because that is what a reader saw that day.

    Adds ``ts_eff`` (row observation time), ``ts_snapshot`` and ``as_of_date``.
    """
    if obs.empty:
        return obs.assign(
            as_of_date=pd.Series(dtype="object"),
            ts_eff=pd.Series(dtype="datetime64[ns, UTC]"),
            ts_snapshot=pd.Series(dtype="datetime64[ns, UTC]"),
        )
    df = obs.copy()
    df["ts_observed"] = pd.to_datetime(df["ts_observed"], utc=True)
    df["ts_eff"] = effective_time(df)
    df["ts_snapshot"] = df.groupby("snapshot_id")["ts_eff"].transform("max")
    df["as_of_date"] = df["ts_snapshot"].dt.date
    last = df.groupby(["source", "as_of_date"])["ts_snapshot"].transform("max")
    return df.loc[df["ts_snapshot"] == last]


def prefer_sources(df: pd.DataFrame, priority: Sequence[str]) -> pd.DataFrame:
    """For each (day, GPU model, provider) keep rows from the best-ranked source only."""
    if df.empty:
        return df
    rank = {s: i for i, s in enumerate(priority)}
    r = df["source"].map(lambda x: rank.get(str(x), len(rank)))
    best = r.groupby([df["as_of_date"], df["gpu_model"], df["provider"]]).transform("min")
    return df.loc[r == best]


def balanced_panel(
    obs: pd.DataFrame,
    cfg: IndexConfig,
    gpu_model: str,
    min_presence: float = 0.9,
    formation_days: int = 30,
) -> tuple[list[str], object]:
    """Fixed provider panel chosen from the first ``formation_days`` days only.

    Returns (providers, last formation date). Providers present on at least
    ``min_presence`` of the formation days form the panel. Using only the
    formation window avoids survivorship look-ahead; index values on or before
    the formation end are in-sample for the panel choice and must be dropped
    by the caller.
    """
    daily = latest_snapshot_per_source_day(obs)
    elig = eligible_listings(daily, cfg, gpu_model)
    if elig.empty:
        return [], None
    days = sorted(elig["as_of_date"].unique())
    window = set(days[:formation_days])
    form = elig.loc[elig["as_of_date"].isin(window)]
    share = form.groupby("provider")["as_of_date"].nunique() / len(window)
    return sorted(share.index[share >= min_presence].astype(str)), max(window)


def build_history_index(
    obs: pd.DataFrame,
    cfg: IndexConfig,
    gpu_models: Sequence[str] = ("H100", "B200"),
    formation_days: int = 30,
) -> pd.DataFrame:
    """Single-publisher, fixed-panel daily index (consistent composition over time)."""
    hist = obs.loc[obs["source"].isin(cfg.history_sources)] if not obs.empty else obs
    frames = []
    for model in gpu_models:
        panel, form_end = balanced_panel(hist, cfg, model, cfg.history_min_presence, formation_days)
        if not panel:
            continue
        idx = build_daily_index(hist, cfg, [model], panel={model: panel})
        idx = idx.loc[idx["as_of_date"] > form_end]
        frames.append(
            idx.assign(method=f"{idx['method'].iloc[0]}|panel{len(panel)}" if len(idx) else "")
        )
    if not frames:
        return pd.DataFrame(columns=list(INDEX_COLUMNS))
    return pd.concat(frames, ignore_index=True)


def build_daily_index(
    obs: pd.DataFrame,
    cfg: IndexConfig,
    gpu_models: Sequence[str] = ("H100", "B200"),
    method: str | None = None,
    panel: dict[str, list[str]] | None = None,
) -> pd.DataFrame:
    """Daily index values per GPU model. Days with no eligible listings are absent.

    ``panel`` optionally restricts each GPU model to a fixed provider panel
    (used for the balanced-panel history series).
    """
    method = method or cfg.method
    daily = latest_snapshot_per_source_day(obs)
    out: list[dict[str, object]] = []
    for model in gpu_models:
        elig = prefer_sources(eligible_listings(daily, cfg, model), cfg.source_priority)
        if panel is not None:
            elig = elig.loc[elig["provider"].isin(panel.get(model, []))]
        if elig.empty:
            continue
        for day, grp in elig.groupby("as_of_date", sort=True):
            prices = grp["price_usd_per_gpu_hour"].to_numpy(dtype=float)
            providers = grp["provider"].astype(str).tolist()
            n_prov = len(set(providers))
            out.append(
                {
                    "as_of_date": day,
                    "gpu_model": model,
                    "value": aggregate(prices, providers, method, cfg.trim_fraction),
                    "method": method,
                    "n_listings": len(prices),
                    "n_providers": n_prov,
                    "meets_coverage": bool(
                        n_prov >= cfg.min_providers and len(prices) >= cfg.min_listings
                    ),
                    "ts_available": grp["ts_snapshot"].max(),
                }
            )
    return pd.DataFrame(out, columns=list(INDEX_COLUMNS))


def provider_breakdown(obs: pd.DataFrame, cfg: IndexConfig, gpu_model: str) -> pd.DataFrame:
    """Per-provider median, min, max and listing count for the latest day."""
    daily = latest_snapshot_per_source_day(obs)
    elig = prefer_sources(eligible_listings(daily, cfg, gpu_model), cfg.source_priority)
    if elig.empty:
        return pd.DataFrame(columns=["provider", "source", "n", "median", "min", "max"])
    latest = elig["as_of_date"].max()
    g = elig.loc[elig["as_of_date"] == latest].groupby(["provider", "source"])[
        "price_usd_per_gpu_hour"
    ]
    return (
        g.agg(n="count", median="median", min="min", max="max")
        .reset_index()
        .sort_values("median")
        .reset_index(drop=True)
    )
