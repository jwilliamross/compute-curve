"""Round-1 data: tidy loaders and the per-dataset time splits.

Each dataset is split by time (docs/exploration_plan.md section 2).
:meth:`Round1Data.restrict` keeps only one set of every dataset *before*
anything is computed, so exploration code cannot compute an outcome from
the confirmation set, and a window that straddles a split date has a
missing end and drops out of both sets.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, replace
from datetime import date, datetime
from typing import Literal

import pandas as pd

from compute_curve.config import Config, ExplorationConfig, IndexConfig, SplitConfig
from compute_curve.index.own_index import (
    eligible_listings,
    latest_snapshot_per_source_day,
    prefer_sources,
)

Which = Literal["explore", "confirm"]

LISTING_COLUMNS = ["as_of_date", "gpu_model", "term", "provider", "listing_id", "price"]
CGI_COLUMNS = ["as_of", "gpu_model", "value"]
GD_COLUMNS = ["week", "gpu_model", "term", "value", "n_listings"]
AWS_COLUMNS = ["day", "az_id", "instance_type", "gpu", "price_per_gpu_hour"]
BAR_COLUMNS = ["symbol", "session", "open", "close"]

GD_SERIES = {
    ("H100", "on_demand"): "GetDeploying nvidia-h100 ON_DEMAND weekly median",
    ("H100", "spot"): "GetDeploying nvidia-h100 SPOT weekly median",
    ("B200", "on_demand"): "GetDeploying nvidia-b200 ON_DEMAND weekly median",
}
CGI_SOURCE = "cgi_hist"


def _stamp(x: date | datetime) -> pd.Timestamp:
    ts = pd.Timestamp(x)
    return ts.tz_convert("UTC") if ts.tzinfo is not None else ts


def set_ranges(split: SplitConfig, which: Which) -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    """Inclusive (start, end) ranges of one set of a split."""
    if which == "explore":
        blocks: Sequence[tuple[date | datetime, date | datetime]] = [split.explore]
    elif which == "confirm":
        blocks = list(split.confirm)
    else:
        raise ValueError(f"unknown set {which!r}")
    return [(_stamp(a), _stamp(b)) for a, b in blocks]


def in_set(values: pd.Series, split: SplitConfig, which: Which) -> pd.Series:
    """True where a date or UTC timestamp lies inside one of the set's ranges."""
    ranges = set_ranges(split, which)
    aware = ranges[0][0].tzinfo is not None
    v = pd.to_datetime(values, utc=aware)
    mask = pd.Series(False, index=values.index)
    for a, b in ranges:
        mask |= (v >= a) & (v <= b)
    return mask


@dataclass(frozen=True)
class Round1Data:
    """Every input of round 1, as tidy frames (see the ``*_COLUMNS`` constants)."""

    listings: pd.DataFrame
    cgi: pd.DataFrame
    gd: pd.DataFrame
    aws: pd.DataFrame
    bars: pd.DataFrame

    def restrict(self, ecfg: ExplorationConfig, which: Which) -> Round1Data:
        """Keep only rows inside ``which`` set of each dataset's own split."""
        s = ecfg.splits

        def cut(df: pd.DataFrame, col: str, key: str) -> pd.DataFrame:
            return df.loc[in_set(df[col], s[key], which)].reset_index(drop=True)

        return replace(
            self,
            listings=cut(self.listings, "as_of_date", "listings"),
            cgi=cut(self.cgi, "as_of", "cgi"),
            gd=cut(self.gd, "week", "getdeploying"),
            aws=cut(self.aws, "day", "aws"),
            bars=cut(self.bars, "session", "equities"),
        )


# ---------------------------------------------------------------------------
# Loaders (real data). Tests build Round1Data directly from synthetic frames.
# ---------------------------------------------------------------------------
def listing_prices(obs: pd.DataFrame, icfg: IndexConfig) -> pd.DataFrame:
    """Daily price per listing from the history sources, with the index's filters.

    On-demand and spot rows for H100 and B200; the latest snapshot per
    source-day and the index's source preference apply (D40).
    """
    if obs.empty:
        return pd.DataFrame(columns=LISTING_COLUMNS)
    hist = obs.loc[obs["source"].isin(icfg.history_sources)]
    daily = latest_snapshot_per_source_day(hist)
    frames = []
    for term in ("on_demand", "spot"):
        tcfg = icfg.model_copy(update={"terms": [term]})
        for gpu in ("H100", "B200"):
            e = prefer_sources(eligible_listings(daily, tcfg, gpu), icfg.source_priority)
            frames.append(
                e.assign(term=term)[
                    [
                        "as_of_date",
                        "gpu_model",
                        "term",
                        "provider",
                        "listing_id",
                        "price_usd_per_gpu_hour",
                    ]
                ]
            )
    df = pd.concat(frames, ignore_index=True).rename(columns={"price_usd_per_gpu_hour": "price"})
    keys = ["as_of_date", "gpu_model", "term", "provider", "listing_id"]
    return df.groupby(keys, as_index=False)["price"].median()[LISTING_COLUMNS]


def cgi_values(ref: pd.DataFrame) -> pd.DataFrame:
    """CGI 15-minute history: one value per (GPU, stamp), the latest observed."""
    c = ref.loc[ref["source"] == CGI_SOURCE].sort_values("ts_observed")
    c = c.drop_duplicates(["gpu_model", "as_of"], keep="last")
    out = c[["as_of", "gpu_model", "value"]].copy()
    out["as_of"] = pd.to_datetime(out["as_of"], utc=True)
    return out.sort_values(["gpu_model", "as_of"]).reset_index(drop=True)


def gd_weekly(ref: pd.DataFrame) -> pd.DataFrame:
    """GetDeploying weekly median and offering count for the three series used."""
    rows = []
    for (gpu, term), name in GD_SERIES.items():
        g = ref.loc[(ref["source"] == "getdeploying") & (ref["index_name"] == name)]
        g = g.sort_values("ts_observed").drop_duplicates("as_of", keep="last")
        rows.append(
            pd.DataFrame(
                {
                    "week": pd.to_datetime(g["as_of"], utc=True).dt.date,
                    "gpu_model": gpu,
                    "term": term,
                    "value": g["value"].astype(float),
                    "n_listings": g["n_listings"].astype(float),
                }
            )
        )
    return pd.concat(rows, ignore_index=True)[GD_COLUMNS]


def load_round1(cfg: Config) -> Round1Data:  # pragma: no cover - reads local data
    """Load every round-1 input from local files. Nothing is fetched."""
    from compute_curve.claim4.market_data import cache_path  # noqa: PLC0415
    from compute_curve.claim5.pipeline import (  # noqa: PLC0415
        apply_member_start,
        claim5_cfg,
        read_pool_daily,
    )
    from compute_curve.claim5.pipeline import paths as c5paths  # noqa: PLC0415
    from compute_curve.pipeline import paths as main_paths  # noqa: PLC0415
    from compute_curve.storage import warehouse as wh  # noqa: PLC0415

    p = main_paths(cfg)
    con = wh.connect(None)
    try:
        wh.register_observations(con, p["raw"])
        wh.register_reference_indices(con, p["raw"])
        obs = wh.observations_frame(con)
        ref = wh.reference_indices_frame(con)
    finally:
        con.close()
    c4 = cfg.claim4
    c5 = claim5_cfg(cfg)
    if c4 is None:
        raise RuntimeError("[claim4] config is required for the equity universe")
    symbols = [*c4.universe.members(), c4.benchmark]
    end = cfg.exploration.splits["equities"].confirm[-1][1] if cfg.exploration else None
    path = cache_path(
        cfg.path("var") / "market_data", symbols, c5.bars_start.isoformat(), str(end), c4.feed
    )
    if not path.exists():
        raise FileNotFoundError(f"cached bars not found: {path}; run claim5 evaluate first")
    from compute_curve.claim4.market_data import _read_duckdb  # noqa: PLC0415

    bars = apply_member_start(_read_duckdb(path), c5.member_start)
    return Round1Data(
        listings=listing_prices(obs, cfg.index),
        cgi=cgi_values(ref),
        gd=gd_weekly(ref),
        aws=read_pool_daily(c5paths(cfg)["pool_daily"]),
        bars=bars[BAR_COLUMNS].reset_index(drop=True),
    )
