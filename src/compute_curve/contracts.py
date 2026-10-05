"""Contract calendar and final-settlement arithmetic for GPU1 / GPU2.

Assumptions (unverified, see ``docs/contract_specs.md``):

* Each contract references one calendar month ``M``.
* Final settlement = arithmetic mean of the daily index over the days of
  ``M`` (calendar or business days per ``ContractSpec.settlement_days``).
* Trading terminates on the last business day of ``M``. Exchange holidays
  are not modelled.
* A day in ``M`` with no published index value takes the most recent prior
  published value (carry-forward). This mirrors common index-average
  contracts but is not verified for GPU1/GPU2.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import numpy as np
import pandas as pd

from compute_curve.config import ContractSpec
from compute_curve.timeutil import add_months, month_days, month_start


@dataclass(frozen=True, order=True)
class ContractMonth:
    product: str
    month: date  # first day of the contract month

    @property
    def code(self) -> str:
        return f"{self.month:%Y-%m}"

    @property
    def key(self) -> tuple[str, str]:
        return (self.product, self.code)


def parse_month(code: str) -> date:
    y, m = code.split("-")
    return date(int(y), int(m), 1)


def last_trading_day(month: date) -> date:
    """Last Monday-Friday day of the contract month (assumption)."""
    return month_days(month, business_days_only=True)[-1]


def listed_contracts(spec: ContractSpec, trade_date: date) -> list[ContractMonth]:
    """Contract months open for trading on ``trade_date``.

    The front month is the current calendar month until its last trading day,
    then the next month. ``spec.listed_months`` consecutive months are listed.
    """
    front = month_start(trade_date)
    if trade_date > last_trading_day(front):
        front = add_months(front, 1)
    return [ContractMonth(spec.product, add_months(front, i)) for i in range(spec.listed_months)]


def settlement_days(spec: ContractSpec, month: date) -> list[date]:
    return month_days(month, business_days_only=spec.settlement_days == "business")


def daily_values_for_month(
    index: pd.Series, spec: ContractSpec, month: date, through: date | None = None
) -> tuple[pd.Series, int]:
    """Index values on the averaging days of ``month`` up to ``through``.

    ``index`` is a Series of published values keyed by ``as_of_date``. Missing
    averaging days carry forward the latest earlier value. Returns the
    filled series and the number of days that had to be carried forward.
    Days before the first available value are left out.
    """
    days = [d for d in settlement_days(spec, month) if through is None or d <= through]
    if not days:
        return pd.Series(dtype=float), 0
    s = index.sort_index()
    s = s[s.index <= days[-1]]
    values: dict[date, float] = {}
    carried = 0
    for d in days:
        if d in s.index:
            values[d] = float(s.loc[d])
        else:
            prior = s[s.index < d]
            if prior.empty:
                continue
            values[d] = float(prior.iloc[-1])
            carried += 1
    return pd.Series(values, dtype=float), carried


def month_to_date_average(
    index: pd.Series, spec: ContractSpec, month: date, through: date
) -> tuple[float | None, int]:
    """Mean of the averaging-day values in ``month`` observed through ``through``."""
    vals, _ = daily_values_for_month(index, spec, month, through)
    if vals.empty:
        return None, 0
    return float(vals.mean()), len(vals)


def final_settlement(
    index: pd.Series, spec: ContractSpec, month: date, max_carried_days: int = 3
) -> float | None:
    """Final settlement price of the contract month, or None if not yet determinable.

    Returns None if the last averaging day has no value yet or if more than
    ``max_carried_days`` days would need carry-forward (data too sparse to
    settle credibly in simulation).
    """
    days = settlement_days(spec, month)
    s = index.sort_index()
    if s.empty or s.index.max() < days[-1]:
        return None
    vals, carried = daily_values_for_month(s, spec, month)
    if len(vals) < len(days) or carried > max_carried_days:
        return None
    return float(np.mean(vals.to_numpy()))
