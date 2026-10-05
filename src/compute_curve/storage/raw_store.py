"""Immutable, append-only raw snapshot store (Parquet).

Layout::

    data/raw/<source>/<YYYY>/<MM>/<source>_<YYYYMMDDTHHMMSSZ>.parquet

A snapshot file is written once, atomically (temp file then rename), and is
never modified or deleted by this code. Writing to an existing path raises.
"""

from __future__ import annotations

import os
from collections.abc import Sequence
from datetime import date, datetime
from pathlib import Path

import duckdb
import pandas as pd

from compute_curve.schema import PriceObservation
from compute_curve.timeutil import ensure_utc, snapshot_stamp

OBSERVATION_COLUMNS: tuple[str, ...] = tuple(PriceObservation.model_fields.keys())


class ImmutableWriteError(FileExistsError):
    """Attempt to overwrite an existing raw snapshot."""


def snapshot_id(source: str, ts: datetime) -> str:
    return f"{source}_{snapshot_stamp(ts)}"


def snapshot_path(raw_dir: Path, source: str, ts: datetime) -> Path:
    ts = ensure_utc(ts)
    return raw_dir / source / f"{ts:%Y}" / f"{ts:%m}" / f"{snapshot_id(source, ts)}.parquet"


def observations_to_frame(rows: Sequence[PriceObservation]) -> pd.DataFrame:
    """Convert validated observations to a frame with a stable column order."""
    records = [r.model_dump(mode="python") for r in rows]
    df = pd.DataFrame.from_records(records, columns=list(OBSERVATION_COLUMNS))
    for col in ("gpu_model", "term", "availability"):
        df[col] = df[col].map(lambda v: v.value if hasattr(v, "value") else v)
    df["ts_observed"] = pd.to_datetime(df["ts_observed"], utc=True)
    return df


def write_snapshot(raw_dir: Path, source: str, ts: datetime, df: pd.DataFrame) -> Path:
    """Write ``df`` as a new immutable snapshot. Raise if the file already exists."""
    path = snapshot_path(raw_dir, source, ts)
    if path.exists():
        raise ImmutableWriteError(str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".parquet.tmp")
    con = duckdb.connect()
    try:
        con.register("snap", df)
        con.execute(
            f"COPY (SELECT * FROM snap) TO '{tmp.as_posix()}' (FORMAT PARQUET, COMPRESSION ZSTD)"
        )
    finally:
        con.close()
    # os.link fails if the destination exists, giving an atomic no-overwrite guarantee.
    try:
        os.link(tmp, path)
    except FileExistsError as exc:
        raise ImmutableWriteError(str(path)) from exc
    finally:
        tmp.unlink(missing_ok=True)
    return path


def snapshots_for_day(raw_dir: Path, source: str, day: date) -> list[Path]:
    """Existing snapshot files for ``source`` observed on UTC date ``day``."""
    folder = raw_dir / source / f"{day:%Y}" / f"{day:%m}"
    if not folder.exists():
        return []
    prefix = f"{source}_{day:%Y%m%d}T"
    return sorted(p for p in folder.glob("*.parquet") if p.name.startswith(prefix))


def read_snapshot(path: Path) -> pd.DataFrame:
    con = duckdb.connect()
    try:
        df = con.execute("SELECT * FROM read_parquet(?)", [path.as_posix()]).df()
    finally:
        con.close()
    return normalize_ts(df, "ts_observed")


def normalize_ts(df: pd.DataFrame, *cols: str) -> pd.DataFrame:
    """Convert timestamp columns to pandas UTC (DuckDB may report 'Etc/UTC')."""
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], utc=True).dt.tz_convert("UTC")
    return df
