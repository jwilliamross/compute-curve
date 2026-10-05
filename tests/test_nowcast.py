from datetime import date, timedelta

import numpy as np
import pandas as pd
import pytest

from compute_curve.models import nowcast as nc
from compute_curve.paper.market import MarketData
from compute_curve.synthetic import synthetic_config
from compute_curve.timeutil import end_of_day_utc
from tests.helpers import index_frame


def _own_frame(values, model="H100"):
    days = sorted(values)
    df = pd.DataFrame({"as_of_date": days, "gpu_model": model, "value": [values[d] for d in days]})
    df["meets_coverage"] = True
    df["ts_available"] = pd.to_datetime(df["as_of_date"]).dt.tz_localize("UTC") + pd.Timedelta(
        hours=18
    )
    df["is_synthetic"] = True
    return df


def _path(start, n, seed):
    rng = np.random.default_rng(seed)
    lv = np.cumsum(rng.normal(0, 0.02, n)) + np.log(2.0)
    return {start + timedelta(days=i): float(np.exp(v)) for i, v in enumerate(lv)}


@pytest.fixture
def spec(cfg):
    """Calendar-day averaging keeps the hand calculations below simple."""
    s = synthetic_config(cfg).contracts["GPU1"]
    return s.model_copy(update={"settlement_days": "calendar"})


@pytest.fixture
def bspec(cfg):
    """Business-day averaging, as in the filed contract rules."""
    return synthetic_config(cfg).contracts["GPU1"]


def test_business_day_averaging(bspec):
    pub = {date(2026, 11, d): float(d) for d in range(1, 11)}
    md = MarketData.build(published_index=index_frame(pub))
    view = md.view(end_of_day_utc(date(2026, 11, 10)))  # knows 1..9
    inp = nc.gather_inputs(view, bspec, "H100", date(2026, 11, 1))
    # Business days 2-6 and 9 of November 2026 are known; 1, 7, 8 are weekend days.
    assert sorted(d.day for d in inp.known.index) == [2, 3, 4, 5, 6, 9]
    assert len(inp.averaging_days) == 21
    assert nc.predict_mtd_carry(inp) == pytest.approx((2 + 3 + 4 + 5 + 6 + 9) / 6)


def test_baselines_by_hand(spec):
    pub = {date(2026, 11, d): float(d) for d in range(1, 11)}  # 1..10
    md = MarketData.build(published_index=index_frame(pub))
    view = md.view(end_of_day_utc(date(2026, 11, 10)))  # lag 1: knows 1..9
    inp = nc.gather_inputs(view, spec, "H100", date(2026, 11, 1))
    assert len(inp.known) == 9
    assert nc.predict_mtd_carry(inp) == pytest.approx(5.0)
    assert nc.predict_last_value(inp) == pytest.approx((45 + 21 * 9) / 30)


def test_own_bridge_scales_last_value(spec):
    pub = {date(2026, 11, d): 2.0 for d in range(1, 11)}
    own = {date(2026, 11, d): 1.0 for d in range(1, 10)} | {date(2026, 11, 10): 1.1}
    md = MarketData.build(published_index=index_frame(pub), own_index=_own_frame(own))
    view = md.view(end_of_day_utc(date(2026, 11, 10)))
    inp = nc.gather_inputs(view, spec, "H100", date(2026, 11, 1))
    assert nc.own_bridge_level(inp) == pytest.approx(2.2)
    assert nc.predict_own_bridge(inp) == pytest.approx((9 * 2.0 + 21 * 2.2) / 30)


def test_predictions_ignore_future_data(spec):
    pub = _path(date(2026, 9, 1), 120, seed=1)
    own = _path(date(2026, 9, 1), 120, seed=2)
    md = MarketData.build(published_index=index_frame(pub), own_index=_own_frame(own))
    pub2 = {d: (v * 3 if d > date(2026, 11, 12) else v) for d, v in pub.items()}
    own2 = {d: (v * 3 if d > date(2026, 11, 12) else v) for d, v in own.items()}
    md2 = MarketData.build(published_index=index_frame(pub2), own_index=_own_frame(own2))
    t = end_of_day_utc(date(2026, 11, 12))
    a = nc.nowcast_all(md.view(t), spec, "H100", date(2026, 11, 1))
    b = nc.nowcast_all(md2.view(t), spec, "H100", date(2026, 11, 1))
    assert a == b


def test_perfect_own_index_beats_baselines(spec):
    pub = _path(date(2026, 1, 1), 300, seed=4)
    md = MarketData.build(published_index=index_frame(pub), own_index=_own_frame(pub))
    months = [date(2026, m, 1) for m in range(3, 10)]
    errs = nc.evaluate(md, spec, "H100", months)
    assert set(errs["method"]) == set(nc.METHODS)
    mse = (errs.assign(se=errs["log_error"] ** 2)).groupby("method")["se"].mean()
    assert mse["own_bridge"] < mse["last_value"] < mse["mtd_carry"] * 1.5
    res = nc.cluster_bootstrap_diff(errs, "own_bridge", "last_value", n_boot=300)
    assert res["n_months"] == 7
    assert res["ci_high"] < 0


def test_uninformative_own_index_is_not_validated(spec):
    pub = _path(date(2026, 1, 1), 300, seed=4)
    noise = _path(date(2026, 1, 1), 300, seed=99)
    md = MarketData.build(published_index=index_frame(pub), own_index=_own_frame(noise))
    errs = nc.evaluate(md, spec, "H100", [date(2026, m, 1) for m in range(3, 10)])
    res = nc.cluster_bootstrap_diff(errs, "own_bridge", "last_value", n_boot=300)
    assert not res["ci_high"] < 0
