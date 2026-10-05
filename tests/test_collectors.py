"""Collector normalization tests on HAND-WRITTEN fixtures (invented values, not market data)."""

import json
from datetime import UTC, date, datetime

import pytest

from compute_curve.collectors.base import canonical_provider, html_to_lines, parse_usd
from compute_curve.collectors.cgi import CgiCollector
from compute_curve.collectors.getdeploying import GetDeployingCollector
from compute_curve.collectors.gpurentalprices import GpuRentalPricesCollector
from compute_curve.collectors.lium import LiumCollector
from compute_curve.collectors.provider_pages import (
    CoreWeaveCollector,
    HyperstackCollector,
    LambdaCollector,
    NebiusCollector,
    VerdaCollector,
)

TS = datetime(2026, 10, 5, 18, tzinfo=UTC)


def test_helpers():
    assert canonical_provider("Lambda Labs") == "lambda"
    assert canonical_provider("DataCrunch") == "verda"
    assert canonical_provider("Vast.ai") == "vast"
    assert parse_usd("On-Demand Price: $1,068.80 / Hour") == 1068.80
    assert parse_usd("Contact sales") is None
    assert html_to_lines("<p>a <b>b</b></p><script>x()</script><p> c </p>") == ["a", "b", "c"]


def test_cgi_index_and_receipts():
    doc = {
        "data": {
            "sku": "H100",
            "observed_at": "2026-10-05T18:00:00.000Z",
            "value_usd_gpu_hr": 3.5,
            "stability_band_usd_gpu_hr": 0.5,
            "receipts": [
                {
                    "source_id": "lambda",
                    "price": 4.0,
                    "currency": "USD",
                    "filter_verdict": "accepted",
                    "status": "ok",
                    "gpu_variant": "SXM",
                    "region": "NORTH AMERICA",
                    "last_seen": "2026-10-05T17:45:00.000Z",
                    "sku_identifier": "H100 SXM",
                },
                {
                    "source_id": "vast",
                    "price": 2.0,
                    "currency": "USD",
                    "filter_verdict": "accepted",
                    "status": "ok",
                },
                {
                    "source_id": "civo",
                    "price": 9.0,
                    "currency": "USD",
                    "filter_verdict": "rejected",
                    "status": "ok",
                },
            ],
        },
        "meta": {"status": "ok", "coverage": {"n_passing": 2}, "methodology_id": "m1"},
    }
    b = CgiCollector().normalize({"H100": doc}, TS, "cgi_x")
    assert len(b.indices) == 1 and b.indices[0].value == 3.5 and b.indices[0].n_providers == 2
    assert [r.provider for r in b.listings] == ["lambda"]
    r = b.listings[0]
    assert r.region == "NA" and r.gpu_variant == "SXM"
    assert r.ts_source == datetime(2026, 10, 5, 17, 45, tzinfo=UTC)
    assert b.n_dropped == 2  # vast excluded by terms, civo rejected by CGI


def test_getdeploying_csv():
    csv = (
        "gpu_slug,date,billing_type,reservation_months,min_price,max_price,median_price,"
        "provider_median_price,provider_count,offering_count\n"
        "nvidia-h100,2026-09-28,ON_DEMAND,,1.0,9.0,3.0,3.1,40,130\n"
        "nvidia-h100,2026-09-28,RESERVATION,12,1.5,2.5,2.0,2.1,3,4\n"
        "nvidia-h100,2026-09-28,CUSTOM,,1.9,1.9,1.9,1.9,1,1\n"
    )
    b = GetDeployingCollector().normalize({"nvidia-h100": csv}, TS, "gd_x")
    names = sorted(i.index_name for i in b.indices)
    assert names == [
        "GetDeploying nvidia-h100 ON_DEMAND weekly median",
        "GetDeploying nvidia-h100 RESERVATION 12m weekly median",
    ]
    od = next(i for i in b.indices if "ON_DEMAND" in i.index_name)
    assert od.value == 3.0 and od.n_providers == 40 and od.as_of.date() == date(2026, 9, 28)
    assert b.n_dropped == 1


def test_gpurentalprices_offers():
    payload = {
        "offers": [
            {
                "provider": "lambda",
                "gpu": "h100-sxm",
                "usd_hr": 3.99,
                "kind": "on-demand",
                "fetched_at": "2026-10-04T23:00:00Z",
                "availability": "in-stock",
            },
            {"provider": "runpod", "gpu": "b200", "usd_hr": 5.98, "kind": "community"},
            {"provider": "modal", "gpu": "h100", "usd_hr": 3.9, "kind": "serverless"},
            {"provider": "x", "gpu": "a100", "usd_hr": 1.0, "kind": "on-demand"},
            {"provider": "lium", "gpu": "b200", "usd_hr": 5.6, "kind": "secure"},
        ]
    }
    b = GpuRentalPricesCollector().normalize(payload, TS, "g_x")
    assert [(r.provider, r.gpu_model.value, r.term.value) for r in b.listings] == [
        ("lambda", "H100", "on_demand"),
        ("lium", "B200", "on_demand"),
    ]
    assert b.listings[0].ts_source == datetime(2026, 10, 4, 23, tzinfo=UTC)
    assert b.listings[0].availability.value == "available"
    assert b.n_dropped == 2  # runpod (terms) and serverless; a100 is out of scope


def test_lium_feed():
    payload = {
        "generated_at": "2026-10-05T17:00:00Z",
        "models": [
            {
                "gpu_model": "H100 80GB HBM3",
                "model": "NVIDIA H100 80GB HBM3",
                "reference_price_usd_per_gpu_hour": 1.5,
                "available_gpus": 0,
                "listed_gpus": 10,
                "rented_gpus": 10,
            },
            {"gpu_model": "RTX 4090", "reference_price_usd_per_gpu_hour": 0.3},
        ],
    }
    b = LiumCollector().normalize(payload, TS, "l_x")
    assert len(b.listings) == 1
    r = b.listings[0]
    assert r.gpu_variant == "SXM" and r.availability.value == "unavailable"
    assert json.loads(r.raw_json)["rented_gpus"] == 10


NEBIUS_MD = """
#### NVIDIA® B200 NVLink, gpu-b200-sxm

The platform is only available in the `us-central1` [region](/overview/regions).

<Tabs>
  <Tab title="USD">
    | **Item — from October 1, 2026** | **Price** | **Per** |
    | - | - | - |
    | NVIDIA® B200 NVLink | \\$8.00 | 1 GPU hour |
    | Preemptible NVIDIA® B200 NVLink | \\$4.00 | 1 GPU hour |
    | **Item — before October 1, 2026** | **Price** | **Per** |
    | NVIDIA® B200 NVLink | \\$7.00 | 1 GPU hour |
  </Tab>
  <Tab title="ILS">
    | NVIDIA® B200 NVLink | ₪30.00 | 1 GPU hour |
  </Tab>
</Tabs>

#### NVIDIA® RTX PRO™ 6000, gpu-rtx6000
"""


@pytest.mark.parametrize(
    ("today", "expected"), [(date(2026, 10, 5), 8.0), (date(2026, 9, 20), 7.0)]
)
def test_nebius_effective_dated_prices(today, expected):
    b = NebiusCollector(today=today).normalize(NEBIUS_MD, TS, "n_x")
    od = [r for r in b.listings if r.term.value == "on_demand"]
    assert len(od) == 1 and od[0].price_usd_per_gpu_hour == expected and od[0].region == "US"


def _html(lines):
    return "".join(f"<div>{x}</div>" for x in lines)


def test_lambda_instance_tables():
    header = ["Plan", "VRAM/GPU", "vCPUs", "RAM", "STORAGE", "PRICE/GPU/HR*"]
    rows = []
    for price in ("$6.00", "$6.10", "$6.20", "$6.30"):
        rows += [*header, "NVIDIA B200 SXM6", "180 GB", "208", "2900 GiB", "22 TiB SSD", price]
        rows += ["* plus applicable sales tax/VAT/GST"]
    b = LambdaCollector().normalize(_html(["8x", "4x", "2x", "1x", *rows]), TS, "lam_x")
    assert [(r.gpus_per_instance, r.price_usd_per_gpu_hour) for r in b.listings] == [
        (8, 6.0),
        (4, 6.1),
        (2, 6.2),
        (1, 6.3),
    ]
    assert LambdaCollector().normalize(_html(["no tables"]), TS, "lam_x").listings == []


def test_coreweave_cards_by_region():
    card = [
        "NVIDIA HGX H100",
        "On-Demand Price:",
        "$48.00",
        "/ Hour",
        "Spot Price:",
        "$16.00",
        "/ Hour",
        "8",
        "GPU Count",
    ]
    page = [
        "On-demand GPU instances",
        "REGION: NORTH AMERICA",
        *card,
        "REGION: EUROPE",
        *card,
        "On-demand CPU instances",
        *card,
    ]
    b = CoreWeaveCollector().normalize(_html(page), TS, "cw_x")
    got = sorted((r.region, r.term.value, r.price_usd_per_gpu_hour) for r in b.listings)
    assert got == [
        ("EU", "on_demand", 6.0),
        ("EU", "spot", 2.0),
        ("NA", "on_demand", 6.0),
        ("NA", "spot", 2.0),
    ]


def test_hyperstack_on_demand_and_reserved():
    page = [
        "NVIDIA H100 SXM",
        "80",
        "24",
        "240",
        "$3.00",
        "Reservation",
        "Pricing",
        "NVIDIA H100 SXM",
        "$2.50",
        "Reserve here",
        "NVIDIA GB200 NVL72",
        "$9.99",
    ]
    b = HyperstackCollector().normalize(_html(page), TS, "h_x")
    assert [(r.term.value, r.price_usd_per_gpu_hour) for r in b.listings] == [
        ("on_demand", 3.0),
        ("reserved", 2.5),
    ]


def test_verda_rows_per_gpu():
    page = ["2x B200 SXM6 180GB", "60", "340 GB", "360 GB", "$14.00/h", "$7.00/h"]
    b = VerdaCollector().normalize(_html(page), TS, "v_x")
    assert [(r.term.value, r.price_usd_per_gpu_hour, r.gpus_per_instance) for r in b.listings] == [
        ("on_demand", 7.0, 2),
        ("spot", 3.5, 2),
    ]
