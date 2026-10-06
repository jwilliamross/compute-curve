"""Claim-5 evaluation end to end against the fake Alpaca. SYNTHETIC data; no network."""

from __future__ import annotations

import json
from datetime import date

import pandas as pd

from compute_curve.claim5 import pipeline as c5p
from compute_curve.synthetic import (
    synthetic_bars_json,
    synthetic_equity_bars,
    synthetic_spot_pools,
    synthetic_weekday_calendar,
)
from tests.test_claim4_pipeline import FakeAlpaca

NOW = pd.Timestamp("2026-10-06 23:40", tz="UTC")


def world(cfg, tmp_path):
    project = cfg.project.model_copy(
        update={"var_dir": tmp_path / "var", "reports_dir": tmp_path / "reports"}
    )
    boot = cfg.bootstrap.model_copy(update={"n_boot": 100})
    cfg = cfg.model_copy(update={"project": project, "bootstrap": boot})
    bc = c5p.battery_config(cfg)
    calendar = synthetic_weekday_calendar(date(2024, 9, 1), date(2026, 12, 31))
    sessions = pd.DataFrame(calendar)
    sessions["session"] = pd.to_datetime(sessions["date"]).dt.date
    past = sessions.loc[sessions["session"] <= date(2026, 10, 5), ["session"]].reset_index(
        drop=True
    )
    bars = synthetic_equity_bars(past, bc.universe.members(), bc.benchmark, seed=3)
    pools = synthetic_spot_pools(date(2024, 10, 1), date(2025, 6, 30), ("A100", "H100"), 4, seed=3)
    return cfg, FakeAlpaca(calendar, synthetic_bars_json(bars)), pools, bars


def test_member_start_drops_earlier_bars(cfg, tmp_path):
    _, _, _, bars = world(cfg, tmp_path)
    kept = c5p.apply_member_start(bars, {"NBIS": date(2024, 10, 21)})
    nbis = kept.loc[kept["symbol"] == "NBIS", "session"]
    assert nbis.min() >= date(2024, 10, 21)
    assert len(kept.loc[kept["symbol"] == "IREN"]) == len(bars.loc[bars["symbol"] == "IREN"])


def test_evaluation_runs_claim4_battery_and_keeps_the_gate(cfg, tmp_path):
    cfg, fake, pools, _ = world(cfg, tmp_path)
    paper, data = fake.clients()
    out = c5p.run_evaluation(cfg, now=NOW, paper=paper, data=data, pools=pools)
    text = out.read_text()
    assert "Claim 5 evaluation" in text and "Family P" in text
    bc = c5p.battery_config(cfg)
    assert bc.min_oos_forecasts == cfg.claim4.min_oos_forecasts  # gate unchanged
    assert bc.signals == cfg.claim5.signals
    validation = json.loads(c5p.paths(cfg)["validation"].read_text())
    assert set(validation["pairs"]) == {f"{s}|h{h}" for s in bc.signals for h in bc.horizons}
    sig = pd.read_csv(c5p.paths(cfg)["signals"])
    assert {"level_a100", "level_h100", "disp_a100", "disp_h100"} <= set(sig.columns)
    assert (
        sig.loc[pd.to_datetime(sig["session"]) > pd.Timestamp("2025-07-02"), "level_a100"]
        .isna()
        .all()
    )
    assert fake.posted == []  # evaluation never trades
