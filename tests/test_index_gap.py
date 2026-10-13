"""Claim 1b gap tests on hand-made series (no Silicon Data values)."""

from datetime import date

import numpy as np
import pandas as pd

from compute_curve.index.gap import align, evaluate, features, near_break, walk_forward


def _days(n: int) -> pd.DatetimeIndex:
    return pd.bdate_range("2026-01-05", periods=n)


def _pair(n: int, lead: bool, seed: int) -> tuple[pd.Series, pd.Series]:
    rng = np.random.default_rng(seed)
    lj = np.cumsum(rng.normal(0, 0.01, n))
    li = np.r_[np.zeros(5), lj[:-5]] if lead else np.cumsum(rng.normal(0, 0.01, n))
    li = li + rng.normal(0, 0.002, n)
    d = _days(n)
    return pd.Series(np.exp(1.0 + li), index=d), pd.Series(np.exp(1.2 + lj), index=d)


def test_lead_lag_is_detected_when_sd_follows_our_index() -> None:
    sd, own = _pair(200, lead=True, seed=1)
    feat = features(align(sd, own), breaks=())
    res = evaluate({"GAP-1": walk_forward(feat, ("dJ", "dI"))})
    assert res["GAP-1"]["verdict"] == "pass"
    assert res["GAP-1"]["mse_model"] < res["GAP-1"]["mse_random_walk"]


def test_independent_series_rarely_pass() -> None:
    passes = 0
    for seed in range(10):
        sd, own = _pair(200, lead=False, seed=100 + seed)
        feat = features(align(sd, own), breaks=())
        passes += (
            evaluate({"GAP-1": walk_forward(feat, ("dJ", "dI"))})["GAP-1"]["verdict"] == "pass"
        )
    assert passes <= 2


def test_features_use_only_the_past_for_the_gap_mean() -> None:
    sd, own = _pair(60, lead=False, seed=3)
    feat = features(align(sd, own), breaks=())
    g = np.log(own) - np.log(sd)
    t = feat.index[30]
    assert np.isclose(feat.loc[t, "dev"], g.loc[t] - g.loc[: feat.index[29]].mean())
    assert np.isnan(feat["dev"].iloc[10])  # fewer than 20 prior days


def test_break_windows_are_excluded() -> None:
    d = pd.bdate_range("2026-09-01", "2026-10-30")
    m = near_break(d, [date(2026, 9, 25)])
    assert m[d.get_loc(pd.Timestamp("2026-09-25"))]
    assert m[d.get_loc(pd.Timestamp("2026-10-09"))]  # 10 business days after
    assert not m[d.get_loc(pd.Timestamp("2026-10-12"))]


def test_waiting_until_enough_out_of_sample_points() -> None:
    sd, own = _pair(80, lead=True, seed=4)
    feat = features(align(sd, own), breaks=())
    res = evaluate({"GAP-1": walk_forward(feat, ("dJ", "dI"))})
    assert res["GAP-1"]["verdict"].startswith("waiting")
