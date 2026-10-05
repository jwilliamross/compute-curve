"""Daily cycle orchestration shared by the CLI.

``daily``: ingest prices (snapshot) -> rebuild our index -> load manual CME
settlements and published index files -> run the forward paper account
through today with validated signals (others in shadow mode) -> write a
markdown report under ``reports/daily/``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import duckdb
import pandas as pd

from compute_curve.config import Config
from compute_curve.index.own_index import build_daily_index, provider_breakdown
from compute_curve.paper import ledger
from compute_curve.paper.market import MarketData
from compute_curve.paper.runner import FORWARD_RUN_ID, run_forward
from compute_curve.paper.signals import SignalBook, load_validated, make_strategy
from compute_curve.reporting import fmt, frame_to_md
from compute_curve.snapshot import SnapshotOutcome, run_snapshot
from compute_curve.storage import warehouse as wh


@dataclass(frozen=True)
class Inputs:
    observations: pd.DataFrame
    own_index: pd.DataFrame
    published: pd.DataFrame
    settlements: pd.DataFrame
    market: MarketData


def paths(cfg: Config) -> dict[str, Path]:
    data, var, rep = cfg.path("data"), cfg.path("var"), cfg.path("reports")
    return {
        "raw": data / "raw",
        "manual_index": data / "manual" / "published_index",
        "manual_settle": data / "manual" / "cme_settlements",
        "warehouse": var / "warehouse.duckdb",
        "paper": var / "paper.duckdb",
        "validation": var / "validation.json",
        "reports": rep,
    }


def load_inputs(cfg: Config) -> Inputs:
    p = paths(cfg)
    con = wh.connect(None)
    try:
        wh.register_observations(con, p["raw"])
        obs = wh.observations_frame(con)
    finally:
        con.close()
    own = (
        build_daily_index(obs, cfg.index)
        if not obs.empty
        else build_daily_index(pd.DataFrame(), cfg.index)
    )
    pub = wh.load_published_index_csvs(p["manual_index"], cfg.nowcast.publication_lag_days)
    st = wh.load_settlement_csvs(p["manual_settle"])
    market = MarketData.build(settlements=st, published_index=pub, own_index=own)
    return Inputs(obs, own, pub, st, market)


def write_own_index_outputs(cfg: Config, inp: Inputs) -> Path:
    rep = paths(cfg)["reports"]
    rep.mkdir(parents=True, exist_ok=True)
    inp.own_index.to_csv(rep / "own_index.csv", index=False)
    lines = [
        "# Our H100 / B200 on-demand index",
        "",
        "Built from collected listings only (no published index values are used).",
        f"Method: `{cfg.index.method}`; methodology in `docs/index_methodology.md`.",
        "A value is used by models only if `meets_coverage` is true "
        f"(at least {cfg.index.min_providers} providers and {cfg.index.min_listings} listings).",
        "",
        frame_to_md(inp.own_index.drop(columns=["ts_available"]), 3),
    ]
    for model in ("H100", "B200"):
        lines += ["", f"## {model} by provider, latest day", ""]
        lines.append(frame_to_md(provider_breakdown(inp.observations, cfg.index, model), 3))
    out = rep / "own_index.md"
    out.write_text("\n".join(lines) + "\n")
    return out


def _write_predictions(con: duckdb.DuckDBPyConnection, book: SignalBook) -> None:
    con.execute(
        "CREATE TABLE IF NOT EXISTS predictions "
        "(run_id VARCHAR, day DATE, signal VARCHAR, payload VARCHAR)"
    )
    for row in book.rows:
        con.execute(
            "INSERT INTO predictions VALUES (?, ?, ?, ?)",
            [
                FORWARD_RUN_ID,
                row.get("decision_date"),
                row.get("signal"),
                json.dumps(row, default=str, sort_keys=True),
            ],
        )


def daily(cfg: Config, today: date, do_snapshot: bool = True) -> Path:
    outcomes: list[SnapshotOutcome] = run_snapshot(cfg) if do_snapshot else []
    inp = load_inputs(cfg)
    write_own_index_outputs(cfg, inp)
    p = paths(cfg)
    validated = load_validated(p["validation"])
    book = SignalBook()
    strategy = make_strategy(cfg, validated, book)
    con = ledger.open_ledger(p["paper"])
    try:
        processed = run_forward(
            inp.market, strategy, today, cfg, con, start_if_new=today, strategy_name="signals"
        )
        _write_predictions(con, book)
        state = ledger.load_state(con, FORWARD_RUN_ID, cfg)
        events = ledger.table(con, "events", FORWARD_RUN_ID)
        fills = ledger.table(con, "fills", FORWARD_RUN_ID)
    finally:
        con.close()
    return write_daily_report(
        cfg, today, outcomes, inp, processed, state, validated, book, events, fills
    )


def write_daily_report(
    cfg: Config,
    today: date,
    outcomes: list[SnapshotOutcome],
    inp: Inputs,
    processed: list[date],
    state: ledger.AccountState,
    validated: set[str],
    book: SignalBook,
    events: pd.DataFrame,
    fills: pd.DataFrame,
) -> Path:
    rep = paths(cfg)["reports"] / "daily"
    rep.mkdir(parents=True, exist_ok=True)
    latest = inp.own_index.sort_values("as_of_date").groupby("gpu_model").tail(1)
    lines = [
        f"# Daily report {today.isoformat()}",
        "",
        "Simulation only. No orders leave this machine.",
        "",
        "## Ingestion",
        "",
    ]
    if outcomes:
        lines.append(
            frame_to_md(
                pd.DataFrame([o.__dict__ for o in outcomes])[
                    ["source", "status", "n_rows", "n_dropped", "detail"]
                ]
            )
        )
    else:
        lines.append("Snapshot skipped by flag.")
    lines += [
        "",
        "## Inputs available",
        "",
        f"- Raw observations: {len(inp.observations)} rows.",
        f"- Published index values (manual files): {len(inp.published)} rows.",
        f"- CME settlements (manual files): {len(inp.settlements)} rows.",
        "",
        "## Our index, latest",
        "",
        frame_to_md(latest.drop(columns=["ts_available"]), 3) if not latest.empty else "_none_",
        "",
        "## Signals",
        "",
        f"Validated signals: {sorted(validated) or 'none'}. "
        "Unvalidated signals run in shadow mode and place no orders.",
        "",
    ]
    if book.rows:
        lines.append(frame_to_md(pd.DataFrame(book.rows).astype(str)))
    else:
        lines.append(
            "No signal evaluations today: no CME settlements are available, so the paper "
            "account has nothing to trade or mark."
        )
    lines += [
        "",
        "## Paper account (forward run)",
        "",
        f"- Days processed this run: {[d.isoformat() for d in processed] or 'none (already up to date)'}",
        f"- Equity: USD {fmt(state.equity, 2)}; peak USD {fmt(state.peak_equity, 2)}",
        f"- Positions: {dict(state.positions) or 'flat'}",
        f"- Pending orders: {len(state.pending)}",
        f"- Halted until: {state.halted_until or 'n/a'}; kill switch: {state.killed}",
        f"- Total fills to date: {len(fills)}; risk events to date: {len(events)}",
    ]
    out = rep / f"{today.isoformat()}.md"
    out.write_text("\n".join(lines) + "\n")
    return out


def status(cfg: Config) -> str:
    p = paths(cfg)
    if not p["paper"].exists():
        return "No forward paper account yet. Run `compute-curve daily` to create it."
    con = ledger.open_ledger(p["paper"])
    try:
        state = ledger.load_state(con, FORWARD_RUN_ID, cfg)
        acct = ledger.table(con, "account_daily", FORWARD_RUN_ID)
    finally:
        con.close()
    summary = ledger.state_summary(state)
    lines = [f"{k}: {v}" for k, v in summary.items()]
    if not acct.empty:
        lines.append(f"days processed: {len(acct)} ({acct['day'].min()} .. {acct['day'].max()})")
    lines.append(f"starting cash: {cfg.risk.starting_cash:,.2f}")
    return "\n".join(lines)
