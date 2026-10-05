"""Vast.ai marketplace offers collector.

Endpoint: ``POST https://console.vast.ai/api/v0/bundles/`` (documented at
https://docs.vast.ai/api-reference/search/search-offers). The search endpoint
returned data without an API key on 2026-10-05, so no credential is sent.

Price basis: ``dph_base / num_gpus``. ``dph_base`` is the offer's hourly price
for GPUs plus bundled CPU and RAM, excluding storage and bandwidth. ``dph_total``
adds storage for the default disk size and is kept in ``raw_json``.

Vast is a marketplace with many independent hosts. For index weighting the
whole marketplace counts as one provider (``vast.ai``) so it cannot dominate
the aggregate through listing count alone.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from compute_curve.http import PoliteClient
from compute_curve.schema import (
    Availability,
    GpuModel,
    PriceObservation,
    Term,
    canonical_gpu_model,
    gpu_variant,
    strip_sensitive,
)

ENDPOINT = "https://console.vast.ai/api/v0/bundles/"
GPU_NAMES: tuple[str, ...] = ("H100 SXM", "H100 PCIE", "H100 NVL", "H200", "H200 NVL", "B200")

# Fields kept in raw_json. Everything else (including host identifiers such as
# public IP and hostname) is dropped at collection time.
KEEP_FIELDS: tuple[str, ...] = (
    "id",
    "ask_contract_id",
    "machine_id",
    "gpu_name",
    "num_gpus",
    "gpu_ram",
    "gpu_frac",
    "dph_base",
    "dph_total",
    "discounted_dph_total",
    "storage_cost",
    "inet_up_cost",
    "inet_down_cost",
    "min_bid",
    "geolocation",
    "verification",
    "reliability",
    "reliability2",
    "rentable",
    "rented",
    "hosting_type",
    "is_bid",
    "dlperf",
    "total_flops",
    "cuda_max_good",
    "compute_cap",
    "start_date",
    "end_date",
)


class VastCollector:
    source_id = "vast"
    terms_url = "https://vast.ai/terms"

    def __init__(self, limit: int = 1000) -> None:
        self.limit = limit

    def request_body(self) -> dict[str, Any]:
        return {
            "limit": self.limit,
            "type": "ondemand",
            "rentable": {"eq": True},
            "gpu_name": {"in": list(GPU_NAMES)},
        }

    def fetch(self, client: PoliteClient) -> Any:
        # The API host's robots.txt governs crawlers of HTML pages; we still
        # check it and refuse if it disallows the path.
        resp = client.post(ENDPOINT, json=self.request_body())
        resp.raise_for_status()
        return resp.json()

    def normalize(
        self, payload: Any, ts_observed: datetime, snapshot_id: str
    ) -> tuple[list[PriceObservation], int]:
        offers = payload.get("offers", []) if isinstance(payload, dict) else []
        rows: list[PriceObservation] = []
        dropped = 0
        for offer in offers:
            row = normalize_offer(offer, ts_observed, snapshot_id)
            if row is None:
                dropped += 1
            else:
                rows.append(row)
        return rows, dropped


def normalize_offer(
    offer: dict[str, Any], ts_observed: datetime, snapshot_id: str
) -> PriceObservation | None:
    """Map one Vast offer to an observation; return None if unusable."""
    name = str(offer.get("gpu_name") or "")
    model = canonical_gpu_model(name)
    n = offer.get("num_gpus")
    base = offer.get("dph_base")
    if model is GpuModel.OTHER or not isinstance(n, int | float) or n < 1:
        return None
    if not isinstance(base, int | float) or base <= 0:
        return None
    if offer.get("is_bid"):
        return None
    per_gpu = float(base) / float(n)
    kept = strip_sensitive({k: offer.get(k) for k in KEEP_FIELDS if k in offer})
    ram_gb = offer.get("gpu_ram")
    ram_txt = f" {round(ram_gb / 1024)}GB" if isinstance(ram_gb, int | float) else ""
    return PriceObservation(
        ts_observed=ts_observed,
        provider="vast.ai",
        gpu_model=model,
        config=f"{int(n)}x {name}{ram_txt}",
        price_usd_per_gpu_hour=per_gpu,
        term=Term.ON_DEMAND,
        region=_region(offer.get("geolocation")),
        availability=Availability.AVAILABLE if offer.get("rentable") else Availability.UNAVAILABLE,
        source="vast",
        snapshot_id=snapshot_id,
        gpu_variant=gpu_variant(name),
        gpus_per_instance=int(n),
        listing_id=str(offer.get("ask_contract_id") or offer.get("id")),
        source_url=ENDPOINT,
        price_basis="instance_base_excl_storage",
        raw_json=json.dumps(kept, sort_keys=True, default=str),
    )


def _region(geo: Any) -> str | None:
    if not isinstance(geo, str) or not geo.strip():
        return None
    parts = [p.strip() for p in geo.split(",") if p.strip()]
    return parts[-1] if parts else None
