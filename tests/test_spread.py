"""Claim 8 spread rules on small hand-made frames (no real data)."""

from datetime import UTC, date, datetime

import numpy as np
import pandas as pd

from compute_curve import spread as sp
from compute_curve.config import load_config


def test_forecast_decide_and_size() -> None:
    assert sp.forecast(0.9, 0.7, 0.5) == 0.8
    assert sp.decide(0.06) == 1 and sp.decide(-0.06) == -1 and sp.decide(0.01) == 0
    assert (
        sp.notional_k(7.9, 3.5) == 2 and sp.notional_k(3.0, 3.0) == 1 and sp.notional_k(20, 3) == 3
    )


def test_spread_pnl_long_gpu2_profits_when_ratio_widens() -> None:
    # long 1 GPU2, short 2 GPU1; GPU2 settles 0.40 above, GPU1 0.10 above the entry price
    pnl = sp.spread_pnl(1, 2, 3.0, 7.0, 3.1, 7.4, 730.0, 60.45)
    assert abs(pnl - ((0.4 - 0.2) * 730 - 3 * 60.45)) < 1e-9
    assert sp.spread_pnl(-1, 2, 3.0, 7.0, 3.1, 7.4, 730.0, 0.0) < 0


def _pub(days: pd.DatetimeIndex, h: np.ndarray, b: np.ndarray) -> pd.DataFrame:
    rows = []
    for d, x, y in zip(days, h, b, strict=True):
        for name, v in (("SDH100RT", x), ("SDB200RT", y)):
            rows.append(
                {
                    "as_of_date": d.date(),
                    "index_name": name,
                    "value": v,
                    "ts_available": pd.Timestamp(d, tz="UTC") + pd.Timedelta(days=1),
                }
            )
    return pd.DataFrame(rows)


def test_index_ratio_history_respects_availability() -> None:
    days = pd.bdate_range("2026-01-05", periods=5)
    pub = _pub(days, np.full(5, 2.0), np.array([4.0, 4.0, 4.0, 4.0, 8.0]))
    r = sp.index_ratio_history(pub, date(2026, 1, 10))  # values through Jan 9 usable at Jan 10
    assert len(r) == 5 and abs(r.iloc[-1] - np.log(4.0)) < 1e-12
    r2 = sp.index_ratio_history(pub, date(2026, 1, 9))
    assert len(r2) == 4


def _settle(rows: list[tuple[str, str, date, float]]) -> pd.DataFrame:
    df = pd.DataFrame(rows, columns=["product", "contract_month", "trade_date", "settle_price"])
    df["ts_available"] = [
        pd.Timestamp(datetime(d.year, d.month, d.day, 23, 59, 59, tzinfo=UTC))
        for d in df["trade_date"]
    ]
    return df


def test_observations_trade_the_planted_reversion() -> None:
    cfg = load_config()
    # SD history: ratio long-run ln 2, currently ln 2.4 (B200 rich vs history).
    days = pd.bdate_range("2026-08-03", "2026-10-30")
    h = np.full(len(days), 3.0)
    b = np.full(len(days), 6.0)
    b[-5:] = 7.2
    pub = _pub(days, h, b)
    # Futures for 2027-01 priced at the current ratio (random walk): F1 3.0, F2 7.2.
    rows = [
        ("GPU1", "2027-01", date(2026, 10, 30), 3.0),
        ("GPU2", "2027-01", date(2026, 10, 30), 7.2),
        ("GPU1", "2027-01", date(2027, 1, 29), 3.0),  # last trading day of Jan 2027
        ("GPU2", "2027-01", date(2027, 1, 29), 6.6),  # ratio reverted part way
    ]
    obs = sp.observations(_settle(rows), pub, cfg, date(2026, 11, 2))
    sp_i = [o for o in obs if o["strategy"] == "SP-I"]
    assert len(sp_i) == 1
    o = sp_i[0]
    assert o["contract_month"] == "2027-01" and o["position"] == -1 and o["k"] == 2
    assert o["pnl"] > 0  # short GPU2 / long 2 GPU1 gains as the ratio falls
    assert not [x for x in obs if x["strategy"] == "SP-F"]  # too few front-month days


def test_evaluate_waits_then_requires_c0_and_profit() -> None:
    rows = [
        {"strategy": "SP-I", "pnl": 100.0, "pnl_stress": 50.0, "realized": 0.0, "forecast": 0.0,
         "random_walk": 0.0}
        for _ in range(3)
    ]  # fmt: skip
    assert sp.evaluate(rows, date(2027, 1, 1))["due"] is False
    out = sp.evaluate(rows, date(2028, 7, 1))
    assert out["strategies"]["SP-I"]["verdict"] == "too little history to conclude"


def test_sp0_forecasts_and_waiting() -> None:
    idx = pd.bdate_range("2026-08-03", periods=120)
    rng = np.random.default_rng(1)
    ratio = pd.Series(0.7 + rng.normal(0, 0.02, len(idx)), index=idx)
    fc = sp.sp0_forecasts(ratio)
    assert len(fc) == 100 and fc["outcome"].notna().sum() == 100 - 40
    assert sp.sp0_evaluate(fc, date(2027, 1, 1))["verdict"].startswith("waiting")
    res = sp.sp0_evaluate(fc, date(2027, 7, 1))
    assert res["verdict"] in {"pass", "not confirmed"}  # 60 outcomes: test runs
