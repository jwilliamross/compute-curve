"""Claim-4 tests: lead-lag, event study, walk-forward forecasts, strategy, gate.

Every function takes the session-level dataset built by :func:`build_dataset`
and an evaluation time ``as_of``. Only outcomes known by ``as_of`` enter any
statistic, and walk-forward training at session ``t`` uses only windows
known by the open of ``t`` minus the buffer (docs/claim4_plan.md 6.4).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field

import numpy as np
import pandas as pd

from compute_curve.backtest.bootstrap import bootstrap_distribution
from compute_curve.claim4 import stats as cs
from compute_curve.claim4.market_data import basket_excess, window_returns
from compute_curve.config import Claim4Config

BASKET = "basket"


# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------
def category_balanced_excess(
    ret: pd.DataFrame, buckets: Mapping[str, Sequence[str]], benchmark: str, min_cov: float
) -> pd.DataFrame:
    """Excess return per bucket (equal weight) and for the category-balanced basket.

    The basket is the mean of the bucket excess returns; it is NaN unless
    every bucket has enough members with a return.
    """
    out = pd.DataFrame(index=ret.index)
    for name, members in buckets.items():
        out[name] = basket_excess(ret, list(members), benchmark, min_cov)
    out[BASKET] = out[list(buckets)].mean(axis=1, skipna=False)
    return out


def build_dataset(
    signals: pd.DataFrame,
    bars: pd.DataFrame,
    sessions: pd.DataFrame,
    cfg: Claim4Config,
) -> pd.DataFrame:
    """One row per session: signals, outcomes ``R_<target>_h<h>`` and ``known_h<h>``.

    Sessions after the last bar are kept (their outcomes are NaN) so a
    forecast can be made for the next session.
    """
    sess = sessions.sort_values("session").reset_index(drop=True)
    df = sess[["session", "open_utc", "close_utc"]].merge(
        signals.drop(columns=["open_utc"]), on="session", how="left"
    )
    buckets = cfg.universe.buckets()
    for h in cfg.horizons:
        ret, known = window_returns(bars, sess, h)
        ex = category_balanced_excess(ret, buckets, cfg.benchmark, cfg.min_bucket_coverage)
        for col in ex.columns:
            df[f"R_{col}_h{h}"] = ex[col].to_numpy()
        df[f"known_h{h}"] = known.to_numpy()
    df["in_sample"] = df["session"] >= cfg.first_session
    return df


def _usable(
    df: pd.DataFrame, signal: str, target: str, h: int, as_of: pd.Timestamp
) -> pd.DataFrame:
    col = f"R_{target}_h{h}"
    m = (
        df["in_sample"]
        & df[signal].notna()
        & df[col].notna()
        & (pd.to_datetime(df[f"known_h{h}"], utc=True) <= as_of)
    )
    return df.loc[m, ["session", "open_utc", signal, col]].rename(columns={signal: "x", col: "y"})


# ---------------------------------------------------------------------------
# Family P / S: lead-lag
# ---------------------------------------------------------------------------
@dataclass
class LeadLag:
    family: str
    target: str
    signal: str
    horizon: int
    n: int
    n_nonzero: int
    slope: float = float("nan")
    slope_se: float = float("nan")
    p_hac: float = float("nan")
    rho: float = float("nan")
    rho_lo: float = float("nan")
    rho_hi: float = float("nan")
    p_perm: float = float("nan")
    n_shifts: int = 0
    p_adj: float = float("nan")
    passes: bool = False
    note: str = ""


def lead_lag(
    df: pd.DataFrame,
    signal: str,
    target: str,
    h: int,
    as_of: pd.Timestamp,
    cfg: Claim4Config,
    family: str,
    n_boot: int,
    seed: int,
) -> LeadLag:
    d = _usable(df, signal, target, h, as_of)
    x, y = d["x"].to_numpy(float), d["y"].to_numpy(float)
    nz = int(np.sum(np.abs(x) > 1e-12))
    res = LeadLag(family, target, signal, h, len(d), nz)
    fit = cs.ols_hac(x, y, lag=h)
    if fit is None:
        if not cs.enough_for_hac(len(d), h):
            res.note = f"too few windows for HAC at h={h} (n < {cs.MIN_N_PER_LAG}h)"
        else:
            res.note = "no variation in signal"
        res.rho = cs.pearson(x, y)
        return res
    res.slope, res.slope_se, res.p_hac = fit.slope, fit.slope_se, fit.p_value
    res.rho = cs.pearson(x, y)
    res.rho_lo, res.rho_hi = cs.block_bootstrap_corr_ci(
        x, y, block_length=max(5, h), n_boot=n_boot, seed=seed
    )
    res.p_perm, res.n_shifts = cs.circular_shift_pvalue(x, y, min_shift=h)
    if nz < cfg.min_nonzero_signal:
        res.note = f"insufficient variation ({nz} non-zero < {cfg.min_nonzero_signal})"
    return res


def lead_lag_family(
    df: pd.DataFrame,
    as_of: pd.Timestamp,
    cfg: Claim4Config,
    targets: Sequence[str],
    family: str,
    adjust: str,
    level: float,
    n_boot: int,
    seed: int,
) -> list[LeadLag]:
    out = [
        lead_lag(df, s, t, h, as_of, cfg, family, n_boot, seed)
        for t in targets
        for s in cfg.signals
        for h in cfg.horizons
    ]
    adj = (cs.holm if adjust == "holm" else cs.benjamini_hochberg)([r.p_hac for r in out])
    for r, p in zip(out, adj, strict=True):
        r.p_adj = p
        r.passes = bool(
            np.isfinite(p)
            and p < level
            and r.p_perm < cfg.alpha
            and r.n_nonzero >= cfg.min_nonzero_signal
        )
    return out


# ---------------------------------------------------------------------------
# Diagnostic: cross-correlogram (not a test)
# ---------------------------------------------------------------------------
def cross_correlogram(
    df: pd.DataFrame,
    signal: str,
    as_of: pd.Timestamp,
    lags: Sequence[int] = range(-5, 6),
    n_boot: int = 2000,
    seed: int = 0,
) -> pd.DataFrame:
    """corr(S_t, R_basket(t+k, 1)); k < 0 means returns realized before the signal."""
    known = pd.to_datetime(df["known_h1"], utc=True) <= as_of
    y = df["R_basket_h1"].where(known)
    rows = []
    for k in lags:
        pair = pd.DataFrame({"x": df[signal], "y": y.shift(-k), "ok": df["in_sample"]})
        pair = pair.loc[pair["ok"]].dropna()
        x_, y_ = pair["x"].to_numpy(float), pair["y"].to_numpy(float)
        lo, hi = cs.block_bootstrap_corr_ci(x_, y_, 5, n_boot=n_boot, seed=seed)
        rho = cs.pearson(x_, y_)
        rows.append({"signal": signal, "k": k, "n": len(pair), "rho": rho, "lo": lo, "hi": hi})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Family E: event study
# ---------------------------------------------------------------------------
@dataclass
class EventResult:
    gpu: str
    horizon: int
    n_events: int
    mean_signed_car: float = float("nan")
    ci_lo: float = float("nan")
    ci_hi: float = float("nan")
    p_sign_flip: float = float("nan")
    p_adj: float = float("nan")
    passes: bool = False
    note: str = ""
    sessions: list[str] = field(default_factory=list)


def event_study(
    df: pd.DataFrame,
    gpu: str,
    h: int,
    as_of: pd.Timestamp,
    cfg: Claim4Config,
    n_boot: int,
    seed: int,
) -> EventResult:
    sig = f"level_{gpu.lower()}"
    d = _usable(df, sig, BASKET, h, as_of).reset_index(drop=True)
    pos = {s: i for i, s in enumerate(df.sort_values("open_utc")["session"])}
    events = d.loc[np.abs(d["x"]) >= cfg.event_threshold].copy()
    kept: list[int] = []
    last = -(10**9)
    for i, row in events.iterrows():
        p = pos[row["session"]]
        if p - last >= h:
            kept.append(i)
            last = p
    ev = events.loc[kept]
    car = (np.sign(ev["x"]) * ev["y"]).to_numpy(float)
    res = EventResult(gpu, h, len(ev), sessions=[str(s) for s in ev["session"]])
    if len(ev) == 0:
        res.note = "no events"
        return res
    res.mean_signed_car = float(car.mean())
    res.p_sign_flip = cs.sign_flip_pvalue(car, seed=seed)
    if len(ev) < cfg.min_events:
        res.note = f"insufficient events ({len(ev)} < {cfg.min_events}); descriptive only"
        return res  # no interval: a bootstrap over a handful of events is not informative
    res.ci_lo, res.ci_hi = cs.iid_bootstrap_ci(car, n_boot=n_boot, seed=seed)
    return res


def event_family(
    df: pd.DataFrame,
    as_of: pd.Timestamp,
    cfg: Claim4Config,
    n_boot: int,
    seed: int,
    gpus: Sequence[str] = ("H100", "B200"),
) -> list[EventResult]:
    out = [event_study(df, g, h, as_of, cfg, n_boot, seed) for g in gpus for h in cfg.horizons]
    for r, p in zip(out, cs.holm([r.p_sign_flip for r in out]), strict=True):
        r.p_adj = p
        r.passes = bool(np.isfinite(p) and p < cfg.alpha and r.n_events >= cfg.min_events)
    return out


# ---------------------------------------------------------------------------
# Family W: walk-forward forecasts
# ---------------------------------------------------------------------------
def walk_forward(
    df: pd.DataFrame,
    signal: str,
    h: int,
    as_of: pd.Timestamp,
    cfg: Claim4Config,
    target: str = BASKET,
) -> pd.DataFrame:
    """Expanding-window OLS forecasts for every in-sample session with a signal.

    Training at session ``t`` uses windows known by ``open_t - buffer`` and by
    ``as_of``. Returns session, forecast, baselines, the actual outcome (NaN
    unless known by ``as_of``) and the training size.
    """
    ycol, kcol = f"R_{target}_h{h}", f"known_h{h}"
    d = df.loc[df["in_sample"]].sort_values("open_utc").reset_index(drop=True)
    known_t = pd.to_datetime(d[kcol], utc=True)
    buffer = pd.Timedelta(minutes=cfg.open_buffer_minutes)
    rows = []
    for _, r in d.iterrows():
        if pd.isna(r[signal]):
            continue
        cut = min(pd.Timestamp(r["open_utc"]) - buffer, as_of)
        tr = d.loc[(known_t <= cut) & d[signal].notna() & d[ycol].notna()]
        if len(tr) < cfg.min_train:
            continue
        x, y = tr[signal].to_numpy(float), tr[ycol].to_numpy(float)
        mean = float(y.mean())
        if np.ptp(x) == 0:
            a, b = mean, 0.0
        else:
            b, a = np.polyfit(x, y, 1)
        actual = r[ycol] if pd.notna(r[kcol]) and pd.Timestamp(r[kcol]) <= as_of else np.nan
        rows.append(
            {
                "session": r["session"],
                "open_utc": r["open_utc"],
                "x": float(r[signal]),
                "forecast": float(a + b * r[signal]),
                "b0": 0.0,
                "b1": mean,
                "actual": float(actual) if pd.notna(actual) else np.nan,
                "n_train": len(tr),
            }
        )
    return pd.DataFrame(
        rows, columns=["session", "open_utc", "x", "forecast", "b0", "b1", "actual", "n_train"]
    )


@dataclass
class WalkForward:
    signal: str
    horizon: int
    n_oos: int
    n_oos_nonzero: int
    msfe_model: float = float("nan")
    msfe_b0: float = float("nan")
    msfe_b1: float = float("nan")
    r2_vs_b0: float = float("nan")
    r2_vs_b1: float = float("nan")
    cw_p_b0: float = float("nan")
    cw_p_b1: float = float("nan")
    hit_rate: float = float("nan")
    p_adj: float = float("nan")
    passes: bool = False
    note: str = ""


def evaluate_forecasts(fc: pd.DataFrame, signal: str, h: int, cfg: Claim4Config) -> WalkForward:
    e = fc.dropna(subset=["actual"])
    res = WalkForward(signal, h, len(e), int(np.sum(np.abs(e["x"]) > 1e-12)) if len(e) else 0)
    if len(e) < 3:
        res.note = f"{len(e)} out-of-sample forecasts"
        return res
    y, m = e["actual"].to_numpy(float), e["forecast"].to_numpy(float)
    b0, b1 = e["b0"].to_numpy(float), e["b1"].to_numpy(float)
    res.msfe_model = float(np.mean((y - m) ** 2))
    res.msfe_b0 = float(np.mean((y - b0) ** 2))
    res.msfe_b1 = float(np.mean((y - b1) ** 2))
    res.r2_vs_b0 = 1 - res.msfe_model / res.msfe_b0 if res.msfe_b0 > 0 else float("nan")
    res.r2_vs_b1 = 1 - res.msfe_model / res.msfe_b1 if res.msfe_b1 > 0 else float("nan")
    cw0, cw1 = cs.clark_west(y, m, b0, lag=h), cs.clark_west(y, m, b1, lag=h)
    res.cw_p_b0 = cw0.p_value if cw0 else float("nan")
    res.cw_p_b1 = cw1.p_value if cw1 else float("nan")
    hits = (np.sign(m) == np.sign(y)) & (m != 0) & (y != 0)
    denom = int(np.sum((m != 0) & (y != 0)))
    res.hit_rate = float(hits.sum() / denom) if denom else float("nan")
    if res.n_oos < cfg.min_oos_forecasts:
        res.note = f"{res.n_oos} out-of-sample forecasts < {cfg.min_oos_forecasts} required"
    return res


def _worse(p0: float, p1: float) -> float:
    return max(p0, p1) if np.isfinite(p0) and np.isfinite(p1) else float("nan")


def walk_forward_family(
    df: pd.DataFrame, as_of: pd.Timestamp, cfg: Claim4Config
) -> tuple[list[WalkForward], dict[tuple[str, int], pd.DataFrame]]:
    results, forecasts = [], {}
    for s in cfg.signals:
        for h in cfg.horizons:
            fc = walk_forward(df, s, h, as_of, cfg)
            forecasts[(s, h)] = fc
            results.append(evaluate_forecasts(fc, s, h, cfg))
    worst = [_worse(r.cw_p_b0, r.cw_p_b1) for r in results]
    for r, p in zip(results, cs.holm(worst), strict=True):
        r.p_adj = p
        r.passes = bool(
            np.isfinite(p)
            and p < cfg.alpha
            and r.r2_vs_b0 > 0
            and r.r2_vs_b1 > 0
            and r.n_oos >= cfg.min_oos_forecasts
        )
    return results, forecasts


# ---------------------------------------------------------------------------
# Strategy (gate G3) and costs
# ---------------------------------------------------------------------------
def round_trip_cost(direction: int, h: int, cfg: Claim4Config, multiplier: float = 1.0) -> float:
    """Cost of one round trip of the pair per unit notional per leg, as a return.

    Both legs enter and exit; one sell per leg; borrow on the short leg for
    ``h`` sessions. ``direction`` +1 = long basket / short XLK.
    """
    c = cfg.costs
    bps = 2 * c.stock_side_bps + 2 * c.benchmark_side_bps + 2 * c.sell_fee_bps
    borrow = c.benchmark_borrow_annual if direction > 0 else c.stock_borrow_annual
    return multiplier * (bps / 1e4 + borrow * h / 252.0)


@dataclass
class StrategyResult:
    signal: str
    horizon: int
    n_windows: int
    n_trades: int
    mean_net: float = float("nan")
    sharpe: float = float("nan")
    sharpe_lo: float = float("nan")
    sharpe_hi: float = float("nan")
    mean_net_2x: float = float("nan")
    by_multiplier: dict[str, float] = field(default_factory=dict)
    passes: bool = False


def strategy_returns(fc: pd.DataFrame, h: int, cfg: Claim4Config, multiplier: float) -> np.ndarray:
    e = fc.dropna(subset=["actual"])
    out = []
    for f, y in zip(e["forecast"].to_numpy(float), e["actual"].to_numpy(float), strict=True):
        d = int(np.sign(f))
        if d == 0 or abs(f) <= round_trip_cost(d, h, cfg):
            out.append(0.0)
            continue
        out.append(d * y - round_trip_cost(d, h, cfg, multiplier))
    return np.asarray(out, dtype=float)


def evaluate_strategy(
    fc: pd.DataFrame, signal: str, h: int, cfg: Claim4Config, n_boot: int, seed: int
) -> StrategyResult:
    base = strategy_returns(fc, h, cfg, 1.0)
    res = StrategyResult(signal, h, base.size, int(np.sum(base != 0)))
    if base.size < 3:
        return res
    res.mean_net = float(base.mean())
    res.sharpe = cs.annualized_sharpe(base, h)
    res.mean_net_2x = float(strategy_returns(fc, h, cfg, 2.0).mean())
    for m in cfg.costs.sensitivity_multipliers:
        res.by_multiplier[f"{m:g}x"] = float(strategy_returns(fc, h, cfg, m).mean())
    if base.size < 2 * max(5, h):
        return res  # too few windows for a block bootstrap; G3 cannot pass
    dist = bootstrap_distribution(
        base, lambda r: cs.annualized_sharpe(r, h), n_boot=n_boot, block_length=max(5, h), seed=seed
    )
    dist = dist[np.isfinite(dist)]
    if dist.size:
        res.sharpe_lo, res.sharpe_hi = (float(v) for v in np.quantile(dist, [0.025, 0.975]))
    res.passes = bool(np.isfinite(res.sharpe_lo) and res.sharpe_lo > 0 and res.mean_net_2x > 0)
    return res


# ---------------------------------------------------------------------------
# Gate
# ---------------------------------------------------------------------------
@dataclass
class GateRow:
    signal: str
    horizon: int
    g1_leadlag: bool
    g2_walkforward: bool
    g3_strategy: bool
    g4_sufficiency: bool
    validated: bool
    p_leadlag_adj: float
    reasons: list[str]


def gate(
    lead: Sequence[LeadLag],
    wf: Sequence[WalkForward],
    strat: Sequence[StrategyResult],
    cfg: Claim4Config,
) -> tuple[list[GateRow], str | None]:
    """G1-G4 per (signal, horizon); G5 is checked at trading time. Returns rows and the pick."""
    L = {(r.signal, r.horizon): r for r in lead if r.target == BASKET}
    W = {(r.signal, r.horizon): r for r in wf}
    S = {(r.signal, r.horizon): r for r in strat}
    rows = []
    for s in cfg.signals:
        for h in cfg.horizons:
            ll, w, st_ = L[(s, h)], W[(s, h)], S[(s, h)]
            g4 = w.n_oos >= cfg.min_oos_forecasts and w.n_oos_nonzero >= cfg.min_oos_nonzero
            reasons = []
            if not ll.passes:
                reasons.append("G1 lead-lag not significant")
            if not w.passes:
                reasons.append("G2 walk-forward does not beat both baselines")
            if not st_.passes:
                reasons.append("G3 net Sharpe CI not above 0")
            if not g4:
                reasons.append(
                    f"G4 {w.n_oos} OOS forecasts (need {cfg.min_oos_forecasts}), "
                    f"{w.n_oos_nonzero} non-zero (need {cfg.min_oos_nonzero})"
                )
            ok = ll.passes and w.passes and st_.passes and g4
            rows.append(GateRow(s, h, ll.passes, w.passes, st_.passes, g4, ok, ll.p_adj, reasons))
    passing = [r for r in rows if r.validated]
    pick = min(passing, key=lambda r: r.p_leadlag_adj) if passing else None
    return rows, (f"{pick.signal}|h{pick.horizon}" if pick else None)


def as_dicts(items: Sequence[object]) -> list[dict[str, object]]:
    return [asdict(i) for i in items]  # type: ignore[call-overload]
