"""H100 versus B200 relative value per performance-normalized unit (Phase 2).

Define the throughput ratio ``r = perf(B200) / perf(H100)`` (an assumption
with a stated range; see ``docs/relative_value.md``). The price of one
H100-equivalent hour of compute bought as B200 time is ``P_B200 / r``. The
log spread

    s_t = ln P_B200,t - ln r - ln P_H100,t

is zero when both deliver compute at the same price, positive when B200 is
the dearer way to buy compute.

Forecast test (walk-forward): does an AR(1) mean-reversion model of ``s``
predict ``s_{t+h} - s_t`` better than the random-walk baseline (zero change)?
The trading rule fades large z-scores only if that test passes.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from compute_curve.backtest.bootstrap import paired_loss_difference_ci


def log_spread(p_b200: pd.Series, p_h100: pd.Series, perf_ratio: float) -> pd.Series:
    """Performance-normalized log spread on dates where both prices exist."""
    both = pd.concat({"b": p_b200, "h": p_h100}, axis=1).dropna()
    return (np.log(both["b"]) - np.log(perf_ratio) - np.log(both["h"])).rename("spread")


def breakeven_ratio(p_b200: float, p_h100: float) -> float:
    """Throughput ratio at which both GPUs cost the same per unit of compute."""
    return p_b200 / p_h100


def rolling_z(spread: pd.Series, window: int) -> pd.Series:
    """z-score of s_t against the *previous* ``window`` values (no look-ahead)."""
    past = spread.shift(1).rolling(window, min_periods=window)
    return ((spread - past.mean()) / past.std(ddof=1)).rename("z")


@dataclass(frozen=True)
class SpreadForecastEval:
    n: int
    horizon: int
    mse_model: float
    mse_random_walk: float
    mean_diff: float
    ci: tuple[float, float]


def walk_forward_ar1(spread: pd.Series, horizon: int, min_train: int) -> pd.DataFrame:
    """Expanding-window AR(1) forecasts of s_{t+h} - s_t made at each t.

    Fit on pairs (s_{u}, s_{u+h}) with ``u + h <= t`` only.
    """
    s = spread.dropna().to_numpy(float)
    idx = spread.dropna().index
    rows: list[dict[str, object]] = []
    for t in range(min_train + horizon, len(s) - horizon):
        x = s[: t - horizon + 1]
        y = s[horizon : t + 1]
        X = np.column_stack([np.ones_like(x), x])
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        pred_level = beta[0] + beta[1] * s[t]
        rows.append(
            {
                "t": idx[t],
                "pred_change": float(pred_level - s[t]),
                "actual_change": float(s[t + horizon] - s[t]),
            }
        )
    return pd.DataFrame(rows)


def fade_signal(z: float, entry: float, exit_: float, current: int) -> int:
    """Position in the spread: -1 short B200/long H100, +1 the reverse, 0 flat.

    Enter when |z| > entry, exit when |z| < exit_, otherwise hold.
    """
    if not np.isfinite(z):
        return current
    if z > entry:
        return -1
    if z < -entry:
        return 1
    if abs(z) < exit_:
        return 0
    return current


def hedge_contracts(n_gpu2: int, p_b200: float, p_h100: float) -> int:
    """GPU1 contracts that match the notional of ``n_gpu2`` GPU2 contracts."""
    return round(n_gpu2 * p_b200 / p_h100)


def evaluate_spread_forecast(
    preds: pd.DataFrame,
    horizon: int,
    n_boot: int = 2000,
    block_length: int = 5,
    seed: int = 0,
) -> SpreadForecastEval | None:
    """Compare AR(1) forecasts with the random walk (zero change) out of sample."""
    if preds.empty:
        return None
    lm = (preds["pred_change"] - preds["actual_change"]) ** 2
    lb = preds["actual_change"] ** 2
    mean, ci = paired_loss_difference_ci(
        lm.to_numpy(),
        lb.to_numpy(),
        n_boot=n_boot,
        block_length=max(block_length, horizon),
        seed=seed,
    )
    return SpreadForecastEval(
        n=len(preds),
        horizon=horizon,
        mse_model=float(lm.mean()),
        mse_random_walk=float(lb.mean()),
        mean_diff=mean,
        ci=ci,
    )
