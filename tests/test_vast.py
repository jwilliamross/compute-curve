import json

from compute_curve.collectors.vast import VastCollector, normalize_offer


def test_normalize_fixture(vast_payload, t0):
    batch = VastCollector().normalize(vast_payload, t0, "vast_20261005T170000Z")
    rows, dropped = batch.listings, batch.n_dropped
    # RTX 4090, zero price and GB200 are dropped
    assert dropped == 3
    assert [r.gpu_model.value for r in rows] == ["H100", "H100", "B200"]
    h100_sxm = rows[0]
    assert h100_sxm.price_usd_per_gpu_hour == 2.0  # 16.0 / 8
    assert h100_sxm.gpu_variant == "SXM"
    assert h100_sxm.region == "US"
    assert h100_sxm.provider == "vast.ai"
    assert h100_sxm.price_basis == "instance_base_excl_storage"


def test_sensitive_fields_never_stored(vast_payload, t0):
    rows = VastCollector().normalize(vast_payload, t0, "x").listings
    for r in rows:
        raw = json.loads(r.raw_json)
        assert "public_ipaddr" not in raw
        assert "hostname" not in raw


def test_bid_offers_dropped(t0):
    offer = {"gpu_name": "H100 SXM", "num_gpus": 1, "dph_base": 2.0, "is_bid": True}
    assert normalize_offer(offer, t0, "x") is None


def test_request_body_is_on_demand_only():
    body = VastCollector().request_body()
    assert body["type"] == "ondemand"
    assert "B200" in body["gpu_name"]["in"]
