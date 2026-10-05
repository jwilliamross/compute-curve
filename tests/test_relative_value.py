import numpy as np
import pandas as pd
import pytest

from compute_curve.models import relative_value as rv


def test_log_spread_zero_at_parity():
    idx = pd.date_range("2026-01-01", periods=3)
    s = rv.log_spread(pd.Series([5.0] * 3, idx), pd.Series([2.0] * 3, idx), 2.5)
    assert np.allclose(s.to_numpy(), 0.0)
    assert rv.breakeven_ratio(5.0, 2.0) == 2.5


def test_rolling_z_uses_only_past():
    s = pd.Series(np.arange(30, dtype=float))
    z = rv.rolling_z(s, 10)
    s2 = s.copy()
    s2.iloc[25:] = 1e6
    z2 = rv.rolling_z(s2, 10)
    pd.testing.assert_series_equal(z.iloc[:25], z2.iloc[:25])


def test_ar1_beats_random_walk_on_mean_reverting_series():
    rng = np.random.default_rng(0)
    x = np.zeros(600)
    for t in range(1, 600):
        x[t] = 0.8 * x[t - 1] + rng.normal(0, 0.05)
    preds = rv.walk_forward_ar1(pd.Series(x), horizon=5, min_train=100)
    ev = rv.evaluate_spread_forecast(preds, horizon=5, n_boot=300)
    assert ev is not None and ev.ci[1] < 0


def test_ar1_does_not_beat_random_walk_on_random_walk():
    rng = np.random.default_rng(1)
    x = np.cumsum(rng.normal(0, 0.05, 600))
    preds = rv.walk_forward_ar1(pd.Series(x), horizon=5, min_train=100)
    ev = rv.evaluate_spread_forecast(preds, horizon=5, n_boot=300)
    assert ev is not None and not ev.ci[1] < 0


@pytest.mark.parametrize(
    ("z", "cur", "out"),
    [(2.5, 0, -1), (-2.5, 0, 1), (1.0, -1, -1), (0.2, -1, 0), (float("nan"), 1, 1)],
)
def test_fade_signal(z, cur, out):
    assert rv.fade_signal(z, 2.0, 0.5, cur) == out


def test_hedge_contracts():
    assert rv.hedge_contracts(2, 5.5, 2.2) == 5
