"""Walk-forward term-structure evaluation for claim 2.

Pipeline at each refit date ``t`` (last trade date of each month):

1. Build the measurement panel from futures settlements available at ``t``:
   one slot per listed month whose averaging period has not started.
2. Fit the Schwartz-Smith model (with the configured depreciation prior and
   scheduled launch jumps) by maximum likelihood on that panel.
3. From the filtered state at ``t``, forecast the real-world expected final
   settlement of each of the next ``max_horizon`` contract months.
4. Score against realized final settlements and two baselines: the market's
   futures price at ``t`` and a random walk (latest index value).

Nothing here runs on real data until GPU1/GPU2 settlements exist.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, timedelta

import numpy as np
import pandas as pd

from compute_curve.config import ContractSpec, HardwareLaunch
from compute_curve.contracts import final_settlement, parse_month, settlement_days
from compute_curve.models.schwartz_smith import (
    SSParams,
    build_panel_design,
    expected_average_level,
    fit_panel,
    forecast_log_spot,
    kalman_filter,
    panel_measurement,
)
from compute_curve.paper.market import MarketData
from compute_curve.timeutil import add_months, end_of_day_utc, month_start

DAYS_PER_YEAR = 365.0


def launch_dates(launches: Sequence[HardwareLaunch], gpu_model: str) -> list[date]:
    """Scheduled jump dates that affect ``gpu_model``."""
    return sorted(x.window_start for x in launches if gpu_model in x.affects)


def jumps_between(t: date, days: Sequence[date], launches: Sequence[date]) -> np.ndarray:
    """For each day in ``days``, the number of launch dates in (t, day]."""
    lz = np.array([(x - t).days for x in launches], dtype=float)
    out = np.zeros(len(days))
    for i, d in enumerate(days):
        h = (d - t).days
        out[i] = float(np.sum((lz > 0) & (lz <= h)))
    return out


@dataclass(frozen=True)
class Panel:
    trade_dates: list[date]
    months: list[list[str | None]]  # contract month code per (t, slot)
    y: np.ndarray  # (T, n_slots) log settlement, NaN when absent
    design: object  # PanelDesign
    jump_steps: list[bool]  # scheduled jump between consecutive trade dates


def build_panel(
    settlements: pd.DataFrame,
    spec: ContractSpec,
    launches: Sequence[date],
    n_slots: int = 6,
    origin: date | None = None,
) -> Panel | None:
    """Measurement panel of log settlements for months not yet averaging."""
    s = settlements.loc[settlements["product"] == spec.product]
    if s.empty:
        return None
    trade = sorted(set(s["trade_date"]))
    # Calendar-day grid: the filter's transition assumes one-day steps, so
    # non-trading days are rows with no observations rather than skipped.
    dates = [trade[0] + timedelta(days=k) for k in range((trade[-1] - trade[0]).days + 1)]
    by_day = {d: g for d, g in s.groupby("trade_date")}
    origin = origin or dates[0]
    t_years = np.array([(d - origin).days / DAYS_PER_YEAR for d in dates])
    y = np.full((len(dates), n_slots), np.nan)
    months: list[list[str | None]] = []
    cells = []
    empty = s.iloc[0:0]
    for i, d in enumerate(dates):
        row = by_day.get(d, empty)
        future = sorted(m for m in row["contract_month"] if parse_month(m) > month_start(d))
        slot_months: list[str | None] = [None] * n_slots
        for j, cm in enumerate(future[:n_slots]):
            days = settlement_days(spec, parse_month(cm))
            grid = np.array([(x - d).days / DAYS_PER_YEAR for x in days])
            if np.any(grid <= 0):
                continue
            price = float(row.loc[row["contract_month"] == cm, "settle_price"].iloc[0])
            y[i, j] = np.log(price)
            slot_months[j] = cm
            cells.append((i, j, grid, jumps_between(d, days, launches)))
        months.append(slot_months)
    design = build_panel_design(t_years, cells, n_slots)
    jump_steps = [False] + [
        any(dates[k - 1] < x <= dates[k] for x in launches) for k in range(1, len(dates))
    ]
    return Panel(dates, months, y, design, jump_steps)


@dataclass(frozen=True)
class ForecastRow:
    refit_date: date
    contract_month: str
    horizon_months: int
    model: float
    futures: float
    random_walk: float


def forecast_months(
    params: SSParams,
    panel: Panel,
    upto: int,
    spec: ContractSpec,
    launches: Sequence[date],
    max_horizon: int,
    dt: float,
) -> list[tuple[str, int, float]]:
    """(month, horizon, E_P[F_M]) from the state filtered through index ``upto``."""
    d, Z = panel_measurement(params, panel.design)
    out = kalman_filter(
        panel.y[: upto + 1],
        np.nan_to_num(d[: upto + 1]),
        Z[: upto + 1],
        params,
        dt,
        panel.jump_steps[: upto + 1],
    )
    x, P = out.filtered_mean[-1], out.filtered_cov[-1]
    t = panel.trade_dates[upto]
    t_years = (t - panel.trade_dates[0]).days / DAYS_PER_YEAR
    res = []
    for h in range(1, max_horizon + 1):
        month = add_months(t, h)
        days = settlement_days(spec, month)
        horizons = [(x_ - t).days for x_ in days]
        jump_days = [(x_ - t).days for x_ in launches if x_ > t]
        m, v = forecast_log_spot(params, x, P, t_years, horizons, 1.0 / DAYS_PER_YEAR, jump_days)
        res.append((f"{month:%Y-%m}", h, expected_average_level(m, v)))
    return res


def walk_forward(
    market: MarketData,
    spec: ContractSpec,
    launches_cfg: Sequence[HardwareLaunch],
    base: SSParams,
    min_observations: int = 120,
    max_horizon: int = 6,
    maxiter: int = 1500,
) -> pd.DataFrame:
    """Monthly walk-forward forecasts scored against realized final settlements."""
    launches = launch_dates(launches_cfg, spec.gpu_model)
    full_index = market.full_published_series(spec.underlying_index)
    panel = build_panel(market.settlements, spec, launches)
    if panel is None:
        return pd.DataFrame()
    dt = 1.0 / DAYS_PER_YEAR
    rows: list[dict[str, object]] = []
    settle = market.settlements.loc[market.settlements["product"] == spec.product]
    traded = set(settle["trade_date"])
    # Refit on the last trade date of each month.
    month_ends = [
        i
        for i, d in enumerate(panel.trade_dates)
        if d in traded
        and not any(
            (x.month == d.month and x > d) for x in panel.trade_dates[i + 1 : i + 8] if x in traded
        )
        and i < len(panel.trade_dates) - 1
    ]
    for i in month_ends:
        if int(np.isfinite(panel.y[: i + 1]).any(axis=1).sum()) < min_observations:
            continue
        t = panel.trade_dates[i]
        sub = Panel(
            panel.trade_dates[: i + 1],
            panel.months[: i + 1],
            panel.y[: i + 1],
            _slice_design(panel, i),
            panel.jump_steps[: i + 1],
        )
        fit = fit_panel(sub.y, sub.design, dt, base, sub.jump_steps, min_observations, maxiter)
        if fit is None:
            continue
        view = market.view(end_of_day_utc(t))
        idx_now = view.published_index(spec.underlying_index)
        rw = float(idx_now.iloc[-1]) if not idx_now.empty else np.nan
        today = settle.loc[settle["trade_date"] == t].set_index("contract_month")["settle_price"]
        for cm, h, pred in forecast_months(fit.params, sub, i, spec, launches, max_horizon, dt):
            realized = final_settlement(full_index, spec, parse_month(cm))
            if realized is None or cm not in today.index:
                continue
            rows.append(
                {
                    "refit_date": t,
                    "contract_month": cm,
                    "horizon_months": h,
                    "model": pred,
                    "futures": float(today[cm]),
                    "random_walk": rw,
                    "realized": realized,
                    "kappa": fit.params.kappa,
                    "loglik": fit.loglik,
                }
            )
    return pd.DataFrame(rows)


def _slice_design(panel: Panel, upto: int) -> object:
    des = panel.design
    keep = des.seg_t <= upto
    lens = np.diff(np.append(des.seg_start, des.tau.size))
    starts, taus, jumps = [], [], []
    off = 0
    for k in np.flatnonzero(keep):
        a, n = des.seg_start[k], lens[k]
        taus.append(des.tau[a : a + n])
        jumps.append(des.n_jumps[a : a + n])
        starts.append(off)
        off += n
    return type(des)(
        T=upto + 1,
        n_slots=des.n_slots,
        t_years=des.t_years[: upto + 1],
        seg_t=des.seg_t[keep],
        seg_slot=des.seg_slot[keep],
        seg_start=np.asarray(starts, int),
        tau=np.concatenate(taus) if taus else np.zeros(0),
        n_jumps=np.concatenate(jumps) if jumps else np.zeros(0),
    )


def score(rows: pd.DataFrame) -> pd.DataFrame:
    """Mean squared log error by method and horizon."""
    if rows.empty:
        return pd.DataFrame()
    out = []
    for h, grp in rows.groupby("horizon_months"):
        r = np.log(grp["realized"].to_numpy())
        for col in ("model", "futures", "random_walk"):
            e = np.log(grp[col].to_numpy()) - r
            out.append(
                {"horizon_months": h, "method": col, "n": len(grp), "mse_log": float(np.mean(e**2))}
            )
    return pd.DataFrame(out)
