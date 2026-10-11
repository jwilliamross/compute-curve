"""Monte Carlo engine checks against closed forms (no data, fixed seeds)."""

from datetime import date

import numpy as np
import pandas as pd
import pytest

from compute_curve.config import load_config
from compute_curve.fairvalue import fit_long_term, fit_short_term, strip
from compute_curve.models import montecarlo as mc
from compute_curve.models.schwartz_smith import SSParams

P = SSParams(
    kappa=6.0, sigma_chi=0.4, sigma_xi=0.25, rho=0.3, mu_xi=-0.2, jump_mean=-0.05, jump_std=0.04
)
X0 = mc.State(chi=0.1, xi=np.log(3.0))


def test_simulated_moments_match_the_closed_form():
    days = [5, 30, 90]
    paths = mc.simulate_log_spot(P, X0, 90, 40000, seed=1, jump_days=[20])
    mean, cov = mc.log_moments(P, X0, days, jump_days=[20])
    sample = paths[:, np.array(days) - 1]
    assert np.allclose(sample.mean(axis=0), mean, atol=0.005)
    assert np.allclose(np.cov(sample.T), cov, rtol=0.05, atol=2e-4)


def test_control_variate_is_unbiased_and_sharper():
    paths = mc.simulate_log_spot(P, X0, 70, 20000, seed=2)
    res = mc.month_result("m", paths, list(range(40, 62)), P, X0, [], [1.0])
    assert abs(res.mc_mean - res.analytic_mean) < 4 * res.mc_se_plain
    assert abs(res.mc_mean_cv - res.analytic_mean) < 4 * res.mc_se_cv + 1e-4
    assert res.mc_se_cv < 0.2 * res.mc_se_plain
    assert res.quantiles["q05"] < res.quantiles["q50"] < res.quantiles["q95"]


def test_black_call_matches_simulation():
    rng = np.random.default_rng(3)
    m, v, k = 1.0, 0.09, 2.8
    x = np.exp(rng.normal(m, np.sqrt(v), 400000))
    assert mc.black_call(m, v, k) == pytest.approx(np.maximum(x - k, 0).mean(), rel=0.01)


def test_asian_calls_fall_with_strike_and_var_is_positive():
    paths = mc.simulate_log_spot(P, X0, 60, 10000, seed=4)
    res = mc.month_result("m", paths, list(range(30, 52)), P, X0, [], [0.9, 1.0, 1.1])
    c = res.asian_calls
    assert c["0.9"] > c["1"] > c["1.1"] > 0
    assert res.var95_long_per_contract > 0


def test_seed_reproducibility():
    a = mc.simulate_log_spot(P, X0, 10, 100, seed=7)
    b = mc.simulate_log_spot(P, X0, 10, 100, seed=7)
    assert np.array_equal(a, b)


def test_short_term_calibration_recovers_a_known_half_life():
    true = SSParams(kappa=np.log(2) / 3 * 365, sigma_chi=0.6, sigma_xi=1e-4)  # half-life 3 days
    path = mc.simulate_log_spot(true, mc.State(0.0, 0.0), 400, 2, seed=5)[0]
    fit = fit_short_term(pd.Series(path), seed=1, n_boot=300)
    assert fit is not None and 1.5 < fit.half_life_days < 6
    assert fit.half_life_ci[0] < fit.half_life_days < fit.half_life_ci[1]
    lt = fit_long_term(pd.Series(np.cumsum(np.full(60, -0.01))))
    assert lt is not None and lt.mu_xi == pytest.approx(-0.52)


def test_strip_uses_future_business_days_only():
    spec = load_config().contracts["GPU1"]
    res = strip(spec, P, mc.State(0.0, 0.0), date(2026, 10, 14), 3, 2000, seed=1)
    assert [r.label for r in res] == ["2026-10", "2026-11", "2026-12"]
    assert res[0].n_days == 12  # business days 15..30 October 2026 (the 31st is a Saturday)
