"""Claim-4 signal construction and timing (no look-ahead)."""

from __future__ import annotations

from datetime import UTC, date, datetime

import numpy as np
import pandas as pd
import pytest

from compute_curve.claim4.market_data import sessions_from_calendar
from compute_curve.claim4.signals import (
    align_to_sessions,
    panel_features,
    session_signals,
    usable_time,
)
from compute_curve.synthetic import synthetic_weekday_calendar


def _sessions(start: date, end: date) -> pd.DataFrame:
    return sessions_from_calendar(synthetic_weekday_calendar(start, end))


def _features(days_vals: list[tuple[date, float]], hour: int = 6) -> pd.DataFrame:
    rows = []
    for d, lvl in days_vals:
        rows.append(
            {
                "as_of_date": d,
                "gpu_model": "H100",
                "level": lvl,
                "dispersion": 0.1,
                "n_listings": 10,
                "n_providers": 5,
                "meets_coverage": True,
                "ts_available": pd.Timestamp(datetime(d.year, d.month, d.day, hour, tzinfo=UTC)),
            }
        )
    f = pd.DataFrame(rows)
    f["ts_usable"] = usable_time(f["ts_available"], f["as_of_date"])
    return f


def test_usable_time_is_later_of_margin_and_daily_cutoff():
    ts = pd.Series(pd.to_datetime(["2026-09-01 06:00", "2026-09-02 23:00"], utc=True))
    days = pd.Series([date(2026, 9, 1), date(2026, 9, 2)])
    u = usable_time(ts, days, 60, "23:30")
    assert u.iloc[0] == pd.Timestamp("2026-09-01 23:30", tz="UTC")
    assert u.iloc[1] == pd.Timestamp("2026-09-03 00:00", tz="UTC")


def test_sessions_convert_new_york_time_with_daylight_saving():
    s = _sessions(date(2026, 10, 30), date(2026, 11, 2))
    by = dict(zip(s["session"], s["open_utc"], strict=True))
    assert by[date(2026, 10, 30)] == pd.Timestamp("2026-10-30 13:30", tz="UTC")  # EDT
    assert by[date(2026, 11, 2)] == pd.Timestamp("2026-11-02 14:30", tz="UTC")  # EST


def test_a_weekday_index_reaches_the_market_at_the_next_open_not_the_same_day():
    s = _sessions(date(2026, 9, 14), date(2026, 9, 18))
    a = align_to_sessions(_features([(date(2026, 9, 14), 3.0), (date(2026, 9, 15), 3.1)]), s)
    asof = dict(zip(a["session"], a["as_of_date"], strict=True))
    assert pd.isna(asof[date(2026, 9, 14)])  # 06:00 snapshot is not usable the same morning
    assert asof[date(2026, 9, 15)] == date(2026, 9, 14)
    assert asof[date(2026, 9, 16)] == date(2026, 9, 15)
    # every used day was usable before the session's open
    used = a.dropna(subset=["ts_usable"])
    assert (pd.to_datetime(used["ts_usable"], utc=True) <= used["open_utc"]).all()


def test_weekend_changes_accumulate_into_monday():
    s = _sessions(date(2026, 9, 10), date(2026, 9, 15))
    f = _features(
        [
            (date(2026, 9, 9), 3.0),
            (date(2026, 9, 10), 3.0),
            (date(2026, 9, 11), 3.0),
            (date(2026, 9, 12), 3.3),
            (date(2026, 9, 13), 3.3),
            (date(2026, 9, 14), 3.3),
        ]
    )
    a = align_to_sessions(f, s)
    sig = session_signals({"H100": a, "B200": a}).set_index("session")
    assert sig.loc[date(2026, 9, 11), "level_h100"] == pytest.approx(0.0)
    assert sig.loc[date(2026, 9, 14), "level_h100"] == pytest.approx(np.log(3.3 / 3.0))
    assert sig.loc[date(2026, 9, 14), "asof_h100"] == date(2026, 9, 13)


def test_a_late_refetch_of_an_older_day_does_not_replace_a_newer_day():
    f = _features([(date(2026, 9, 14), 3.0), (date(2026, 9, 15), 3.2)])
    late = f.iloc[[0]].copy()
    late["ts_available"] = pd.Timestamp("2026-09-16 05:00", tz="UTC")
    late["ts_usable"] = usable_time(late["ts_available"], late["as_of_date"])
    late["level"] = 9.9
    a = align_to_sessions(
        pd.concat([f, late], ignore_index=True), _sessions(date(2026, 9, 14), date(2026, 9, 18))
    )
    asof = dict(zip(a["session"], a["as_of_date"], strict=True))
    assert asof[date(2026, 9, 17)] == date(2026, 9, 15)


def test_uncovered_days_are_skipped():
    f = _features([(date(2026, 9, 14), 3.0), (date(2026, 9, 15), 3.2)])
    f.loc[1, "meets_coverage"] = False
    a = align_to_sessions(f, _sessions(date(2026, 9, 14), date(2026, 9, 18)))
    assert a.loc[a["session"] == date(2026, 9, 17), "as_of_date"].iloc[0] == date(2026, 9, 14)


def _obs(
    provider: str, price: float, ts: datetime, avail: str = "unknown", synthetic: bool = False
) -> dict:
    # Hand-built fixture rows, as in tests/test_own_index.py; not market data.
    return {
        "ts_observed": ts,
        "ts_source": ts,
        "provider": provider,
        "gpu_model": "H100",
        "gpu_variant": "SXM",
        "price_usd_per_gpu_hour": price,
        "term": "on_demand",
        "availability": avail,
        "region": None,
        "source": "gpurentalprices_hist",
        "snapshot_id": f"gpurentalprices_hist_{ts:%Y%m%dT%H%M%SZ}",
        "is_synthetic": synthetic,
    }


def test_panel_features_dispersion_count_and_panel_filter(cfg):
    ts = datetime(2026, 9, 1, 6, tzinfo=UTC)
    rows = [
        _obs(p, px, ts) for p, px in [("a", 2.0), ("b", 3.0), ("c", 4.0), ("d", 5.0), ("e", 6.0)]
    ]
    rows += [
        _obs("a", 2.2, ts),
        _obs("outsider", 100.0, ts),
        _obs("b", 3.5, ts, avail="unavailable"),
    ]
    f = panel_features(pd.DataFrame(rows), cfg.index, "H100", ["a", "b", "c", "d", "e"])
    r = f.iloc[0]
    assert r["n_listings"] == 6  # the unavailable listing and the outsider are excluded
    assert r["n_providers"] == 5
    logs = np.log([2.1, 3.0, 4.0, 5.0, 6.0])
    assert r["dispersion"] == pytest.approx(np.percentile(logs, 75) - np.percentile(logs, 25))
    assert r["ts_usable"] == pd.Timestamp("2026-09-01 23:30", tz="UTC")


def test_synthetic_rows_never_enter_features(cfg):
    ts = datetime(2026, 9, 1, 6, tzinfo=UTC)
    rows = [_obs(p, 3.0, ts, synthetic=True) for p in "abcde"]
    assert panel_features(pd.DataFrame(rows), cfg.index, "H100", list("abcde")).empty
