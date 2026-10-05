"""gpurentalprices.com daily offers, plus a one-off backfill of its snapshots.

Live source: https://gpurentalprices.com/api/latest.json (keyless JSON).
Backfill: append-only daily snapshots published at
https://raw.githubusercontent.com/adriannutiu/gpu-rental-prices/main/data/snapshots/YYYY-MM-DD.json
(the GitHub mirror keeps a rolling window).
Licence: CC BY 4.0, attribution "GPU rental price data by gpurentalprices.com".

Each offer carries the publisher's own ``fetched_at``; it becomes
``ts_source`` so backfilled history is dated when it was actually observed.
Serverless offers are dropped (not comparable with instance rental), and so
are providers whose terms prohibit index use (``DEFAULT_EXCLUDED_PROVIDERS``).
"""

from __future__ import annotations

import json
from datetime import date, datetime
from typing import Any

from compute_curve.collectors.base import (
    DEFAULT_EXCLUDED_PROVIDERS,
    CollectedBatch,
    canonical_provider,
)
from compute_curve.http import PoliteClient
from compute_curve.schema import Availability, GpuModel, PriceObservation, Term

LATEST = "https://gpurentalprices.com/api/latest.json"
SNAPSHOT = (
    "https://raw.githubusercontent.com/adriannutiu/gpu-rental-prices/main/data/snapshots/{d}.json"
)
ATTRIBUTION = "GPU rental price data by gpurentalprices.com, CC BY 4.0"

GPUS: dict[str, tuple[GpuModel, str]] = {
    "h100": (GpuModel.H100, "UNKNOWN"),
    "h100-sxm": (GpuModel.H100, "SXM"),
    "h100-pcie": (GpuModel.H100, "PCIE"),
    "h100-nvl": (GpuModel.H100, "NVL"),
    "h200": (GpuModel.H200, "UNKNOWN"),
    "h200-nvl": (GpuModel.H200, "NVL"),
    "b200": (GpuModel.B200, "SXM"),
}
KINDS: dict[str, Term] = {
    "on-demand": Term.ON_DEMAND,
    "secure": Term.ON_DEMAND,
    "community": Term.ON_DEMAND,
    "spot": Term.SPOT,
    "reserved": Term.RESERVED,
}
AVAIL: dict[str | None, Availability] = {
    "in-stock": Availability.AVAILABLE,
    "out-of-stock": Availability.UNAVAILABLE,
    "waitlist": Availability.LIMITED,
    "not-reported": Availability.UNKNOWN,
    None: Availability.UNKNOWN,
}


class GpuRentalPricesCollector:
    source_id = "gpurentalprices"
    terms_url = "https://gpurentalprices.com/data"
    attribution = ATTRIBUTION

    def __init__(self, excluded: frozenset[str] = DEFAULT_EXCLUDED_PROVIDERS) -> None:
        self.excluded = excluded

    def fetch(self, client: PoliteClient) -> Any:
        resp = client.get(LATEST)
        resp.raise_for_status()
        return resp.json()

    def normalize(self, payload: Any, ts_observed: datetime, snapshot_id: str) -> CollectedBatch:
        return normalize_snapshot(payload, ts_observed, snapshot_id, self.source_id, self.excluded)


def normalize_snapshot(
    payload: Any,
    ts_observed: datetime,
    snapshot_id: str,
    source: str,
    excluded: frozenset[str] = DEFAULT_EXCLUDED_PROVIDERS,
) -> CollectedBatch:
    offers = payload.get("offers", []) if isinstance(payload, dict) else []
    rows: list[PriceObservation] = []
    dropped = 0
    for o in offers:
        gpu = GPUS.get(str(o.get("gpu")))
        if gpu is None:
            continue  # other GPU families are out of scope, not "dropped"
        row = _offer(o, gpu, ts_observed, snapshot_id, source, excluded)
        if row is None:
            dropped += 1
        else:
            rows.append(row)
    return CollectedBatch(listings=rows, n_dropped=dropped)


def _offer(
    o: dict[str, Any],
    gpu: tuple[GpuModel, str],
    ts_observed: datetime,
    snapshot_id: str,
    source: str,
    excluded: frozenset[str],
) -> PriceObservation | None:
    provider = canonical_provider(str(o.get("provider") or ""))
    term = KINDS.get(str(o.get("kind")))
    price = o.get("usd_hr")
    if not provider or provider in excluded or term is None:
        return None
    if not isinstance(price, int | float) or not 0 < price < 1000:
        return None
    fetched = o.get("fetched_at")
    model, variant = gpu
    kept = {k: o.get(k) for k in ("provider", "gpu", "kind", "vram_gb", "instance", "availability")}
    return PriceObservation(
        ts_observed=ts_observed,
        provider=provider,
        gpu_model=model,
        config=str(o.get("instance") or o.get("gpu")),
        price_usd_per_gpu_hour=float(price),
        term=term,
        region=None,
        availability=AVAIL.get(o.get("availability"), Availability.UNKNOWN),
        source=source,
        snapshot_id=snapshot_id,
        ts_source=datetime.fromisoformat(str(fetched).replace("Z", "+00:00")) if fetched else None,
        gpu_variant=variant,
        listing_id=f"{provider}:{o.get('gpu')}:{o.get('kind')}:{o.get('instance') or ''}",
        source_url=o.get("source_url"),
        price_basis="gpu_hour_list",
        raw_json=json.dumps(kept, sort_keys=True, default=str),
    )


def snapshot_url(d: date) -> str:
    return SNAPSHOT.format(d=d.isoformat())


def snapshot_generated_at(payload: Any) -> datetime | None:
    g = payload.get("generated_at") if isinstance(payload, dict) else None
    return datetime.fromisoformat(str(g).replace("Z", "+00:00")) if g else None
