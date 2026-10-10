"""Statistics for claim 6: Sharpe inference, the pooled region, Monte Carlo checks.

Sharpe inference follows the non-IID formulas in
``.claude/skills/sharpe-ratio-non-iid-corrections`` (Lopez de Prado, Lipton and
Zoonekynd 2026; Bailey and Lopez de Prado 2014 for the deflated Sharpe). SR is
per observation (daily) unless a name says ``annual``.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
import scipy.stats as st

from compute_curve.claim4 import stats as cs
from compute_curve.statarb.engine import TRADING_DAYS

EULER = 0.5772156649015329


# ---------------------------------------------------------------------------
# Sharpe inference (non-IID)
# ---------------------------------------------------------------------------
def ar1_coefficients(rho: float) -> tuple[float, float, float]:
    a = (1 + rho) / (1 - rho)
    b = (1 + rho + rho**2) / (1 - rho**2)
    c = (1 + rho**2) / (1 - rho**2)
    return a, b, c


def sr_variance(sr: float, t: int, skew: float, kurt: float, rho: float) -> float:
    """Eq 2-3: variance of the per-period Sharpe estimate (Pearson kurtosis)."""
    a, b, c = ar1_coefficients(rho)
    return (a - b * skew * sr + c * (kurt - 1) / 4 * sr**2) / t


def psr(sr: float, sr0: float, t: int, skew: float, kurt: float, rho: float) -> float:
    """Eq 9: probability that the true Sharpe exceeds ``sr0`` (sd evaluated at ``sr0``)."""
    v = sr_variance(sr0, t, skew, kurt, rho)
    return float(st.norm.cdf((sr - sr0) / np.sqrt(v))) if v > 0 else float("nan")


def expected_max_sr(var_trials: float, k: int, sr0: float = 0.0) -> float:
    """Eq 28: expected maximum of ``k`` Sharpe estimates under the null."""
    if k < 2 or var_trials <= 0:
        return sr0
    z1 = st.norm.ppf(1 - 1 / k)
    z2 = st.norm.ppf(1 - 1 / (k * np.e))
    return float(sr0 + np.sqrt(var_trials) * ((1 - EULER) * z1 + EULER * z2))


def deflated_sharpe(
    sr: float, trial_srs: list[float], t: int, skew: float, kurt: float, rho: float
) -> float:
    """Eq 29-31: PSR against the expected maximum Sharpe of the trials."""
    k = len(trial_srs)
    sr0 = expected_max_sr(float(np.var(trial_srs, ddof=1)) if k > 1 else 0.0, k)
    return psr(sr, sr0, t, skew, kurt, rho)


@dataclass(frozen=True)
class Moments:
    n: int
    mean: float
    sd: float
    sr: float  # daily
    sr_annual: float
    sr_annual_se: float  # non-IID, annualized
    skew: float
    kurt: float  # Pearson
    rho: float
    effective_n: float


def moments(r: np.ndarray) -> Moments:
    r = np.asarray(r, dtype=float)
    r = r[np.isfinite(r)]
    n = r.size
    if n < 3 or r.std(ddof=1) == 0:
        nan = float("nan")
        return Moments(n, nan, nan, nan, nan, nan, nan, nan, nan, 0.0)
    sd = float(r.std(ddof=1))
    sr = float(r.mean() / sd)
    skew = float(st.skew(r))
    kurt = float(st.kurtosis(r, fisher=False))
    rho = float(np.clip(np.corrcoef(r[:-1], r[1:])[0, 1], -0.9, 0.9))
    se = np.sqrt(max(sr_variance(sr, n, skew, kurt, rho), 0.0)) * np.sqrt(TRADING_DAYS)
    eff = n * (1 - rho) / (1 + rho)
    return Moments(
        n, float(r.mean()), sd, sr, sr * np.sqrt(TRADING_DAYS), float(se), skew, kurt, rho, eff
    )


def hac_p_one_sided(r: np.ndarray, lag: int) -> float:
    """One-sided p that the mean daily return is above zero (Newey-West)."""
    r = np.asarray(r, dtype=float)
    se = cs.hac_mean_se(r, lag)
    if not np.isfinite(se) or se <= 0:
        return float("nan")
    return float(st.t.sf(r.mean() / se, df=r.size - 1))


# ---------------------------------------------------------------------------
# Surface -> region -> pool (quant-research skill)
# ---------------------------------------------------------------------------
def smooth_grid(grid: np.ndarray) -> np.ndarray:
    """Mean over each cell's 3x3 neighbourhood (clipped at the edges)."""
    out = np.empty_like(grid)
    rows, cols = grid.shape
    for i in range(rows):
        for j in range(cols):
            out[i, j] = np.nanmean(grid[max(i - 1, 0) : i + 2, max(j - 1, 0) : j + 2])
    return out


def region(grid_sr_annual: np.ndarray, years: float) -> list[tuple[int, int]]:
    """Cells within one SE of the best smoothed Sharpe, SE = sqrt((1 + S^2/2) / T)."""
    sm = smooth_grid(grid_sr_annual)
    if not np.isfinite(sm).any():
        return []
    best = float(np.nanmax(sm))
    se = np.sqrt((1 + best**2 / 2) / max(years, 1e-9))
    return [tuple(ix) for ix in np.argwhere(sm >= best - se)]  # type: ignore[misc]


def pool(series: list[pd.Series]) -> pd.Series:
    return pd.concat(series, axis=1).mean(axis=1) if series else pd.Series(dtype=float)


# ---------------------------------------------------------------------------
# Monte Carlo
# ---------------------------------------------------------------------------
def max_drawdown(r: np.ndarray) -> float:
    eq = np.cumprod(1 + r)
    return float(np.max(1 - eq / np.maximum.accumulate(eq))) if r.size else 0.0


def drawdown_tail(r: np.ndarray, n_paths: int, block: int, seed: int, q: float = 0.95) -> float:
    """``q`` quantile of the max drawdown over block-bootstrap paths of the same length."""
    r = np.asarray(r, dtype=float)
    n = r.size
    if n < block:
        return float("nan")
    rng = np.random.default_rng(seed)
    n_blocks = int(np.ceil(n / block))
    dd = np.empty(n_paths)
    for k in range(n_paths):
        starts = rng.integers(0, n - block + 1, n_blocks)
        path = np.concatenate([r[s : s + block] for s in starts])[:n]
        dd[k] = max_drawdown(path)
    return float(np.quantile(dd, q))


def cost_breakeven(r_free: np.ndarray, r_base: np.ndarray, base_bps: float) -> float:
    """Stock cost per side (bps) at which the mean net return reaches zero.

    Net return is linear in the per-side cost, so two runs fix the line:
    ``r_free`` with no per-side cost (fees and borrow kept) and ``r_base`` at
    ``base_bps`` (ETF cost scaled in proportion).
    """
    m0, m1 = float(np.mean(r_free)), float(np.mean(r_base))
    if m0 <= m1:
        return float("inf") if m1 > 0 else float("nan")
    return float(base_bps * m0 / (m0 - m1))


def null_percentile(real_sr: float, null_srs: np.ndarray) -> float:
    """Share of random-entry Sharpe ratios below the real one."""
    null_srs = null_srs[np.isfinite(null_srs)]
    return float(np.mean(null_srs < real_sr)) if null_srs.size else float("nan")
