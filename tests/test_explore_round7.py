"""Round 7 statistics on small hand-made panels (no real data)."""

import numpy as np
import pandas as pd

from compute_curve.explore import round7 as r7


def _mondays(n: int) -> pd.DatetimeIndex:
    return pd.date_range("2025-01-06", periods=n, freq="W-MON")


def _hist(panel: pd.DataFrame, gpu: str) -> pd.DataFrame:
    rows = []
    for t, row in panel.iterrows():
        for prov, v in row.items():
            if np.isfinite(v):
                rows.append(
                    {
                        "date": f"{t:%Y-%m-%d}",
                        "gpu_model": gpu,
                        "provider": prov,
                        "billing_type": "ON_DEMAND",
                        "reservation_months": None,
                        "median_price": float(np.exp(v)),
                    }
                )
    return pd.DataFrame(rows)


def test_weekly_panel_keeps_mondays_on_demand_and_drops_excluded() -> None:
    h = pd.DataFrame(
        [
            {
                "date": "2026-10-05",
                "provider": "a",
                "billing_type": "ON_DEMAND",
                "median_price": 2.0,
            },
            {
                "date": "2026-10-06",
                "provider": "a",
                "billing_type": "ON_DEMAND",
                "median_price": 9.0,
            },
            {"date": "2026-10-05", "provider": "b", "billing_type": "SPOT", "median_price": 1.0},
            {
                "date": "2026-10-05",
                "provider": "runpod",
                "billing_type": "ON_DEMAND",
                "median_price": 1.0,
            },
            {
                "date": "2026-10-12",
                "provider": "a",
                "billing_type": "ON_DEMAND",
                "median_price": 2.2,
            },
            {
                "date": "2026-10-19",
                "provider": "a",
                "billing_type": "ON_DEMAND",
                "median_price": 5.0,
            },
        ]
    ).assign(gpu_model="nvidia-h100", reservation_months=None)
    p = r7.weekly_panel(h, "nvidia-h100")
    assert list(p.columns) == ["a"] and len(p) == 2
    assert np.allclose(np.exp(p["a"].to_numpy()), [2.0, 2.2])


def test_r701_detects_planted_gap_closure() -> None:
    rng = np.random.default_rng(3)
    n, k = 80, 12
    level = rng.normal(0, 0.2, k)
    v = np.zeros((n, k))
    v[0] = level
    for t in range(1, n):
        v[t] = v[t - 1] - 0.15 * (v[t - 1] - v[t - 1].mean()) + rng.normal(0, 0.02, k)
    panel = pd.DataFrame(v, index=_mondays(n), columns=[f"p{i}" for i in range(k)])
    r = r7.r701(panel, seed=1)
    assert r["estimate"] < 0 and r["p_one_sided"] < 0.01
    assert r["ci95"][1] < 0


def test_r702_breadth_and_r703_need_enough_history() -> None:
    panel = pd.DataFrame(np.zeros((10, 9)), index=_mondays(10), columns=[f"p{i}" for i in range(9)])
    assert r7.r702(panel, 1)["verdict"] == "too little history to conclude"
    assert r7.r703(panel)["verdict"] == "too little history to conclude"
    b = r7.breadth(panel)
    assert (b["x"] == 0).all() and (b["y"] == 0).all()


def test_r702_detects_planted_diffusion() -> None:
    rng = np.random.default_rng(5)
    n, k = 120, 15
    shocks = np.repeat(rng.normal(0, 0.03, n // 8), 8)  # persistent market moves
    v = np.zeros((n, k))
    for t in range(1, n):
        moves = rng.random(k) < 0.5
        v[t] = v[t - 1] + np.where(moves, shocks[t] + rng.normal(0, 0.005, k), 0.0)
    panel = pd.DataFrame(v, index=_mondays(n), columns=[f"p{i}" for i in range(k)])
    r = r7.r702(panel, seed=2)
    assert r["estimate"] > 0 and r["p_one_sided"] < 0.05


def test_finish_applies_holm_over_four_and_checks_sign() -> None:
    tests = {
        "R7-01": {"n": 30, "estimate": -0.2, "p_one_sided": 0.001},
        "R7-02": {"n": 30, "estimate": -0.5, "p_one_sided": 0.001},
        "R7-03": {"n": 30, "verdict": "too little history to conclude"},
        "R7-04": {"n": 30, "estimate": -0.1, "p_one_sided": 0.2},
    }
    r7.finish(tests, r7.SIGNS)
    assert abs(tests["R7-01"]["p_holm"] - 0.004) < 1e-12
    assert tests["R7-01"]["verdict"] == "confirmed"
    assert tests["R7-02"]["verdict"] == "not confirmed"  # wrong sign
    assert tests["R7-03"]["verdict"] == "too little history to conclude"
    assert tests["R7-04"]["verdict"] == "not confirmed"


def test_run_tests_end_to_end_on_a_small_panel() -> None:
    rng = np.random.default_rng(7)
    n, k = 70, 10
    h = rng.normal(0, 0.01, (n, k)).cumsum(axis=0) + 1.0
    b = h + 0.6 + rng.normal(0, 0.02, (n, k))
    idx = _mondays(n)
    cols = [f"p{i}" for i in range(k)]
    hist = pd.concat(
        [
            _hist(pd.DataFrame(h, idx, cols), "nvidia-h100"),
            _hist(pd.DataFrame(b, idx, cols), "nvidia-b200"),
        ]
    )
    res = r7.run_tests(hist, seed=1)
    assert set(res["tests"]) == {"R7-01", "R7-02", "R7-03", "R7-04"}
    assert all("verdict" in t for t in res["tests"].values())
    assert res["descriptive"]["H100"]["n_providers_ever"] == k
    assert res["descriptive"]["H200"] == {"n_mondays": 0}
    text = r7.render(res, "v1")
    assert "GetDeploying" in text and "R7-04" in text
