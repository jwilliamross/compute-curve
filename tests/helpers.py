"""Hand-built SYNTHETIC markets for engine tests. Not market data."""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd

from compute_curve.paper.market import MarketData

INDEX = "SYNTHETIC Silicon Data H100 Rental Index"


def settlements(rows: list[tuple[date, str, float]], product: str = "GPU1") -> pd.DataFrame:
    df = pd.DataFrame(rows, columns=["trade_date", "contract_month", "settle_price"])
    df["product"] = product
    df["ts_available"] = (
        pd.to_datetime(df["trade_date"]).dt.tz_localize("UTC")
        + pd.Timedelta(days=1)
        - pd.Timedelta(microseconds=1)
    )
    df["is_synthetic"] = True
    return df


def index_frame(values: dict[date, float], name: str = INDEX, lag_days: int = 1) -> pd.DataFrame:
    days = sorted(values)
    df = pd.DataFrame({"index_name": name, "as_of_date": days, "value": [values[d] for d in days]})
    df["ts_available"] = pd.to_datetime(df["as_of_date"]).dt.tz_localize("UTC") + pd.Timedelta(
        days=lag_days
    )
    df["is_synthetic"] = True
    return df


def weekdays(start: date, end: date) -> list[date]:
    out = []
    d = start
    while d <= end:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return out


def flat_curve_market(start: date, end: date, months: list[str], price: float = 2.0) -> MarketData:
    rows = [(d, m, price) for d in weekdays(start, end) for m in months]
    return MarketData.build(settlements=settlements(rows))
