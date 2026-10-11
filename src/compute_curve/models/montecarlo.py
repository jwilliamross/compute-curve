"""Monte Carlo of monthly-average settlement under Schwartz-Smith (docs/montecarlo_fair_value.md).

Exact simulation of (chi, xi) with correlated shocks and antithetic paths,
arithmetic monthly averages over the averaging days, and a Kemna-Vorst
geometric-average control variate whose expectation is analytic because the
log index is jointly Gaussian over the averaging days.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
import scipy.stats as st

from compute_curve.models.schwartz_smith import SSParams, transition

DAYS_PER_YEAR = 365.0
GPU_HOURS = 730.0


@dataclass(frozen=True)
class State:
    chi: float
    xi: float


def simulate_log_spot(
    p: SSParams,
    x0: State,
    n_days: int,
    n_paths: int,
    seed: int,
    jump_days: Sequence[int] = (),
    t0_years: float = 0.0,
) -> np.ndarray:
    """ln S on days 1..n_days for ``2 * (n_paths // 2)`` antithetic paths (rows)."""
    half = max(n_paths // 2, 1)
    dt = 1.0 / DAYS_PER_YEAR
    rng = np.random.default_rng(seed)
    jd = set(int(j) for j in jump_days)
    c0, g0, w0 = transition(p, dt, False)
    l0 = np.linalg.cholesky(w0)
    a = g0[0, 0]
    chi = np.full(2 * half, x0.chi)
    xi = np.full(2 * half, x0.xi)
    out = np.empty((2 * half, n_days))
    for d in range(1, n_days + 1):
        z = rng.standard_normal((half, 2))
        z = np.vstack([z, -z])
        eps = z @ l0.T
        chi = a * chi + eps[:, 0]
        xi = xi + c0[1] + eps[:, 1]
        if d in jd:
            j = (
                rng.normal(p.jump_mean, p.jump_std, half)
                if p.jump_std > 0
                else np.full(half, p.jump_mean)
            )
            xi = xi + np.concatenate([j, j])
        out[:, d - 1] = -p.delta * (t0_years + d * dt) + chi + xi
    return out


def log_moments(
    p: SSParams,
    x0: State,
    days: Sequence[int],
    jump_days: Sequence[int] = (),
    t0_years: float = 0.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Mean vector and covariance matrix of ln S on ``days`` (days from the known state)."""
    t = np.asarray(days, dtype=float) / DAYS_PER_YEAR
    k, sc, sx, rho = p.kappa, p.sigma_chi, p.sigma_xi, p.rho
    n_j = np.array([sum(1 for j in jump_days if 0 < j <= d) for d in days], dtype=float)
    mean = (
        -p.delta * (t0_years + t)
        + np.exp(-k * t) * x0.chi
        + x0.xi
        + p.mu_xi * t
        + n_j * p.jump_mean
    )
    s, u = np.meshgrid(t, t, indexing="ij")
    lo, hi = np.minimum(s, u), np.maximum(s, u)
    cov_chi = sc**2 * np.exp(-k * (hi - lo)) * (1 - np.exp(-2 * k * lo)) / (2 * k)
    nj_lo = np.minimum.outer(n_j, n_j)
    cov_xi = sx**2 * lo + p.jump_std**2 * nj_lo

    def cross(a_: np.ndarray, b_: np.ndarray) -> np.ndarray:  # Cov(chi_a, xi_b)
        m = np.minimum(a_, b_)
        return rho * sc * sx * np.exp(-k * a_) * (np.exp(k * m) - 1) / k

    cov = cov_chi + cov_xi + cross(s, u) + cross(u, s)
    return mean, cov


def geometric_moments(mean: np.ndarray, cov: np.ndarray) -> tuple[float, float]:
    """Mean and variance of the log geometric average over the averaging days."""
    n = mean.size
    return float(mean.mean()), float(cov.sum() / n**2)


def black_call(m: float, v: float, k: float) -> float:
    """E[(X - K)^+] for ln X ~ N(m, v)."""
    if k <= 0:
        return float(np.exp(m + v / 2) - k)
    sd = np.sqrt(v)
    d1 = (m - np.log(k) + v) / sd
    return float(np.exp(m + v / 2) * st.norm.cdf(d1) - k * st.norm.cdf(d1 - sd))


@dataclass(frozen=True)
class MonthResult:
    label: str
    n_days: int
    analytic_mean: float
    mc_mean: float
    mc_mean_cv: float
    mc_se_plain: float
    mc_se_cv: float
    quantiles: dict[str, float]
    var95_long_per_contract: float  # loss of one long contract bought at the analytic mean
    asian_calls: dict[str, float]


def controlled_mean(x: np.ndarray, g: np.ndarray, g_mean: float) -> tuple[float, float]:
    """Control-variate estimate of E[x] and its standard error."""
    c = float(np.cov(x, g)[0, 1] / np.var(g, ddof=1)) if np.var(g) > 0 else 0.0
    adj = x - c * (g - g_mean)
    return float(adj.mean()), float(adj.std(ddof=1) / np.sqrt(adj.size))


def month_result(
    label: str,
    paths: np.ndarray,
    day_idx: Sequence[int],
    p: SSParams,
    x0: State,
    jump_days: Sequence[int],
    strikes_rel: Sequence[float],
) -> MonthResult:
    """Statistics of the arithmetic average over ``day_idx`` (1-based day numbers)."""
    cols = np.asarray(day_idx, dtype=int) - 1
    logs = paths[:, cols]
    avg = np.exp(logs).mean(axis=1)
    geo = np.exp(logs.mean(axis=1))
    mean, cov = log_moments(p, x0, day_idx, jump_days)
    analytic = float(np.mean(np.exp(mean + 0.5 * np.diag(cov))))
    m_g, v_g = geometric_moments(mean, cov)
    mc_cv, se_cv = controlled_mean(avg, geo, float(np.exp(m_g + v_g / 2)))
    q = np.quantile(avg, [0.05, 0.25, 0.5, 0.75, 0.95])
    calls: dict[str, float] = {}
    for kr in strikes_rel:
        k = kr * analytic
        est, _ = controlled_mean(
            np.maximum(avg - k, 0.0), np.maximum(geo - k, 0.0), black_call(m_g, v_g, k)
        )
        calls[f"{kr:g}"] = est
    return MonthResult(
        label,
        len(cols),
        analytic,
        float(avg.mean()),
        mc_cv,
        float(avg.std(ddof=1) / np.sqrt(avg.size)),
        se_cv,
        {
            f"q{int(x * 100):02d}": float(v)
            for x, v in zip((0.05, 0.25, 0.5, 0.75, 0.95), q, strict=True)
        },
        float(GPU_HOURS * (analytic - q[0])),
        calls,
    )
