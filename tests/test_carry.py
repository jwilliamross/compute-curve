"""FP-D rules on hand-made settlements (no real data)."""

from datetime import UTC, date, datetime

import pandas as pd

from compute_curve import carry
from compute_curve.config import load_config


def _settle(rows: list[tuple[str, str, date, float]]) -> pd.DataFrame:
    df = pd.DataFrame(rows, columns=["product", "contract_month", "trade_date", "settle_price"])
    df["ts_available"] = [
        pd.Timestamp(datetime(d.year, d.month, d.day, 23, 59, 59, tzinfo=UTC))
        for d in df["trade_date"]
    ]
    return df


def test_go_long_only_in_backwardation_beyond_gap() -> None:
    assert (
        carry.go_long(2.80, 3.00) and not carry.go_long(2.90, 3.00) and not carry.go_long(3.3, 3.0)
    )


def test_futures_only_variant_trades_and_settles() -> None:
    cfg = load_config()
    rows = [
        ("GPU1", "2026-12", date(2026, 10, 30), 3.00),  # M1 for a 2026-11-02 decision
        ("GPU1", "2027-02", date(2026, 10, 30), 2.70),  # M3, 10% below M1
        ("GPU1", "2027-02", date(2027, 2, 26), 3.00),  # final settlement on the last trading day
    ]
    obs = carry.observations(_settle(rows), pd.DataFrame(), cfg, date(2026, 11, 2))
    assert len(obs) == 1
    o = obs[0]
    assert o["variant"] == "FP-D-F" and o["long"] and o["contract_month"] == "2027-02"
    assert abs(o["pnl"] - (0.30 * 730 - 60.45)) < 1e-6 and o["realized_premium"] > 0


def test_evaluate_waits_and_reports_premium() -> None:
    rows = [{"variant": "FP-D-F", "pnl": 10.0, "pnl_stress": 5.0, "realized_premium": 0.05}] * 3
    res = carry.evaluate(rows, date(2027, 1, 1))
    assert res["due"] is False and abs(res["mean_realized_premium"] - 0.05) < 1e-12
    assert carry.evaluate(rows, date(2028, 7, 1))["variants"]["FP-D-F"]["verdict"].startswith(
        "too little"
    )
