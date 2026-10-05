from datetime import UTC, datetime

import numpy as np
import pandas as pd
import pytest

from compute_curve.index.own_index import (
    build_daily_index,
    provider_weights,
    trimmed_mean,
    weighted_median,
)


def test_weighted_median_equal_weights_matches_median():
    rng = np.random.default_rng(1)
    for n in (1, 2, 3, 10, 11):
        x = rng.normal(size=n)
        assert weighted_median(x, np.ones(n)) == pytest.approx(np.median(x))


def test_weighted_median_respects_weights():
    assert weighted_median([1.0, 2.0, 3.0], [0.1, 0.1, 0.8]) == 3.0


def test_provider_weights_sum_to_one_per_provider():
    w = provider_weights(["a", "a", "a", "b"])
    assert w.tolist() == pytest.approx([1 / 3, 1 / 3, 1 / 3, 1.0])


def test_trimmed_mean():
    assert trimmed_mean([1, 2, 3, 4, 100], 0.2) == pytest.approx(3.0)


def _obs(provider, price, ts, model="H100", variant="SXM", term="on_demand", avail="available"):
    return {
        "ts_observed": ts,
        "provider": provider,
        "gpu_model": model,
        "gpu_variant": variant,
        "price_usd_per_gpu_hour": price,
        "term": term,
        "availability": avail,
        "source": provider,
        "snapshot_id": f"{provider}_{ts:%H}",
        "is_synthetic": False,
    }


def test_marketplace_cannot_outvote(cfg):
    ts = datetime(2026, 10, 5, 12, tzinfo=UTC)
    rows = [_obs("market", 1.0, ts) for _ in range(50)]
    rows += [_obs("p2", 3.0, ts), _obs("p3", 3.2, ts)]
    idx = build_daily_index(pd.DataFrame(rows), cfg.index, gpu_models=["H100"])
    assert len(idx) == 1
    # Three providers with weight 1 each: the weighted median is p2's 3.0, not 1.0.
    assert idx.iloc[0]["value"] == pytest.approx(3.0)
    assert idx.iloc[0]["n_providers"] == 3
    assert bool(idx.iloc[0]["meets_coverage"])


def test_only_latest_snapshot_per_day_and_filters(cfg):
    early = datetime(2026, 10, 5, 1, tzinfo=UTC)
    late = datetime(2026, 10, 5, 20, tzinfo=UTC)
    rows = [
        _obs("a", 9.0, early),
        _obs("a", 2.0, late),
        _obs("b", 2.2, late),
        _obs("b", 0.5, late, term="spot"),
        _obs("b", 0.6, late, avail="unavailable"),
    ]
    idx = build_daily_index(pd.DataFrame(rows), cfg.index, gpu_models=["H100"])
    assert idx.iloc[0]["n_listings"] == 2
    assert idx.iloc[0]["value"] == pytest.approx(2.1)
    assert idx.iloc[0]["ts_available"] == pd.Timestamp(late)
