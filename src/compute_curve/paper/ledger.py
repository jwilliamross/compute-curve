"""DuckDB ledger for the simulated account.

Tables (all keyed by ``run_id`` so forward and backtest runs never mix):

* ``runs``           run metadata (mode, config hash, cost multiplier, synthetic flag)
* ``account_daily``  one row per processed calendar day
* ``positions``      end-of-day positions
* ``orders``         order state transitions (pending, filled, replaced, cancelled)
* ``fills``          simulated fills with cost breakdown
* ``cash_flows``     every cash movement (variation margin, costs, fees, final settlement)
* ``events``         risk breaches, limit clips, expiries

Rows are only ever inserted. The ledger is the full audit trail.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from datetime import date
from pathlib import Path

import duckdb
import pandas as pd

from compute_curve.config import Config
from compute_curve.paper.engine import AccountState, DayRecord, Order, Position

DDL = """
CREATE TABLE IF NOT EXISTS runs (
    run_id VARCHAR PRIMARY KEY, mode VARCHAR, created_ts TIMESTAMPTZ, config_hash VARCHAR,
    cost_multiplier DOUBLE, is_synthetic BOOLEAN, strategy VARCHAR, note VARCHAR
);
CREATE TABLE IF NOT EXISTS account_daily (
    run_id VARCHAR, day DATE, cash DOUBLE, equity DOUBLE, peak_equity DOUBLE, drawdown DOUBLE,
    day_pnl DOUBLE, gross_contracts INTEGER, n_pending INTEGER, halted BOOLEAN, killed BOOLEAN,
    trading_day BOOLEAN, halted_until DATE, order_seq INTEGER,
    PRIMARY KEY (run_id, day)
);
CREATE TABLE IF NOT EXISTS positions (
    run_id VARCHAR, day DATE, product VARCHAR, contract_month VARCHAR, qty INTEGER, mark DOUBLE
);
CREATE TABLE IF NOT EXISTS orders (
    run_id VARCHAR, day DATE, order_id VARCHAR, decision_date DATE, product VARCHAR,
    contract_month VARCHAR, qty INTEGER, reason VARCHAR, status VARCHAR, fill_date DATE
);
CREATE TABLE IF NOT EXISTS fills (
    run_id VARCHAR, day DATE, order_id VARCHAR, product VARCHAR, contract_month VARCHAR,
    qty INTEGER, settle_price DOUBLE, fill_price DOUBLE, spread_slippage_cost DOUBLE, fees DOUBLE
);
CREATE TABLE IF NOT EXISTS cash_flows (
    run_id VARCHAR, day DATE, kind VARCHAR, product VARCHAR, contract_month VARCHAR, amount DOUBLE
);
CREATE TABLE IF NOT EXISTS events (run_id VARCHAR, day DATE, kind VARCHAR, detail VARCHAR);
"""


def config_hash(cfg: Config) -> str:
    blob = json.dumps(cfg.model_dump(mode="json"), sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest()[:16]


def open_ledger(path: Path | None) -> duckdb.DuckDBPyConnection:
    if path is None:
        con = duckdb.connect()
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        con = duckdb.connect(path.as_posix())
    con.execute("SET TimeZone = 'UTC'")
    con.execute(DDL)
    return con


def register_run(
    con: duckdb.DuckDBPyConnection,
    run_id: str,
    mode: str,
    cfg: Config,
    cost_multiplier: float,
    is_synthetic: bool,
    strategy: str,
    note: str = "",
) -> None:
    exists = con.execute("SELECT 1 FROM runs WHERE run_id = ?", [run_id]).fetchone()
    if exists:
        return
    con.execute(
        "INSERT INTO runs VALUES (?, ?, now(), ?, ?, ?, ?, ?)",
        [run_id, mode, config_hash(cfg), cost_multiplier, is_synthetic, strategy, note],
    )


def _insert(con: duckdb.DuckDBPyConnection, table: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    df = pd.DataFrame(rows)
    cols = [r[0] for r in con.execute(f"DESCRIBE {table}").fetchall()]
    df = df.reindex(columns=cols)
    con.register("_tmp_rows", df)
    try:
        con.execute(f"INSERT INTO {table} SELECT * FROM _tmp_rows")  # noqa: S608
    finally:
        con.unregister("_tmp_rows")


TABLES = ("account_daily", "positions", "orders", "fills", "cash_flows", "events")


def rows_for_day(
    run_id: str, rec: DayRecord, state: AccountState
) -> dict[str, list[dict[str, object]]]:
    """Ledger rows produced by one processed day, keyed by table."""
    base = {"run_id": run_id, "day": rec.day}
    return {
        "account_daily": [
            {
                **base,
                **rec.account,
                "halted_until": state.halted_until,
                "order_seq": state.order_seq,
            }
        ],
        "positions": [{**base, **p} for p in rec.positions],
        "orders": [{**base, **o} for o in rec.orders],
        "fills": [{**base, **f} for f in rec.fills],
        "cash_flows": [{**base, **c} for c in rec.cash_flows],
        "events": [{**base, **e} for e in rec.events],
    }


class LedgerBuffer:
    """Accumulates rows in memory and inserts them in one batch per table."""

    def __init__(self) -> None:
        self.rows: dict[str, list[dict[str, object]]] = {t: [] for t in TABLES}

    def add(self, run_id: str, rec: DayRecord, state: AccountState) -> None:
        for table, rows in rows_for_day(run_id, rec, state).items():
            self.rows[table].extend(rows)

    def flush(self, con: duckdb.DuckDBPyConnection) -> None:
        for table in TABLES:
            _insert(con, table, self.rows[table])
            self.rows[table] = []


def write_day(
    con: duckdb.DuckDBPyConnection, run_id: str, rec: DayRecord, state: AccountState
) -> None:
    buf = LedgerBuffer()
    buf.add(run_id, rec, state)
    buf.flush(con)


def last_day(con: duckdb.DuckDBPyConnection, run_id: str) -> date | None:
    row = con.execute("SELECT max(day) FROM account_daily WHERE run_id = ?", [run_id]).fetchone()
    return row[0] if row and row[0] is not None else None


def load_state(con: duckdb.DuckDBPyConnection, run_id: str, cfg: Config) -> AccountState:
    """Rebuild the account state at the end of the last processed day."""
    d = last_day(con, run_id)
    if d is None:
        cash = cfg.risk.starting_cash
        return AccountState(cash=cash, peak_equity=cash)
    acct = con.execute(
        "SELECT cash, peak_equity, halted_until, killed, order_seq FROM account_daily "
        "WHERE run_id = ? AND day = ?",
        [run_id, d],
    ).fetchone()
    if acct is None:
        raise RuntimeError("inconsistent ledger")
    cash, peak, halted_until, killed, seq = acct
    pos_rows = con.execute(
        "SELECT product, contract_month, qty, mark FROM positions WHERE run_id = ? AND day = ?",
        [run_id, d],
    ).fetchall()
    pend_rows = con.execute(
        "SELECT order_id, decision_date, product, contract_month, qty, reason FROM orders "
        "WHERE run_id = ? AND day = ? AND status = 'pending' ORDER BY order_id",
        [run_id, d],
    ).fetchall()
    return AccountState(
        cash=float(cash),
        peak_equity=float(peak),
        positions={(p, m): Position(int(q), float(mk)) for p, m, q, mk in pos_rows},
        pending=[Order(o, dd, p, m, int(q), r) for o, dd, p, m, q, r in pend_rows],
        halted_until=halted_until,
        killed=bool(killed),
        last_date=d,
        order_seq=int(seq or 0),
    )


DATE_COLUMNS = ("day", "decision_date", "fill_date", "halted_until")


def table(con: duckdb.DuckDBPyConnection, name: str, run_id: str) -> pd.DataFrame:
    """All rows of ``name`` for ``run_id``; DATE columns come back as ``datetime.date``."""
    df = con.execute(
        f"SELECT * FROM {name} WHERE run_id = ? ORDER BY day",  # noqa: S608
        [run_id],
    ).df()
    for c in DATE_COLUMNS:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c]).dt.date
    return df


def state_summary(state: AccountState) -> dict[str, object]:
    return {
        "cash": state.cash,
        "equity": state.equity,
        "peak_equity": state.peak_equity,
        "positions": {f"{k[0]} {k[1]}": asdict(p) for k, p in state.positions.items()},
        "pending_orders": [asdict(o) for o in state.pending],
        "halted_until": state.halted_until,
        "killed": state.killed,
        "last_date": state.last_date,
    }
