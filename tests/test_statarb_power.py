"""Forward-test power calculation (statarb.power). Random arrays only; no real data."""

import numpy as np
import pandas as pd
import pytest

from compute_curve.claim4 import stats as cs
from compute_curve.statarb.pipeline import EXTENDED_SESSIONS, FORWARD_START, forward_window
from compute_curve.statarb.power import (
    ACCOUNTINGS,
    Series,
    dependence,
    forward_rule,
    holm,
    pass_probability,
)


def _book(mean: float, n: int, seed: int, stress_gap: float = 1e-4) -> list[Series]:
    rng = np.random.default_rng(seed)
    out = []
    for strat in ("SA2-M", "SA2-L"):
        for acc in ACCOUNTINGS:
            x = rng.normal(0.0, 0.01, n)
            x = x - x.mean() + mean  # exact sample mean
            out.append(Series(strat, acc, x, x - stress_gap))
    return out


def test_holm_matches_claim4_holm() -> None:
    rng = np.random.default_rng(1)
    for _ in range(100):
        p = list(rng.uniform(0, 0.3, rng.integers(1, 6)))
        assert np.allclose(holm(p), cs.holm(p))


def test_forward_rule_needs_both_accountings() -> None:
    strong = _book(0.01, 60, 2)
    assert forward_rule(strong, 10, 0.05) == {"SA2-M": True, "SA2-L": True}
    weak_shares = [
        Series(s.strategy, s.accounting, -s.base, -s.stress)
        if s.strategy == "SA2-M" and s.accounting == "shares"
        else s
        for s in strong
    ]
    assert forward_rule(weak_shares, 10, 0.05) == {"SA2-M": False, "SA2-L": True}


def test_forward_rule_needs_positive_stress_mean() -> None:
    book = _book(0.01, 60, 3, stress_gap=0.02)
    assert forward_rule(book, 10, 0.05) == {"SA2-M": False, "SA2-L": False}


def test_pass_probability_is_small_without_edge_and_large_with_one() -> None:
    book = _book(0.004, 157, 4)  # daily Sharpe 0.4: a strong planted edge
    null = pass_probability(book, 60, 0.0, 300, 20, 10, 0.05, 5)
    full = pass_probability(book, 60, 1.0, 300, 20, 10, 0.05, 5)
    assert max(null.values()) < 0.1
    assert min(full.values()) > 0.8


def test_pass_probability_rises_with_length() -> None:
    book = _book(0.0015, 157, 6)
    short = pass_probability(book, 60, 1.0, 300, 20, 10, 0.05, 7)
    long = pass_probability(book, 250, 1.0, 300, 20, 10, 0.05, 7)
    assert long["SA2-M"] > short["SA2-M"]


def test_pass_probability_rejects_misaligned_series() -> None:
    book = _book(0.001, 50, 8)
    bad = [*book[:-1], Series("SA2-L", "shares", np.zeros(49), np.zeros(49))]
    with pytest.raises(ValueError, match="aligned"):
        pass_probability(bad, 60, 1.0, 10, 20, 10, 0.05, 9)


def test_dependence_detects_negative_autocorrelation() -> None:
    rng = np.random.default_rng(10)
    e = rng.normal(0, 0.01, 2001)
    x = 0.001 + e[1:] - 0.6 * e[:-1]  # MA(1), negative lag-1 autocorrelation
    d = dependence(x, 10)
    assert d["sum_autocorr"] < -0.3
    assert d["t_hac"] > d["t_iid"]


def test_extended_forward_window_has_its_own_length() -> None:
    sessions = pd.bdate_range("2026-09-01", periods=400)
    win = forward_window(sessions, EXTENDED_SESSIONS)
    assert win is not None and win[0] == FORWARD_START
    assert len(pd.bdate_range(win[0], win[1])) == EXTENDED_SESSIONS
    assert forward_window(pd.bdate_range(FORWARD_START, periods=249), EXTENDED_SESSIONS) is None
