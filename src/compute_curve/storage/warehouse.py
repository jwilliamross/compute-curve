"""DuckDB warehouse: derived, rebuildable views over immutable inputs.

Inputs:

* ``data/raw/listings/**.parquet``             listing snapshots (immutable)
* ``data/raw/indices/**.parquet``              third-party index snapshots (immutable)
* ``data/manual/published_index/*.csv``        published index values the user
                                               downloads by hand
* ``data/manual/cme_settlements/*.csv``        CME daily settlements the user
                                               downloads by hand

The warehouse never modifies inputs. Deleting ``var/warehouse.duckdb`` loses
nothing.

Every row exposed to models carries a ``ts_available`` column. Point-in-time
queries filter on it, which is how look-ahead is prevented.
"""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

import duckdb
import pandas as pd

from compute_curve.storage.raw_store import (
    INDICES,
    LISTINGS,
    index_observations_to_frame,
    normalize_ts,
    observations_to_frame,
)
from compute_curve.timeutil import ensure_utc

PUBLISHED_INDEX_COLUMNS = ("index_name", "as_of_date", "value")
SETTLEMENT_COLUMNS = ("product", "contract_month", "trade_date", "settle_price")


def _glob_has_files(folder: Path, pattern: str) -> bool:
    return folder.exists() and any(folder.glob(pattern))


def connect(db_path: Path | None = None) -> duckdb.DuckDBPyConnection:
    """Open the warehouse (in-memory if ``db_path`` is None)."""
    if db_path is not None:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return duckdb.connect(db_path.as_posix())
    return duckdb.connect()


def _register_parquet_view(
    con: duckdb.DuckDBPyConnection, name: str, folder: Path, empty: pd.DataFrame
) -> int:
    """(Re)create view ``name`` over all Parquet under ``folder``; return row count."""
    if not _glob_has_files(folder, "**/*.parquet"):
        con.register(f"_{name}_empty", empty)
        con.execute(f"CREATE OR REPLACE VIEW {name} AS SELECT * FROM _{name}_empty")
        return 0
    pattern = (folder / "**" / "*.parquet").as_posix()
    con.execute(
        f"""
        CREATE OR REPLACE VIEW {name} AS
        SELECT * FROM read_parquet('{pattern}', union_by_name = true)
        WHERE NOT coalesce(is_synthetic, false)
        """
    )
    row = con.execute(f"SELECT count(*) FROM {name}").fetchone()
    return int(row[0]) if row else 0


def register_observations(con: duckdb.DuckDBPyConnection, raw_dir: Path) -> int:
    """View ``observations`` over ``<raw_dir>/listings``; return row count."""
    return _register_parquet_view(
        con, "observations", raw_dir / LISTINGS, observations_to_frame([])
    )


def register_reference_indices(con: duckdb.DuckDBPyConnection, raw_dir: Path) -> int:
    """View ``reference_indices`` over ``<raw_dir>/indices``; return row count."""
    return _register_parquet_view(
        con, "reference_indices", raw_dir / INDICES, index_observations_to_frame([])
    )


def reference_indices_frame(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """Latest vintage of every third-party index value (one row per name and as_of)."""
    df = con.execute(
        """
        SELECT * FROM reference_indices
        QUALIFY row_number() OVER (PARTITION BY index_name, as_of ORDER BY ts_observed DESC) = 1
        ORDER BY index_name, as_of
        """
    ).df()
    return normalize_ts(df, "ts_observed", "as_of")


def load_published_index_csvs(folder: Path, publication_lag_days: int) -> pd.DataFrame:
    """Read manual published-index CSVs and attach an assumed availability time.

    ``ts_available = as_of_date + publication_lag_days`` at 00:00 UTC. The lag
    is an assumption from config, not a verified publication schedule.
    """
    frames: list[pd.DataFrame] = []
    for csv in sorted(folder.glob("*.csv")) if folder.exists() else []:
        df = pd.read_csv(csv, comment="#")
        missing = set(PUBLISHED_INDEX_COLUMNS) - set(df.columns)
        if missing:
            raise ValueError(f"{csv.name}: missing columns {sorted(missing)}")
        df = df.loc[:, list(PUBLISHED_INDEX_COLUMNS)].copy()
        df["source"] = f"manual:{csv.name}"
        frames.append(df)
    if not frames:
        return pd.DataFrame(
            columns=[*PUBLISHED_INDEX_COLUMNS, "source", "ts_available", "is_synthetic"]
        )
    out = pd.concat(frames, ignore_index=True)
    out["as_of_date"] = pd.to_datetime(out["as_of_date"]).dt.date
    out["value"] = out["value"].astype(float)
    if (out["value"] <= 0).any():
        raise ValueError("published index values must be positive")
    out["ts_available"] = pd.to_datetime(out["as_of_date"]).dt.tz_localize("UTC") + pd.to_timedelta(
        publication_lag_days, unit="D"
    )
    out["is_synthetic"] = False
    dupes = out.duplicated(subset=["index_name", "as_of_date"], keep=False)
    if dupes.any():
        conflict = out[dupes].groupby(["index_name", "as_of_date"])["value"].nunique()
        if (conflict > 1).any():
            raise ValueError("conflicting published index values for the same date")
        out = out.drop_duplicates(subset=["index_name", "as_of_date"])
    return out.sort_values(["index_name", "as_of_date"]).reset_index(drop=True)


def load_settlement_csvs(folder: Path) -> pd.DataFrame:
    """Read manual CME settlement CSVs.

    A settlement for trade date ``d`` is treated as available at 23:59:59 UTC
    on ``d`` (CME publishes daily settlements in the US afternoon).
    """
    frames: list[pd.DataFrame] = []
    for csv in sorted(folder.glob("*.csv")) if folder.exists() else []:
        df = pd.read_csv(csv, comment="#")
        missing = set(SETTLEMENT_COLUMNS) - set(df.columns)
        if missing:
            raise ValueError(f"{csv.name}: missing columns {sorted(missing)}")
        keep = [*SETTLEMENT_COLUMNS, *[c for c in ("volume", "open_interest") if c in df.columns]]
        df = df.loc[:, keep].copy()
        df["source"] = f"manual:{csv.name}"
        frames.append(df)
    cols = [*SETTLEMENT_COLUMNS, "volume", "open_interest", "source", "ts_available"]
    if not frames:
        return pd.DataFrame(columns=[*cols, "is_synthetic"])
    out = pd.concat(frames, ignore_index=True)
    for c in ("volume", "open_interest"):
        if c not in out.columns:
            out[c] = pd.NA
    out["trade_date"] = pd.to_datetime(out["trade_date"]).dt.date
    out["contract_month"] = out["contract_month"].astype(str)
    out["settle_price"] = out["settle_price"].astype(float)
    out["ts_available"] = (
        pd.to_datetime(out["trade_date"]).dt.tz_localize("UTC")
        + pd.Timedelta(days=1)
        - pd.Timedelta(microseconds=1)
    )
    out["is_synthetic"] = False
    out = out.drop_duplicates(subset=["product", "contract_month", "trade_date"], keep="last")
    return (
        out.loc[:, [*cols, "is_synthetic"]]
        .sort_values(["product", "contract_month", "trade_date"])
        .reset_index(drop=True)
    )


def point_in_time(df: pd.DataFrame, as_of: datetime, ts_col: str = "ts_available") -> pd.DataFrame:
    """Rows of ``df`` that were available at ``as_of``. The single look-ahead guard."""
    as_of = ensure_utc(as_of)
    if df.empty:
        return df
    ts = pd.to_datetime(df[ts_col], utc=True)
    return df.loc[ts <= pd.Timestamp(as_of)]


def observations_frame(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """All non-synthetic observations, with ``ts_available = ts_observed``."""
    df = con.execute("SELECT * FROM observations ORDER BY ts_observed").df()
    df = normalize_ts(df, "ts_observed", "ts_source")
    df["ts_available"] = df["ts_observed"]
    return df


def days_between(start: date, end: date) -> list[date]:
    return [d.date() for d in pd.date_range(start, end, freq="D")]
