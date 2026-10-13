"""Round 6 statistics on small hand-made series (no real data)."""

import numpy as np
import pandas as pd

from compute_curve.explore.round6 import (
    finish,
    monthly_stock_excess,
    ols_slope_test,
    r601,
    r602,
    r603,
    ratio_series,
)


def test_slope_test_finds_a_planted_slope_and_respects_direction() -> None:
    rng = np.random.default_rng(1)
    x = rng.normal(0, 1, 40)
    y = 0.8 * x + rng.normal(0, 0.5, 40)
    up = ols_slope_test(x, y, lag=1, sign=1)
    assert abs(up["slope"] - 0.8) < 0.3 and up["p_one_sided"] < 0.01
    assert ols_slope_test(x, y, lag=1, sign=-1)["p_one_sided"] > 0.99
    assert ols_slope_test(x[:5], y[:5], 1, 1)["verdict"] == "too little history to conclude"


def _months(n: int) -> pd.DatetimeIndex:
    return pd.date_range("2024-01-31", periods=n, freq="ME", tz="UTC")


def test_r601_detects_mean_reversion_in_a_planted_ratio() -> None:
    rng = np.random.default_rng(2)
    v = np.zeros(40)
    for t in range(1, 40):
        v[t] = 0.5 * v[t - 1] + rng.normal(0, 0.1)
    r = r601(pd.Series(v + 0.6, index=_months(40)))
    assert r["slope"] < 0 and r["p_one_sided"] < 0.05


def test_ratio_uses_only_providers_with_both() -> None:
    idx = _months(2)
    h = pd.DataFrame({"a": [2.0, 2.0], "b": [np.nan, 3.0]}, index=idx)
    b = pd.DataFrame({"a": [4.0, 4.0], "b": [6.0, np.nan]}, index=idx)
    assert np.allclose(ratio_series(h, b), np.log(2.0))


def test_monthly_excess_is_member_mean_minus_benchmark() -> None:
    idx = pd.to_datetime(["2024-01-30", "2024-01-31", "2024-02-28", "2024-02-29"])
    closes = pd.DataFrame(
        {"A": [1.0, 10.0, 11.0, 11.0], "B": [1.0, 20.0, 20.0, 24.0], "X": [1.0, 100, 100, 101]},
        index=idx,
    )
    ex = monthly_stock_excess(closes, ["A", "B"], "X")
    assert len(ex) == 1 and abs(ex.iloc[0] - ((0.1 + 0.2) / 2 - 0.01)) < 1e-12


def test_r602_aligns_signal_month_with_next_month_return() -> None:
    idx = _months(30)
    rng = np.random.default_rng(3)
    lp = np.cumsum(rng.normal(0, 0.05, 30))
    med = pd.Series(lp, index=idx)
    # excess in month k = 2 x the price change from k-2 to k-1 (the signal month k-1)
    sig = np.r_[np.nan, np.nan, 2.0 * np.diff(lp)[:-1]] + rng.normal(0, 0.02, 30)
    ex = pd.Series(sig, index=idx.tz_localize(None))
    r = r602(med, ex.dropna())
    assert r["slope"] > 1.5 and r["p_one_sided"] < 0.01


def test_r603_beats_random_walk_on_a_planted_ar1() -> None:
    rng = np.random.default_rng(4)
    d = np.zeros(60)
    for t in range(1, 60):
        d[t] = 0.7 * d[t - 1] + rng.normal(0, 0.02)
    med = pd.Series(np.cumsum(d), index=pd.date_range("2021-01-31", periods=60, freq="ME"))
    r = r603(med)
    assert r["mse_model"] < r["mse_random_walk"] and r["p_one_sided"] < 0.05


def test_finish_holm_counts_three_tests_even_if_one_cannot_run() -> None:
    t = {"R6-01": {"n": 5, "verdict": "too little"}, "R6-02": {"p_one_sided": 0.02},
         "R6-03": {"p_one_sided": 0.04}}  # fmt: skip
    finish(t)
    assert t["R6-02"]["p_holm"] == 0.06 and t["R6-02"]["verdict"] == "not confirmed"
