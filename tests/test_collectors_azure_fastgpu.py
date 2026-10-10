"""Azure Retail Prices and FastGPU collectors on HAND-WRITTEN payloads.

Every value below is invented for the test; none is market data. The HTTP
layer is an in-memory httpx.MockTransport (no network).
"""

from datetime import UTC, datetime

import httpx
import pytest

from compute_curve.collectors.azure_retail import (
    AzureRetailCollector,
    next_page_url,
    odata_filter,
    reservation_years,
)
from compute_curve.collectors.fastgpu import FastGpuCollector
from compute_curve.config import load_config
from compute_curve.http import PoliteClient
from compute_curve.snapshot import registry, run_snapshot

TS = datetime(2026, 10, 10, 12, tzinfo=UTC)


def _meter(**kw: object) -> dict[str, object]:
    base: dict[str, object] = {
        "currencyCode": "USD",
        "retailPrice": 80.0,
        "armRegionName": "eastus",
        "location": "US East",
        "meterName": "ND96isr H100 v5",
        "productName": "Virtual Machines NDsr H100 v5 Series",
        "skuName": "ND96isr H100 v5",
        "unitOfMeasure": "1 Hour",
        "type": "Consumption",
        "isPrimaryMeterRegion": True,
        "armSkuName": "Standard_ND96isr_H100_v5",
        "meterId": "00000000-test",
    }
    base.update(kw)
    return base


PAGE1 = {
    "Items": [
        _meter(),
        _meter(meterName="ND96isr H100 v5 Spot", retailPrice=16.0),
        _meter(type="Reservation", reservationTerm="1 Year", retailPrice=350400.0),
        _meter(productName="Virtual Machines NDsr H100 v5 Series Windows", retailPrice=99.0),
        _meter(meterName="ND96isr H100 v5 Low Priority", retailPrice=10.0),
    ],
    "NextPageLink": "https://prices.azure.com:443/api/retail/prices?$filter=x&$skip=1000",
}
PAGE2 = {
    "Items": [
        _meter(
            armSkuName="Standard_NC80adis_H100_v5",
            meterName="NC80adis H100 v5",
            productName="Virtual Machines NCadsH100v5 Series",
            retailPrice=10.0,
            location="EU West",
            armRegionName="westeurope",
        ),
        _meter(armSkuName="Standard_ND96is_flex_H100_v5", retailPrice=70.0),  # unmapped
        _meter(currencyCode="EUR"),
    ],
    "NextPageLink": None,
}

HEADER = (
    "provider,provider_label,gpu_model,gpu_slug,vram_gb,offer_type,region,price_usd_hr,"
    "min_gpu_count,available_count,interconnect,source_url,fetched_at\n"
)
CSV = (
    HEADER
    + """lambdalabs,Lambda,H100 SXM,h100-sxm,80,on-demand,,3.00,8,2,,https://example.test/lambda,2026-10-10T00:15:00+00:00
examplecloud,Example,H200,h200,141,spot,US,2.50,1,0,,,2026-10-10T00:15:00+00:00
examplecloud,Example,B200,b200,180,reserved,,4.00,8,,nvlink,,2026-10-10T00:15:00+00:00
modal,Modal,H100 PCIe,h100-pcie,80,on-demand,,3.50,1,,,,2026-10-10T00:15:00+00:00
vast,Vast.ai,H100 SXM,h100-sxm,80,on-demand,,1.00,1,5,,,2026-10-10T00:15:00+00:00
runpod,RunPod,B200,b200,180,community,,2.00,1,,,,2026-10-10T00:15:00+00:00
examplecloud,Example,H100 NVL,h100-nvl,94,serverless,,5.00,1,,,,2026-10-10T00:15:00+00:00
examplecloud,Example,H100 SXM,h100-sxm,80,on-demand,,,1,,,,2026-10-10T00:15:00+00:00
examplecloud,Example,GB200,gb200,186,on-demand,,9.00,4,,,,2026-10-10T00:15:00+00:00
examplecloud,Example,RTX 4090,rtx-4090,24,on-demand,,0.50,1,,,,2026-10-10T00:15:00+00:00
"""
)


def handler(requests: list[httpx.Request]):
    def _handle(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path == "/robots.txt":
            if request.url.host == "fastgpu.co":
                return httpx.Response(
                    200,
                    text="User-Agent: *\nAllow: /\nAllow: /api/v1/dataset/\nDisallow: /api/\n",
                )
            return httpx.Response(404)
        if request.url.host == "prices.azure.com":
            page = PAGE2 if "skip" in str(request.url) else PAGE1
            return httpx.Response(200, json=page)
        if request.url.host == "fastgpu.co":
            return httpx.Response(200, text=CSV)
        return httpx.Response(500)

    return _handle


def client(requests: list[httpx.Request], sleeps: list[float] | None = None) -> PoliteClient:
    return PoliteClient(
        user_agent="test",
        transport=httpx.MockTransport(handler(requests)),
        sleep=(sleeps.append if sleeps is not None else (lambda s: None)),
    )


def test_azure_helpers():
    f = odata_filter(["Standard_X"])
    assert "armSkuName eq 'Standard_X'" in f and "priceType eq 'Reservation'" in f
    assert "DevTest" not in f
    assert next_page_url("https://prices.azure.com:443/api/retail/prices?$skip=1000") == (
        "https://prices.azure.com/api/retail/prices?$skip=1000"
    )
    assert next_page_url("https://elsewhere.example/api?$skip=1000") is None
    assert next_page_url(None) is None
    assert reservation_years("3 Years") == 3 and reservation_years("1 Year") == 1
    assert reservation_years("1 Month") is None


def test_azure_paginates_politely_and_normalizes():
    reqs: list[httpx.Request] = []
    sleeps: list[float] = []
    c = AzureRetailCollector()
    payload = c.fetch(client(reqs, sleeps))
    api_calls = [r for r in reqs if r.url.path != "/robots.txt"]
    assert len(api_calls) == 2 and payload["pages"] == 2 and not payload["truncated"]
    assert "filter" in str(api_calls[0].url) and "Standard_ND96isr_H100_v5" in str(api_calls[0].url)
    assert all(r.url.port in (None, 443) for r in api_calls)
    assert sleeps and max(sleeps) >= 6.0  # pages are spaced out

    batch = c.normalize(payload, TS, "azure_retail_x")
    by_term = {(r.term.value, r.gpus_per_instance): r for r in batch.listings}
    assert len(batch.listings) == 4
    assert batch.n_dropped == 2  # unmapped SKU and non-USD meter
    assert by_term[("on_demand", 8)].price_usd_per_gpu_hour == pytest.approx(10.0)
    assert by_term[("spot", 8)].price_usd_per_gpu_hour == pytest.approx(2.0)
    reserved = by_term[("reserved", 8)]
    assert reserved.price_usd_per_gpu_hour == pytest.approx(350400.0 / 8760 / 8)
    assert reserved.listing_id is not None and ":1y:" in reserved.listing_id
    nc = by_term[("on_demand", 2)]
    assert nc.price_usd_per_gpu_hour == pytest.approx(5.0)
    assert nc.region == "EU" and nc.gpu_variant == "NVL"
    assert all(r.provider == "azure" for r in batch.listings)
    assert by_term[("on_demand", 8)].region == "US"


def test_azure_retries_once_after_rate_limit():
    calls: list[str] = []
    sleeps: list[float] = []

    def limited(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            return httpx.Response(404)
        calls.append(str(request.url))
        if len(calls) <= 3:  # the client's own retries also see 429
            return httpx.Response(429, headers={"x-ms-ratelimit-retailprices-retry-after": "30"})
        return httpx.Response(200, json={"Items": [_meter()], "NextPageLink": None})

    c = PoliteClient(
        user_agent="test",
        transport=httpx.MockTransport(limited),
        sleep=sleeps.append,
    )
    payload = AzureRetailCollector().fetch(c)
    assert len(payload["items"]) == 1
    assert 30.0 in sleeps


def test_fastgpu_keeps_h100_h200_b200_and_drops_excluded_providers():
    reqs: list[httpx.Request] = []
    c = FastGpuCollector()
    text = c.fetch(client(reqs))
    assert [r.url.path for r in reqs if r.url.path != "/robots.txt"] == [
        "/api/v1/dataset/gpu-prices-current.csv"
    ]
    batch = c.normalize(text, TS, "fastgpu_x")
    providers = {r.provider for r in batch.listings}
    assert providers == {"lambda", "examplecloud", "modal"}
    assert "vast" not in providers and "runpod" not in providers
    assert len(batch.listings) == 4
    assert batch.n_dropped == 4  # vast, runpod, serverless, blank price
    by_model = {(r.gpu_model.value, r.term.value): r for r in batch.listings}
    lam = next(r for r in batch.listings if r.provider == "lambda")
    assert lam.gpu_variant == "SXM" and lam.gpus_per_instance == 8
    assert '"available_count": 2' in (lam.raw_json or "")
    assert lam.availability.value == "available"
    assert lam.ts_source == datetime(2026, 10, 10, 0, 15, tzinfo=UTC)
    h200 = by_model[("H200", "spot")]
    assert h200.availability.value == "unavailable" and h200.region == "US"
    b200 = by_model[("B200", "reserved")]
    assert b200.availability.value == "unknown" and b200.gpu_variant == "UNKNOWN"
    modal = next(r for r in batch.listings if r.provider == "modal")
    assert modal.price_basis == "gpu_only" and modal.gpu_variant == "PCIE"


def test_fastgpu_rejects_unexpected_columns():
    with pytest.raises(ValueError):
        FastGpuCollector().normalize("a,b\n1,2\n", TS, "fastgpu_x")


def test_snapshot_writes_both_new_sources(tmp_path):
    cfg = load_config()
    cfg = cfg.model_copy(
        update={"project": cfg.project.model_copy(update={"data_dir": tmp_path / "data"})}
    )
    assert {"azure_retail", "fastgpu"} <= set(registry(cfg))
    assert {"azure_retail", "fastgpu"} <= set(cfg.collectors.enabled)
    reqs: list[httpx.Request] = []
    out = run_snapshot(cfg, ["azure_retail", "fastgpu"], client=client(reqs))
    assert [(o.source, o.status, o.n_listings) for o in out] == [
        ("azure_retail", "written", 4),
        ("fastgpu", "written", 4),
    ]
    for src in ("azure_retail", "fastgpu"):
        assert list((tmp_path / "data" / "raw" / "listings" / src).rglob("*.parquet"))
    again = run_snapshot(cfg, ["azure_retail", "fastgpu"], client=client(reqs))
    assert [o.status for o in again] == ["skipped_exists", "skipped_exists"]
