"""Market data container and the point-in-time view handed to strategies.

Strategies never receive :class:`MarketData` directly. They receive a
:class:`MarketView` built for a decision time ``as_of``; every accessor on
the view filters on ``ts_available <= as_of``. This is the structural
look-ahead guard for both backtest and forward modes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime

import numpy as np
import pandas as pd

from compute_curve.timeutil import ensure_utc

SETTLE_COLS = ["product", "contract_month", "trade_date", "settle_price", "ts_available"]
PUB_COLS = ["index_name", "as_of_date", "value", "ts_available"]
OWN_COLS = ["as_of_date", "gpu_model", "value", "meets_coverage", "ts_available"]


def _ensure(df: pd.DataFrame | None, cols: list[str]) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=cols)
    missing = set(cols) - set(df.columns)
    if missing:
        raise ValueError(f"missing columns {sorted(missing)}")
    out = df.copy()
    out["ts_available"] = pd.to_datetime(out["ts_available"], utc=True)
    if "is_synthetic" not in out.columns:
        out["is_synthetic"] = False
    return out


def _sorted_by_ts(df: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray]:
    if df.empty:
        return df, np.array([], dtype="int64")
    out = df.sort_values("ts_available", kind="mergesort").reset_index(drop=True)
    naive = pd.to_datetime(out["ts_available"], utc=True).dt.tz_localize(None)
    ts = naive.to_numpy(dtype="datetime64[us]").astype("int64")
    return out, ts


def _cut(df: pd.DataFrame, ts: np.ndarray, as_of: datetime) -> pd.DataFrame:
    """Rows with ts_available <= as_of, by binary search on a sorted column."""
    if df.empty:
        return df
    key = np.datetime64(ensure_utc(as_of).replace(tzinfo=None), "us").astype("int64")
    k = int(np.searchsorted(ts, key, side="right"))
    return df.iloc[:k]


@dataclass(frozen=True)
class MarketData:
    """All market inputs for a run. Engine-side object; not given to strategies.

    Point-in-time lookups use frames pre-sorted by ``ts_available`` so each
    view slice is a binary search rather than a full scan.
    """

    settlements: pd.DataFrame = field(default_factory=lambda: pd.DataFrame(columns=SETTLE_COLS))
    published_index: pd.DataFrame = field(default_factory=lambda: pd.DataFrame(columns=PUB_COLS))
    own_index: pd.DataFrame = field(default_factory=lambda: pd.DataFrame(columns=OWN_COLS))
    _cache: dict[str, object] = field(default_factory=dict, init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        st, st_ts = _sorted_by_ts(self.settlements)
        self._cache["settle"] = (st, st_ts)
        by_day: dict[date, dict[tuple[str, str], float]] = {}
        for r in st.itertuples(index=False):
            by_day.setdefault(r.trade_date, {})[(str(r.product), str(r.contract_month))] = float(
                r.settle_price
            )
        self._cache["settle_by_day"] = by_day
        pub: dict[str, tuple[pd.DataFrame, np.ndarray]] = {}
        if not self.published_index.empty:
            for name, grp in self.published_index.groupby("index_name"):
                pub[str(name)] = _sorted_by_ts(grp)
        self._cache["pub"] = pub
        own: dict[tuple[str, bool], tuple[pd.DataFrame, np.ndarray]] = {}
        if not self.own_index.empty:
            for model, grp in self.own_index.groupby("gpu_model"):
                own[(str(model), False)] = _sorted_by_ts(grp)
                own[(str(model), True)] = _sorted_by_ts(grp.loc[grp["meets_coverage"].astype(bool)])
        self._cache["own"] = own

    @staticmethod
    def build(
        settlements: pd.DataFrame | None = None,
        published_index: pd.DataFrame | None = None,
        own_index: pd.DataFrame | None = None,
    ) -> MarketData:
        return MarketData(
            settlements=_ensure(settlements, SETTLE_COLS),
            published_index=_ensure(published_index, PUB_COLS),
            own_index=_ensure(own_index, OWN_COLS),
        )

    @property
    def is_synthetic(self) -> bool:
        frames = (self.settlements, self.published_index, self.own_index)
        return any(bool(f["is_synthetic"].astype(bool).any()) for f in frames if not f.empty)

    def trade_dates(self) -> list[date]:
        return sorted(self._cache["settle_by_day"])  # type: ignore[arg-type]

    def settlement_on(self, day: date) -> dict[tuple[str, str], float]:
        """Settlements for trade date ``day`` (engine use: fills and marks)."""
        by_day: dict[date, dict[tuple[str, str], float]] = self._cache["settle_by_day"]  # type: ignore[assignment]
        return dict(by_day.get(day, {}))

    def view(self, as_of: datetime) -> MarketView:
        return MarketView(self, ensure_utc(as_of))

    def full_published_series(self, index_name: str) -> pd.Series:
        """Entire published history for scoring realized targets (never a model input)."""
        pub: dict[str, tuple[pd.DataFrame, np.ndarray]] = self._cache["pub"]  # type: ignore[assignment]
        return _series(pub[index_name][0]) if index_name in pub else pd.Series(dtype=float)


def _series(df: pd.DataFrame) -> pd.Series:
    if df.empty:
        return pd.Series(dtype=float)
    out = pd.Series(df["value"].to_numpy(float), index=list(df["as_of_date"]), dtype=float)
    return out.sort_index()


@dataclass(frozen=True)
class MarketView:
    """Read-only, point-in-time view of :class:`MarketData` at ``as_of``."""

    _data: MarketData
    as_of: datetime

    def settlements(self) -> pd.DataFrame:
        st, ts = self._data._cache["settle"]  # type: ignore[misc]
        return _cut(st, ts, self.as_of)

    def latest_settles(self) -> dict[tuple[str, str], float]:
        """Settlement curve of the most recent available trade date, per product."""
        s = self.settlements()
        if s.empty:
            return {}
        last_day = s.groupby("product")["trade_date"].transform("max")
        cur = s.loc[s["trade_date"] == last_day]
        return {
            (str(r.product), str(r.contract_month)): float(r.settle_price)
            for r in cur.itertuples(index=False)
        }

    def published_index(self, index_name: str) -> pd.Series:
        pub: dict[str, tuple[pd.DataFrame, np.ndarray]] = self._data._cache["pub"]  # type: ignore[assignment]
        if index_name not in pub:
            return pd.Series(dtype=float)
        df, ts = pub[index_name]
        return _series(_cut(df, ts, self.as_of))

    def own_index(self, gpu_model: str, require_coverage: bool = True) -> pd.Series:
        own: dict[tuple[str, bool], tuple[pd.DataFrame, np.ndarray]] = self._data._cache["own"]  # type: ignore[assignment]
        key = (gpu_model, require_coverage)
        if key not in own:
            return pd.Series(dtype=float)
        df, ts = own[key]
        return _series(_cut(df, ts, self.as_of))
