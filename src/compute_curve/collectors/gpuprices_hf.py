"""GPU Price Tracker (Alex Hubbard) on Hugging Face: one-off listing backfill.

Dataset: https://huggingface.co/datasets/afhubbard/gpu-prices, CC BY 4.0
(dataset card ``license: cc-by-4.0``; upstream ``DATA_LICENSE``). Attribution:
"GPU Price Tracker by Alex Hubbard, CC BY 4.0". huggingface.co/robots.txt
allows everything for ``*``.

The publisher scrapes provider pricing via the ``gpuhunt`` library about
twice a day and publishes one immutable Parquet file per snapshot under
``prices/dt=YYYY-MM-DD/snapshot_<UTC stamp>.parquet``. Each row is one
``(provider, instance_type, region, is_spot)`` listing. ``price_per_hour`` is
USD per hour for the whole SKU, so the per-GPU price is
``price_per_hour / gpu_count`` (verified in the data, e.g. Lambda
``gpu_8x_h100_sxm5`` at 31.92 = 8 x 3.99).

Provenance (docs/data_sources.md, D54). The Hugging Face repository was
created on 2026-05-07; its first upload (2026-05-07T20:26Z) carried every
snapshot from 2026-01-12 on. Snapshots stamped before that upload cannot be
shown to have been collected when stamped, so they are skipped
(``FIRST_PUBLISHED``). Later snapshots appear on the hub within hours of
their stamp.

Kept: H100, H200 and B200 rows with ``quality == 'ok'`` (GB200, GH200, B300
and A100 are out of scope). Dropped: Vast.ai and RunPod (D13), and Oracle
and Vultr, whose direct collection was rejected on their terms
(docs/data_sources.md). Raw regions are coarse provider region names; the
row's ``region`` is the ISO country when the publisher gives one.
"""

from __future__ import annotations

import json
import re
import tempfile
from collections import Counter
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import duckdb
import pandas as pd

from compute_curve.collectors.base import (
    DEFAULT_EXCLUDED_PROVIDERS,
    CollectedBatch,
    canonical_provider,
)
from compute_curve.schema import (
    Availability,
    GpuModel,
    PriceObservation,
    Term,
    gpu_variant,
    normalize_region,
)
from compute_curve.storage.raw_store import snapshot_id

REPO = "https://huggingface.co/datasets/afhubbard/gpu-prices"
TREE = "https://huggingface.co/api/datasets/afhubbard/gpu-prices/tree/main/prices?recursive=1"
RESOLVE = "https://huggingface.co/datasets/afhubbard/gpu-prices/resolve/main/{path}"
TERMS_URL = REPO
ATTRIBUTION = (
    "GPU Price Tracker by Alex Hubbard (https://huggingface.co/datasets/afhubbard/gpu-prices), "
    "CC BY 4.0"
)
# Time of the repository's first data upload. Earlier snapshot stamps are not
# verifiable as contemporaneous and are skipped (D54).
FIRST_PUBLISHED = datetime(2026, 5, 7, 20, 26, 7, tzinfo=UTC)
# Oracle and Vultr: their direct collection was rejected on terms
# (docs/data_sources.md); dropped here too, conservatively (D54).
EXTRA_EXCLUDED: frozenset[str] = frozenset({"oci", "vultr"})
GPUS: dict[str, tuple[GpuModel, str | None]] = {
    "H100": (GpuModel.H100, None),
    "H100NVL": (GpuModel.H100, "NVL"),
    "H200": (GpuModel.H200, None),
    "H200NVL": (GpuModel.H200, "NVL"),
    "B200": (GpuModel.B200, None),
}
COLUMNS = (
    "timestamp",
    "provider",
    "instance_type",
    "gpu_type",
    "gpu_count",
    "gpu_memory_gb",
    "vcpus",
    "ram_gb",
    "region",
    "price_per_hour",
    "is_spot",
    "available",
    "quality",
    "region_canonical",
    "country",
    "region_group",
)
KEPT_FIELDS = tuple(c for c in COLUMNS if c != "timestamp")
_FILE = re.compile(r"^prices/dt=(\d{4}-\d{2}-\d{2})/snapshot_(\d{8}T\d{6}Z)\.parquet$")


def partition_files(tree: Any) -> dict[date, list[str]]:
    """Snapshot file paths in a tree listing, grouped by partition date."""
    out: dict[date, list[str]] = {}
    for item in tree if isinstance(tree, list) else []:
        m = _FILE.match(str(item.get("path", ""))) if item.get("type") == "file" else None
        if m:
            out.setdefault(date.fromisoformat(m.group(1)), []).append(m.group(0))
    return {d: sorted(v) for d, v in sorted(out.items())}


def file_stamp(path: str) -> datetime:
    """Snapshot time encoded in a file name."""
    m = _FILE.match(path)
    if not m:
        raise ValueError(f"not a snapshot file: {path}")
    return datetime.strptime(m.group(2), "%Y%m%dT%H%M%SZ").replace(tzinfo=UTC)


def read_snapshot_bytes(blob: bytes) -> pd.DataFrame:
    """Rows of one snapshot file (only the columns used), read with DuckDB."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "snapshot.parquet"
        path.write_bytes(blob)
        con = duckdb.connect()
        try:
            probe = con.execute("SELECT * FROM read_parquet(?) LIMIT 0", [path.as_posix()])
            missing = set(COLUMNS) - {c[0] for c in probe.description or []}
            if missing:
                raise ValueError(f"snapshot is missing columns {sorted(missing)}")
            cols = ", ".join(f'"{c}"' for c in COLUMNS if c != "timestamp")
            query = f"SELECT epoch_us(timestamp) AS ts_us, {cols} FROM read_parquet(?)"  # noqa: S608
            df = con.execute(query, [path.as_posix()]).df()
        finally:
            con.close()
    return df


def _clean(v: Any) -> Any:
    """JSON-safe scalar: NaN/NA become None, numpy scalars become Python."""
    if v is None or (not isinstance(v, str) and pd.isna(v)):
        return None
    return v.item() if hasattr(v, "item") else v


def _int(v: Any) -> int | None:
    """Integer value of an int or integral float (nullable columns load as float)."""
    v = _clean(v)
    if isinstance(v, bool):
        return None
    if isinstance(v, float) and v.is_integer():
        return int(v)
    return v if isinstance(v, int) else None


def normalize_frame(
    df: pd.DataFrame,
    ts_observed: datetime,
    source: str,
    hf_path: str,
    excluded: frozenset[str] = DEFAULT_EXCLUDED_PROVIDERS,
) -> tuple[CollectedBatch, Counter[str]]:
    """Map one snapshot file's rows to observations; also count drops by reason.

    ``ts_observed`` is when we downloaded the file; the row's own
    ``timestamp`` becomes ``ts_source``. ``hf_path`` is kept in ``raw_json``.
    """
    rows: list[PriceObservation] = []
    drops: Counter[str] = Counter()
    for rec in df.to_dict(orient="records"):
        gpu = GPUS.get(str(rec.get("gpu_type")))
        if gpu is None:
            continue  # other GPU families are out of scope, not "dropped"
        provider = canonical_provider(str(rec.get("provider") or ""))
        if not provider or provider in excluded or provider in EXTRA_EXCLUDED:
            drops[f"provider:{provider or 'missing'}"] += 1
            continue
        if rec.get("quality") != "ok":
            drops["quality_not_ok"] += 1
            continue
        row = _row(rec, gpu, provider, ts_observed, source, hf_path)
        if row is None:
            drops["bad_price_or_count"] += 1
        else:
            rows.append(row)
    return CollectedBatch(listings=rows, n_dropped=sum(drops.values())), drops


def _row(
    rec: dict[str, Any],
    gpu: tuple[GpuModel, str | None],
    provider: str,
    ts_observed: datetime,
    source: str,
    hf_path: str,
) -> PriceObservation | None:
    n_gpu, price = _int(rec.get("gpu_count")), _clean(rec.get("price_per_hour"))
    if n_gpu is None or n_gpu < 1 or not isinstance(price, int | float):
        return None
    per_gpu = float(price) / n_gpu
    if not 0 < per_gpu < 1000:
        return None
    ts_us = _int(rec.get("ts_us"))
    if ts_us is None:
        return None
    ts_source = datetime.fromtimestamp(ts_us / 1e6, tz=UTC)
    model, variant = gpu
    instance = str(_clean(rec.get("instance_type")) or "")
    raw_region = _clean(rec.get("region"))
    country = _clean(rec.get("country"))
    spot = bool(_clean(rec.get("is_spot")))
    avail = _clean(rec.get("available"))
    kept = {k: _clean(rec.get(k)) for k in KEPT_FIELDS}
    kept["hf_path"] = hf_path
    return PriceObservation(
        ts_observed=ts_observed,
        provider=provider,
        gpu_model=model,
        config=f"{n_gpu}x {rec.get('gpu_type')} {instance}".strip(),
        price_usd_per_gpu_hour=per_gpu,
        term=Term.SPOT if spot else Term.ON_DEMAND,
        region=str(country) if country else normalize_region(raw_region),
        availability=(
            Availability.UNKNOWN
            if avail is None
            else Availability.AVAILABLE
            if avail
            else Availability.UNAVAILABLE
        ),
        source=source,
        snapshot_id=snapshot_id(source, ts_source),
        ts_source=ts_source,
        gpu_variant=variant or gpu_variant(instance.replace("_", " ")),
        gpus_per_instance=n_gpu,
        listing_id=f"{provider}:{instance}:{raw_region or ''}:{'spot' if spot else 'od'}",
        source_url=REPO,
        price_basis="instance_hour_list_div_gpus",
        raw_json=json.dumps(kept, sort_keys=True, default=str),
    )
