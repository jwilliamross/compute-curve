"""Claim 12 helpers on hand-made frames (no real data)."""

import numpy as np
import pandas as pd

from compute_curve import replication as rp


def _pools() -> pd.DataFrame:
    rows = []
    days = pd.date_range("2030-01-01", "2030-03-31", freq="D")
    for k in range(6):
        for d in days:
            if k == 0 and d.day % 10:  # sparse pool: only every 10th day
                continue
            rows.append(
                {"day": d.date(), "az_id": f"az{k}", "instance_type": "p5", "gpu": "H100",
                 "price_per_gpu_hour": 2.0 + 0.01 * k + 0.001 * d.dayofyear}
            )  # fmt: skip
    return pd.DataFrame(rows)


def test_pool_panel_uses_only_the_last_seven_days() -> None:
    panel = rp.pool_monday_panel(_pools(), "H100")
    assert (panel.index.dayofweek == 0).all()
    sparse = panel["az0|p5"]
    # A Monday more than 6 days after its last observation is missing, never stale.
    assert sparse.isna().any() and sparse.notna().any()
    assert rp.pool_monday_panel(_pools(), "A100").empty


def test_pool_forward_change_needs_enough_pools() -> None:
    panel = rp.pool_monday_panel(_pools(), "H100")
    y = rp.pool_forward_change(panel, h=4, min_pools=5)
    assert y.dropna().gt(0).all()  # prices rise by construction
    assert rp.pool_forward_change(panel, h=4, min_pools=7).isna().all()


def test_verdict_needs_every_condition_under_both_accountings() -> None:
    good = {
        "hac_p_one_sided": 0.01,
        "moments": {"mean": 1e-4},
        "c2": True,
        "ci_mean": [-1e-5, 2e-4],
    }
    assert rp.verdict_a([good, good])
    assert not rp.verdict_a([good, good | {"c2": False}])
    assert not rp.verdict_a([good, good | {"hac_p_one_sided": 0.2}])
    assert not rp.verdict_a([good | {"ci_mean": [-2e-4, -1e-5]}, good])


def test_by_year_groups_sessions() -> None:
    idx = pd.bdate_range("2030-12-20", "2031-01-10")
    r = pd.Series(np.linspace(-1e-3, 1e-3, len(idx)), index=idx)
    ys = rp.by_year(r)
    assert [y["year"] for y in ys] == [2030, 2031]
    assert sum(y["n"] for y in ys) == len(idx)


def test_window_is_before_the_existing_data() -> None:
    assert rp.WINDOW_A[1] < pd.Timestamp("2024-09-03").date()
    assert rp.MEMBER_START_A["NBIS"] == rp.NEVER


def test_high_regime_is_lagged() -> None:
    idx = pd.bdate_range("2030-01-01", periods=400)
    rng = np.random.default_rng(2)
    r = np.where(np.arange(400) < 250, 0.005, 0.02) * rng.normal(size=400)
    xlk = pd.Series(100 * np.exp(np.cumsum(r)), index=idx)
    h = rp.high_regime(xlk)
    assert h.iloc[:180].isna().all()
    assert h.iloc[-50:].mean() > 0.9  # the volatile tail is "high"
    bumped = xlk.copy()
    bumped.iloc[300:] *= np.exp(np.cumsum(rng.normal(0, 0.1, 100)))
    pd.testing.assert_series_equal(rp.high_regime(bumped).iloc[:301], h.iloc[:301])


def test_regime_tests_detect_a_planted_split() -> None:
    idx = pd.bdate_range("2030-01-01", periods=600)
    rng = np.random.default_rng(3)
    high = pd.Series((np.arange(600) // 50) % 2, index=idx, dtype=float)
    r = pd.Series(rng.normal(0, 0.005, 600) + 0.002 * high.to_numpy(), index=idx)
    t = rp.regime_tests(r, high)
    rp.finish_13(t)
    assert t["diff_bps"] > 0 and t["p_n13_1"] < 0.01 and t["passes"]
