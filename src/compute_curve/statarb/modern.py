"""Claim 10: modern strategies on the SA2 universe (docs/modern_plan.md).

MX1 volatility-managed SA2-M, MX2 volume-conditioned reversal, MX3 statistical-
factor residual reversal, MX4 walk-forward ridge forecast. Simulation and shadow
only: nothing here sends an order. Every book is a weight matrix decided at the
close of t and held from the open of t+1 (``statarb.engine``).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import date

import numpy as np
import pandas as pd
import scipy.stats as st
import statsmodels.api as sm

from compute_curve.claim4 import stats as cs
from compute_curve.config import ResidualConfig, StatArbConfig
from compute_curve.statarb import evaluate as ev
from compute_curve.statarb.engine import Costs, Trade, book_returns, weight_matrix
from compute_curve.statarb.strategies import fit_ar1, s_scores

ETF = "XLK"
FORWARD_START = date(2026, 10, 19)
FORWARD_SESSIONS = 60
SCREEN_P = 0.20
MIN_EFFECTIVE_N = 30
VOL_LOOKBACK, VOL_MIN_OBS, SCALE_CAP = 20, 60, 2.0
AV_SHORT, AV_LONG = 5, 60
PCA_KS = (1, 2, 3)
BETA_WINDOW = 60
HORIZON, REFIT_EVERY, MIN_TRAIN_SESSIONS = 5, 20, 120
RIDGE_FRAC, N_SIDE, MIN_NAMES, IC_LAG = 0.1, 3, 8, 5
Z_CLIP = 3.0
STRATEGIES = ("MX1", "MX2a", "MX2b", "MX3-k1", "MX3-k2", "MX3-k3", "MX4")

Scorer = Callable[[pd.DataFrame, int, int], dict[str, tuple[float, float]]]
Gate = Callable[[str, int], int]  # +1 reversal, -1 momentum (fixed hold), 0 skip


# ---------------------------------------------------------------------------
# Residual trades with a pluggable scorer and entry gate
# ---------------------------------------------------------------------------
def etf_scorer(etf: str = ETF) -> Scorer:
    return lambda rets, t, window: s_scores(rets, etf, t, window)


def memo(scorer: Scorer) -> Scorer:
    """Cache scores by (t, window); use one memo per returns frame only."""
    cache: dict[tuple[int, int], dict[str, tuple[float, float]]] = {}

    def f(rets: pd.DataFrame, t: int, window: int) -> dict[str, tuple[float, float]]:
        key = (t, window)
        if key not in cache:
            cache[key] = scorer(rets, t, window)
        return cache[key]

    return f


def gated_trades(
    logp: pd.DataFrame,
    window: int,
    entry: float,
    rcfg: ResidualConfig,
    max_positions: int,
    max_hold: int,
    entry_lo: int,
    entry_hi: int,
    scorer: Scorer,
    gate: Gate | None = None,
    etf: str = ETF,
) -> list[Trade]:
    """SA2's trade loop with the s-score source and the entry decision swappable.

    With ``etf_scorer()`` and no gate this reproduces ``residual_trades`` exactly.
    A gate returning -1 opens the opposite (momentum) trade, held ``max_hold``
    sessions with no s-score exit.
    """
    rets = logp.diff()
    n = len(logp)
    gross = 1.0 / max_positions
    open_pos: dict[str, tuple[int, int, float, bool]] = {}  # sym -> (start, sign, beta, fixed)
    trades: list[Trade] = []
    for t in range(max(window, entry_lo), n):
        scores = scorer(rets, t, window) if t >= window else {}
        for sym, (start, sign, beta, fixed) in list(open_pos.items()):
            s = scores.get(sym, (np.nan, beta))[0]
            close = t + 1 - start >= max_hold or t == n - 1
            if not fixed:
                close = (
                    close
                    or (sign > 0 and np.isfinite(s) and s >= rcfg.close_long)
                    or (sign < 0 and np.isfinite(s) and s <= rcfg.close_short)
                )
            if close:
                trades.append(Trade(start, t + 1, {sym: sign * gross, etf: -sign * beta * gross}))
                del open_pos[sym]
        if not (entry_lo <= t <= entry_hi) or t >= n - 1:
            continue
        cands = sorted(
            ((abs(s), sym, s, b) for sym, (s, b) in scores.items() if sym not in open_pos),
            reverse=True,
        )
        for _, sym, s, b in cands:
            if len(open_pos) >= max_positions:
                break
            if abs(s) < entry:
                continue
            mode = gate(sym, t) if gate is not None else 1
            if mode == 0:
                continue
            reversal = 1 if s <= -entry else -1
            open_pos[sym] = (t + 1, reversal * mode, b, mode < 0)
    for sym, (start, sign, beta, _) in open_pos.items():
        trades.append(Trade(start, n, {sym: sign * gross, etf: -sign * beta * gross}))
    return trades


# ---------------------------------------------------------------------------
# MX2: abnormal volume
# ---------------------------------------------------------------------------
def abnormal_volume(volume: pd.DataFrame) -> pd.DataFrame:
    """mean(volume, t-4..t) / mean(volume, t-64..t-5)."""
    short = volume.rolling(AV_SHORT, min_periods=AV_SHORT).mean()
    long = volume.rolling(AV_LONG, min_periods=AV_LONG).mean().shift(AV_SHORT)
    return short / long.where(long > 0)


def volume_gate(av: pd.DataFrame, eligible: pd.DataFrame, loud: bool) -> Gate:
    """MX2a (``loud=False``): reversal on quiet candidates. MX2b: momentum on loud ones."""
    a = av.to_numpy(float)
    ok = eligible.to_numpy(bool) & np.isfinite(a)
    med = np.array([np.median(a[t, ok[t]]) if ok[t].any() else np.nan for t in range(len(a))])
    col = {s: j for j, s in enumerate(av.columns)}

    def gate(sym: str, t: int) -> int:
        j = col.get(sym)
        if j is None or not ok[t, j] or not np.isfinite(med[t]):
            return 0
        quiet = a[t, j] <= med[t]
        if loud:
            return 0 if quiet else -1
        return 1 if quiet else 0

    return gate


# ---------------------------------------------------------------------------
# MX3: statistical-factor s-scores
# ---------------------------------------------------------------------------
def pca_scorer(k: int, etf: str = ETF) -> Scorer:
    def scorer(rets: pd.DataFrame, t: int, window: int) -> dict[str, tuple[float, float]]:
        return pca_s_scores(rets, etf, t, window, k)

    return scorer


def pca_s_scores(
    rets: pd.DataFrame, etf: str, t: int, window: int, k: int
) -> dict[str, tuple[float, float]]:
    """s-scores of residuals on the top ``k`` principal components; beta is to ``etf``."""
    block = rets.iloc[t - window + 1 : t + 1]
    m = block[etf].to_numpy(float)
    if np.isnan(m).any() or np.ptp(m) == 0:
        return {}
    stocks = [c for c in block.columns if c != etf and not block[c].isna().any()]
    r = block[stocks].to_numpy(float)
    sd = r.std(axis=0, ddof=1) if stocks else np.array([])
    keep = sd > 0
    stocks, r, sd = [s for s, kp in zip(stocks, keep, strict=True) if kp], r[:, keep], sd[keep]
    if len(stocks) <= k + 1:
        return {}
    z = (r - r.mean(axis=0)) / sd
    _, _, vt = np.linalg.svd(z, full_matrices=False)
    x_f = np.column_stack([np.ones(window), z @ vt[:k].T])
    coef, *_ = np.linalg.lstsq(x_f, r, rcond=None)
    resid = r - x_f @ coef
    out: dict[str, tuple[float, float]] = {}
    for j, sym in enumerate(stocks):
        x = np.cumsum(resid[:, j])
        ar = fit_ar1(x)
        if not (0 < ar.b < 1) or not np.isfinite(ar.sd_eq) or ar.sd_eq <= 0:
            continue
        if -1.0 / np.log(ar.b) >= window / 2:
            continue
        beta = float(np.polyfit(m, r[:, j], 1)[0])
        out[sym] = (float((x[-1] - ar.mean) / ar.sd_eq), beta)
    return out


# ---------------------------------------------------------------------------
# Pooled books
# ---------------------------------------------------------------------------
def pooled_weights(trades_by_cell: list[list[Trade]], n: int, symbols: list[str]) -> np.ndarray:
    """Cell weights averaged, as the paper account holds a pooled book."""
    if not trades_by_cell:
        return np.zeros((n, len(symbols)))
    return sum(weight_matrix(tr, n, symbols) for tr in trades_by_cell) / len(trades_by_cell)  # type: ignore[return-value]


def region_weights(
    logp: pd.DataFrame,
    sa: StatArbConfig,
    region: list[list[float]],
    entry_hi: int,
    scorer: Scorer,
    gate: Gate | None = None,
) -> tuple[np.ndarray, int]:
    """Pooled weights over the region's cells (entries from the first session) and trade count."""
    cells = [
        gated_trades(
            logp,
            int(w),
            e,
            sa.residual,
            sa.max_positions,
            sa.max_hold,
            int(w),
            entry_hi,
            scorer,
            gate,
        )
        for w, e in region
    ]
    return pooled_weights(cells, len(logp), list(logp.columns)), sum(len(c) for c in cells)


# ---------------------------------------------------------------------------
# MX1: volatility management
# ---------------------------------------------------------------------------
def vol_scale(r: np.ndarray, w: np.ndarray) -> np.ndarray:
    """c_d = clip(sd(all past) / sd(last 20), 0, 2) from returns up to d-1; 1 before 60 obs."""
    n = len(r)
    c = np.ones(n)
    active = np.flatnonzero(np.abs(w).sum(axis=1) > 0)
    if not active.size:
        return c
    first = int(active[0])
    for d in range(first + VOL_MIN_OBS, n):
        past = r[first:d]
        recent = past[-VOL_LOOKBACK:]
        s_all, s_recent = float(np.std(past, ddof=1)), float(np.std(recent, ddof=1))
        c[d] = float(np.clip(s_all / s_recent, 0.0, SCALE_CAP)) if s_recent > 0 else SCALE_CAP
    return c


def mm_alpha_p(managed: np.ndarray, unmanaged: np.ndarray, lag: int) -> tuple[float, float]:
    """Moreira-Muir alpha of managed on unmanaged returns and its one-sided HAC p."""
    if not cs.enough_for_hac(len(managed), lag) or np.ptp(unmanaged) == 0:
        return float("nan"), float("nan")
    x = sm.add_constant(np.asarray(unmanaged, float), has_constant="add")
    res = sm.OLS(np.asarray(managed, float), x).fit(cov_type="HAC", cov_kwds={"maxlags": lag})
    a, se = float(res.params[0]), float(res.bse[0])
    p = float(st.t.sf(a / se, df=len(managed) - 2)) if se > 0 else float("nan")
    return a, p


# ---------------------------------------------------------------------------
# MX4: walk-forward ridge
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class RidgeOut:
    weights: np.ndarray  # sessions x symbols
    n_trades: int
    forecast_dates: list[int]
    ic_model: list[float]
    ic_base: list[float]


def rolling_beta(r: pd.DataFrame, m: pd.Series, window: int = BETA_WINDOW) -> pd.DataFrame:
    """OLS slope of each column on ``m`` over the ``window`` sessions ending at t."""
    mm = m.rolling(window, min_periods=window).mean()
    var = (m * m).rolling(window, min_periods=window).mean() - mm**2
    cross = r.mul(m, axis=0).rolling(window, min_periods=window).mean()
    cov = cross - r.rolling(window, min_periods=window).mean().mul(mm, axis=0)
    return cov.div(var.where(var > 0), axis=0)


def _z(x: np.ndarray) -> np.ndarray:
    sd = x.std(axis=0, ddof=0)
    z = (x - x.mean(axis=0)) / np.where(sd > 0, sd, 1.0)
    return np.clip(np.nan_to_num(z), -Z_CLIP, Z_CLIP)


def feature_panel(
    logp: pd.DataFrame, opens: pd.DataFrame, volume: pd.DataFrame, etf: str = ETF
) -> tuple[dict[int, tuple[list[str], np.ndarray]], pd.DataFrame, pd.DataFrame]:
    """Per session t: (names, z-scored features); also the residuals e and betas B (ending t)."""
    r = logp.diff()
    stocks = [c for c in logp.columns if c != etf]
    beta = rolling_beta(r[stocks], r[etf])
    e = r[stocks] - beta.shift(1).mul(r[etf], axis=0)
    lo = np.log(opens) - logp.shift(1)
    e_on = lo[stocks] - beta.shift(1).mul(lo[etf], axis=0)
    raw = [
        e,
        e.rolling(5, min_periods=5).sum(),
        e.rolling(20, min_periods=20).sum(),
        e_on.rolling(20, min_periods=20).sum(),
        np.log(abnormal_volume(volume[stocks])),
        np.log(r[stocks].rolling(20, min_periods=20).std()),
    ]
    cube = np.stack([f.reindex(columns=stocks).to_numpy(float) for f in raw], axis=2)
    ok = logp[stocks].notna().to_numpy() & np.isfinite(cube).all(axis=2)
    panel: dict[int, tuple[list[str], np.ndarray]] = {}
    for t in range(BETA_WINDOW + 1, len(logp)):
        js = np.flatnonzero(ok[t])
        if js.size < MIN_NAMES:
            continue
        names = [stocks[j] for j in js]
        sc = s_scores(r, etf, t, BETA_WINDOW)
        s_col = np.array([sc.get(s, (np.nan, 0.0))[0] for s in names])
        fill = float(np.nanmean(s_col)) if np.isfinite(s_col).any() else 0.0
        x = np.column_stack(
            [cube[t, js, :4], np.where(np.isfinite(s_col), s_col, fill), cube[t, js, 4:]]
        )
        panel[t] = (names, _z(x))
    return panel, e, beta


def ridge_fit(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    lam = RIDGE_FRAC * len(y)
    return np.linalg.solve(x.T @ x + lam * np.eye(x.shape[1]), x.T @ y)


def ridge_book(
    logp: pd.DataFrame,
    opens: pd.DataFrame,
    volume: pd.DataFrame,
    entry_hi: int,
    max_positions: int,
    etf: str = ETF,
) -> RidgeOut:
    """MX4: walk-forward ridge forecasts, top/bottom 3 tranches held 5 sessions."""
    panel, e, beta = feature_panel(logp, opens, volume, etf)
    n = len(logp)
    symbols = list(logp.columns)
    fwd = e.rolling(HORIZON, min_periods=HORIZON).sum().shift(-HORIZON)  # e over t+1..t+5
    targets: dict[int, np.ndarray] = {}
    for t, (names, _) in panel.items():
        y = fwd[names].iloc[t].to_numpy(float)
        if np.isfinite(y).all():
            targets[t] = y - y.mean()
    gross = 1.0 / max_positions / HORIZON
    trades: list[Trade] = []
    dates: list[int] = []
    ic_m: list[float] = []
    ic_b: list[float] = []
    coef: np.ndarray | None = None
    last_fit = -REFIT_EVERY
    col_e5 = 1
    for t in sorted(panel):
        train = [s for s in targets if s + HORIZON <= t]
        if len(train) < MIN_TRAIN_SESSIONS:
            continue
        if coef is None or t - last_fit >= REFIT_EVERY:
            coef = ridge_fit(
                np.vstack([panel[s][1] for s in train]), np.concatenate([targets[s] for s in train])
            )
            last_fit = t
        names, x = panel[t]
        f = x @ coef
        if t in targets:
            dates.append(t)
            ic_m.append(float(st.spearmanr(f, targets[t])[0]))
            ic_b.append(float(st.spearmanr(-x[:, col_e5], targets[t])[0]))
        if t > entry_hi or t >= n - 1:
            continue
        order = np.argsort(f)
        for idx, sign in [*((i, -1) for i in order[:N_SIDE]), *((i, 1) for i in order[-N_SIDE:])]:
            sym = names[int(idx)]
            b = float(beta[sym].iloc[t]) if np.isfinite(beta[sym].iloc[t]) else 1.0
            trades.append(
                Trade(t + 1, min(t + 1 + HORIZON, n), {sym: sign * gross, etf: -sign * b * gross})
            )
    return RidgeOut(weight_matrix(trades, n, symbols), len(trades), dates, ic_m, ic_b)


# ---------------------------------------------------------------------------
# Evaluation on a window
# ---------------------------------------------------------------------------
@dataclass
class MxResult:
    strategy: str
    window: tuple[str, str]
    n_sessions: int
    n_trades: int
    moments: dict[str, float]
    test: str
    p: float
    ci_mean: tuple[float, float]
    ci_sharpe: tuple[float, float]
    stress_mean: float
    gross_mean: float  # average gross stock exposure
    extra: dict[str, float]


def window_mask(index: pd.DatetimeIndex, window: tuple[date, date]) -> np.ndarray:
    return np.asarray((index >= pd.Timestamp(window[0])) & (index <= pd.Timestamp(window[1])))


def summarize(
    name: str,
    w: np.ndarray,
    opens: pd.DataFrame,
    closes: pd.DataFrame,
    costs: tuple[Costs, Costs, Costs],
    window: tuple[date, date],
    n_trades: int,
    lag: int,
    seed: int,
    block: int,
) -> tuple[MxResult, np.ndarray]:
    """Net returns of a weight book inside ``window``; mean test by default."""
    from compute_curve.statarb.pipeline import _mean, _sharpe, boot_ci  # noqa: PLC0415

    symbols = list(closes.columns)
    o, c = opens.to_numpy(float), closes.to_numpy(float)
    mask = window_mask(closes.index, window)
    base = book_returns(w, o, c, costs[0], symbols)[mask]
    stress = book_returns(w, o, c, costs[2], symbols)[mask]
    m = ev.moments(base)
    etf_col = symbols.index(ETF) if ETF in symbols else -1
    stock_w = np.delete(w[mask], etf_col, axis=1) if etf_col >= 0 else w[mask]
    res = MxResult(
        name,
        (str(window[0]), str(window[1])),
        int(m.n),
        n_trades,
        {k: float(v) for k, v in asdict(m).items()},
        "net mean > 0 (HAC)",
        ev.hac_p_one_sided(base, lag),
        boot_ci(base, block, seed, _mean),
        boot_ci(base, block, seed, _sharpe),
        float(np.mean(stress)) if stress.size else float("nan"),
        float(np.abs(stock_w).sum(axis=1).mean()) if stock_w.size else 0.0,
        {},
    )
    return res, base


def screen(r: MxResult) -> bool:
    """Exploration screen (plan section 4)."""
    ok = (
        np.isfinite(r.p)
        and r.p <= SCREEN_P
        and r.moments.get("mean", float("nan")) > 0
        and r.moments.get("effective_n", 0.0) >= MIN_EFFECTIVE_N
    )
    if r.strategy == "MX4":
        ok = ok and r.extra.get("ic_p", 1.0) <= SCREEN_P
    return bool(ok)


def confirm(rows: list[MxResult], alpha: float) -> list[dict[str, float | bool | str]]:
    """Holm over the survivors; C1 and C2 (and MX4's IC gate)."""
    ps = [r.p if np.isfinite(r.p) else 1.0 for r in rows]
    out: list[dict[str, float | bool | str]] = []
    for r, pa in zip(rows, cs.holm(ps), strict=True):
        c1 = bool(pa <= alpha and r.moments["mean"] > 0)
        c2 = bool(r.stress_mean > 0)
        gate = r.strategy != "MX4" or r.extra.get("ic_p", 1.0) <= alpha
        ok = c1 and c2 and bool(gate)
        out.append(
            {
                "strategy": r.strategy,
                "p_holm": float(pa),
                "c1": c1,
                "c2": c2,
                "gate": bool(gate),
                "confirmed": ok,
                "verdict": "confirmed: forward shadow decides" if ok else "not confirmed",
            }
        )
    return out
