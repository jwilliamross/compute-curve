import numpy as np
import pytest

from compute_curve.models.schwartz_smith import (
    SSParams,
    a_tau,
    build_panel_design,
    expected_average_level,
    fit_panel,
    fit_spot_only,
    forecast_log_spot,
    futures_log_price,
    kalman_filter,
    panel_measurement,
    spot_loglik,
    spot_measurement,
    transition,
)
from compute_curve.synthetic import simulate_ss_path

DT = 1 / 365
TRUE = SSParams(
    kappa=4.0,
    sigma_chi=0.5,
    sigma_xi=0.2,
    rho=0.3,
    mu_xi=-0.15,
    mu_xi_star=-0.2,
    lambda_chi=0.1,
    meas_std=0.005,
)


def test_a_tau_zero_at_zero():
    assert a_tau(TRUE, 0.0) == pytest.approx(0.0)


def test_futures_converge_to_spot_at_expiry():
    assert futures_log_price(TRUE, 0.2, 0.7, 0.0) == pytest.approx(0.9)


def test_long_maturity_limit_slope():
    # For large tau, d ln F / d tau -> mu* + sigma_xi^2 / 2.
    slope = (a_tau(TRUE, 30.0) - a_tau(TRUE, 29.0)).item()
    assert slope == pytest.approx(TRUE.mu_xi_star + 0.5 * TRUE.sigma_xi**2, rel=1e-6)


def test_jump_adds_mean_and_convexity():
    p = SSParams(jump_mean=-0.1, jump_std=0.2)
    base = futures_log_price(p, 0.0, 0.0, 0.5, n_jumps=0)
    jumped = futures_log_price(p, 0.0, 0.0, 0.5, n_jumps=1)
    assert jumped - base == pytest.approx(-0.1 + 0.5 * 0.04)


def test_transition_covariance_psd():
    _, _, W = transition(TRUE, DT, jump=True)
    assert np.all(np.linalg.eigvalsh(W) > 0)


def test_fast_spot_loglik_matches_general_filter():
    chi, xi = simulate_ss_path(TRUE, 400, 0.1, np.log(2.0), seed=3)
    y = chi + xi + np.random.default_rng(9).normal(0, 0.01, 400)
    y[50:55] = np.nan
    jumps = [i == 200 for i in range(400)]
    p = SSParams(kappa=3.0, sigma_chi=0.4, sigma_xi=0.1, rho=0.1, delta=0.2, jump_std=0.1)
    yy, d, Z = spot_measurement(y, np.arange(400) * DT, p.delta)
    general = kalman_filter(yy, d, Z, p, DT, jumps).loglik
    assert spot_loglik(y, p, DT, jumps=jumps) == pytest.approx(general, rel=1e-10)


def test_spot_fit_refuses_short_history():
    assert fit_spot_only(np.log(np.full(50, 2.0)), DT, min_observations=180) is None


def _panel(T, n, seed):
    chi, xi = simulate_ss_path(TRUE, T, 0.1, np.log(2.0), seed=seed)
    ty = np.arange(T) * DT
    cells = []
    for t in range(T):
        for j in range(n):
            start = 30 * (j + 1) - (t % 30)
            cells.append((t, j, np.arange(start, start + 30) / 365, np.zeros(30)))
    des = build_panel_design(ty, cells, n)
    d, Z = panel_measurement(TRUE, des)
    x = np.stack([chi, xi], 1)
    rng = np.random.default_rng(seed + 1)
    y = d + np.einsum("tnk,tk->tn", Z, x) + rng.normal(0, TRUE.meas_std, (T, n))
    return y, des


def test_panel_loglik_prefers_truth():
    y, des = _panel(200, 4, seed=5)
    d, Z = panel_measurement(TRUE, des)
    ll_true = kalman_filter(y, d, Z, TRUE, DT).loglik
    wrong = SSParams(kappa=1.0, sigma_chi=0.2, sigma_xi=0.4, rho=-0.3, meas_std=0.02)
    d2, Z2 = panel_measurement(wrong, des)
    assert ll_true > kalman_filter(y, d2, Z2, wrong, DT).loglik + 50


@pytest.mark.slow
def test_panel_fit_recovers_identified_parameters():
    y, des = _panel(300, 4, seed=3)
    fit = fit_panel(y, des, DT, base=SSParams(), min_observations=100, maxiter=3000)
    assert fit is not None
    assert fit.params.kappa == pytest.approx(TRUE.kappa, rel=0.25)
    assert fit.params.sigma_chi == pytest.approx(TRUE.sigma_chi, rel=0.2)
    assert fit.params.sigma_xi == pytest.approx(TRUE.sigma_xi, rel=0.3)
    assert fit.params.mu_xi_star == pytest.approx(TRUE.mu_xi_star, abs=0.05)


def test_forecast_variance_grows_and_average_level():
    x = np.array([0.0, np.log(2.0)])
    P = np.zeros((2, 2))
    m, v = forecast_log_spot(TRUE, x, P, 0.0, [1, 10, 30], DT, jump_days=[])
    assert np.all(np.diff(v) > 0)
    assert expected_average_level(np.array([0.0, 0.0]), np.array([0.0, 0.0])) == 1.0
