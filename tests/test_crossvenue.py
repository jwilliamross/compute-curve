"""FP-K and the Kalshi implied median on hand-made inputs (no real data)."""

from datetime import UTC, date, datetime

import pandas as pd

from compute_curve import crossvenue as cv
from compute_curve import kalshi as k
from compute_curve.config import load_config


def _m(strike: float, bid: float, ask: float) -> dict:
    return {
        "strike_type": "greater",
        "floor_strike": strike,
        "yes_bid_dollars": str(bid),
        "yes_ask_dollars": str(ask),
    }


def test_implied_median_interpolates_and_filters() -> None:
    ms = [_m(2.5, 0.88, 0.92), _m(2.75, 0.68, 0.72), _m(3.0, 0.28, 0.32), _m(3.25, 0.05, 0.09)]
    r = k.implied_median(ms)
    assert r is not None and abs(r["implied_median"] - 2.875) < 1e-9 and r["n_strikes"] == 4
    wide = [_m(2.5, 0.1, 0.9), _m(2.75, 0.1, 0.9), _m(3.0, 0.1, 0.9)]
    assert k.implied_median(wide) is None


def test_quote_age_and_decision() -> None:
    curve = pd.DataFrame(
        [
            {"date": "2026-10-28", "series": "KXH100MS", "month": "2026-12", "implied_median": 2.9},
            {"date": "2026-10-31", "series": "KXH100MS", "month": "2026-12", "implied_median": 3.0},
        ]
    )
    assert cv.kalshi_quote(curve, "2026-12", date(2026, 11, 2)) == 3.0
    assert cv.kalshi_quote(curve, "2026-12", date(2026, 11, 10)) is None  # too old
    assert cv.decide(3.3, 3.0) == -1 and cv.decide(2.7, 3.0) == 1 and cv.decide(3.1, 3.0) == 0


def test_observations_trade_and_settle() -> None:
    cfg = load_config()
    rows = [
        ("GPU1", "2026-12", date(2026, 10, 30), 3.30),
        ("GPU1", "2026-12", date(2026, 12, 31), 3.00),
    ]
    settle = pd.DataFrame(rows, columns=["product", "contract_month", "trade_date", "settle_price"])
    settle["ts_available"] = [
        pd.Timestamp(datetime(d.year, d.month, d.day, 23, 59, 59, tzinfo=UTC))
        for d in settle["trade_date"]
    ]
    curve = pd.DataFrame(
        [{"date": "2026-11-01", "series": "KXH100MS", "month": "2026-12", "implied_median": 3.0}]
    )
    obs = cv.observations(settle, curve, cfg, date(2026, 11, 2))
    assert len(obs) == 1 and obs[0]["position"] == -1
    assert abs(obs[0]["pnl"] - (0.30 * 730 - 60.45)) < 1e-6
    assert cv.evaluate(obs, date(2027, 1, 1))["due"] is False
