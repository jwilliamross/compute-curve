"""Market data container and the point-in-time view handed to strategies.

Strategies never receive :class:`MarketData` directly. They receive a
:class:`MarketView` built for a decision time ``as_of``; every accessor on
the view filters on ``ts_available <= as_of``. This is the structural
look-ahead guard for both backtest and forward modes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime

import pandas as pd

from compute_curve.storage.warehouse import point_in_time
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


@dataclass(frozen=True)
class MarketData:
    """All market inputs for a run. Engine-side object; not given to strategies."""

    settlements: pd.DataFrame = field(default_factory=lambda: pd.DataFrame(columns=SETTLE_COLS))
    published_index: pd.DataFrame = field(default_factory=lambda: pd.DataFrame(columns=PUB_COLS))
    own_index: pd.DataFrame = field(default_factory=lambda: pd.DataFrame(columns=OWN_COLS))

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
        if self.settlements.empty:
            return []
        return sorted(set(self.settlements["trade_date"]))

    def settlement_on(self, day: date) -> dict[tuple[str, str], float]:
        """Settlements for trade date ``day`` (engine use: fills and marks)."""
        s = self.settlements
        if s.empty:
            return {}
        rows = s.loc[s["trade_date"] == day]
        return {
            (str(r.product), str(r.contract_month)): float(r.settle_price)
            for r in rows.itertuples(index=False)
        }

    def view(self, as_of: datetime) -> MarketView:
        return MarketView(self, ensure_utc(as_of))


@dataclass(frozen=True)
class MarketView:
    """Read-only, point-in-time view of :class:`MarketData` at ``as_of``."""

    _data: MarketData
    as_of: datetime

    def settlements(self) -> pd.DataFrame:
        return point_in_time(self._data.settlements, self.as_of)

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
        p = point_in_time(self._data.published_index, self.as_of)
        p = p.loc[p["index_name"] == index_name] if not p.empty else p
        return pd.Series(
            p["value"].to_numpy(float) if not p.empty else [],
            index=list(p["as_of_date"]) if not p.empty else [],
            dtype=float,
        ).sort_index()

    def own_index(self, gpu_model: str, require_coverage: bool = True) -> pd.Series:
        o = point_in_time(self._data.own_index, self.as_of)
        if not o.empty:
            o = o.loc[o["gpu_model"] == gpu_model]
            if require_coverage:
                o = o.loc[o["meets_coverage"].astype(bool)]
        return pd.Series(
            o["value"].to_numpy(float) if not o.empty else [],
            index=list(o["as_of_date"]) if not o.empty else [],
            dtype=float,
        ).sort_index()
