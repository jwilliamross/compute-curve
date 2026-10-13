"""Claim 7 futures-premium logic on hand-made settlement frames (labelled synthetic)."""

from datetime import UTC, date, datetime
from pathlib import Path

import pandas as pd
import pytest

from compute_curve.config import load_config
from compute_curve.futures_premium import (
    curve_before,
    decide,
    decision_days,
    evaluate,
    index_before,
    leg_cost,
    observations,
    premia_today,
    realized,
    run_shadow,
)

CFG = load_config()


def _settle(rows: list[tuple[str, str, date, float]]) -> pd.DataFrame:
    df = pd.DataFrame(rows, columns=["product", "contract_month", "trade_date", "settle_price"])
    df["ts_available"] = (
        pd.to_datetime(df["trade_date"]).dt.tz_localize("UTC")
        + pd.Timedelta(days=1)
        - pd.Timedelta(microseconds=1)
    )
    df["is_synthetic"] = True
    return df


def _pub(name: str, d: date, v: float) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "index_name": [name],
            "as_of_date": [d],
            "value": [v],
            "ts_available": [
                pd.Timestamp(datetime(d.year, d.month, d.day, tzinfo=UTC)) + pd.Timedelta(days=1)
            ],
            "is_synthetic": [True],
        }
    )


# Decision day 2027-02-01 (Monday): M1 = 2027-03, M2 = 2027-04 (February is averaging).
SETTLE = _settle(
    [
        ("GPU1", "2027-03", date(2027, 1, 29), 3.30),
        ("GPU1", "2027-04", date(2027, 1, 29), 3.52),
        ("GPU1", "2027-03", date(2027, 2, 1), 9.99),  # same day: must be ignored
        ("GPU1", "2027-03", date(2027, 3, 31), 3.00),  # last trading day of Mar: final
        ("GPU1", "2027-04", date(2027, 4, 30), 3.30),  # last trading day of Apr: final
    ]
)
PUB = _pub("SDH100RT", date(2027, 1, 29), 3.00)


def test_decision_days_are_first_business_days() -> None:
    assert decision_days(date(2027, 1, 1), date(2027, 5, 31)) == [
        date(2027, 1, 1), date(2027, 2, 1), date(2027, 3, 1), date(2027, 4, 1), date(2027, 5, 3),
    ]  # fmt: skip


def test_curve_uses_only_settlements_usable_before_the_day() -> None:
    c = curve_before(SETTLE, "GPU1", date(2027, 2, 1))
    assert c["2027-03"] == 3.30 and c["2027-04"] == 3.52
    assert index_before(PUB, "SDH100RT", date(2027, 2, 1)) == 3.00
    assert index_before(PUB, "SDH100RT", date(2027, 1, 29)) is None  # lag not yet passed


def test_realized_is_the_last_trading_day_settle() -> None:
    assert realized(SETTLE, "GPU1", date(2027, 3, 1)) == 3.00
    assert realized(SETTLE, "GPU1", date(2027, 5, 1)) is None


def test_leg_cost_matches_the_cost_assumptions() -> None:
    spec = CFG.contracts["GPU1"]
    assert leg_cost(spec, CFG.costs) == pytest.approx(7 * 0.01 * 730 + 5.50 + 2.50 + 1.35)


def test_decide_sells_rich_and_buys_cheap() -> None:
    assert decide(0.06, 0.05) == -1 and decide(-0.06, 0.05) == 1 and decide(0.01, 0.05) == 0


def test_observations_compute_pre_registered_pnl() -> None:
    rows = observations(SETTLE, PUB, CFG, date(2027, 5, 31))
    a = next(r for r in rows if r["strategy"] == "FP-A" and r["decision_day"] == "2027-02-01")
    cost = leg_cost(CFG.contracts["GPU1"], CFG.costs)
    assert a["position"] == -1  # ln(3.30/3.00) = 0.095 > 0.05
    assert a["pnl"] == pytest.approx(0.30 * 730 - cost)
    b = next(r for r in rows if r["strategy"] == "FP-B" and r["decision_day"] == "2027-02-01")
    assert b["position"] == -1  # ln(3.52/3.30) = 0.065 > 0.03: short M2, long M1
    # (A2 - F2) - (A1 - F1) = (3.30 - 3.52) - (3.00 - 3.30) = 0.08; position -1
    assert b["pnl"] == pytest.approx(-0.08 * 730 - 2 * cost)


def test_without_published_index_only_the_calendar_strategy_exists() -> None:
    rows = observations(SETTLE, PUB.iloc[0:0], CFG, date(2027, 5, 31))
    assert {r["strategy"] for r in rows} == {"FP-B"}
    p = premia_today(SETTLE, PUB.iloc[0:0], CFG, date(2027, 2, 1))
    assert p[0]["pi_outright"] is None and p[0]["slope_m2_m1"] == pytest.approx(0.0645, abs=1e-3)


def test_evaluation_waits_then_runs_once_with_holm() -> None:
    few = [{"strategy": "FP-A", "decision_day": f"2027-{i:02d}-01", "pnl": 100.0,
            "pnl_stress": 40.0} for i in range(1, 6)]  # fmt: skip
    assert evaluate(few, date(2027, 6, 1))["due"] is False
    many = [{"strategy": "FP-A", "decision_day": f"2027-{i:02d}-01", "pnl": 100.0 + 10 * (i % 3),
             "pnl_stress": 40.0} for i in range(1, 13)]  # fmt: skip
    out = evaluate(many, date(2028, 1, 2))
    assert out["due"] and out["strategies"]["FP-A"]["verdict"] == "pass"
    assert out["strategies"]["FP-B"]["verdict"] == "too little history to conclude"


def test_run_shadow_end_to_end_in_a_temp_dir(tmp_path: Path) -> None:
    base = tmp_path
    proj = CFG.project.model_copy(
        update={
            "data_dir": base / "data",
            "reports_dir": base / "reports",
            "var_dir": base / "var",
        }
    )
    cfg = CFG.model_copy(update={"project": proj})
    folder = base / "data" / "manual" / "cme_settlements"
    folder.mkdir(parents=True)
    SETTLE.loc[:, ["product", "contract_month", "trade_date", "settle_price"]].to_csv(
        folder / "synthetic_test.csv", index=False
    )
    md = run_shadow(cfg, date(2027, 5, 31))
    text = md.read_text()
    assert "FP-B: 1 settled traded decisions" in text
    log = (base / "reports" / "futures_premium" / "decisions.csv").read_text()
    assert "3.52" not in log and "3.3" not in log.split("\n")[1]  # no prices stored
