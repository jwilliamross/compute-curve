"""Claim 11 (docs/macro_drivers_plan.md) on SYNTHETIC or hand-made frames only."""

from datetime import date

import numpy as np
import pandas as pd

from compute_curve import macro as mc
from compute_curve.synthetic import synthetic_macro_inputs

BUCKETS = {"gpu_semis": ["S1", "S2"], "neocloud": ["S3"], "power_capacity": ["S2", "S3"]}


def test_forward_change_needs_enough_providers() -> None:
    idx = pd.date_range("2030-01-07", periods=6, freq="W-MON")
    p = pd.DataFrame(
        {"a": np.log([1, 1, 1, 1, 1.1, 1.1]), "b": np.log([2, 2, 2, 2, 2, 2.2])}, index=idx
    )
    y = mc.forward_change(p, h=4, min_cs=2)
    assert np.isclose(y.iloc[0], np.log(1.1) / 2) and np.isnan(y.iloc[-1])
    assert mc.forward_change(p, h=4, min_cs=3).isna().all()


def test_basket_excess_is_basket_minus_market() -> None:
    idx = pd.bdate_range("2030-01-01", periods=25)
    cl = pd.DataFrame(
        {"A": np.exp(np.arange(25) * 0.01), "B": np.exp(np.arange(25) * 0.03), "SPY": np.ones(25)},
        index=idx,
    )
    x = mc.basket_excess(cl, ["A", "B", "MISSING"], window=20)
    assert np.isclose(x.iloc[-1], 0.4) and x.iloc[:20].isna().all()


def test_asof_friday_never_uses_the_monday_or_weekend() -> None:
    days = pd.date_range("2030-01-01", "2030-01-21", freq="D")
    s = pd.Series(np.arange(len(days), dtype=float), index=days)
    out = mc.asof_friday(s, pd.DatetimeIndex([pd.Timestamp("2030-01-14")]))  # a Monday
    assert out.iloc[0] == s.loc["2030-01-11"]  # the Friday before


def test_correlogram_finds_the_lead() -> None:
    rng = np.random.default_rng(0)
    x = pd.Series(rng.normal(size=200))
    y = x.shift(2) + rng.normal(scale=0.3, size=200)
    c = mc.correlogram(x, y, leads=4)
    assert max(c, key=lambda k: c[k]) == 2


def test_event_windows_take_the_next_monday() -> None:
    idx = pd.date_range("2030-01-07", periods=10, freq="W-MON")
    y = pd.Series(np.arange(10, dtype=float), index=idx)
    ev = mc.event_windows(y, [date(2030, 1, 9)])  # a Wednesday
    assert ev["events"] == [("2030-01-09", 1.0)]
    assert ev["mean_other"] == y.drop(idx[1]).mean()


def test_analyse_detects_a_planted_lead_and_not_a_null() -> None:
    panel, cl, dgs2 = synthetic_macro_inputs(120, seed=5, lead=1.0)
    assert panel.attrs["is_synthetic"] and cl.attrs["is_synthetic"]
    r = mc.analyse({"H100": panel}, cl, dgs2, BUCKETS, seed=1)
    assert set(r["tests"]) == set(mc.TESTS)
    assert r["tests"]["MD-1"]["slope"] > 0 and r["tests"]["MD-1"]["p_one_sided"] < 0.01
    assert "p_holm" in r["tests"]["MD-1"]
    p0, cl0, d0 = synthetic_macro_inputs(120, seed=6, lead=0.0)
    r0 = mc.analyse({"H100": p0}, cl0, d0, BUCKETS, seed=1)
    assert r0["tests"]["MD-1"]["verdict"] == "not confirmed"
    md = mc.render(r)
    assert "| MD-4 |" in md and "Granger" in md


def test_earnings_dates_are_sorted_and_in_window() -> None:
    assert sorted(mc.NVDA_EARNINGS) == mc.NVDA_EARNINGS
    assert all(mc.BARS_START < d <= mc.LAST_FRIDAY for d in mc.NVDA_EARNINGS)
