"""Exploration round 1: splits, no look-ahead, planted effects, BH, echo filter, one shot.

All data here are SYNTHETIC (compute_curve.synthetic.synthetic_round1).
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import date

import numpy as np
import pandas as pd
import pytest
from pydantic import ValidationError

from compute_curve.cli import _parser
from compute_curve.config import Config, ExplorationConfig, SplitConfig, load_config
from compute_curve.explore import pipeline as xp
from compute_curve.explore.data import Round1Data, in_set
from compute_curve.explore.hypotheses import (
    SPECS,
    Built,
    build,
    gd_series,
    log_wide,
    provider_change,
)
from compute_curve.explore.run import (
    Result,
    apply_round,
    confirm_one,
    finish_confirmation,
    freeze,
    ranked_survivors,
    ts_test,
)
from compute_curve.synthetic import synthetic_round1


@pytest.fixture(scope="module")
def cfg() -> Config:
    return load_config()


@pytest.fixture(scope="module")
def ecfg(cfg: Config) -> ExplorationConfig:
    assert cfg.exploration is not None
    return cfg.exploration.model_copy(update={"n_boot": 200})


def _data(cfg: Config, seed: int, plant: frozenset[str] = frozenset()) -> Round1Data:
    assert cfg.claim4 is not None
    f = synthetic_round1(seed, plant, cfg.claim4.universe.buckets(), cfg.claim4.benchmark)
    assert all(bool(df["is_synthetic"].all()) for df in f.values())
    return Round1Data(**f)


def _explore(cfg: Config, ecfg: ExplorationConfig, data: Round1Data) -> list[Result]:
    assert cfg.claim4 is not None
    results, _ = xp.explore(data, ecfg, cfg.claim4, seed=1)
    return results


# ---------------------------------------------------------------------------
# Splits
# ---------------------------------------------------------------------------
def test_config_splits_match_the_plan(cfg: Config) -> None:
    assert cfg.exploration is not None
    s = cfg.exploration.splits
    assert s["listings"].explore == (date(2026, 7, 19), date(2026, 9, 12))
    assert s["aws"].confirm == [
        (date(2025, 12, 1), date(2026, 2, 28)),
        (date(2026, 7, 1), date(2026, 9, 30)),
    ]
    assert s["equities"].explore[1] == date(2026, 2, 19)
    assert len(SPECS) == 12
    assert sum(1 for k in SPECS if k in {"H12"}) == 1  # one equity target


def test_split_blocks_must_be_ordered() -> None:
    with pytest.raises(ValidationError):
        SplitConfig(
            explore=(date(2026, 1, 1), date(2026, 2, 1)),
            confirm=[(date(2026, 1, 15), date(2026, 3, 1))],
        )


def test_restrict_keeps_only_the_requested_set(cfg: Config, ecfg: ExplorationConfig) -> None:
    data = _data(cfg, 3)
    for which in ("explore", "confirm"):
        r = data.restrict(ecfg, which)
        assert in_set(r.listings["as_of_date"], ecfg.splits["listings"], which).all()
        assert in_set(r.aws["day"], ecfg.splits["aws"], which).all()
        assert in_set(r.cgi["as_of"], ecfg.splits["cgi"], which).all()
        assert in_set(r.gd["week"], ecfg.splits["getdeploying"], which).all()
        assert in_set(r.bars["session"], ecfg.splits["equities"], which).all()
    exp = data.restrict(ecfg, "explore")
    assert max(exp.listings["as_of_date"]) == date(2026, 9, 12)
    assert max(exp.aws["day"]) == date(2025, 11, 30)


def test_exploration_ignores_confirmation_outcomes(cfg: Config, ecfg: ExplorationConfig) -> None:
    """Outcome poisoning: rewriting every confirmation-set value changes nothing."""
    data = _data(cfg, 5)
    rng = np.random.default_rng(0)

    def poison(df: pd.DataFrame, col: str, key: str, value_cols: list[str]) -> pd.DataFrame:
        out = df.copy()
        m = ~in_set(out[col], ecfg.splits[key], "explore")
        for c in value_cols:
            out.loc[m, c] = out.loc[m, c] * np.exp(rng.normal(0, 1.0, int(m.sum())))
        return out

    bad = Round1Data(
        listings=poison(data.listings, "as_of_date", "listings", ["price"]),
        cgi=poison(data.cgi, "as_of", "cgi", ["value"]),
        gd=poison(data.gd, "week", "getdeploying", ["value", "n_listings"]),
        aws=poison(data.aws, "day", "aws", ["price_per_gpu_hour"]),
        bars=poison(data.bars, "session", "equities", ["open", "close"]),
    )
    a = [asdict(r) for r in _explore(cfg, ecfg, data)]
    b = [asdict(r) for r in _explore(cfg, ecfg, bad)]
    assert json.dumps(a, default=str) == json.dumps(b, default=str)


def test_windows_never_straddle_a_split(cfg: Config, ecfg: ExplorationConfig) -> None:
    assert cfg.claim4 is not None
    exp = _data(cfg, 2).restrict(ecfg, "explore")
    for hid in ("H02", "H09", "H11", "H12"):
        t = pd.to_datetime(build(hid, exp, ecfg, cfg.claim4).frame["t"])
        end = pd.Timestamp(ecfg.splits["aws" if hid != "H02" else "listings"].explore[1])
        # H12's signal day is the calendar day before the session.
        lag = pd.Timedelta(days=1 if hid == "H12" else 0)
        assert (t - lag).max() <= end
    t09 = pd.to_datetime(build("H09", exp, ecfg, cfg.claim4).frame["t"])
    assert t09.max() == pd.Timestamp("2025-11-23")  # 7 days before the AWS split end


# ---------------------------------------------------------------------------
# Building blocks
# ---------------------------------------------------------------------------
def test_matched_listing_change_ignores_new_listings() -> None:
    days = pd.date_range("2026-07-19", periods=6, freq="D").date
    rows = [(d, "H100", "on_demand", "p", "p:a", 2.0) for d in days]
    rows += [(d, "H100", "on_demand", "p", "p:b", 1.0) for d in days[3:]]  # appears on day 4
    df = pd.DataFrame(
        rows, columns=["as_of_date", "gpu_model", "term", "provider", "listing_id", "price"]
    )
    w, owner = log_wide(df, "H100", "on_demand")
    chg = provider_change(w, owner, 1)
    assert np.allclose(chg["p"].dropna().to_numpy(), 0.0)


def test_gd_series_marks_a_missing_week_as_gap() -> None:
    gd = pd.DataFrame(
        {
            "week": [date(2026, 1, 5), date(2026, 1, 12), date(2026, 1, 26)],
            "gpu_model": "H100",
            "term": "on_demand",
            "value": [3.0, 3.1, 3.2],
            "n_listings": [10.0, 11.0, 12.0],
        }
    )
    s = gd_series(gd, "H100", "on_demand", "value")
    assert len(s) == 4
    assert np.isnan(s.iloc[2])


# ---------------------------------------------------------------------------
# Planted effects and the null world
# ---------------------------------------------------------------------------
def test_null_world_has_no_survivor(cfg: Config, ecfg: ExplorationConfig) -> None:
    results = _explore(cfg, ecfg, _data(cfg, 7))
    assert [r.hid for r in results if r.survives] == []
    assert len(results) == 12


def test_planted_effects_are_found(cfg: Config, ecfg: ExplorationConfig) -> None:
    results = {r.hid: r for r in _explore(cfg, ecfg, _data(cfg, 7, frozenset({"H01", "H09"})))}
    assert results["H09"].survives and results["H09"].slope > 0
    assert results["H01"].survives and results["H01"].slope < 0
    # H10's signal contains minus H100's own past change: the echo filter rejects it.
    assert results["H10"].q <= ecfg.fdr_q
    assert not results["H10"].survives


def test_planted_leadership_has_the_right_sign(cfg: Config, ecfg: ExplorationConfig) -> None:
    for seed in (7, 8, 9):
        r = _explore(cfg, ecfg, _data(cfg, seed, frozenset({"H02"})))[1]
        assert r.hid == "H02" and r.slope > 0


def test_not_testable_counts_as_p_one(ecfg: ExplorationConfig) -> None:
    rs = [Result(h, SPECS[h].kind) for h in SPECS]
    for r in rs:
        r.sufficient, r.p_hac, r.p_perm, r.slope = True, 0.5, 0.5, 1.0
    rs[0].p_hac, rs[0].p_perm, rs[0].echo_t, rs[0].echo_slope = 0.001, 0.01, 2.0, 1.0
    rs[1].p_hac, rs[1].sufficient = 0.0001, False  # tiny p, but not testable
    apply_round(rs, ecfg)
    assert rs[0].q == pytest.approx(0.001 * 12 / 1)
    assert rs[0].survives
    assert not rs[1].survives
    assert ranked_survivors(rs, 3) == [rs[0]]


def test_echo_filter_rejects_own_momentum(ecfg: ExplorationConfig) -> None:
    rng = np.random.default_rng(1)
    own = rng.normal(0, 1, 400)
    y = 0.8 * own + rng.normal(0, 0.3, 400)
    x = own + rng.normal(0, 0.05, 400)  # the signal is only the target's own past
    frame = pd.DataFrame({"t": pd.RangeIndex(400), "x": x, "y": y, "ctrl": own})
    r = ts_test(Built(frame, 400), SPECS["H06"], ecfg, seed=1)
    assert r.p_hac < 1e-6
    assert abs(r.echo_t) < 3  # most of the slope disappears once own past is removed
    apply_round([r] + [Result(h, SPECS[h].kind) for h in SPECS if h != "H06"], ecfg)
    assert r.q <= ecfg.fdr_q


# ---------------------------------------------------------------------------
# Confirmation
# ---------------------------------------------------------------------------
def test_confirmation_passes_a_real_effect_and_rejects_noise(
    cfg: Config, ecfg: ExplorationConfig
) -> None:
    assert cfg.claim4 is not None
    planted = _data(cfg, 7, frozenset({"H09"}))
    res = {r.hid: r for r in _explore(cfg, ecfg, planted)}
    fz = freeze(res["H09"])
    conf = planted.restrict(ecfg, "confirm")
    good = confirm_one(build("H09", conf, ecfg, cfg.claim4), fz, ecfg)
    null_conf = _data(cfg, 11).restrict(ecfg, "confirm")
    bad = confirm_one(build("H09", null_conf, ecfg, cfg.claim4), fz, ecfg)
    rows = finish_confirmation([good, bad], ecfg)
    assert rows[0].confirmed and rows[0].oos_r2_zero > 0
    assert not rows[1].confirmed
    assert rows[1].oos_r2_zero < 0


def test_confirmation_is_one_shot(cfg: Config, tmp_path: pytest.TempPathFactory) -> None:
    c = cfg.model_copy(update={"project": cfg.project.model_copy(update={"reports_dir": tmp_path})})
    p = xp.paths(c)
    p["dir"].mkdir(parents=True)
    p["confirm_json"].write_text("{}")
    with pytest.raises(FileExistsError):
        xp.run_confirmation(c)
    p["frozen"].write_text("{}")
    with pytest.raises(FileExistsError):
        xp.run_freeze(c)


def test_cli_has_explore_command() -> None:
    args = _parser().parse_args(["explore", "round1", "exploration"])
    assert (args.command, args.round, args.stage) == ("explore", "round1", "exploration")


def test_reports_label_results_exploratory(cfg: Config, ecfg: ExplorationConfig) -> None:
    results = _explore(cfg, ecfg, _data(cfg, 7))
    md = xp.render_exploration(results, {}, ecfg)
    assert "EXPLORATORY" in md and "exploratory" in md
    assert md.count("| H") == 12
