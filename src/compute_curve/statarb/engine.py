"""Trade-based book: trades -> daily weights -> net daily returns.

A trade is active from the open of session ``start`` to the open of session
``end`` (exclusive), so it earns the intraday return of ``start`` and every
close-to-close return up to the open of ``end``. Signals are decided at the
close before ``start``, so nothing uses a later price.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

TRADING_DAYS = 252


@dataclass(frozen=True)
class Trade:
    start: int  # session index of the entry open
    end: int  # session index of the exit open (exclusive); may equal n (closed at last close)
    weights: dict[str, float]  # capital weights per symbol (+ long, - short)


@dataclass(frozen=True)
class Costs:
    stock_side: float  # fraction per side, e.g. 0.0015
    etf_side: float
    sell_fee: float
    borrow_annual: float
    etf: str = "XLK"

    def scaled(self, k: float, borrow_annual: float) -> Costs:
        return Costs(
            self.stock_side * k, self.etf_side * k, self.sell_fee * k, borrow_annual, self.etf
        )


def weight_matrix(trades: list[Trade], n: int, symbols: list[str]) -> np.ndarray:
    """Sum of active trade weights per session (rows) and symbol (columns)."""
    col = {s: j for j, s in enumerate(symbols)}
    w = np.zeros((n, len(symbols)))
    for t in trades:
        a, b = max(t.start, 0), min(t.end, n)
        if a >= b:
            continue
        for sym, x in t.weights.items():
            w[a:b, col[sym]] += x
    return w


def book_returns(
    w: np.ndarray, opens: np.ndarray, closes: np.ndarray, costs: Costs, symbols: list[str]
) -> np.ndarray:
    """Net daily return of a book holding ``w[d]`` from the open of session d.

    Gross: previous weights earn the overnight return (close d-1 to open d),
    current weights the intraday return (open d to close d). Costs: per-side
    cost on turnover at the open, a sell fee on sold notional, borrow on shorts.
    A position held past the last session is closed at the last close.
    """
    n = len(w)
    overnight = np.zeros_like(opens)
    overnight[1:] = opens[1:] / closes[:-1] - 1.0
    intraday = closes / opens - 1.0
    overnight, intraday = np.nan_to_num(overnight), np.nan_to_num(intraday)
    prev = np.vstack([np.zeros((1, w.shape[1])), w[:-1]])
    gross = (prev * overnight).sum(axis=1) + (w * intraday).sum(axis=1)
    side = np.array([costs.etf_side if s == costs.etf else costs.stock_side for s in symbols])
    trade = w - prev
    cost = (np.abs(trade) * side).sum(axis=1) + (np.clip(-trade, 0, None).sum(axis=1)) * (
        costs.sell_fee
    )
    cost += np.clip(-w, 0, None).sum(axis=1) * costs.borrow_annual / TRADING_DAYS
    final = np.abs(w[-1]) if n else np.zeros(len(symbols))
    out = gross - cost
    if n:
        out[-1] -= float((final * side).sum() + np.clip(w[-1], 0, None).sum() * costs.sell_fee)
    return out


def run_book(
    trades: list[Trade], opens: pd.DataFrame, closes: pd.DataFrame, costs: Costs
) -> pd.Series:
    """Net daily returns of a list of trades on aligned open/close frames."""
    symbols = list(closes.columns)
    w = weight_matrix(trades, len(closes), symbols)
    r = book_returns(w, opens.to_numpy(float), closes.to_numpy(float), costs, symbols)
    return pd.Series(r, index=closes.index)
