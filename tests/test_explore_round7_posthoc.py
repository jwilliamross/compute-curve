"""Round 7 post-hoc helpers on hand-made data (no real data)."""

import numpy as np
import pandas as pd

from compute_curve.explore import round7_posthoc as ph


def test_weighted_median_and_trimmed_mean() -> None:
    assert ph.weighted_median(np.array([1.0, 2.0, 10.0]), np.array([1.0, 1.0, 5.0])) == 10.0
    assert ph.weighted_median(np.array([3.0, 1.0, 2.0]), np.ones(3)) == 2.0
    assert ph.trimmed_mean(pd.Series([1.0, 2.0, 3.0, 4.0, 100.0])) == 3.0


def test_index_methods_and_settlement_risk() -> None:
    days = pd.date_range("2026-08-03", periods=28, freq="D")
    rows = []
    for d in days:
        for prov, price, n in (("aws", 9.0, 1), ("a", 2.0, 5), ("b", 3.0, 1), ("c", 4.0, 1)):
            rows.append({"date": d, "provider": prov, "price": price, "weight": float(n)})
    h = pd.DataFrame(rows)
    m = ph.index_methods(h)
    assert (m["provider_median"] == 3.5).all()
    assert (m["offering_weighted_median"] == 2.0).all()
    assert (m["provider_median_ex_hyperscalers"] == 3.0).all()
    r = ph.settlement_risk(h)
    assert r["n_months"] == 1.0  # only August has three or more Mondays


def test_fm_slope_variants_run() -> None:
    rng = np.random.default_rng(4)
    v = rng.normal(0, 0.2, (40, 10)).cumsum(axis=0) * 0.01 + rng.normal(0, 0.2, 10)
    panel = pd.DataFrame(v, index=pd.date_range("2025-01-06", periods=40, freq="W-MON"))
    panel.columns = [f"p{i}" for i in range(10)]
    out = ph.fm_slope(panel, lag_premium=1, drop=("p0",), horizon=4)
    assert out["n"] > 0 and "mean" in out
