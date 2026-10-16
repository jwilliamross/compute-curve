"""Claim 9 rules on hand-made quotes and trades (no real data)."""

import numpy as np
import pandas as pd

from compute_curve import kalshi as k


def test_fee_rounds_up_to_the_cent() -> None:
    assert k.fee(0.10) == 0.01  # 0.0063 -> 0.01
    assert k.fee(0.50) == 0.02  # 0.0175 -> 0.02
    assert k.fee(0.97) == 0.01


def _c(ts: int, bid: str | None, ask: str | None) -> dict:
    return {
        "end_period_ts": ts,
        "yes_bid": {"close_dollars": bid},
        "yes_ask": {"close_dollars": ask},
    }


def test_decision_quote_uses_last_candle_two_days_before_close() -> None:
    close = 10 * 86400
    cs = [_c(5 * 86400, "0.10", "0.12"), _c(8 * 86400, "0.15", "0.18"), _c(9 * 86400, "0.5", "0.6")]
    q = k.decision_quote(cs, close)
    assert q is not None and q["bid"] == 0.15 and q["ask"] == 0.18
    assert k.decision_quote([_c(9 * 86400, "0.1", "0.2")], close) is None
    assert k.decision_quote([_c(1, None, "0.2")], close) is None
    assert k.decision_quote([_c(1, "0.3", "0.2")], close) is None  # crossed


def test_trade_rules_and_pnl() -> None:
    t = k.trade({"bid": 0.10, "ask": 0.12}, "no")
    assert t is not None and t["side"] == "no" and t["win"]
    assert abs(t["pnl"] - (1 - 0.90 - k.fee(0.90))) < 1e-12
    t2 = k.trade({"bid": 0.84, "ask": 0.86}, "no")
    assert t2 is not None and t2["side"] == "yes" and t2["pnl"] < 0
    assert k.trade({"bid": 0.40, "ask": 0.45}, "yes") is None
    assert k.trade({"bid": 0.01, "ask": 0.02}, "no") is None  # below the longshot band
    assert t["pnl_stress"] < t["pnl"]


def _trades(n_dates: int, pnl: float) -> pd.DataFrame:
    days = pd.date_range("2026-08-01", periods=n_dates, freq="7D", tz="UTC")
    rows = []
    for i, d in enumerate(days):
        for j in range(2):
            rows.append(
                {
                    "close_time": d.isoformat(),
                    "pnl": pnl + 0.01 * ((i + j) % 3 - 1),
                    "pnl_stress": pnl - 0.02,
                    "win": True,
                    "side": "no",
                    "bid": 0.1,
                    "ask": 0.12,
                    "result": "no",
                    "decision_ts": d.timestamp() - 3 * 86400,
                }
            )
    return pd.DataFrame(rows)


def test_kb1_test_detects_positive_edge_and_respects_minimum() -> None:
    res = k.kb1_test(_trades(12, 0.05), 10, seed=1)
    assert res["n_dates"] == 12 and res["verdict"] == "pass" and res["ci95_per_date"][0] > 0
    assert k.kb1_test(_trades(5, 0.05), 10, seed=1)["verdict"] == "too little history to conclude"
    neg = k.kb1_test(_trades(12, -0.05), 10, seed=1)
    assert neg["verdict"] == "not confirmed"


def test_split_and_calibration() -> None:
    t = _trades(10, 0.0)  # last close 2026-10-03, before the retrospective cut-off
    retro, fwd = k.split(t)
    assert len(retro) == len(t) and fwd.empty
    t["result"] = np.where(np.arange(len(t)) % 5 == 0, "yes", "no")
    c = k.calibration(t)
    assert c["n"] == len(t) and 0 <= c["brier"] <= 1 and c["table"][0]["bucket"] == "0.1-0.2"
