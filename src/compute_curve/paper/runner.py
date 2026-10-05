"""Backtest and forward drivers. Both call the same :func:`run_day`.

* **Backtest**: iterate calendar days over a historical window with a fresh
  account and write to a run-scoped ledger.
* **Forward**: load the persisted forward account, process each day since the
  last processed day up to ``today``, persist. Running twice on the same day
  is a no-op (idempotent).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

import duckdb
import pandas as pd

from compute_curve.config import Config
from compute_curve.paper import ledger
from compute_curve.paper.engine import CostModel, Strategy, new_account, run_day
from compute_curve.paper.market import MarketData

FORWARD_RUN_ID = "forward"


@dataclass(frozen=True)
class RunResult:
    run_id: str
    account: pd.DataFrame
    fills: pd.DataFrame
    cash_flows: pd.DataFrame
    events: pd.DataFrame
    is_synthetic: bool
    cost_multiplier: float


def _days(start: date, end: date) -> list[date]:
    return [start + timedelta(days=i) for i in range((end - start).days + 1)]


def run_backtest(
    market: MarketData,
    strategy: Strategy,
    start: date,
    end: date,
    cfg: Config,
    run_id: str,
    cost_multiplier: float = 1.0,
    con: duckdb.DuckDBPyConnection | None = None,
    strategy_name: str = "",
) -> RunResult:
    if run_id == FORWARD_RUN_ID:
        raise ValueError("backtests may not use the forward run id")
    con = con or ledger.open_ledger(None)
    ledger.register_run(
        con, run_id, "backtest", cfg, cost_multiplier, market.is_synthetic, strategy_name
    )
    if ledger.last_day(con, run_id) is not None:
        raise ValueError(f"run {run_id} already exists in this ledger")
    state = new_account(cfg)
    costs = CostModel.from_config(cfg, cost_multiplier)
    buf = ledger.LedgerBuffer()
    for d in _days(start, end):
        rec = run_day(state, d, market, strategy, cfg, costs)
        buf.add(run_id, rec, state)
    buf.flush(con)
    return RunResult(
        run_id=run_id,
        account=ledger.table(con, "account_daily", run_id),
        fills=ledger.table(con, "fills", run_id),
        cash_flows=ledger.table(con, "cash_flows", run_id),
        events=ledger.table(con, "events", run_id),
        is_synthetic=market.is_synthetic,
        cost_multiplier=cost_multiplier,
    )


def run_forward(
    market: MarketData,
    strategy: Strategy,
    today: date,
    cfg: Config,
    con: duckdb.DuckDBPyConnection,
    start_if_new: date | None = None,
    strategy_name: str = "",
    allow_synthetic_for_tests: bool = False,
) -> list[date]:
    """Process forward days up to ``today``. Return the days processed (maybe none)."""
    if market.is_synthetic and not allow_synthetic_for_tests:
        raise ValueError("forward mode refuses synthetic market data")
    ledger.register_run(
        con, FORWARD_RUN_ID, "forward", cfg, 1.0, market.is_synthetic, strategy_name
    )
    state = ledger.load_state(con, FORWARD_RUN_ID, cfg)
    first = (state.last_date + timedelta(days=1)) if state.last_date else (start_if_new or today)
    processed: list[date] = []
    costs = CostModel.from_config(cfg, 1.0)
    for d in _days(first, today) if first <= today else []:
        rec = run_day(state, d, market, strategy, cfg, costs)
        ledger.write_day(con, FORWARD_RUN_ID, rec, state)
        processed.append(d)
    return processed
