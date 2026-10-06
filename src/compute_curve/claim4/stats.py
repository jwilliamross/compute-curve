"""Statistics for claim 4 (docs/claim4_plan.md section 6).

Small pure functions: predictive OLS with Newey-West HAC errors, a
circular-shift permutation test, Holm and Benjamini-Hochberg adjustments, a
sign-flip randomization test, the Clark-West (2007) test for nested
forecasts, block-bootstrap correlation intervals and Fisher-z power formulas.

References: Newey and West (1987), Econometrica 55(3); Holm (1979), Scand. J.
Statist. 6(2); Benjamini and Hochberg (1995), JRSS-B 57(1); Clark and West
(2007), J. Econometrics 138(1); Politis and Romano (1992) for the circular
block bootstrap.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

import numpy as np
import statsmodels.api as sm
from scipy import stats as st
from statsmodels.stats.multitest import multipletests

from compute_curve.backtest.bootstrap import circular_block_indices


@dataclass(frozen=True)
class OlsHac:
    n: int
    intercept: float
    slope: float
    slope_se: float
    t_stat: float
    p_value: float


MIN_N_PER_LAG = 3


def enough_for_hac(n: int, lag: int) -> bool:
    """Newey-West needs the lag to be small relative to n; require n >= 3 x lag."""
    return n >= max(4, MIN_N_PER_LAG * max(lag, 1))


def ols_hac(x: np.ndarray, y: np.ndarray, lag: int) -> OlsHac | None:
    """OLS ``y = a + b x`` with Newey-West (Bartlett) errors at ``lag``; t(n-2) p-value.

    Returns None when ``x`` has no variation or there are too few points for
    the lag (:func:`enough_for_hac`).
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = x.size
    if not enough_for_hac(n, lag) or np.ptp(x) == 0:
        return None
    X = sm.add_constant(x, has_constant="add")
    fit = sm.OLS(y, X).fit(cov_type="HAC", cov_kwds={"maxlags": max(0, int(lag))})
    b, se = float(fit.params[1]), float(fit.bse[1])
    t = b / se if se > 0 else float("nan")
    p = float(2 * st.t.sf(abs(t), df=n - 2)) if np.isfinite(t) else float("nan")
    return OlsHac(n, float(fit.params[0]), b, se, float(t), p)


def pearson(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.size < 3 or np.std(x) == 0 or np.std(y) == 0:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def circular_shift_pvalue(x: np.ndarray, y: np.ndarray, min_shift: int) -> tuple[float, int]:
    """Two-sided permutation p-value for corr(x, y) using circular shifts of ``y``.

    Shifts ``k`` run over ``min_shift <= k <= n - min_shift``. Returns
    ``(p, K)`` with ``p = (1 + #{|rho_k| >= |rho|}) / (1 + K)``; ``p = 1`` when
    no shift is possible or the correlation is undefined.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n = x.size
    rho = pearson(x, y)
    shifts = list(range(max(1, min_shift), n - max(1, min_shift) + 1))
    if not np.isfinite(rho) or not shifts:
        return float("nan"), len(shifts)
    null = np.array([pearson(x, np.roll(y, k)) for k in shifts])
    null = null[np.isfinite(null)]
    count = int(np.sum(np.abs(null) >= abs(rho) - 1e-12))
    return float((1 + count) / (1 + null.size)), int(null.size)


def block_bootstrap_corr_ci(
    x: np.ndarray,
    y: np.ndarray,
    block_length: int,
    n_boot: int = 2000,
    confidence: float = 0.95,
    seed: int = 0,
) -> tuple[float, float]:
    """Percentile CI for corr(x, y), resampling (x, y) pairs in circular blocks."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.size < max(4, 2 * block_length):
        # With n < 2 blocks every resample is a rotation of the whole sample and
        # the interval collapses to a point; report none instead.
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    out = np.empty(n_boot)
    for i in range(n_boot):
        idx = circular_block_indices(x.size, block_length, rng)
        out[i] = pearson(x[idx], y[idx])
    out = out[np.isfinite(out)]
    if out.size == 0:
        return (float("nan"), float("nan"))
    a = (1 - confidence) / 2
    lo, hi = np.quantile(out, [a, 1 - a])
    return (float(lo), float(hi))


def holm(pvalues: list[float]) -> list[float]:
    """Holm step-down adjusted p-values over all declared tests.

    A test that could not be computed (NaN) counts as p = 1, so the family
    size stays as declared; its adjusted value is reported as NaN.
    """
    return _adjust(pvalues, "holm")


def benjamini_hochberg(pvalues: list[float]) -> list[float]:
    """Benjamini-Hochberg q-values over all declared tests (NaN counts as p = 1)."""
    return _adjust(pvalues, "fdr_bh")


def _adjust(pvalues: list[float], method: str) -> list[float]:
    p = np.asarray(pvalues, dtype=float)
    ok = np.isfinite(p)
    if not ok.any():
        return [float("nan")] * p.size
    adj = multipletests(np.where(ok, p, 1.0), method=method)[1]
    return [float(a) if k else float("nan") for a, k in zip(adj, ok, strict=True)]


def sign_flip_pvalue(
    values: np.ndarray, n_random: int = 20000, exact_max: int = 16, seed: int = 0
) -> float:
    """Two-sided randomization p-value for mean(values) = 0 under symmetric sign flips."""
    v = np.asarray(values, dtype=float)
    n = v.size
    if n == 0:
        return float("nan")
    obs = abs(v.mean())
    if n <= exact_max:
        signs = np.array(list(product((-1.0, 1.0), repeat=n)))
    else:
        rng = np.random.default_rng(seed)
        signs = rng.choice((-1.0, 1.0), size=(n_random, n))
    means = np.abs((signs * v).mean(axis=1))
    return float(np.mean(means >= obs - 1e-15))


def iid_bootstrap_ci(
    values: np.ndarray, n_boot: int = 2000, confidence: float = 0.95, seed: int = 0
) -> tuple[float, float]:
    """Percentile CI for the mean under an iid bootstrap (events are resampled)."""
    v = np.asarray(values, dtype=float)
    if v.size < 2:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    means = v[rng.integers(0, v.size, size=(n_boot, v.size))].mean(axis=1)
    a = (1 - confidence) / 2
    lo, hi = np.quantile(means, [a, 1 - a])
    return (float(lo), float(hi))


def hac_mean_se(x: np.ndarray, lag: int) -> float:
    """Newey-West standard error of the sample mean of ``x`` (Bartlett weights)."""
    x = np.asarray(x, dtype=float)
    n = x.size
    if n < 2:
        return float("nan")
    e = x - x.mean()
    s = float(e @ e) / n
    for k in range(1, min(lag, n - 1) + 1):
        w = 1.0 - k / (lag + 1.0)
        s += 2.0 * w * float(e[k:] @ e[:-k]) / n
    return float(np.sqrt(max(s, 0.0) / n))


@dataclass(frozen=True)
class ClarkWest:
    n: int
    stat: float
    p_value: float  # one-sided: the model (larger, nested) beats the baseline


def clark_west(
    actual: np.ndarray, model: np.ndarray, baseline: np.ndarray, lag: int
) -> ClarkWest | None:
    """Clark-West adjusted MSPE test; the baseline is nested in the model.

    ``f_t = (y - b)^2 - [(y - m)^2 - (b - m)^2]``; statistic = mean(f) / HAC se.
    """
    y = np.asarray(actual, dtype=float)
    m = np.asarray(model, dtype=float)
    b = np.asarray(baseline, dtype=float)
    if not enough_for_hac(y.size, lag) or y.size < 5:
        return None
    f = (y - b) ** 2 - ((y - m) ** 2 - (b - m) ** 2)
    se = hac_mean_se(f, lag)
    if not np.isfinite(se) or se == 0:
        return ClarkWest(y.size, float("nan"), float("nan"))
    z = float(f.mean() / se)
    return ClarkWest(y.size, z, float(st.norm.sf(z)))


def mde_correlation(n: int, alpha: float, power: float = 0.8) -> float:
    """Smallest correlation detectable with ``n`` points (Fisher z, two-sided)."""
    if n <= 3:
        return float("nan")
    z = st.norm.ppf(1 - alpha / 2) + st.norm.ppf(power)
    return float(np.tanh(z / np.sqrt(n - 3)))


def n_for_correlation(rho: float, alpha: float, power: float = 0.8) -> int:
    """Observations needed to detect correlation ``rho`` (Fisher z, two-sided)."""
    z = st.norm.ppf(1 - alpha / 2) + st.norm.ppf(power)
    return int(np.ceil((z / np.arctanh(rho)) ** 2 + 3))


def annualized_sharpe(per_window: np.ndarray, horizon: int) -> float:
    """Annualized Sharpe of per-window returns; a strategy that never trades scores 0."""
    r = np.asarray(per_window, dtype=float)
    if r.size < 2:
        return float("nan")
    if np.ptp(r) == 0:  # constant: never traded (0) or undefined
        return 0.0 if np.all(r == 0) else float("nan")
    return float(r.mean() / np.std(r, ddof=1) * np.sqrt(252.0 / horizon))
