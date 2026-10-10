"""FastGPU open dataset: current snapshot of live GPU offers (CC BY 4.0).

Source: https://fastgpu.co/api/v1/dataset/gpu-prices-current.csv, one of the
"published dataset files" at https://fastgpu.co/dataset. Licence: CC BY 4.0,
attribution "Data: FastGPU GPU cloud pricing dataset
(https://fastgpu.co/dataset), CC BY 4.0." robots.txt allows
``/api/v1/dataset/``. FastGPU's terms forbid automated collection from the
rest of the site, so this collector requests the dataset file only, once per
run (docs/data_sources.md, D51).

Each row is one live offer with a per-GPU-hour price, the GPUs in the
instance (``min_gpu_count``) and ``available_count`` (instances available,
blank if the provider does not expose it). The publisher's ``fetched_at``
becomes ``ts_source``. H100, H200 and B200 rows are kept (GB200, GH200 and
B300 are different products). Serverless offers and providers whose terms
prohibit index use (``DEFAULT_EXCLUDED_PROVIDERS``: Vast.ai, RunPod) are
dropped.
"""

from __future__ import annotations

import csv
import io
import json
from datetime import datetime
from typing import Any

from compute_curve.collectors.base import (
    DEFAULT_EXCLUDED_PROVIDERS,
    CollectedBatch,
    canonical_provider,
)
from compute_curve.http import PoliteClient
from compute_curve.schema import (
    Availability,
    GpuModel,
    PriceObservation,
    Term,
    canonical_gpu_model,
    gpu_variant,
    normalize_region,
)

CURRENT = "https://fastgpu.co/api/v1/dataset/gpu-prices-current.csv"
ATTRIBUTION = "Data: FastGPU GPU cloud pricing dataset (https://fastgpu.co/dataset), CC BY 4.0."
REQUIRED_COLUMNS = frozenset(
    {"provider", "gpu_model", "offer_type", "price_usd_hr", "min_gpu_count", "fetched_at"}
)
OFFER_TYPES: dict[str, Term] = {
    "on-demand": Term.ON_DEMAND,
    "community": Term.ON_DEMAND,  # a marketplace's shared-host tier, rented the same way
    "spot": Term.SPOT,
    "reserved": Term.RESERVED,
}
# Providers that, per the dataset's column notes, price the GPU alone and bill
# CPU and memory on top.
GPU_ONLY: frozenset[str] = frozenset({"modal", "cudo", "cudocompute", "tensordock", "daytona"})
KEPT_FIELDS = (
    "provider",
    "provider_label",
    "gpu_model",
    "gpu_slug",
    "vram_gb",
    "offer_type",
    "region",
    "price_usd_hr",
    "min_gpu_count",
    "available_count",
    "interconnect",
)


class FastGpuCollector:
    source_id = "fastgpu"
    terms_url = "https://fastgpu.co/legal/terms"
    attribution = ATTRIBUTION

    def __init__(self, excluded: frozenset[str] = DEFAULT_EXCLUDED_PROVIDERS) -> None:
        self.excluded = excluded

    def fetch(self, client: PoliteClient) -> Any:
        resp = client.get(CURRENT)
        resp.raise_for_status()
        return resp.text

    def normalize(self, payload: Any, ts_observed: datetime, snapshot_id: str) -> CollectedBatch:
        reader = csv.DictReader(io.StringIO(str(payload or "")))
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"FastGPU dataset is missing columns {sorted(missing)}")
        rows: list[PriceObservation] = []
        dropped = 0
        for rec in reader:
            model = canonical_gpu_model(str(rec.get("gpu_model") or ""))
            if model == GpuModel.OTHER:
                continue  # other GPU families are out of scope, not "dropped"
            row = _offer(rec, model, ts_observed, snapshot_id, self.source_id, self.excluded)
            if row is None:
                dropped += 1
            else:
                rows.append(row)
        return CollectedBatch(listings=rows, n_dropped=dropped)


def _int(x: str | None) -> int | None:
    try:
        return int(float(x)) if x not in (None, "") else None
    except ValueError:
        return None


def _float(x: str | None) -> float | None:
    try:
        return float(x) if x not in (None, "") else None
    except ValueError:
        return None


def _ts(x: str | None) -> datetime | None:
    """Publisher timestamp; a timezone-naive or unparsable value becomes None."""
    try:
        ts = datetime.fromisoformat(str(x).replace("Z", "+00:00")) if x else None
    except ValueError:
        return None
    return ts if ts is not None and ts.tzinfo is not None else None


def availability(count: int | None) -> Availability:
    """Instances available now: 0 is sold out, blank is not reported."""
    if count is None:
        return Availability.UNKNOWN
    return Availability.AVAILABLE if count > 0 else Availability.UNAVAILABLE


def _offer(
    rec: dict[str, str],
    model: GpuModel,
    ts_observed: datetime,
    snapshot_id: str,
    source: str,
    excluded: frozenset[str],
) -> PriceObservation | None:
    provider = canonical_provider(str(rec.get("provider") or ""))
    term = OFFER_TYPES.get(str(rec.get("offer_type") or "").strip().lower())
    price = _float(rec.get("price_usd_hr"))
    if not provider or provider in excluded or term is None:
        return None
    if price is None or not 0 < price < 1000:
        return None
    n_gpu = _int(rec.get("min_gpu_count"))
    n_gpu = n_gpu if n_gpu and n_gpu > 0 else None
    name = str(rec.get("gpu_model"))
    kept: dict[str, Any] = {k: rec.get(k) for k in KEPT_FIELDS if k in rec}
    kept["available_count"] = _int(rec.get("available_count"))
    return PriceObservation(
        ts_observed=ts_observed,
        provider=provider,
        gpu_model=model,
        config=f"{n_gpu}x {name}" if n_gpu else name,
        price_usd_per_gpu_hour=price,
        term=term,
        region=normalize_region(rec.get("region")),
        availability=availability(kept["available_count"]),
        source=source,
        snapshot_id=snapshot_id,
        ts_source=_ts(rec.get("fetched_at")),
        gpu_variant=gpu_variant(name),
        gpus_per_instance=n_gpu,
        listing_id=(
            f"{provider}:{rec.get('gpu_slug') or name}:{rec.get('offer_type')}:"
            f"{rec.get('region') or ''}:{n_gpu or ''}:{rec.get('vram_gb') or ''}"
        ),
        source_url=rec.get("source_url") or None,
        price_basis="gpu_only" if provider in GPU_ONLY else "gpu_hour_list",
        raw_json=json.dumps(kept, sort_keys=True, default=str),
    )
