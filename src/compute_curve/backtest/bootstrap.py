"""Block bootstrap confidence intervals for dependent (time-series) data.

Circular block bootstrap (Politis and Romano, 1992): resample blocks of
``block_length`` consecutive observations, wrapping around the end, until
the resample has the original length. Percentile intervals. Fixed seed.
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np


def circular_block_indices(n: int, block_length: int, rng: np.random.Generator) -> np.ndarray:
    """Indices of one circular block-bootstrap resample of length ``n``."""
    if n <= 0:
        raise ValueError("n must be positive")
    b = max(1, min(block_length, n))
    n_blocks = int(np.ceil(n / b))
    starts = rng.integers(0, n, size=n_blocks)
    idx = (starts[:, None] + np.arange(b)[None, :]) % n
    return idx.ravel()[:n]


def bootstrap_distribution(
    x: np.ndarray,
    stat: Callable[[np.ndarray], float],
    n_boot: int = 2000,
    block_length: int = 5,
    seed: int = 0,
) -> np.ndarray:
    """Bootstrap distribution of ``stat`` under the circular block bootstrap."""
    arr = np.asarray(x, dtype=float)
    rng = np.random.default_rng(seed)
    out = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        out[i] = stat(arr[circular_block_indices(arr.size, block_length, rng)])
    return out


def block_bootstrap_ci(
    x: np.ndarray,
    stat: Callable[[np.ndarray], float],
    n_boot: int = 2000,
    block_length: int = 5,
    confidence: float = 0.95,
    seed: int = 0,
) -> tuple[float, float]:
    """Percentile confidence interval for ``stat(x)``."""
    dist = bootstrap_distribution(x, stat, n_boot=n_boot, block_length=block_length, seed=seed)
    dist = dist[np.isfinite(dist)]
    if dist.size == 0:
        return (float("nan"), float("nan"))
    alpha = (1.0 - confidence) / 2.0
    lo, hi = np.quantile(dist, [alpha, 1.0 - alpha])
    return (float(lo), float(hi))


def paired_loss_difference_ci(
    loss_model: np.ndarray,
    loss_baseline: np.ndarray,
    n_boot: int = 2000,
    block_length: int = 5,
    confidence: float = 0.95,
    seed: int = 0,
) -> tuple[float, tuple[float, float]]:
    """Mean of ``loss_model - loss_baseline`` and its block-bootstrap CI.

    A model beats the baseline out of sample only if the whole interval lies
    below zero.
    """
    d = np.asarray(loss_model, float) - np.asarray(loss_baseline, float)
    ci = block_bootstrap_ci(d, np.mean, n_boot, block_length, confidence, seed)
    return float(d.mean()), ci
