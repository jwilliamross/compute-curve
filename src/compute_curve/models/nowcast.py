"""Nowcast of the month-average settlement index (claim 1).

Target: ``F_M``, the arithmetic mean of the published daily index over the
averaging days of contract month ``M`` (see ``contracts.final_settlement``).

At decision time ``t`` (end of a calendar day) the information set is:

* published index values with ``ts_available <= t`` (publication lag applies),
* our own index values with ``ts_available <= t`` (observed the same day).

Methods (pre-registered; see ``docs/research_plan.md``):

* ``mtd_carry`` (baseline, from the brief): the month-to-date average of the
  known published values, carried forward. Before any value of ``M`` is known,
  the latest published value.
* ``last_value`` (stronger naive baseline): known days at their values, every
  unknown day at the latest published value.
* ``own_bridge`` (model, primary): known days at their values; unknown days
  up to ``t`` and all future days at the latest published value scaled by the
  change in our own index since that value's date. No fitted parameters.

A model is "validated" only if it beats the *stronger* of the two baselines
out of sample with a month-clustered bootstrap CI that excludes zero.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, timedelta

import numpy as np
import pandas as pd

from compute_curve.config import ContractSpec
from compute_curve.contracts import final_settlement, settlement_days
from compute_curve.paper.market import MarketData, MarketView
from compute_curve.timeutil import end_of_day_utc

METHODS: tuple[str, ...] = ("mtd_carry", "last_value", "own_bridge")
BASELINES: tuple[str, ...] = ("mtd_carry", "last_value")


@dataclass(frozen=True)
class NowcastInputs:
    month: date
    as_of: date
    averaging_days: list[date]
    known: pd.Series  # published values for averaging days available at as_of
    last_pub_date: date | None
    last_pub_value: float | None
    own: pd.Series  # own index values available at as_of


def gather_inputs(
    view: MarketView, spec: ContractSpec, gpu_model: str, month: date
) -> NowcastInputs:
    pub = view.published_index(spec.underlying_index)
    days = settlement_days(spec, month)
    known = pub[[d in set(days) for d in pub.index]] if not pub.empty else pub
    last_d = pub.index[-1] if not pub.empty else None
    last_v = float(pub.iloc[-1]) if not pub.empty else None
    return NowcastInputs(
        month=month,
        as_of=view.as_of.date(),
        averaging_days=days,
        known=known,
        last_pub_date=last_d,
        last_pub_value=last_v,
        own=view.own_index(gpu_model),
    )


def predict_mtd_carry(inp: NowcastInputs) -> float | None:
    if not inp.known.empty:
        return float(inp.known.mean())
    return inp.last_pub_value


def predict_last_value(inp: NowcastInputs) -> float | None:
    if inp.last_pub_value is None:
        return None
    n = len(inp.averaging_days)
    return float((inp.known.sum() + (n - len(inp.known)) * inp.last_pub_value) / n)


def own_bridge_level(inp: NowcastInputs) -> float | None:
    """Latest published value scaled by our index's change since that date.

    Returns None if our index has no value on or before both dates (no bridge).
    """
    if inp.last_pub_value is None or inp.last_pub_date is None or inp.own.empty:
        return None
    own = inp.own.sort_index()
    base = own[own.index <= inp.last_pub_date]
    if base.empty:
        return None
    ratio = float(own.iloc[-1]) / float(base.iloc[-1])
    return inp.last_pub_value * ratio


def predict_own_bridge(inp: NowcastInputs) -> float | None:
    level = own_bridge_level(inp)
    if level is None:
        return None
    n = len(inp.averaging_days)
    return float((inp.known.sum() + (n - len(inp.known)) * level) / n)


PREDICTORS = {
    "mtd_carry": predict_mtd_carry,
    "last_value": predict_last_value,
    "own_bridge": predict_own_bridge,
}


def nowcast_all(
    view: MarketView, spec: ContractSpec, gpu_model: str, month: date
) -> dict[str, float | None]:
    inp = gather_inputs(view, spec, gpu_model, month)
    return {m: f(inp) for m, f in PREDICTORS.items()}


def evaluate(
    market: MarketData,
    spec: ContractSpec,
    gpu_model: str,
    months: Sequence[date],
    start_offset_days: int = -5,
) -> pd.DataFrame:
    """Walk-forward predictions for each month and each decision day.

    Decision days run from ``month start + start_offset_days`` to the day
    before the last averaging day. The realized target uses the full
    published history (it is only used for scoring, never as an input).
    """
    full = market.full_published_series(spec.underlying_index)
    rows: list[dict[str, object]] = []
    for month in months:
        target = final_settlement(full, spec, month)
        if target is None:
            continue
        days = settlement_days(spec, month)
        d = month + timedelta(days=start_offset_days)
        while d < days[-1]:
            view = market.view(end_of_day_utc(d))
            preds = nowcast_all(view, spec, gpu_model, month)
            for method, pred in preds.items():
                if pred is None:
                    continue
                rows.append(
                    {
                        "month": month,
                        "decision_date": d,
                        "days_to_end": (days[-1] - d).days,
                        "method": method,
                        "pred": pred,
                        "target": target,
                        "log_error": float(np.log(pred) - np.log(target)),
                    }
                )
            d += timedelta(days=1)
    return pd.DataFrame(rows)


def cluster_bootstrap_diff(
    errors: pd.DataFrame,
    model: str,
    baseline: str,
    n_boot: int = 2000,
    confidence: float = 0.95,
    seed: int = 0,
) -> dict[str, float]:
    """Mean squared-log-error difference (model - baseline), months resampled.

    Only decision points where both methods produced a prediction are used.
    """
    wide = errors.pivot_table(
        index=["month", "decision_date"], columns="method", values="log_error"
    ).dropna(subset=[model, baseline])
    if wide.empty:
        return {"n_months": 0, "n_points": 0}
    diff = (wide[model] ** 2 - wide[baseline] ** 2).groupby(level="month")
    per_month_sum = diff.sum()
    per_month_n = diff.count()
    months = per_month_sum.index.to_numpy()
    rng = np.random.default_rng(seed)
    stats = np.empty(n_boot)
    for i in range(n_boot):
        pick = rng.integers(0, len(months), len(months))
        stats[i] = per_month_sum.iloc[pick].sum() / per_month_n.iloc[pick].sum()
    alpha = (1 - confidence) / 2
    lo, hi = np.quantile(stats, [alpha, 1 - alpha])
    return {
        "n_months": len(months),
        "n_points": int(per_month_n.sum()),
        "mean_diff": float(per_month_sum.sum() / per_month_n.sum()),
        "ci_low": float(lo),
        "ci_high": float(hi),
    }
