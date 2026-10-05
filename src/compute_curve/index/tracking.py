"""Tracking error of our index against the published Silicon Data index.

Error is measured in log points: ``e_d = ln(own_d) - ln(published_d)`` on
days where both exist. Reported statistics carry block-bootstrap confidence
intervals. With fewer than ``min_days`` overlapping days the function
returns ``None`` and the caller must report "insufficient overlap".
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from compute_curve.backtest.bootstrap import block_bootstrap_ci


@dataclass(frozen=True)
class TrackingStats:
    gpu_model: str
    n_days: int
    mean_log_error: float
    mean_log_error_ci: tuple[float, float]
    rmse_log: float
    rmse_log_ci: tuple[float, float]
    corr_daily_changes: float | None


def join_own_and_published(
    own: pd.DataFrame, published: pd.DataFrame, gpu_model: str, index_name: str
) -> pd.DataFrame:
    o = own.loc[own["gpu_model"] == gpu_model, ["as_of_date", "value"]].rename(
        columns={"value": "own"}
    )
    p = published.loc[published["index_name"] == index_name, ["as_of_date", "value"]].rename(
        columns={"value": "published"}
    )
    return o.merge(p, on="as_of_date", how="inner").sort_values("as_of_date")


def tracking_stats(
    joined: pd.DataFrame,
    gpu_model: str,
    min_days: int = 20,
    n_boot: int = 2000,
    block_length: int = 5,
    seed: int = 0,
) -> TrackingStats | None:
    if len(joined) < min_days:
        return None
    e = np.log(joined["own"].to_numpy(float)) - np.log(joined["published"].to_numpy(float))
    mean_ci = block_bootstrap_ci(e, np.mean, n_boot=n_boot, block_length=block_length, seed=seed)
    rmse_ci = block_bootstrap_ci(
        e,
        lambda x: float(np.sqrt(np.mean(x**2))),
        n_boot=n_boot,
        block_length=block_length,
        seed=seed,
    )
    d_own = np.diff(np.log(joined["own"].to_numpy(float)))
    d_pub = np.diff(np.log(joined["published"].to_numpy(float)))
    corr = None
    if d_own.size >= 3 and np.std(d_own) > 0 and np.std(d_pub) > 0:
        corr = float(np.corrcoef(d_own, d_pub)[0, 1])
    return TrackingStats(
        gpu_model=gpu_model,
        n_days=len(joined),
        mean_log_error=float(e.mean()),
        mean_log_error_ci=mean_ci,
        rmse_log=float(np.sqrt(np.mean(e**2))),
        rmse_log_ci=rmse_ci,
        corr_daily_changes=corr,
    )
