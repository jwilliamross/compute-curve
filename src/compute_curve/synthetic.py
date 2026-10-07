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

import json
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


def _sticky_path(
    rng: np.random.Generator, n: int, start: float, p_move: float, jump: float
) -> np.ndarray:
    """Log price that changes only on random days (list prices are sticky). SYNTHETIC."""
    moves = (rng.random(n) < p_move) * rng.normal(0.0, jump, n)
    moves[0] = 0.0
    return start + np.cumsum(moves)


def _synthetic_listings(rng: np.random.Generator, plant: frozenset[str]) -> pd.DataFrame:
    """SYNTHETIC listings for round 1: one listing per provider, sticky prices."""
    days = pd.date_range("2026-07-19", "2026-10-06", freq="D")
    n = len(days)
    leaders = ["coreweave", "lambda", "nebius", "crusoe", "together"]
    followers = [f"synth{k:02d}" for k in range(10)]
    p_lead = 0.2 if "H02" in plant else 0.08
    paths = {
        p: _sticky_path(rng, n, np.log(2.5) + rng.normal(0, 0.1), p_lead, 0.05) for p in leaders
    }
    lead_chg = np.diff(np.mean(list(paths.values()), axis=0), prepend=0.0)
    copy = np.roll(lead_chg, 2) if "H02" in plant else np.zeros(n)
    copy[:3] = 0.0
    for prov in followers:
        base = _sticky_path(rng, n, np.log(2.5) + rng.normal(0, 0.15), 0.08, 0.05)
        paths[prov] = base + np.cumsum(copy)
    if "H01" in plant:
        mat = np.vstack(list(paths.values()))
        for t in range(1, n):
            mat[:, t] = mat[:, t - 1]
            prem = mat[:, t] - np.median(mat[:, t])
            move = rng.random(mat.shape[0]) < 0.25
            mat[move, t] -= 0.5 * prem[move] + rng.normal(0, 0.005, int(move.sum()))
        paths = {p: mat[i] for i, p in enumerate(paths)}
    specs = [("H100", "on_demand", prov, lp) for prov, lp in paths.items()]
    for prov in (leaders + followers)[:6]:
        lp = _sticky_path(rng, n, np.log(6.0) + rng.normal(0, 0.1), 0.1, 0.05)
        specs.append(("B200", "on_demand", prov, lp))
    for prov in followers[:4]:
        specs.append(("H100", "spot", prov, _sticky_path(rng, n, np.log(1.8), 0.3, 0.05)))
    frames = [
        pd.DataFrame(
            {
                "as_of_date": days.date,
                "gpu_model": gpu,
                "term": term,
                "provider": prov,
                "listing_id": f"{prov}:{gpu.lower()}:{term}:",
                "price": np.exp(lp),
            }
        )
        for gpu, term, prov, lp in specs
    ]
    return pd.concat(frames, ignore_index=True).assign(is_synthetic=True)


def _synthetic_cgi(rng: np.random.Generator) -> pd.DataFrame:
    """SYNTHETIC CGI 15-minute values."""
    stamps = pd.date_range("2026-08-30 00:00", "2026-10-05 18:30", freq="15min", tz="UTC")
    cgi = []
    for gpu, base in (("H100", 3.5), ("B200", 7.0)):
        lv = np.log(base) + np.cumsum(rng.normal(0.0, 0.002, len(stamps)))
        cgi.append(pd.DataFrame({"as_of": stamps, "gpu_model": gpu, "value": np.exp(lv)}))
    return pd.concat(cgi, ignore_index=True).assign(is_synthetic=True)


def _synthetic_gd(rng: np.random.Generator) -> pd.DataFrame:
    """SYNTHETIC GetDeploying weekly medians and offering counts."""
    weeks = pd.date_range("2025-10-06", "2026-10-05", freq="7D")
    gd = []
    for gpu, term, base in (
        ("H100", "on_demand", 3.4),
        ("H100", "spot", 2.0),
        ("B200", "on_demand", 6.8),
    ):
        lv = np.log(base) + np.cumsum(rng.normal(0.0, 0.02, len(weeks)))
        cnt = np.maximum(5, 60 + np.cumsum(rng.integers(-3, 4, len(weeks))))
        gd.append(
            pd.DataFrame(
                {
                    "week": weeks.date,
                    "gpu_model": gpu,
                    "term": term,
                    "value": np.exp(lv),
                    "n_listings": cnt.astype(float),
                }
            )
        )
    return pd.concat(gd, ignore_index=True).assign(is_synthetic=True)


def _synthetic_aws(rng: np.random.Generator, plant: frozenset[str]) -> pd.DataFrame:
    """SYNTHETIC AWS pool prices; 2026-03 to 2026-06 absent as in the archive."""
    days = pd.date_range("2024-10-01", "2026-09-30", freq="D")
    keep = ~((days >= "2026-03-01") & (days <= "2026-06-30"))
    rows = []
    for gpu, itype, n_pools, base in (
        ("H100", "p5.48xlarge", 5, 3.0),
        ("H200", "p5e.48xlarge", 4, 4.0),
    ):
        eps = rng.normal(0.0, 0.01, len(days))
        common = np.zeros(len(days))
        phi = 0.9 if (gpu == "H100" and "H09" in plant) else 0.0
        for t in range(1, len(days)):
            common[t] = phi * common[t - 1] + eps[t]
        level = np.log(base) + np.cumsum(common)
        for k in range(n_pools):
            lp = level + np.cumsum(rng.normal(0.0, 0.002, len(days)))
            frame = pd.DataFrame(
                {
                    "day": days.date,
                    "az_id": f"use1-az{k + 1}",
                    "instance_type": itype,
                    "gpu": gpu,
                    "price_per_gpu_hour": np.exp(lp),
                }
            )
            rows.append(frame.loc[keep])
    return pd.concat(rows, ignore_index=True).assign(is_synthetic=True)


def synthetic_round1(
    seed: int,
    plant: frozenset[str] = frozenset(),
    universe: dict[str, list[str]] | None = None,
    benchmark: str = "XLK",
) -> dict[str, pd.DataFrame]:
    """SYNTHETIC inputs for exploration round 1, every frame flagged ``is_synthetic``.

    Spans match the real datasets (docs/exploration_plan.md section 2).
    ``plant`` adds a known effect: ``H01`` (repricing toward the median),
    ``H02`` (followers copy the leaders two days later) or ``H09`` (AWS spot
    changes with strong persistence). Without it every series is independent.
    """
    from compute_curve.claim4.market_data import sessions_from_calendar  # noqa: PLC0415

    rng = np.random.default_rng(seed)
    uni = universe or {"neocloud": ["NC1", "NC2"], "gpu_semis": ["GS1", "GS2"]}
    members = [s for b in uni.values() for s in b]
    sessions = sessions_from_calendar(
        synthetic_weekday_calendar(date(2024, 9, 3), date(2026, 10, 5))
    )
    bars = synthetic_equity_bars(sessions, members, benchmark, seed + 1)
    return {
        "listings": _synthetic_listings(rng, plant),
        "cgi": _synthetic_cgi(rng),
        "gd": _synthetic_gd(rng),
        "aws": _synthetic_aws(rng, plant),
        "bars": bars[["symbol", "session", "open", "close", "is_synthetic"]],
    }


def synthetic_cgi_vintages(
    start: str, end: str, seed: int, transient: float = 0.0, observed: str | None = None
) -> pd.DataFrame:
    """SYNTHETIC CGI H100 15-minute vintage rows (``as_of``, ``value``, ``ts_observed``,
    ``raw_json`` with ``generated_at``), flagged ``is_synthetic``.

    The log value is a random walk plus independent transient noise with
    standard deviation ``transient``; transient noise makes 6-hour changes
    revert. Every value is generated 3 minutes after its stamp.
    """
    rng = np.random.default_rng(seed)
    stamps = pd.date_range(start, end, freq="15min", tz="UTC")
    n = len(stamps)
    lv = np.log(3.5) + np.cumsum(rng.normal(0.0, 0.001, n)) + rng.normal(0.0, transient, n)
    gen = stamps + pd.Timedelta(minutes=3)
    obs = pd.Timestamp(observed, tz="UTC") if observed else stamps[-1] + pd.Timedelta(hours=1)
    return pd.DataFrame(
        {
            "as_of": stamps,
            "gpu_model": "H100",
            "value": np.exp(lv),
            "ts_observed": obs,
            "raw_json": [json.dumps({"generated_at": g.isoformat()}) for g in gen],
            "is_synthetic": True,
        }
    )
