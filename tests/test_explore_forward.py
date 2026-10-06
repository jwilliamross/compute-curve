"""Shadow forward test of round-1 candidates. All data are SYNTHETIC."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

from compute_curve.config import ExplorationConfig, ForwardConfig, load_config
from compute_curve.explore import forward as fw
from compute_curve.synthetic import synthetic_cgi_vintages

FWD = ForwardConfig(
    start=pd.Timestamp("2026-10-07", tz="UTC").to_pydatetime(),
    end=pd.Timestamp("2026-10-20 23:59:59", tz="UTC").to_pydatetime(),
    sessions=10,
)
FROZEN = {
    "hid": "H05",
    "direction": -1,
    "intercept": 0.0,
    "slope": -0.35,
    "y_mean_explore": 0.0,
}


@pytest.fixture(scope="module")
def ecfg() -> ExplorationConfig:
    cfg = load_config()
    assert cfg.exploration is not None
    return cfg.exploration


def _values(transient: float = 0.0, seed: int = 1) -> pd.DataFrame:
    rows = synthetic_cgi_vintages("2026-10-06 12:00", "2026-10-21 06:00", seed, transient)
    assert rows["is_synthetic"].all()
    values, counts = fw.point_in_time(rows, "H100", FWD.max_publish_lag_minutes)
    assert counts == {"revised": 0, "late": 0}
    return values


def test_h05_forward_window_is_sixty_sessions() -> None:
    cfg = load_config()
    assert cfg.exploration is not None
    f = cfg.exploration.forward["H05"]
    assert f.sessions == 60
    hol = ["2026-11-26", "2026-12-25"]
    end_next = (pd.Timestamp(f.end) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    assert np.busday_count(f.start.date().isoformat(), end_next, holidays=hol) == 60


def test_point_in_time_keeps_first_vintage_and_drops_late_values() -> None:
    a = synthetic_cgi_vintages("2026-10-07", "2026-10-07 02:00", 1, observed="2026-10-07 03:00")
    b = a.copy()
    b["ts_observed"] = pd.Timestamp("2026-10-08", tz="UTC")
    b.loc[0, "value"] = 99.0  # a later revision of the first stamp
    late = a.iloc[[3]].copy()
    late["raw_json"] = json.dumps({"generated_at": "2026-10-07T05:00:00+00:00"})
    a = pd.concat([a.drop(index=3), late], ignore_index=True)
    values, counts = fw.point_in_time(pd.concat([a, b], ignore_index=True), "H100", 15)
    assert counts["revised"] == 1
    assert counts["late"] == 1
    assert values["value"].max() < 99.0
    assert len(values) == len(a) - 1


def test_shadow_rows_use_only_past_values_and_known_outcomes(ecfg: ExplorationConfig) -> None:
    values = _values()
    now = pd.Timestamp("2026-10-09 12:00", tz="UTC")
    rows = fw.shadow_rows(values, FROZEN, FWD, now, ecfg.cgi_max_age_minutes)
    assert (rows["decided_at"] <= now).all()
    assert rows["tau"].min() == pd.Timestamp("2026-10-07 06:00", tz="UTC")
    assert rows.loc[rows["known_at"] > now, "y"].isna().all()
    assert rows.loc[rows["known_at"] <= now, "y"].notna().all()
    # Poisoning everything after a decision point leaves its signal unchanged.
    tau = rows["tau"].iloc[10]
    bad = values.copy()
    later = bad["as_of"] > tau
    bad.loc[later, "value"] = bad.loc[later, "value"] * 5.0
    rows2 = fw.shadow_rows(bad, FROZEN, FWD, now, ecfg.cgi_max_age_minutes)
    assert rows2.loc[rows2["tau"] == tau, "x"].iloc[0] == pytest.approx(
        rows.loc[rows["tau"] == tau, "x"].iloc[0]
    )


def test_values_before_the_window_are_not_used(ecfg: ExplorationConfig) -> None:
    values = _values()
    now = pd.Timestamp("2026-10-08", tz="UTC")
    rows = fw.shadow_rows(values, FROZEN, FWD, now, ecfg.cgi_max_age_minutes)
    bad = values.copy()
    early = bad["as_of"] < pd.Timestamp(FWD.start)
    bad.loc[early, "value"] = 50.0
    rows2 = fw.shadow_rows(bad, FROZEN, FWD, now, ecfg.cgi_max_age_minutes)
    pd.testing.assert_frame_equal(rows, rows2)


def test_merge_log_never_rewrites_a_forecast(tmp_path: pytest.TempPathFactory) -> None:
    values = _values()
    day1 = pd.Timestamp("2026-10-08", tz="UTC")
    day2 = pd.Timestamp("2026-10-09", tz="UTC")
    log1 = fw.merge_log(None, fw.shadow_rows(values, FROZEN, FWD, day1, 30))
    revised = values.copy()
    revised["value"] = revised["value"] * 1.01
    new = fw.shadow_rows(revised, FROZEN, FWD, day2, 30)
    path = tmp_path / "log.csv"  # the daily step stores the log as CSV
    log1.to_csv(path, index=False)
    log2 = fw.merge_log(pd.read_csv(path), new)
    old_part = log2.loc[log2["tau"].isin(log1["tau"])].reset_index(drop=True)
    assert np.allclose(old_part["forecast"], log1["forecast"])
    assert len(log2) > len(log1)
    assert log2.loc[log2["known_at"] <= day2, "y"].notna().all()


def test_forward_evaluation_passes_a_real_reversal_and_fails_noise(
    ecfg: ExplorationConfig,
) -> None:
    end = pd.Timestamp("2026-10-21 12:00", tz="UTC")
    assert fw.window_complete(pd.DataFrame(), FWD, end)
    good = fw.shadow_rows(_values(0.01), FROZEN, FWD, end, 30)
    noise = fw.shadow_rows(_values(0.0, seed=4), FROZEN, FWD, end, 30)
    r_good = fw.evaluate_forward(good, FROZEN, ecfg, 1)
    r_noise = fw.evaluate_forward(noise, FROZEN, ecfg, 1)
    assert r_good["passed"] and r_good["oos_r2_zero"] > 0
    assert not r_noise["passed"]
    assert not fw.window_complete(pd.DataFrame(), FWD, pd.Timestamp("2026-10-15", tz="UTC"))
