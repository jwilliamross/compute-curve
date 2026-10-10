"""Azure Retail Prices API: H100 and H200 virtual machine prices by region.

Source: https://prices.azure.com/api/retail/prices (keyless JSON, OData
``$filter``, pages of up to 1,000 items linked by ``NextPageLink``).
Terms: Microsoft's documentation describes "an unauthenticated experience"
for "internal analysis and price comparison across SKUs and regions"
(docs/data_sources.md, D50). prices.azure.com serves no robots.txt (404).

One filtered query covers every mapped SKU; it fits in one or two pages.
The service rate-limits bursts (HTTP 429 with a ``Retry-After``-style header),
so pages are spaced by ``PAGE_PAUSE_S`` and a 429 is retried once after the
advertised wait.

Normalization:

* Only SKUs whose GPU count is stated on Microsoft's VM size pages are
  mapped (``SKUS``). Others, including GB200 (a different product, see
  :func:`compute_curve.schema.canonical_gpu_model`), are not requested.
* Linux meters only: Windows meters include an OS licence and DevTest
  meters are not public prices. Non-primary meter regions are skipped.
* ``Consumption`` meters are on-demand, or spot when the meter name ends in
  "Spot"; "Low Priority" meters are skipped. ``Reservation`` meters quote the
  total price for the term, converted to an hourly rate with 8,760 hours per
  year (an assumption: Azure's own calculator uses 730 hours per month).
* Price per GPU-hour = VM price per hour / GPUs per VM.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any
from urllib.parse import urlsplit, urlunsplit

from compute_curve.collectors.base import CollectedBatch
from compute_curve.http import PoliteClient
from compute_curve.schema import (
    Availability,
    GpuModel,
    PriceObservation,
    Term,
    normalize_region,
)

API = "https://prices.azure.com/api/retail/prices"
HOST = "prices.azure.com"
DOCS = (
    "https://learn.microsoft.com/en-us/rest/api/cost-management/retail-prices/azure-retail-prices"
)
ATTRIBUTION = "Microsoft Azure Retail Prices API, https://prices.azure.com/api/retail/prices"
_SIZES = "https://learn.microsoft.com/en-us/azure/virtual-machines/sizes/gpu-accelerated/"

# armSkuName -> (GPU family, form factor, GPUs per VM, Microsoft page stating the count)
SKUS: dict[str, tuple[GpuModel, str, int, str]] = {
    "Standard_ND96isr_H100_v5": (GpuModel.H100, "NVLINK", 8, _SIZES + "ndh100v5-series"),
    "Standard_NC40ads_H100_v5": (GpuModel.H100, "NVL", 1, _SIZES + "ncadsh100v5-series"),
    "Standard_NC80adis_H100_v5": (GpuModel.H100, "NVL", 2, _SIZES + "ncadsh100v5-series"),
    "Standard_NCC40ads_H100_v5": (GpuModel.H100, "NVL", 1, _SIZES + "nccadsh100v5-series"),
    "Standard_ND96isr_H200_v5": (GpuModel.H200, "NVLINK", 8, _SIZES + "nd-h200-v5-series"),
}
HOURS_PER_YEAR = 8760.0
MAX_PAGES = 10
PAGE_PAUSE_S = 6.0
MAX_RETRY_AFTER_S = 90.0
KEPT_FIELDS = (
    "armSkuName",
    "armRegionName",
    "location",
    "meterName",
    "productName",
    "skuName",
    "type",
    "reservationTerm",
    "retailPrice",
    "unitOfMeasure",
    "currencyCode",
    "effectiveStartDate",
    "isPrimaryMeterRegion",
    "meterId",
)


def odata_filter(skus: list[str] | None = None) -> str:
    """OData filter for the mapped SKUs' consumption and reservation VM meters."""
    names = " or ".join(f"armSkuName eq '{s}'" for s in (skus or list(SKUS)))
    return (
        "serviceName eq 'Virtual Machines' "
        "and (priceType eq 'Consumption' or priceType eq 'Reservation') "
        f"and ({names})"
    )


def next_page_url(link: Any) -> str | None:
    """The API's ``NextPageLink`` with the default port removed; None if absent or foreign."""
    if not link or not isinstance(link, str):
        return None
    parts = urlsplit(link)
    if parts.scheme != "https" or parts.hostname != HOST:
        return None
    return urlunsplit(("https", HOST, parts.path, parts.query, ""))


class AzureRetailCollector:
    source_id = "azure_retail"
    terms_url = DOCS
    attribution = ATTRIBUTION

    def fetch(self, client: PoliteClient) -> Any:
        items: list[dict[str, Any]] = []
        url: str | None = API
        params: dict[str, Any] | None = {"$filter": odata_filter()}
        pages = 0
        while url and pages < MAX_PAGES:
            if pages:
                client.sleep(PAGE_PAUSE_S)
            doc = _get_json(client, url, params)
            items.extend(i for i in doc.get("Items") or [] if isinstance(i, dict))
            url, params = next_page_url(doc.get("NextPageLink")), None
            pages += 1
        return {"items": items, "pages": pages, "truncated": url is not None}

    def normalize(self, payload: Any, ts_observed: datetime, snapshot_id: str) -> CollectedBatch:
        items = payload.get("items", []) if isinstance(payload, dict) else []
        rows: list[PriceObservation] = []
        dropped = skipped = 0
        for item in items:
            if not _in_scope(item):
                skipped += 1
                continue
            row = _item(item, ts_observed, snapshot_id, self.source_id)
            if row is None:
                dropped += 1
            else:
                rows.append(row)
        notes = [f"{skipped} Windows, low-priority or non-primary meters skipped"]
        if isinstance(payload, dict) and payload.get("truncated"):
            notes.append(f"stopped after {MAX_PAGES} pages")
        return CollectedBatch(listings=rows, n_dropped=dropped, notes=notes)


def _get_json(client: PoliteClient, url: str, params: dict[str, Any] | None) -> dict[str, Any]:
    resp = client.get(url, params=params)
    if resp.status_code == 429:
        try:
            wait = float(resp.headers.get("x-ms-ratelimit-retailprices-retry-after", "60"))
        except ValueError:
            wait = 60.0
        client.sleep(min(max(wait, 1.0), MAX_RETRY_AFTER_S))
        resp = client.get(url, params=params)
    resp.raise_for_status()
    doc = resp.json()
    if not isinstance(doc, dict):
        raise ValueError("unexpected Azure Retail Prices response")
    return doc


def _in_scope(item: dict[str, Any]) -> bool:
    """Linux, primary-region, non-low-priority meters."""
    product = str(item.get("productName") or "")
    meter = str(item.get("meterName") or "")
    if product.endswith(("Windows", " Win")) or "Low Priority" in meter:
        return False
    if item.get("type") not in ("Consumption", "Reservation"):
        return False
    return item.get("isPrimaryMeterRegion") is not False


def reservation_years(term: Any) -> int | None:
    """Years in a reservation term such as '1 Year' or '3 Years'."""
    parts = str(term or "").split()
    if len(parts) == 2 and parts[0].isdigit() and parts[1].lower().startswith("year"):
        return int(parts[0])
    return None


def _item(
    item: dict[str, Any], ts_observed: datetime, snapshot_id: str, source: str
) -> PriceObservation | None:
    spec = SKUS.get(str(item.get("armSkuName")))
    price = item.get("retailPrice")
    if spec is None or item.get("currencyCode", "USD") != "USD":
        return None
    if item.get("unitOfMeasure") != "1 Hour":
        return None
    if not isinstance(price, int | float) or price <= 0:
        return None
    model, variant, n_gpu, _ = spec
    meter = str(item.get("meterName") or "")
    years: int | None = None
    if item.get("type") == "Reservation":
        years = reservation_years(item.get("reservationTerm"))
        if years is None:
            return None
        term, vm_hour = Term.RESERVED, float(price) / (years * HOURS_PER_YEAR)
        basis = f"reservation_{years}y_total_per_8760h_per_gpu"
    else:
        term = Term.SPOT if meter.endswith("Spot") else Term.ON_DEMAND
        vm_hour, basis = float(price), "vm_hour_per_gpu"
    per_gpu = vm_hour / n_gpu
    if not 0 < per_gpu < 1000:
        return None
    region_code = str(item.get("armRegionName") or "")
    kept = {k: item.get(k) for k in KEPT_FIELDS if k in item}
    kept["gpus_per_vm"] = n_gpu
    return PriceObservation(
        ts_observed=ts_observed,
        provider="azure",
        gpu_model=model,
        config=f"{n_gpu}x {model.value} {variant} ({item.get('armSkuName')})",
        price_usd_per_gpu_hour=per_gpu,
        term=term,
        region=normalize_region(str(item.get("location") or "")) or region_code or None,
        availability=Availability.UNKNOWN,
        source=source,
        snapshot_id=snapshot_id,
        ts_source=None,
        gpu_variant=variant,
        gpus_per_instance=n_gpu,
        listing_id=f"azure:{item.get('armSkuName')}:{region_code}:{term.value}"
        + (f":{years}y" if years else "")
        + f":{meter}",
        source_url=API,
        price_basis=basis,
        raw_json=json.dumps(kept, sort_keys=True, default=str),
    )
