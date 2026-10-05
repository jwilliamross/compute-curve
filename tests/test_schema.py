from datetime import datetime

import pytest
from pydantic import ValidationError

from compute_curve.schema import (
    GpuModel,
    PriceObservation,
    canonical_gpu_model,
    gpu_variant,
    strip_sensitive,
)


@pytest.mark.parametrize(
    ("name", "model"),
    [
        ("H100 SXM", GpuModel.H100),
        ("NVIDIA H100 80GB HBM3", GpuModel.H100),
        ("h100-pcie", GpuModel.H100),
        ("H200 NVL", GpuModel.H200),
        ("B200", GpuModel.B200),
        ("NVIDIA B200 180GB", GpuModel.B200),
        ("GB200", GpuModel.OTHER),
        ("GH200", GpuModel.OTHER),
        ("B300", GpuModel.OTHER),
        ("A100 SXM4", GpuModel.OTHER),
    ],
)
def test_canonical_gpu_model(name, model):
    assert canonical_gpu_model(name) is model


def test_gpu_variant():
    assert gpu_variant("H100 SXM") == "SXM"
    assert gpu_variant("H100-PCIe") == "PCIE"
    assert gpu_variant("H100 NVL") == "NVL"
    assert gpu_variant("B200") == "UNKNOWN"


def _obs(**kw):
    base = dict(
        ts_observed=datetime.fromisoformat("2026-10-05T17:00:00+00:00"),
        provider="p",
        gpu_model="H100",
        config="1x H100",
        price_usd_per_gpu_hour=2.0,
        term="on_demand",
        region=None,
        availability="available",
        source="s",
        snapshot_id="s_x",
    )
    base.update(kw)
    return PriceObservation(**base)


def test_observation_requires_aware_timestamp():
    with pytest.raises(ValidationError):
        _obs(ts_observed=datetime(2026, 10, 5, 17))  # noqa: DTZ001


def test_observation_rejects_bad_price():
    with pytest.raises(ValidationError):
        _obs(price_usd_per_gpu_hour=0.0)


def test_observation_rejects_unknown_field():
    with pytest.raises(ValidationError):
        _obs(secret="x")


def test_strip_sensitive():
    out = strip_sensitive({"public_ipaddr": "1.2.3.4", "hostname": "h", "gpu_name": "H100"})
    assert out == {"gpu_name": "H100"}
