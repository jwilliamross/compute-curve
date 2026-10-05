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
from compute_curve.index.own_index import (
    build_daily_index,
    build_history_index,
    provider_breakdown,
)
from compute_curve.paper import ledger
from compute_curve.paper.market import MarketData
from compute_curve.paper.runner import FORWARD_RUN_ID, run_forward
from compute_curve.paper.signals import SignalBook, load_validated, make_strategy
from compute_curve.reporting import fmt, frame_to_md
from compute_curve.snapshot import run_snapshot
from compute_curve.storage import warehouse as wh


@dataclass(frozen=True)
class Inputs:
    observations: pd.DataFrame
    own_index: pd.DataFrame  # headline multi-source index
    own_index_hist: pd.DataFrame  # fixed-panel single-publisher series used by models
    reference: pd.DataFrame  # third-party index values (CGI, GetDeploying)
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
        wh.register_reference_indices(con, p["raw"])
        obs = wh.observations_frame(con)
        ref = wh.reference_indices_frame(con)
    finally:
        con.close()
    own = build_daily_index(obs, cfg.index)
    own_hist = build_history_index(obs, cfg.index) if not obs.empty else own.iloc[0:0]
    pub = wh.load_published_index_csvs(p["manual_index"], cfg.nowcast.publication_lag_days)
    st = wh.load_settlement_csvs(p["manual_settle"])
    # Models read the fixed-panel series: its composition is stable over time.
    market = MarketData.build(settlements=st, published_index=pub, own_index=own_hist)
    return Inputs(obs, own, own_hist, ref, pub, st, market)


def write_own_index_outputs(cfg: Config, inp: Inputs) -> Path:
    rep = paths(cfg)["reports"]
    rep.mkdir(parents=True, exist_ok=True)
    both = pd.concat(
        [
            inp.own_index.assign(series="headline"),
            inp.own_index_hist.assign(series="history_panel"),
        ],
        ignore_index=True,
    )
    both.to_csv(rep / "own_index.csv", index=False)
    latest = inp.own_index.sort_values("as_of_date").groupby("gpu_model").tail(1)
    hist_tail = inp.own_index_hist.sort_values("as_of_date").groupby("gpu_model").tail(10)
    lines = [
        "# Our H100 / B200 on-demand index",
        "",
        "Built from collected listings only; no Silicon Data values are used.",
        f"Method: `{cfg.index.method}`. Methodology and caveats: `docs/index_methodology.md`.",
        "A value is used only if `meets_coverage` is true "
        f"(at least {cfg.index.min_providers} providers and {cfg.index.min_listings} listings).",
        "",
        "Two series are kept (full history in `reports/own_index.csv`):",
        "",
        "- **headline**: every approved source, one source per provider per day. Its "
        "composition changes when sources are added, so it is not used for time-series models.",
        "- **history_panel**: the gpurentalprices.com archive and live feed only, restricted to a "
        "provider panel fixed from the first 30 days. Models and evaluations use this series.",
        "",
        "## Headline, latest day",
        "",
        frame_to_md(latest.drop(columns=["ts_available"]), 3) if not latest.empty else "_none_",
        "",
        "## History panel, last 10 days",
        "",
        frame_to_md(hist_tail.drop(columns=["ts_available"]), 3)
        if not hist_tail.empty
        else "_none_",
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
    """Run the daily cycle for ``today`` and write its report.

    Idempotent: every output is a function of stored state (raw data, the
    collection log and the paper ledger), so a same-day re-run rewrites the
    report with identical content.
    """
    if do_snapshot:
        run_snapshot(cfg)
    inp = load_inputs(cfg)
    write_own_index_outputs(cfg, inp)
    p = paths(cfg)
    validated = load_validated(p["validation"])
    book = SignalBook()
    strategy = make_strategy(cfg, validated, book)
    con = ledger.open_ledger(p["paper"])
    try:
        run_forward(
            inp.market, strategy, today, cfg, con, start_if_new=today, strategy_name="signals"
        )
        _write_predictions(con, book)
        state = ledger.load_state(con, FORWARD_RUN_ID, cfg)
        acct = ledger.table(con, "account_daily", FORWARD_RUN_ID)
        events = ledger.table(con, "events", FORWARD_RUN_ID)
        fills = ledger.table(con, "fills", FORWARD_RUN_ID)
        preds = _predictions_for(con, today)
    finally:
        con.close()
    log_rows = collection_log_for(cfg, today)
    return write_daily_report(
        cfg, today, log_rows, inp, state, acct, validated, preds, events, fills
    )


def collection_log_for(cfg: Config, day: date) -> pd.DataFrame:
    """Collection attempts logged on UTC date ``day``."""
    path = cfg.path("data") / "collection_log.jsonl"
    cols = ["source", "status", "n_listings", "n_indices", "n_dropped", "detail"]
    if not path.exists():
        return pd.DataFrame(columns=cols)
    rows = [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
    # Skips made no request; older runs logged them, so filter them here.
    rows = [
        r
        for r in rows
        if str(r.get("ts", ""))[:10] == day.isoformat() and r.get("status") != "skipped_exists"
    ]
    if not rows:
        return pd.DataFrame(columns=cols)
    df = pd.DataFrame(rows)
    for c in cols:
        if c not in df.columns:
            df[c] = None
    return df[cols]


def _predictions_for(con: duckdb.DuckDBPyConnection, day: date) -> pd.DataFrame:
    exists = con.execute(
        "SELECT count(*) FROM information_schema.tables WHERE table_name = 'predictions'"
    ).fetchone()
    if not exists or not exists[0]:
        return pd.DataFrame()
    rows = con.execute(
        "SELECT payload FROM predictions WHERE run_id = ? AND day = ? ORDER BY signal, payload",
        [FORWARD_RUN_ID, day],
    ).fetchall()
    return pd.DataFrame([json.loads(r[0]) for r in rows]) if rows else pd.DataFrame()


def write_daily_report(
    cfg: Config,
    today: date,
    log_rows: pd.DataFrame,
    inp: Inputs,
    state: ledger.AccountState,
    acct: pd.DataFrame,
    validated: set[str],
    preds: pd.DataFrame,
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
        "## Ingestion (collection log for this UTC date)",
        "",
        frame_to_md(log_rows) if not log_rows.empty else "No collection attempts logged today.",
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
    if not preds.empty:
        lines.append(frame_to_md(preds.astype(str)))
    else:
        lines.append(
            "No signal evaluations today: no CME settlements are available, so the paper "
            "account has nothing to trade or mark."
        )
    first = acct["day"].min() if not acct.empty else None
    lines += [
        "",
        "## Paper account (forward run)",
        "",
        f"- Days processed: {len(acct)} (first {first or 'n/a'}, last {state.last_date or 'n/a'})",
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
