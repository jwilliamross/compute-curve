"""SYNTHETIC DATA FOR TESTS AND ENGINE VALIDATION ONLY.

Nothing generated here is market data. Every frame carries
``is_synthetic=True`` and every index name is prefixed ``SYNTHETIC``. Forward
mode refuses synthetic inputs, the warehouse filters them out, and reports
built from synthetic runs are stamped "SYNTHETIC - NOT A RESULT".

The generator simulates a Schwartz-Smith two-factor log price for the spot
index and prices futures with the model's closed form, so the engine and the
Kalman filter can be checked against a known data-generating process.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

import numpy as np
import pandas as pd

from compute_curve.config import Config, ContractSpec
from compute_curve.contracts import final_settlement, last_trading_day, listed_contracts
from compute_curve.models.schwartz_smith import SSParams, futures_log_price

SYNTHETIC_PREFIX = "SYNTHETIC"


def synthetic_name(index_name: str) -> str:
    """Prefix an index name with SYNTHETIC exactly once."""
    if index_name.startswith(SYNTHETIC_PREFIX):
        return index_name
    return f"{SYNTHETIC_PREFIX} {index_name}"


def synthetic_config(cfg: Config) -> Config:
    """Copy of ``cfg`` whose contracts reference SYNTHETIC index names."""
    contracts = {
        k: v.model_copy(update={"underlying_index": synthetic_name(v.underlying_index)})
        for k, v in cfg.contracts.items()
    }
    return cfg.model_copy(update={"contracts": contracts})


@dataclass(frozen=True)
class SyntheticMarket:
    spot: pd.DataFrame  # as_of_date, value, chi, xi
    published_index: pd.DataFrame
    settlements: pd.DataFrame
    params: SSParams


def simulate_ss_path(
    params: SSParams, n_days: int, chi0: float, xi0: float, seed: int, dt: float = 1 / 365
) -> tuple[np.ndarray, np.ndarray]:
    """Exact discretization of the Schwartz-Smith state under the real-world measure."""
    rng = np.random.default_rng(seed)
    k, sc, sx, rho = params.kappa, params.sigma_chi, params.sigma_xi, params.rho
    a = np.exp(-k * dt)
    var_c = sc**2 * (1 - np.exp(-2 * k * dt)) / (2 * k)
    var_x = sx**2 * dt
    cov = rho * sc * sx * (1 - np.exp(-k * dt)) / k
    L = np.linalg.cholesky(np.array([[var_c, cov], [cov, var_x]]))
    chi = np.empty(n_days)
    xi = np.empty(n_days)
    chi[0], xi[0] = chi0, xi0
    for t in range(1, n_days):
        z = L @ rng.standard_normal(2)
        chi[t] = a * chi[t - 1] + z[0]
        xi[t] = xi[t - 1] + params.mu_xi * dt + z[1]
    return chi, xi


def synthetic_market(
    spec: ContractSpec,
    start: date,
    n_days: int,
    params: SSParams,
    seed: int,
    meas_noise: float = 0.002,
    chi0: float = 0.1,
    xi0: float = float(np.log(2.0)),
) -> SyntheticMarket:
    """Synthetic spot index, published index and daily futures settlements."""
    chi, xi = simulate_ss_path(params, n_days, chi0, xi0, seed)
    days = [start + timedelta(days=i) for i in range(n_days)]
    spot = np.exp(chi + xi)
    name = synthetic_name(spec.underlying_index)
    spot_df = pd.DataFrame({"as_of_date": days, "value": spot, "chi": chi, "xi": xi})
    pub = pd.DataFrame(
        {
            "index_name": name,
            "as_of_date": days,
            "value": spot,
            "ts_available": pd.to_datetime(days).tz_localize("UTC") + pd.Timedelta(days=1),
            "is_synthetic": True,
        }
    )
    rng = np.random.default_rng(seed + 1)
    rows: list[dict[str, object]] = []
    idx_series = pd.Series(spot, index=days)
    for i, d in enumerate(days):
        if d.weekday() >= 5:
            continue
        for cm in listed_contracts(spec, d)[:12]:
            ltd = last_trading_day(cm.month)
            if d > ltd:
                continue
            # Average-price contract: approximate with the futures price at the
            # month's mid-point, blended with known month-to-date values.
            mid = cm.month + timedelta(days=14)
            tau = max((mid - d).days, 0) / 365.0
            f = float(np.exp(futures_log_price(params, chi[i], xi[i], tau)))
            if cm.month <= d:
                known = idx_series[(idx_series.index >= cm.month) & (idx_series.index <= d)]
                n_month = (ltd.replace(day=28) + timedelta(days=4)).replace(day=1) - cm.month
                frac = len(known) / n_month.days
                f = frac * float(known.mean()) + (1 - frac) * f
            f *= float(np.exp(rng.normal(0, meas_noise)))
            rows.append(
                {
                    "product": spec.product,
                    "contract_month": cm.code,
                    "trade_date": d,
                    "settle_price": round(f, 4),
                }
            )
    st = pd.DataFrame(rows)
    st["ts_available"] = (
        pd.to_datetime(st["trade_date"]).dt.tz_localize("UTC")
        + pd.Timedelta(days=1)
        - pd.Timedelta(microseconds=1)
    )
    st["is_synthetic"] = True
    return SyntheticMarket(spot=spot_df, published_index=pub, settlements=st, params=params)


def synthetic_final_settlement(
    sm: SyntheticMarket, spec: ContractSpec, month: date
) -> float | None:
    s = pd.Series(sm.spot["value"].to_numpy(), index=list(sm.spot["as_of_date"]))
    return final_settlement(s, spec, month)


# ---------------------------------------------------------------------------
# Claim 4: SYNTHETIC sessions, signals and equity bars (tests only)
# ---------------------------------------------------------------------------
def synthetic_weekday_calendar(start: date, end: date) -> list[dict[str, str]]:
    """Alpaca-style calendar rows for every weekday (no holidays). SYNTHETIC."""
    out = []
    d = start
    while d <= end:
        if d.weekday() < 5:
            out.append({"date": d.isoformat(), "open": "09:30", "close": "16:00"})
        d += timedelta(days=1)
    return out


def synthetic_signals(
    sessions: pd.DataFrame, seed: int, nonzero_share: float = 1.0, scale: float = 0.02
) -> pd.DataFrame:
    """SYNTHETIC session signals in the claim-4 layout, flagged ``is_synthetic``."""
    from compute_curve.claim4.signals import SIGNAL_NAMES  # noqa: PLC0415

    rng = np.random.default_rng(seed)
    n = len(sessions)
    df = sessions[["session", "open_utc"]].copy().reset_index(drop=True)
    prev = [s - timedelta(days=1) for s in df["session"]]
    df["asof_h100"] = prev
    df["asof_b200"] = prev
    for name in SIGNAL_NAMES:
        x = rng.normal(0.0, scale, n)
        x[rng.random(n) >= nonzero_share] = 0.0
        df[name] = x
    df["is_synthetic"] = True
    return df


def synthetic_equity_bars(
    sessions: pd.DataFrame,
    symbols: list[str],
    benchmark: str,
    seed: int,
    effect: float = 0.0,
    driver: np.ndarray | None = None,
    vol: float = 0.02,
) -> pd.DataFrame:
    """SYNTHETIC daily bars. Each non-benchmark symbol's open-to-close return is
    ``market + noise + effect * driver[t]``; the benchmark's is ``market``."""
    rng = np.random.default_rng(seed)
    n = len(sessions)
    drv = np.zeros(n) if driver is None else np.asarray(driver, dtype=float)
    market = rng.normal(0.0, vol / 2, n)
    rows = []
    for sym in [*symbols, benchmark]:
        px = 100.0
        for t, s in enumerate(sessions["session"]):
            o = px * float(np.exp(rng.normal(0.0, vol / 4)))
            r = (
                market[t]
                if sym == benchmark
                else market[t] + rng.normal(0.0, vol) + effect * drv[t]
            )
            c = max(o * (1.0 + r), 0.01)
            rows.append(
                {
                    "symbol": sym,
                    "session": s,
                    "open": o,
                    "high": max(o, c),
                    "low": min(o, c),
                    "close": c,
                    "volume": 1e6,
                    "vwap": (o + c) / 2,
                    "n_trades": 1000.0,
                    "is_synthetic": True,
                }
            )
            px = c
    return pd.DataFrame(rows)


def synthetic_bars_json(bars: pd.DataFrame) -> dict[str, list[dict[str, object]]]:
    """Alpaca ``/v2/stocks/bars`` payload for SYNTHETIC bars (``t`` = midnight New York)."""
    from zoneinfo import ZoneInfo  # noqa: PLC0415

    ny = ZoneInfo("America/New_York")
    out: dict[str, list[dict[str, object]]] = {}
    for r in bars.itertuples(index=False):
        t = pd.Timestamp(datetime.combine(r.session, time(0, 0), tzinfo=ny)).tz_convert("UTC")
        out.setdefault(r.symbol, []).append(
            {
                "t": t.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "o": r.open,
                "h": r.high,
                "l": r.low,
                "c": r.close,
                "v": r.volume,
                "vw": r.vwap,
                "n": r.n_trades,
            }
        )
    return out


def synthetic_spot_pools(
    start: date, end: date, gpus: tuple[str, ...], n_pools: int, seed: int, vol: float = 0.02
) -> pd.DataFrame:
    """SYNTHETIC per-pool daily spot prices per GPU-hour (claim 5), flagged ``is_synthetic``."""
    rng = np.random.default_rng(seed)
    days = [start + timedelta(days=i) for i in range((end - start).days + 1)]
    rows = []
    for gpu in gpus:
        for k in range(n_pools):
            logp = np.log(2.0) + np.cumsum(rng.normal(0.0, vol, len(days)))
            for d, lp in zip(days, logp, strict=True):
                rows.append((d, f"use1-az{k + 1}", f"SYNTHETIC-{gpu}", gpu, float(np.exp(lp))))
    df = pd.DataFrame(rows, columns=["day", "az_id", "instance_type", "gpu", "price_per_gpu_hour"])
    df["is_synthetic"] = True
    return df
