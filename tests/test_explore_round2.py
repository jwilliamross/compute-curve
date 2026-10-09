"""Exploration round 2: builders, mechanism test, walk-forward, replication. SYNTHETIC data."""

from __future__ import annotations

import json
from dataclasses import asdict

import numpy as np
import pandas as pd
import pytest

from compute_curve.config import Config, ExplorationConfig, Round2Config, load_config
from compute_curve.explore.data import Round1Data, in_set
from compute_curve.explore.hypotheses import Built
from compute_curve.explore.pipeline import explore
from compute_curve.explore.round2 import (
    R2_SPECS,
    explore2,
    r2_02,
    replicate_h01,
    residualize,
    walk_forward,
)
from compute_curve.synthetic import synthetic_round1


@pytest.fixture(scope="module")
def cfg() -> Config:
    return load_config()


@pytest.fixture(scope="module")
def ecfg(cfg: Config) -> ExplorationConfig:
    assert cfg.exploration is not None
    return cfg.exploration.model_copy(update={"n_boot": 200})


@pytest.fixture(scope="module")
def r2cfg(cfg: Config) -> Round2Config:
    assert cfg.exploration2 is not None
    return cfg.exploration2


def _data(cfg: Config, seed: int, plant: frozenset[str] = frozenset()) -> Round1Data:
    assert cfg.claim4 is not None
    f = synthetic_round1(seed, plant, cfg.claim4.universe.buckets(), cfg.claim4.benchmark)
    assert all(bool(df["is_synthetic"].all()) for df in f.values())
    return Round1Data(**{k: v for k, v in f.items()})


def test_round2_inputs_leave_round1_unchanged(cfg: Config, ecfg: ExplorationConfig) -> None:
    """Adding provider counts and the reservation series must not move round-1 results."""
    assert cfg.claim4 is not None
    data = _data(cfg, 7)
    plain = Round1Data(
        listings=data.listings,
        cgi=data.cgi.drop(columns=["n_providers"]),
        gd=data.gd.loc[data.gd["term"] != "reserved_12m"],
        aws=data.aws,
        bars=data.bars,
    )
    a, _ = explore(data, ecfg, cfg.claim4, seed=1)
    b, _ = explore(plain, ecfg, cfg.claim4, seed=1)
    assert json.dumps([asdict(r) for r in a], default=str) == json.dumps(
        [asdict(r) for r in b], default=str
    )


def test_four_exploratory_tests_and_no_survivor_in_null(
    cfg: Config, ecfg: ExplorationConfig, r2cfg: Round2Config
) -> None:
    results, extra = explore2(_data(cfg, 7), ecfg, r2cfg, seed=1)
    assert [r.hid for r in results] == ["R2-02", "R2-03", "R2-04", "R2-06"]
    assert not any(r.survives for r in results)
    assert extra["R2-04_n_oos"] >= r2cfg.min_oos


def test_planted_provider_churn_reversal_is_found(
    cfg: Config, ecfg: ExplorationConfig, r2cfg: Round2Config
) -> None:
    results, extra = explore2(_data(cfg, 7, frozenset({"R2-02"})), ecfg, r2cfg, seed=1)
    r = results[0]
    assert extra["R2-02_D_windows"] >= r2cfg.min_provider_change_windows
    assert r.slope < 0 and r.p_hac < 0.01


def test_planted_aws_persistence_beats_zero_walk_forward(
    cfg: Config, ecfg: ExplorationConfig, r2cfg: Round2Config
) -> None:
    results, _ = explore2(_data(cfg, 7, frozenset({"H09"})), ecfg, r2cfg, seed=1)
    r04 = results[2]
    assert r04.survives and r04.ci_lo > 0 and r04.ci_hi > 0


def test_walk_forward_uses_only_known_outcomes() -> None:
    t = pd.date_range("2025-01-01", periods=200, freq="D")
    rng = np.random.default_rng(0)
    frame = pd.DataFrame({"t": t, "x": rng.normal(size=200), "y": rng.normal(size=200)})
    fc = walk_forward(frame, pd.Timedelta(days=7), 60)
    bad = frame.copy()
    cut = bad["t"] > t[120]
    bad.loc[cut, "y"] = 1e6  # poison outcomes after day 120
    fc2 = walk_forward(bad, pd.Timedelta(days=7), 60)
    early = fc["t"] <= t[127]  # forecasts at t use outcomes up to t - 7
    assert np.allclose(fc.loc[early, "forecast"], fc2.loc[early, "forecast"])


def test_residualize_removes_the_control() -> None:
    rng = np.random.default_rng(1)
    c = rng.normal(size=300)
    frame = pd.DataFrame({"t": range(300), "x": 2 * c + rng.normal(size=300), "y": c, "ctrl": c})
    r = residualize(frame)
    assert abs(np.corrcoef(r["x"], c)[0, 1]) < 1e-8
    assert np.allclose(r["y"], 0, atol=1e-10)


def test_r2_02_counts_provider_change_windows(cfg: Config, ecfg: ExplorationConfig) -> None:
    exp = _data(cfg, 3).restrict(ecfg, "explore")
    built, d = r2_02(exp, ecfg)
    assert isinstance(built, Built) and d > 0
    assert set(R2_SPECS) == {"R2-02", "R2-03", "R2-04", "R2-06"}


def test_replication_uses_only_the_listings_confirmation_set(
    cfg: Config, ecfg: ExplorationConfig
) -> None:
    data = _data(cfg, 5, frozenset({"H01"}))
    h01 = {
        "hid": "H01",
        "kind": "panel",
        "intercept": 0.0,
        "slope": -0.4,
        "slope_se": 0.05,
        "n": 900,
        "n_cross_sections": 51,
        "rho": -0.3,
        "y_mean": 0.0,
    }
    out = replicate_h01(data, h01, ecfg)
    first, last = (pd.Timestamp(x) for x in out["window"])
    split = ecfg.splits["listings"]
    assert in_set(pd.Series([first.date(), last.date()]), split, "confirm").all()
    assert out["c1"] and out["confirmed"]
