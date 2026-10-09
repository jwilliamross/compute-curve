"""Computable GPU Index (CGI) collector.

Source: https://api.getcomputable.com (keyless JSON API; robots.txt absent).
Licence: data CC BY-NC 4.0. Attribution required; non-commercial use only;
not to be used for settlement or in a product (docs/data_sources.md).

Stores two things per GPU:

* the CGI index value itself as an :class:`IndexObservation` (a third-party
  reference index, *not* the CME settlement index), and
* each accepted per-provider receipt as a :class:`PriceObservation` with the
  provider's price and CGI's ``last_seen`` as ``ts_source``.
"""

from __future__ import annotations

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
    IndexObservation,
    PriceObservation,
    Term,
    canonical_gpu_model,
    normalize_region,
)

BASE = "https://api.getcomputable.com/v1/index"
SKUS: tuple[str, ...] = ("H100", "B200")
LICENSE = "CC-BY-NC-4.0"
ATTRIBUTION = (
    "Computable GPU Index (CGI), (c) 2026 Computable, "
    "https://github.com/getcomputable/gpu-index, licensed CC BY-NC 4.0"
)


class CgiCollector:
    source_id = "cgi"
    terms_url = "https://github.com/getcomputable/gpu-index/blob/main/LICENSE-DATA.md"
    attribution = ATTRIBUTION

    def __init__(self, excluded: frozenset[str] = DEFAULT_EXCLUDED_PROVIDERS) -> None:
        self.excluded = excluded

    def fetch(self, client: PoliteClient) -> Any:
        out: dict[str, Any] = {}
        for sku in SKUS:
            resp = client.get(f"{BASE}/{sku}/latest", params={"include": "receipts"})
            resp.raise_for_status()
            out[sku] = resp.json()
        return out

    def normalize(self, payload: Any, ts_observed: datetime, snapshot_id: str) -> CollectedBatch:
        listings: list[PriceObservation] = []
        indices: list[IndexObservation] = []
        dropped = 0
        for sku, doc in (payload or {}).items():
            data = (doc or {}).get("data") or {}
            meta = (doc or {}).get("meta") or {}
            model = canonical_gpu_model(str(data.get("sku") or sku))
            if model is GpuModel.OTHER:
                continue
            value = data.get("value_usd_gpu_hr")
            if isinstance(value, int | float) and value > 0 and meta.get("status") == "ok":
                cov = meta.get("coverage") or {}
                indices.append(
                    IndexObservation(
                        ts_observed=ts_observed,
                        source=self.source_id,
                        snapshot_id=snapshot_id,
                        index_name=f"Computable GPU Index {sku}",
                        gpu_model=model,
                        term=Term.ON_DEMAND,
                        as_of=datetime.fromisoformat(
                            str(data["observed_at"]).replace("Z", "+00:00")
                        ),
                        value=float(value),
                        n_providers=cov.get("n_passing"),
                        methodology_id=meta.get("methodology_id"),
                        license=LICENSE,
                        raw_json=json.dumps(
                            {
                                "stability_band_usd_gpu_hr": data.get("stability_band_usd_gpu_hr"),
                                "coverage": cov,
                                "freshness": meta.get("freshness"),
                                "attribution": ATTRIBUTION,
                            },
                            sort_keys=True,
                        ),
                    )
                )
            for r in data.get("receipts") or []:
                row = _receipt(r, model, ts_observed, snapshot_id, self.excluded)
                if row is None:
                    dropped += 1
                else:
                    listings.append(row)
        return CollectedBatch(listings=listings, indices=indices, n_dropped=dropped)


def _receipt(
    r: dict[str, Any],
    model: GpuModel,
    ts_observed: datetime,
    snapshot_id: str,
    excluded: frozenset[str],
) -> PriceObservation | None:
    provider = canonical_provider(str(r.get("source_id") or ""))
    price = r.get("price")
    if not provider or provider in excluded:
        return None
    if r.get("filter_verdict") != "accepted" or r.get("status") != "ok":
        return None
    if not isinstance(price, int | float) or price <= 0 or r.get("currency", "USD") != "USD":
        return None
    seen = r.get("last_seen")
    variant = str(r.get("gpu_variant") or "UNKNOWN").upper()
    return PriceObservation(
        ts_observed=ts_observed,
        provider=provider,
        gpu_model=model,
        config=str(r.get("sku_identifier") or model.value),
        price_usd_per_gpu_hour=float(price),
        term=Term.ON_DEMAND,
        region=normalize_region(r.get("region")),
        availability=Availability.UNKNOWN,
        source="cgi",
        snapshot_id=snapshot_id,
        ts_source=datetime.fromisoformat(str(seen).replace("Z", "+00:00")) if seen else None,
        gpu_variant=variant if variant in {"SXM", "PCIE", "NVL", "NVLINK"} else "UNKNOWN",
        gpus_per_instance=r.get("gpu_count_basis")
        if isinstance(r.get("gpu_count_basis"), int)
        else None,
        listing_id=f"{provider}:{r.get('sku_identifier')}",
        source_url=r.get("source_url"),
        price_basis="gpu_hour_list",
        raw_json=json.dumps(
            {
                k: r.get(k)
                for k in ("provider_class", "weight", "smoothed_vote_usd", "liveness_score")
            },
            sort_keys=True,
        ),
    )


# ---------------------------------------------------------------------------
# History backfill (index values only; the API serves the last 90 days)
# ---------------------------------------------------------------------------
HISTORY_LIMIT = 2976  # documented maximum page size (31 days of 15-minute values)


def _on_grid(ts: datetime) -> str:
    """UTC timestamp floored to the index's 15-minute grid, in the API's format."""
    floored = ts.replace(minute=ts.minute - ts.minute % 15, second=0, microsecond=0)
    return floored.strftime("%Y-%m-%dT%H:%M:00.000Z")


def fetch_history(
    client: PoliteClient, sku: str, start: datetime, end: datetime
) -> list[dict[str, Any]]:
    """All published values for ``sku`` in [start, end], following ``next_cursor``.

    The API refuses bounds off its 15-minute grid: seconds give HTTP 400 and an
    end after the latest stamp gives HTTP 404. Both bounds are floored to the
    grid (checked 2026-10-09).
    """
    values: list[dict[str, Any]] = []
    params: dict[str, Any] = {
        "from": _on_grid(start),
        "to": _on_grid(end),
        "limit": HISTORY_LIMIT,
    }
    for _ in range(100):  # hard stop against a cursor loop
        resp = client.get(f"{BASE}/{sku}/history", params=params)
        resp.raise_for_status()
        data = resp.json().get("data") or {}
        values.extend(data.get("values") or [])
        cursor = data.get("next_cursor")
        if not cursor:
            break
        params["cursor"] = cursor
    return values


def normalize_history(
    sku: str, values: list[dict[str, Any]], ts_observed: datetime, snapshot_id: str
) -> CollectedBatch:
    model = canonical_gpu_model(sku)
    rows: list[IndexObservation] = []
    dropped = 0
    seen: set[str] = set()
    for v in values:
        val = v.get("value_usd_gpu_hr")
        at = v.get("observed_at")
        if (
            not at
            or at in seen
            or v.get("status") != "ok"
            or not isinstance(val, int | float)
            or val <= 0
        ):
            dropped += 1
            continue
        seen.add(at)
        cov = v.get("coverage") or {}
        rows.append(
            IndexObservation(
                ts_observed=ts_observed,
                source="cgi_hist",
                snapshot_id=snapshot_id,
                index_name=f"Computable GPU Index {sku}",
                gpu_model=model,
                term=Term.ON_DEMAND,
                as_of=datetime.fromisoformat(str(at).replace("Z", "+00:00")),
                value=float(val),
                n_providers=cov.get("n_passing"),
                methodology_id=v.get("methodology_id"),
                license=LICENSE,
                raw_json=json.dumps(
                    {
                        "stability_band_usd_gpu_hr": v.get("stability_band_usd_gpu_hr"),
                        "generated_at": v.get("generated_at"),
                    },
                    sort_keys=True,
                ),
            )
        )
    return CollectedBatch(indices=rows, n_dropped=dropped)
