"""Round-3 tests on SYNTHETIC CGI rows (compute_curve.synthetic, is_synthetic=True)."""

import json

import numpy as np
import pandas as pd
import pytest

from compute_curve.config import load_config
from compute_curve.explore import round3 as r3
from compute_curve.synthetic import synthetic_cgi_channels

CFG = load_config()
ECFG = CFG.exploration
R3CFG = CFG.exploration3


def rows(seed=1, half_life=12.0, jump_rate=0.02, start="2026-09-01", end="2026-09-24 23:45"):
    h = synthetic_cgi_channels(
        start, end, seed, "H100", jump_rate=jump_rate, half_life_stamps=half_life
    )
    b = synthetic_cgi_channels(
        start, end, seed + 1, "B200", jump_rate=jump_rate, half_life_stamps=half_life
    )
    return pd.concat([h, b], ignore_index=True)


def by_id(results):
    return {r.hid: r for r in results}


def test_synthetic_rows_are_labelled():
    assert rows()["is_synthetic"].all()


def test_planted_transient_jumps_are_recovered():
    res, frozen, desc = r3.explore3(rows(), ECFG, R3CFG, 15, 7)
    out = by_id(res)
    for hid in ("R3-01", "R3-02", "R3-03"):
        assert out[hid].sufficient
        assert out[hid].c < 0 and out[hid].p_one_sided < 0.01, hid
    assert out["R3-04"].c > 0 and out["R3-04"].p_one_sided < 0.01
    assert set(frozen) == set(r3.R3_TESTS)
    assert {"R3-02@0.001", "R3-03@0.005"} <= set(desc)


def test_persistent_jumps_show_no_reversal():
    res, _, _ = r3.explore3(rows(seed=3, half_life=1e9), ECFG, R3CFG, 15, 7)
    for r in res[:3]:
        assert not (r.p_one_sided < 0.01), r.hid


def test_whole_window_rule_drops_a_methodology_switch_and_gaps():
    df = rows(jump_rate=0.0)
    h = df.loc[df["gpu_model"] == "H100"].copy()
    switch = pd.Timestamp("2026-09-10 12:00", tz="UTC")
    h.loc[h["as_of"] >= switch, "methodology_id"] = "synthetic_v2"
    gap = pd.Timestamp("2026-09-15 03:15", tz="UTC")
    h = h.loc[h["as_of"] != gap]
    g = r3.grid15(r3.point_in_time_full(h, "H100", 15))
    ch = r3.channels(g, 0.0025)
    t = pd.to_datetime(ch["t"])
    for event in (switch, gap):
        near = (t > event - pd.Timedelta(hours=6)) & (t < event + pd.Timedelta(hours=6))
        assert not near.any()
    assert len(ch) > 400


def test_point_in_time_keeps_first_vintage_and_drops_late_rows():
    h = synthetic_cgi_channels("2026-09-01", "2026-09-02", 5, "H100")
    revised = h.assign(value=h["value"] * 1.5, ts_observed=h["ts_observed"] + pd.Timedelta(days=1))
    late = h.iloc[[10]].copy()
    late_stamp = late["as_of"].iloc[0]
    meta = {"generated_at": (late_stamp + pd.Timedelta(minutes=40)).isoformat()}
    h.loc[h.index[10], "raw_json"] = json.dumps(meta | {"stability_band_usd_gpu_hr": 0.1})
    pit = r3.point_in_time_full(pd.concat([h, revised]), "H100", 15)
    assert late_stamp not in set(pit["as_of"])
    merged = pit.merge(h[["as_of", "value"]], on="as_of", suffixes=("", "_first"))
    assert np.allclose(merged["value"], merged["value_first"])
    assert pit["band"].notna().all()


def test_window_is_truncated_before_compute():
    built = r3.build_all(
        rows(start="2026-09-20", end="2026-10-20"), R3CFG.confirm, R3CFG.jump_threshold, 15
    )
    for frame, _ in built.values():
        assert pd.to_datetime(frame["t"]).min() >= pd.Timestamp(R3CFG.confirm[0]) + r3.HORIZON


def test_confirmation_applies_holm_and_both_criteria():
    _, frozen, _ = r3.explore3(rows(), ECFG, R3CFG, 15, 7)
    future = rows(seed=11, start="2026-10-11", end="2026-11-10")
    res = r3.confirm3(future, frozen, ECFG, R3CFG, 15, 7)
    assert all(r.p_holm >= r.p_one_sided for r in res)
    out = by_id(res)
    assert out["R3-02"].confirmed and out["R3-02"].oos_r2_vs_past > 0
    null = rows(seed=12, start="2026-10-11", end="2026-11-10", jump_rate=0.0)
    assert not any(r.confirmed for r in r3.confirm3(null, frozen, ECFG, R3CFG, 15, 7))


@pytest.mark.parametrize(
    ("now", "done"),
    [("2026-12-31 23:59", False), ("2027-01-01 05:54", False), ("2027-01-01 05:55", True)],
)
def test_confirmation_waits_for_the_window(now, done):
    assert r3.confirm_window_complete(R3CFG, pd.Timestamp(now, tz="UTC")) is done
