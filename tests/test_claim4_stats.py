"""Claim-4 statistics against known answers and statsmodels."""

from __future__ import annotations

import numpy as np
import pytest
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

from compute_curve.claim4 import stats as cs


def test_holm_and_bh_count_uncomputable_tests_as_p_one():
    p = [0.01, 0.04, float("nan"), 0.03]
    as_one = [0.01, 0.04, 1.0, 0.03]
    h, q = cs.holm(p), cs.benjamini_hochberg(p)
    assert np.isnan(h[2]) and np.isnan(q[2])
    exp_h = multipletests(as_one, method="holm")[1]
    exp_q = multipletests(as_one, method="fdr_bh")[1]
    assert [h[0], h[1], h[3]] == pytest.approx([exp_h[0], exp_h[1], exp_h[3]])
    assert [q[0], q[1], q[3]] == pytest.approx([exp_q[0], exp_q[1], exp_q[3]])
    # dropping the NaN would have been less conservative
    assert h[0] > multipletests([0.01, 0.04, 0.03], method="holm")[1][0]


def test_ols_hac_matches_statsmodels():
    rng = np.random.default_rng(0)
    x = rng.normal(size=120)
    y = 0.6 * x + rng.normal(size=120)
    res = cs.ols_hac(x, y, lag=3)
    fit = sm.OLS(y, sm.add_constant(x)).fit(cov_type="HAC", cov_kwds={"maxlags": 3})
    assert res is not None
    assert res.slope == pytest.approx(fit.params[1])
    assert res.slope_se == pytest.approx(fit.bse[1])
    assert 0 <= res.p_value < 0.05


def test_ols_hac_refuses_a_constant_signal():
    assert cs.ols_hac(np.zeros(10), np.arange(10.0), 1) is None


def test_permutation_detects_strong_link_and_not_independence():
    rng = np.random.default_rng(1)
    x = rng.normal(size=200)
    p, k = cs.circular_shift_pvalue(x, 0.8 * x + rng.normal(size=200), 1)
    assert p < 0.01 and k == 199
    p2, _ = cs.circular_shift_pvalue(x, rng.normal(size=200), 1)
    assert p2 > 0.05


def test_permutation_resolution_is_limited_by_sample_size():
    rng = np.random.default_rng(2)
    x = rng.normal(size=32)
    p, k = cs.circular_shift_pvalue(x, x, 1)
    assert k == 31 and p == pytest.approx(1 / 32)


def test_sign_flip_exact_enumeration():
    assert cs.sign_flip_pvalue(np.ones(5)) == pytest.approx(2 / 32)
    assert cs.sign_flip_pvalue(np.array([1.0, -1.0])) == pytest.approx(1.0)


def test_clark_west_rewards_real_predictability_only():
    rng = np.random.default_rng(3)
    x = rng.normal(size=500)
    y = 0.5 * x + rng.normal(size=500)
    good = cs.clark_west(y, 0.5 * x, np.zeros(500), lag=1)
    assert good is not None and good.p_value < 0.01
    noise = cs.clark_west(rng.normal(size=500), 0.5 * rng.normal(size=500), np.zeros(500), lag=1)
    assert noise is not None and noise.p_value > 0.05


def test_power_formulas_are_consistent():
    assert cs.mde_correlation(32, 0.05) == pytest.approx(0.48, abs=0.01)
    n = cs.n_for_correlation(0.2, 0.05)
    assert cs.mde_correlation(n, 0.05) <= 0.2 < cs.mde_correlation(n - 2, 0.05)


def test_hac_mean_se_reduces_to_iid_without_lags():
    x = np.random.default_rng(4).normal(size=400)
    assert cs.hac_mean_se(x, 0) == pytest.approx(np.std(x) / np.sqrt(x.size))


def test_hac_and_clark_west_need_enough_windows_for_the_lag():
    rng = np.random.default_rng(5)
    x = rng.normal(size=13)
    y = x + rng.normal(size=13)
    assert cs.ols_hac(x, y, lag=20) is None
    assert cs.ols_hac(x, y, lag=1) is not None
    assert cs.clark_west(y, x, np.zeros(13), lag=20) is None


def test_block_interval_needs_two_blocks():
    rng = np.random.default_rng(6)
    x = rng.normal(size=13)
    lo, hi = cs.block_bootstrap_corr_ci(x, x + rng.normal(size=13), block_length=20, n_boot=50)
    assert np.isnan(lo) and np.isnan(hi)


def test_permutation_without_any_shift_is_unavailable():
    x = np.arange(13.0)
    p, k = cs.circular_shift_pvalue(x, x[::-1].copy(), 20)
    assert k == 0 and np.isnan(p)


def test_a_strategy_that_never_trades_has_zero_sharpe():
    assert cs.annualized_sharpe(np.zeros(10), 1) == 0.0
    assert np.isnan(cs.annualized_sharpe(np.full(10, 0.01), 1))
