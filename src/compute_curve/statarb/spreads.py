"""Corwin-Schultz (2012) high-low effective spread estimator (docs/statarb_plan2.md).

Corwin, S. A. and Schultz, P. (2012). A simple way to estimate bid-ask spreads
from daily high and low prices. Journal of Finance 67(2), 719-760. Includes
their overnight adjustment; negative two-day estimates are set to zero.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

K = 3.0 - 2.0 * np.sqrt(2.0)


def corwin_schultz(high: np.ndarray, low: np.ndarray, close: np.ndarray) -> np.ndarray:
    """Two-day spread estimates S_t for t = 0..n-2 (fraction of price)."""
    h, lo, c = (np.asarray(x, dtype=float) for x in (high, low, close))
    h1, l1 = h[1:].copy(), lo[1:].copy()
    prev_close = c[:-1]
    up = l1 > prev_close  # gap up: shift day t+1 down
    dn = h1 < prev_close  # gap down: shift day t+1 up
    shift = np.where(up, l1 - prev_close, np.where(dn, h1 - prev_close, 0.0))
    h1, l1 = h1 - shift, l1 - shift
    h0, l0 = h[:-1], lo[:-1]
    beta = np.log(h0 / l0) ** 2 + np.log(h1 / l1) ** 2
    gamma = np.log(np.maximum(h0, h1) / np.minimum(l0, l1)) ** 2
    alpha = (np.sqrt(2 * beta) - np.sqrt(beta)) / K - np.sqrt(gamma / K)
    s = 2 * (np.exp(alpha) - 1) / (1 + np.exp(alpha))
    return np.clip(s, 0.0, None)


def median_spreads(bars: pd.DataFrame, start: object, end: object) -> pd.Series:
    """Median Corwin-Schultz spread per symbol over sessions in [start, end]."""
    b = bars.copy()
    b["session"] = pd.to_datetime(b["session"])
    b = b.loc[(b["session"] >= pd.Timestamp(start)) & (b["session"] <= pd.Timestamp(end))]
    out = {}
    for sym, grp in b.sort_values("session").groupby("symbol"):
        g = grp.dropna(subset=["high", "low", "close"])
        g = g.loc[(g["high"] > 0) & (g["low"] > 0)]
        if len(g) < 20:
            continue
        s = corwin_schultz(g["high"].to_numpy(), g["low"].to_numpy(), g["close"].to_numpy())
        out[sym] = float(np.median(s))
    return pd.Series(out, dtype=float).sort_values()
