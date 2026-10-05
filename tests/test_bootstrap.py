import numpy as np

from compute_curve.backtest.bootstrap import (
    block_bootstrap_ci,
    circular_block_indices,
    paired_loss_difference_ci,
)


def test_indices_shape_and_range():
    rng = np.random.default_rng(0)
    idx = circular_block_indices(17, 5, rng)
    assert idx.shape == (17,)
    assert idx.min() >= 0 and idx.max() < 17


def test_ci_is_reproducible_and_covers_mean():
    x = np.random.default_rng(3).normal(1.0, 1.0, 500)
    a = block_bootstrap_ci(x, np.mean, n_boot=500, seed=7)
    b = block_bootstrap_ci(x, np.mean, n_boot=500, seed=7)
    assert a == b
    assert a[0] < 1.0 < a[1]


def test_paired_difference_detects_better_model():
    rng = np.random.default_rng(5)
    base = rng.normal(2.0, 0.3, 300) ** 2
    model = base * 0.5
    mean, (lo, hi) = paired_loss_difference_ci(model, base, n_boot=500)
    assert mean < 0 and hi < 0
