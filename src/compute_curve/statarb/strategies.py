"""SA1 cointegrated pairs and SA2 residual reversal (docs/statarb_plan.md section 4).

Both take log closes (sessions x symbols, NaN before a name is eligible) and
return :class:`Trade` lists. A decision at the close of session ``t`` uses
closes up to ``t`` only and trades at the open of ``t + 1``. Entries are
allowed only at decision sessions in ``[entry_lo, entry_hi]``.
"""

from __future__ import annotations

import itertools
import warnings
from dataclasses import dataclass

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import coint

from compute_curve.config import PairsConfig, ResidualConfig
from compute_curve.statarb.engine import Trade


# ---------------------------------------------------------------------------
# Shared OU / AR(1) helpers
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Ar1:
    a: float
    b: float
    resid_sd: float

    @property
    def half_life(self) -> float:
        return float(-np.log(2.0) / np.log(self.b)) if 0 < self.b < 1 else float("inf")

    @property
    def mean(self) -> float:
        return self.a / (1.0 - self.b)

    @property
    def sd_eq(self) -> float:
        return self.resid_sd / np.sqrt(1.0 - self.b**2) if 0 < self.b < 1 else float("nan")


def fit_ar1(x: np.ndarray) -> Ar1:
    """OLS of ``x[k+1]`` on ``x[k]``: the discrete Ornstein-Uhlenbeck fit."""
    x0, x1 = x[:-1], x[1:]
    z = np.column_stack([np.ones_like(x0), x0])
    (a, b), *_ = np.linalg.lstsq(z, x1, rcond=None)
    e = x1 - z @ np.array([a, b])
    return Ar1(float(a), float(b), float(e.std(ddof=2)) if e.size > 2 else float("nan"))


# ---------------------------------------------------------------------------
# SA1 pairs
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class PairFit:
    y: str
    x: str
    beta: float
    alpha: float
    p: float
    mean: float
    sd: float
    half_life: float


def fit_pair(ly: np.ndarray, lx: np.ndarray, y: str, x: str) -> PairFit | None:
    """Engle-Granger on a formation window of log prices; None if degenerate."""
    if np.ptp(lx) == 0 or np.ptp(ly) == 0:
        return None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        p = float(coint(ly, lx, trend="c", autolag="aic")[1])
    beta, alpha = np.polyfit(lx, ly, 1)
    s = ly - beta * lx
    ar = fit_ar1(s)
    return PairFit(
        y, x, float(beta), float(alpha), p, float(s.mean()), float(s.std()), ar.half_life
    )


def select_pairs(
    logp: pd.DataFrame, f: int, lookback: int, groups: dict[str, list[str]], pcfg: PairsConfig
) -> list[PairFit]:
    """Pairs that pass the cointegration and half-life filters at formation index ``f``."""
    window = logp.iloc[f - lookback + 1 : f + 1]
    fits = []
    for members in groups.values():
        names = sorted(m for m in members if m in window.columns)
        for y, x in itertools.combinations(names, 2):
            ly, lx = window[y].to_numpy(float), window[x].to_numpy(float)
            if np.isnan(ly).any() or np.isnan(lx).any():
                continue
            fit = fit_pair(ly, lx, y, x)
            lo, hi = pcfg.half_life
            if (
                fit is not None
                and fit.beta > 0
                and fit.sd > 0
                and fit.p < pcfg.coint_p
                and lo <= fit.half_life <= hi
            ):
                fits.append(fit)
    return sorted(fits, key=lambda q: q.p)


def pair_weights(fit: PairFit, sign: int, gross: float) -> dict[str, float]:
    """Hedge-ratio weights: +sign on y, -sign*beta on x, scaled to ``gross``."""
    k = gross / (1.0 + abs(fit.beta))
    return {fit.y: sign * k, fit.x: -sign * fit.beta * k}


def pairs_trades(
    logp: pd.DataFrame,
    groups: dict[str, list[str]],
    lookback: int,
    entry: float,
    pcfg: PairsConfig,
    max_positions: int,
    max_hold: int,
    entry_lo: int,
    entry_hi: int,
) -> list[Trade]:
    """SA1: re-form pairs every ``reform_every`` sessions, trade them until the next formation."""
    n = len(logp)
    trades: list[Trade] = []
    gross = 1.0 / max_positions
    first = max(lookback - 1, entry_lo - 1)
    for f in range(first, min(entry_hi, n - 1) + 1, pcfg.reform_every):
        fits = select_pairs(logp, f, lookback, groups, pcfg)[:max_positions]
        period_end = min(f + pcfg.reform_every, n - 1)  # last decision close of this period
        for fit in fits:
            open_at: int | None = None
            sign = 0
            for t in range(f, period_end + 1):
                z = (logp[fit.y].iloc[t] - fit.beta * logp[fit.x].iloc[t] - fit.mean) / fit.sd
                if not np.isfinite(z):
                    continue
                if open_at is None:
                    if entry_lo <= t <= entry_hi and t < period_end and abs(z) >= entry:
                        open_at, sign = t + 1, (-1 if z > 0 else 1)
                    continue
                held = t + 1 - open_at
                if abs(z) <= pcfg.exit_z or abs(z) >= pcfg.stop_z or held >= max_hold:
                    trades.append(Trade(open_at, t + 1, pair_weights(fit, sign, gross)))
                    open_at = None
            if open_at is not None:
                trades.append(Trade(open_at, period_end + 1, pair_weights(fit, sign, gross)))
    return trades


# ---------------------------------------------------------------------------
# SA2 residual reversal (Avellaneda-Lee, ETF version)
# ---------------------------------------------------------------------------
def s_scores(rets: pd.DataFrame, etf: str, t: int, window: int) -> dict[str, tuple[float, float]]:
    """``{symbol: (s_score, beta)}`` at close ``t`` for names with a mean-reverting residual."""
    block = rets.iloc[t - window + 1 : t + 1]
    m = block[etf].to_numpy(float)
    out: dict[str, tuple[float, float]] = {}
    if np.isnan(m).any() or np.ptp(m) == 0:
        return out
    for sym in block.columns:
        if sym == etf:
            continue
        r = block[sym].to_numpy(float)
        if np.isnan(r).any():
            continue
        beta, alpha = np.polyfit(m, r, 1)
        x = np.cumsum(r - alpha - beta * m)
        ar = fit_ar1(x)
        if not (0 < ar.b < 1) or not np.isfinite(ar.sd_eq) or ar.sd_eq <= 0:
            continue
        if -1.0 / np.log(ar.b) >= window / 2:  # mean-reversion time 1/kappa in sessions
            continue
        out[sym] = (float((x[-1] - ar.mean) / ar.sd_eq), float(beta))
    return out


def residual_trades(
    logp: pd.DataFrame,
    etf: str,
    window: int,
    entry: float,
    rcfg: ResidualConfig,
    max_positions: int,
    max_hold: int,
    entry_lo: int,
    entry_hi: int,
) -> list[Trade]:
    """SA2: long (short) a stock against beta * ETF when its s-score is below -e (above e)."""
    rets = logp.diff()
    n = len(logp)
    gross = 1.0 / max_positions
    open_pos: dict[str, tuple[int, int, float]] = {}  # sym -> (start, sign, beta)
    trades: list[Trade] = []
    for t in range(max(window, entry_lo), n):
        scores = s_scores(rets, etf, t, window) if t >= window else {}
        for sym, (start, sign, beta) in list(open_pos.items()):
            s = scores.get(sym, (np.nan, beta))[0]
            held = t + 1 - start
            close = (
                held >= max_hold
                or t == n - 1
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
            if s <= -entry:
                open_pos[sym] = (t + 1, 1, b)
            elif s >= entry:
                open_pos[sym] = (t + 1, -1, b)
    for sym, (start, sign, beta) in open_pos.items():
        trades.append(Trade(start, n, {sym: sign * gross, etf: -sign * beta * gross}))
    return trades
