"""Lium marketplace public pricing feed.

Source: https://lium.io/pricing.json (keyless; robots.txt advertises it;
documented limit 60 requests per minute). Terms (effective 2026-09-27) carry no
restriction on reading the public feed (docs/data_sources.md).

One row per GPU model: the marketplace reference price, with listed, rented
and idle GPU counts kept in ``raw_json`` as a utilization signal.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from compute_curve.collectors.base import CollectedBatch
from compute_curve.http import PoliteClient
from compute_curve.schema import (
    Availability,
    PriceObservation,
    Term,
    canonical_gpu_model,
    gpu_variant,
)

URL = "https://lium.io/pricing.json"
VARIANT_BY_NAME = {"H100 80GB HBM3": "SXM", "H100 PCIe": "PCIE", "H100 NVL": "NVL", "B200": "SXM"}


class LiumCollector:
    source_id = "lium"
    terms_url = "https://lium.io/terms"
    attribution = "Lium public pricing feed, https://lium.io/pricing.json"

    def fetch(self, client: PoliteClient) -> Any:
        resp = client.get(URL)
        resp.raise_for_status()
        return resp.json()

    def normalize(self, payload: Any, ts_observed: datetime, snapshot_id: str) -> CollectedBatch:
        rows: list[PriceObservation] = []
        dropped = 0
        for m in (payload or {}).get("models", []) if isinstance(payload, dict) else []:
            name = str(m.get("gpu_model") or m.get("name") or "")
            model = canonical_gpu_model(name)
            if model.value == "OTHER":
                continue
            price = m.get("reference_price_usd_per_gpu_hour")
            if not isinstance(price, int | float) or price <= 0:
                dropped += 1
                continue
            idle = m.get("available_gpus")
            avail = (
                Availability.AVAILABLE
                if isinstance(idle, int) and idle > 0
                else Availability.UNAVAILABLE
                if isinstance(idle, int)
                else Availability.UNKNOWN
            )
            upd = m.get("updated_at") or payload.get("generated_at")
            keep = (
                "min_price_usd_per_gpu_hour",
                "max_price_usd_per_gpu_hour",
                "listed_gpus",
                "rented_gpus",
                "idle_gpus",
                "available_gpus",
                "available_nodes",
                "vram_gb",
            )
            rows.append(
                PriceObservation(
                    ts_observed=ts_observed,
                    provider="lium",
                    gpu_model=model,
                    config=str(m.get("model") or name),
                    price_usd_per_gpu_hour=float(price),
                    term=Term.ON_DEMAND,
                    region=None,
                    availability=avail,
                    source=self.source_id,
                    snapshot_id=snapshot_id,
                    ts_source=datetime.fromisoformat(str(upd).replace("Z", "+00:00"))
                    if upd
                    else None,
                    gpu_variant=VARIANT_BY_NAME.get(name, gpu_variant(name)),
                    listing_id=f"lium:{m.get('slug') or name}",
                    source_url=m.get("url") or URL,
                    price_basis="marketplace_reference",
                    raw_json=json.dumps({k: m.get(k) for k in keep}, sort_keys=True),
                )
            )
        return CollectedBatch(listings=rows, n_dropped=dropped)
