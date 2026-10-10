"""Mechanism-check tests (SYNTHETIC panels from compute_curve.synthetic)."""

import numpy as np

from compute_curve.explore import mechanism as mc
from compute_curve.synthetic import synthetic_cgi_panel


def test_trimmed_vote_mean_matches_hand_calculation():
    # 3 seats -> 9 equal votes; the middle third is votes 4..6 = c(2)(0.97), c(2), c(2)(1.03)
    out = mc.trimmed_vote_mean(np.array([[1.0, 2.0, 3.0]]), 0.03)
    votes = np.sort([0.97, 1.0, 1.03, 1.94, 2.0, 2.06, 2.91, 3.0, 3.09])
    assert np.isclose(out[0], votes[3:6].mean())


def test_absent_seats_are_ignored():
    with_nan = mc.trimmed_vote_mean(np.array([[1.0, 2.0, np.nan, 3.0]]), 0.03)
    without = mc.trimmed_vote_mean(np.array([[1.0, 2.0, 3.0]]), 0.03)
    assert np.isclose(with_nan[0], without[0])


def test_transient_seat_deviations_create_reversal_and_random_walks_do_not():
    rw = synthetic_cgi_panel(17, 30, 1)
    tr = synthetic_cgi_panel(17, 30, 1, transient_sd=0.03, sigma_u=0.0005)
    assert rw["is_synthetic"].all() and tr["is_synthetic"].all()
    b_rw = mc.reversal_stats(
        np.log(mc.trimmed_vote_mean(np.exp(rw.iloc[:, :-1].to_numpy()), 0.03))
    )[0]
    b_tr = mc.reversal_stats(
        np.log(mc.trimmed_vote_mean(np.exp(tr.iloc[:, :-1].to_numpy()), 0.03))
    )[0]
    assert b_tr < -0.15 and b_tr < b_rw - 0.1


def test_reversal_stats_on_a_pure_random_walk():
    rng = np.random.default_rng(0)
    beta, vr, _ = mc.reversal_stats(np.cumsum(rng.normal(0, 0.001, 96 * 200)))
    assert abs(beta) < 0.1 and 0.8 < vr < 1.2


def test_verdict_rules():
    assert mc.verdict(-0.02, -0.05).startswith("aggregation and drop-outs alone cannot")
    assert mc.verdict(-0.30, -0.01).startswith("the aggregation rule alone can")
    assert mc.verdict(-0.18, -0.01) == "inconclusive"
