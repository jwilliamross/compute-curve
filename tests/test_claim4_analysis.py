"""Claim-4 tests on SYNTHETIC data: outcomes, no look-ahead, detection, events, gate."""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
import pytest

from compute_curve.claim4 import analysis as an
from compute_curve.claim4.market_data import (
    BAR_DELAY,
    manifest,
    sessions_from_calendar,
    window_returns,
)
from compute_curve.synthetic import (
    synthetic_equity_bars,
    synthetic_signals,
    synthetic_weekday_calendar,
)

START = date(2025, 1, 6)


def world(cfg, n: int = 260, effect: float = 0.0, seed: int = 1):
    c4 = cfg.claim4.model_copy(update={"first_session": START})
    sessions = sessions_from_calendar(synthetic_weekday_calendar(START, date(2026, 6, 30))).iloc[:n]
    sessions = sessions.reset_index(drop=True)
    signals = synthetic_signals(sessions, seed)
    bars = synthetic_equity_bars(
        sessions,
        c4.universe.members(),
        c4.benchmark,
        seed,
        effect=effect,
        driver=signals["level_h100"].to_numpy(),
    )
    df = an.build_dataset(signals, bars, sessions, c4)
    as_of = pd.Timestamp(sessions["close_utc"].max()) + pd.Timedelta(hours=1)
    return c4, sessions, signals, bars, df, as_of


def test_window_return_runs_from_open_to_close_h_sessions_later(cfg):
    c4, sessions, _, bars, _, _ = world(cfg, n=30)
    ret, known = window_returns(bars, sessions, 5)
    nv = bars.loc[bars["symbol"] == "NVDA"].reset_index(drop=True)
    i = 7
    assert ret["NVDA"].iloc[i] == pytest.approx(nv["close"].iloc[i + 4] / nv["open"].iloc[i] - 1)
    assert known.iloc[i] == sessions["close_utc"].iloc[i + 4] + BAR_DELAY
    assert np.isnan(ret["NVDA"].iloc[-1])  # window runs past the data


def test_basket_is_nan_when_a_bucket_lacks_coverage(cfg):
    c4, sessions, signals, bars, _, _ = world(cfg, n=30)
    day = sessions["session"].iloc[10]
    drop = (bars["session"] == day) & bars["symbol"].isin(["CRWV", "NBIS", "IREN"])
    df = an.build_dataset(signals, bars.loc[~drop], sessions, c4)
    r = df.set_index("session")
    assert np.isnan(r.loc[day, "R_neocloud_h1"])  # 1 of 4 members < 50%
    assert np.isnan(r.loc[day, "R_basket_h1"])
    assert np.isfinite(r.loc[day, "R_gpu_semis_h1"])


def test_category_balanced_basket_is_mean_of_bucket_excess(cfg):
    _, _, _, _, df, _ = world(cfg, n=40)
    cols = ["R_neocloud_h1", "R_gpu_semis_h1", "R_power_capacity_h1"]
    ok = df[[*cols, "R_basket_h1"]].dropna()
    assert np.allclose(ok[cols].mean(axis=1), ok["R_basket_h1"])


def test_walk_forward_never_uses_an_outcome_unknown_at_the_open(cfg):
    c4, _, _, _, df, as_of = world(cfg, n=120, effect=0.5)
    h = 5
    fc = an.walk_forward(df, "level_h100", h, as_of, c4).set_index("session")
    t = df["session"].iloc[80]
    t_open = df.loc[df["session"] == t, "open_utc"].iloc[0]
    cut = t_open - pd.Timedelta(minutes=c4.open_buffer_minutes)
    known = pd.to_datetime(df[f"known_h{h}"], utc=True) <= cut
    poisoned = df.copy()
    poisoned.loc[~known, f"R_basket_h{h}"] = 1e3
    fc2 = an.walk_forward(poisoned, "level_h100", h, as_of, c4).set_index("session")
    assert fc2.loc[t, "forecast"] == pytest.approx(fc.loc[t, "forecast"])
    # sanity: changing a window that was known does change the forecast
    known_rows = df.index[known & df["in_sample"] & df[f"R_basket_h{h}"].notna()]
    changed = df.copy()
    changed.loc[known_rows[-1], f"R_basket_h{h}"] += 0.5
    fc3 = an.walk_forward(changed, "level_h100", h, as_of, c4).set_index("session")
    assert fc3.loc[t, "forecast"] != pytest.approx(fc.loc[t, "forecast"])


def test_training_size_grows_one_window_per_session_for_h1(cfg):
    c4, _, _, _, df, as_of = world(cfg, n=60)
    fc = an.walk_forward(df, "level_h100", 1, as_of, c4)
    assert fc["n_train"].iloc[0] == c4.min_train
    assert (fc["n_train"].diff().dropna() == 1).all()


def test_planted_effect_is_found_and_null_is_not(cfg):
    c4, _, _, _, df, as_of = world(cfg, n=260, effect=0.5)
    res = an.lead_lag_family(df, as_of, c4, [an.BASKET], "P", "holm", c4.alpha, 200, 0)
    by = {(r.signal, r.horizon): r for r in res}
    assert by[("level_h100", 1)].passes
    assert by[("level_h100", 1)].rho > 0.5
    assert not any(r.passes for r in res if r.signal != "level_h100")
    c4n, _, _, _, dfn, as_ofn = world(cfg, n=260, effect=0.0, seed=7)
    null = an.lead_lag_family(dfn, as_ofn, c4n, [an.BASKET], "P", "holm", c4n.alpha, 200, 0)
    assert not any(r.passes for r in null)


def test_sparse_signal_is_flagged_insufficient(cfg):
    c4, sessions, _, bars, _, _ = world(cfg, n=80)
    sparse = synthetic_signals(sessions, 3, nonzero_share=0.05)
    df = an.build_dataset(sparse, bars, sessions, c4)
    as_of = pd.Timestamp(sessions["close_utc"].max()) + pd.Timedelta(hours=1)
    r = an.lead_lag(df, "level_h100", an.BASKET, 1, as_of, c4, "P", 100, 0)
    assert r.n_nonzero < c4.min_nonzero_signal
    assert "insufficient variation" in r.note


def test_walk_forward_family_finds_planted_effect(cfg):
    c4, _, _, _, df, as_of = world(cfg, n=260, effect=0.5)
    c4 = c4.model_copy(update={"min_oos_forecasts": 100})
    wf, _ = an.walk_forward_family(df, as_of, c4)
    by = {(r.signal, r.horizon): r for r in wf}
    best = by[("level_h100", 1)]
    assert best.passes and best.r2_vs_b0 > 0 and best.r2_vs_b1 > 0


def test_event_study_drops_overlapping_events(cfg):
    c4, sessions, signals, bars, _, _ = world(cfg, n=60)
    sig = signals.copy()
    sig["level_h100"] = 0.0
    for i in (30, 31, 32, 40):
        sig.loc[i, "level_h100"] = 0.05
    df = an.build_dataset(sig, bars, sessions, c4)
    as_of = pd.Timestamp(sessions["close_utc"].max()) + pd.Timedelta(hours=1)
    assert an.event_study(df, "H100", 1, as_of, c4, 100, 0).n_events == 4
    five = an.event_study(df, "H100", 5, as_of, c4, 100, 0)
    assert five.n_events == 2  # 31 and 32 fall inside the first event's window
    assert "insufficient events" in five.note and not five.passes


def test_round_trip_cost_matches_the_plan(cfg):
    c4 = cfg.claim4
    base = (2 * 15 + 2 * 3 + 2 * 1) / 1e4
    assert an.round_trip_cost(1, 1, c4) == pytest.approx(base + 0.005 / 252)
    assert an.round_trip_cost(-1, 5, c4) == pytest.approx(base + 0.05 * 5 / 252)
    assert an.round_trip_cost(-1, 5, c4, 2.0) == pytest.approx(2 * (base + 0.05 * 5 / 252))


def _ll(sig, h, passes, p):
    r = an.LeadLag("P", an.BASKET, sig, h, 200, 50)
    r.passes, r.p_adj = passes, p
    return r


def _wf(sig, h, passes, n=200):
    r = an.WalkForward(sig, h, n, 60)
    r.passes = passes
    return r


def _st(sig, h, passes):
    r = an.StrategyResult(sig, h, 200, 50)
    r.passes = passes
    return r


def test_gate_needs_every_condition_and_picks_the_smallest_p(cfg):
    c4 = cfg.claim4
    pairs = [(s, h) for s in c4.signals for h in c4.horizons]
    lead = [
        _ll(
            s,
            h,
            (s, h) in {("level_h100", 1), ("disp_b200", 5)},
            0.01 if s == "disp_b200" else 0.03,
        )
        for s, h in pairs
    ]
    wf = [_wf(s, h, True) for s, h in pairs]
    st = [_st(s, h, (s, h) != ("level_b200", 1)) for s, h in pairs]
    rows, pick = an.gate(lead, wf, st, c4)
    assert pick == "disp_b200|h5"
    assert sum(r.validated for r in rows) == 2
    wf_short = [_wf(s, h, True, n=50) for s, h in pairs]
    _, pick2 = an.gate(lead, wf_short, st, c4)
    assert pick2 is None  # G4: too few out-of-sample forecasts


def test_manifest_holds_no_prices(cfg):
    _, _, _, bars, _, _ = world(cfg, n=10)
    m = manifest(bars, "2025-01-06", "2025-01-17", "sip", "all")
    text = str(m)
    for col in ("open", "close", "high", "low", "vwap"):
        assert f"'{col}'" not in text
    assert m["rows"] == len(bars) and len(m["sha256"]) == 64


def test_sparse_strategy_cannot_pass_g3(cfg):
    c4 = cfg.claim4
    fc = pd.DataFrame(
        {
            "session": range(12),
            "forecast": [0.0] * 10 + [0.02, 0.02],
            "actual": [0.001] * 10 + [0.03, 0.03],
            "x": [0.0] * 12,
            "b0": [0.0] * 12,
            "b1": [0.0] * 12,
        }
    )
    r = an.evaluate_strategy(fc, "level_h100", 1, c4, 500, 0)
    assert r.n_trades == 2
    assert not r.passes  # flat resamples count as Sharpe 0, so the lower bound is not above 0
