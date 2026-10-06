"""Claim-4 orchestration: evaluation (tests, gate, reports) and the daily cycle.

``run_evaluation`` fetches bars, runs every pre-registered family, writes
``reports/claim4/evaluation.md``, the data manifest and the validation file
``var/claim4_validation.json``.

``run_daily`` decides for the next session inside its decision window,
appends the shadow prediction to ``reports/claim4/predictions.csv``, sends
paper orders only if the gate selected a pair and every risk check passes,
and writes ``reports/claim4/daily/<date>.md``.

Nothing written under ``reports/`` contains a price, a per-stock return
series or a dollar balance (decision D29).
"""

from __future__ import annotations

import csv
import json
import logging
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from datetime import timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from compute_curve.backtest import variants
from compute_curve.claim4 import analysis as an
from compute_curve.claim4 import stats as cs
from compute_curve.claim4.alpaca import AlpacaDataClient, AlpacaPaperClient
from compute_curve.claim4.market_data import (
    BAR_DELAY,
    fetch_bars_cached,
    manifest,
    sessions_from_calendar,
    write_manifest,
)
from compute_curve.claim4.risk import RiskState, evaluate_risk
from compute_curve.claim4.signals import SIGNAL_NAMES, build_signals
from compute_curve.claim4.strategy import (
    CLIENT_PREFIX,
    Order,
    apply_limits,
    cohort_target,
    flatten_orders,
    orders_for_targets,
)
from compute_curve.config import Claim4Config, Config
from compute_curve.reporting import fmt, frame_to_md
from compute_curve.timeutil import utc_now

log = logging.getLogger(__name__)

PRED_FIELDS = (
    "decided_at_utc",
    "target_session",
    "asof_h100",
    "asof_b200",
    *SIGNAL_NAMES,
    "selected_pair",
    "action",
    "forecasts_json",
)


def claim4_cfg(cfg: Config) -> Claim4Config:
    if cfg.claim4 is None:
        raise RuntimeError("config has no [claim4] section")
    return cfg.claim4


def paths(cfg: Config) -> dict[str, Path]:
    rep = cfg.path("reports") / "claim4"
    var = cfg.path("var")
    return {
        "reports": rep,
        "daily": rep / "daily",
        "evaluation": rep / "evaluation.md",
        "manifest": rep / "data_manifest.json",
        "signals": rep / "signals.csv",
        "predictions": rep / "predictions.csv",
        "orders": rep / "orders.csv",
        "validation": var / "claim4_validation.json",
        "cache": var / "market_data",
    }


# ---------------------------------------------------------------------------
# Shared context
# ---------------------------------------------------------------------------
@dataclass
class Context:
    now: pd.Timestamp
    sessions: pd.DataFrame
    signals: pd.DataFrame
    features: dict[str, pd.DataFrame]
    bars: pd.DataFrame
    dataset: pd.DataFrame
    manifest: dict[str, Any]


def last_final_session(sessions: pd.DataFrame, now: pd.Timestamp) -> Any:
    """Latest session whose daily bar is final at ``now`` (close + BAR_DELAY)."""
    done = sessions.loc[pd.to_datetime(sessions["close_utc"], utc=True) + BAR_DELAY <= now]
    return done["session"].max() if not done.empty else None


def build_context(
    cfg: Config,
    now: pd.Timestamp,
    paper: AlpacaPaperClient,
    data: AlpacaDataClient,
    observations: pd.DataFrame | None = None,
    refresh: bool = True,
) -> Context:
    c4 = claim4_cfg(cfg)
    cal = paper.calendar(c4.bars_start.isoformat(), (now.date() + timedelta(days=14)).isoformat())
    sessions = sessions_from_calendar(cal)
    if observations is None:
        from compute_curve.pipeline import load_inputs  # noqa: PLC0415

        observations = load_inputs(cfg).observations
    signals, feats = build_signals(
        observations,
        cfg.index,
        c4.panels,
        sessions,
        c4.open_buffer_minutes,
        c4.availability_margin_minutes,
        c4.daily_cutoff_utc,
    )
    end = last_final_session(sessions, now)
    if end is None:
        raise RuntimeError("no completed session to fetch bars for")
    symbols = [*c4.universe.members(), c4.benchmark]
    start = c4.bars_start.isoformat()
    end_close = sessions.loc[sessions["session"] == end, "close_utc"].iloc[0]
    end_param = (pd.Timestamp(end_close) + BAR_DELAY).strftime("%Y-%m-%dT%H:%M:%SZ")
    bars = fetch_bars_cached(
        data,
        symbols,
        start,
        end.isoformat(),
        paths(cfg)["cache"],
        c4.feed,
        c4.adjustment,
        refresh,
        end_param=end_param,
    )
    bars = bars.loc[bars["session"] <= end]
    dataset = an.build_dataset(signals, bars, sessions, c4)
    man = manifest(bars, start, end.isoformat(), c4.feed, c4.adjustment)
    man["universe"] = c4.universe.buckets()
    man["benchmark"] = c4.benchmark
    return Context(now, sessions, signals, feats, bars, dataset, man)


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------
@dataclass
class Evaluation:
    generated: str
    lead: list[an.LeadLag]
    buckets: list[an.LeadLag]
    events: list[an.EventResult]
    wf: list[an.WalkForward]
    strategies: list[an.StrategyResult]
    gate_rows: list[an.GateRow]
    selected: str | None
    crosscorr: pd.DataFrame
    sample: dict[str, Any] = field(default_factory=dict)


def evaluate(ctx: Context, cfg: Config) -> Evaluation:
    c4 = claim4_cfg(cfg)
    seed, nb = cfg.project.seed, cfg.bootstrap.n_boot
    df, now = ctx.dataset, ctx.now
    lead = an.lead_lag_family(df, now, c4, [an.BASKET], "P", "holm", c4.alpha, nb, seed)
    buckets = an.lead_lag_family(
        df, now, c4, list(c4.universe.buckets()), "S", "bh", c4.fdr_q, nb, seed
    )
    events = an.event_family(df, now, c4, nb, seed)
    wf, forecasts = an.walk_forward_family(df, now, c4)
    strategies = [
        an.evaluate_strategy(forecasts[(s, h)], s, h, c4, nb, seed)
        for s in c4.signals
        for h in c4.horizons
    ]
    rows, selected = an.gate(lead, wf, strategies, c4)
    cc = pd.concat(
        [
            an.cross_correlogram(df, s, now, n_boot=nb, seed=seed)
            for s in ("level_h100", "level_b200")
        ],
        ignore_index=True,
    )
    sample = {}
    for h in c4.horizons:
        known = pd.to_datetime(df[f"known_h{h}"], utc=True) <= now
        m = df["in_sample"] & known & df[f"R_basket_h{h}"].notna()
        sess = df.loc[m, "session"]
        sample[h] = {
            "n": int(m.sum()),
            "first": str(sess.min()) if len(sess) else None,
            "last": str(sess.max()) if len(sess) else None,
        }
    return Evaluation(
        now.isoformat(), lead, buckets, events, wf, strategies, rows, selected, cc, sample
    )


def validation_payload(ev: Evaluation, cfg: Config) -> dict[str, Any]:
    return {
        "generated": ev.generated,
        "plan": "docs/claim4_plan.md",
        "selected": ev.selected,
        "pairs": {
            f"{r.signal}|h{r.horizon}": {
                "G1": r.g1_leadlag,
                "G2": r.g2_walkforward,
                "G3": r.g3_strategy,
                "G4": r.g4_sufficiency,
                "validated": r.validated,
                "reasons": r.reasons,
            }
            for r in ev.gate_rows
        },
        "tests_declared_claim4": variants.count_tests("claim4"),
        "seed": cfg.project.seed,
    }


def run_evaluation(
    cfg: Config,
    now: pd.Timestamp | None = None,
    paper: AlpacaPaperClient | None = None,
    data: AlpacaDataClient | None = None,
    observations: pd.DataFrame | None = None,
) -> Path:
    now = now or pd.Timestamp(utc_now())
    p = paths(cfg)
    own_p, own_d = paper is None, data is None
    paper = paper or AlpacaPaperClient()
    data = data or AlpacaDataClient()
    try:
        ctx = build_context(cfg, now, paper, data, observations)
    finally:
        if own_p:
            paper.close()
        if own_d:
            data.close()
    ev = evaluate(ctx, cfg)
    p["reports"].mkdir(parents=True, exist_ok=True)
    p["validation"].parent.mkdir(parents=True, exist_ok=True)
    p["validation"].write_text(json.dumps(validation_payload(ev, cfg), indent=2, default=str))
    write_manifest(p["manifest"], ctx.manifest)
    write_signals_csv(ctx, cfg, p["signals"])
    p["evaluation"].write_text(render_evaluation(ev, ctx, cfg))
    return p["evaluation"]


def write_signals_csv(ctx: Context, cfg: Config, path: Path) -> None:
    """Our own signals per session (derived from CC BY 4.0 listings; no market data)."""
    c4 = claim4_cfg(cfg)
    cols = ["session", "asof_h100", "asof_b200", *SIGNAL_NAMES]
    s = ctx.signals.loc[ctx.signals["session"] >= c4.first_session, cols]
    s = s.loc[pd.to_datetime(s["session"]) <= pd.Timestamp(ctx.now.date())]
    path.parent.mkdir(parents=True, exist_ok=True)
    s.to_csv(path, index=False, float_format="%.6f")


def _rows(items: list[Any], keys: list[str]) -> pd.DataFrame:
    return pd.DataFrame([{k: asdict(i)[k] for k in keys} for i in items])


def render_evaluation(ev: Evaluation, ctx: Context, cfg: Config) -> str:
    c4 = claim4_cfg(cfg)
    n_tests = variants.count_tests("claim4")
    lines = [
        "# Claim 4 evaluation: does our GPU rental index lead compute-linked equities?",
        "",
        f"Generated {ev.generated}. Pre-registration: `docs/claim4_plan.md`. "
        f"Tests and evaluations declared for claim 4: {n_tests}; variant entries project-wide: "
        f"{variants.count()}.",
        "",
        "Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends. Bars are not "
        f"stored in the repository (D29); manifest `reports/claim4/data_manifest.json`, SHA-256 "
        f"`{(ctx.manifest.get('sha256') or '')[:16]}...`. Index: fixed-panel history series built "
        'from gpurentalprices.com data (CC BY 4.0, "GPU rental price data by gpurentalprices.com").',
        "",
        "This report shows aggregate statistics only. Outcome: category-balanced basket of "
        f"{len(c4.universe.members())} compute-linked stocks minus {c4.benchmark}, from the open "
        "after the signal to the close h sessions later.",
        "",
        "## Verdict",
        "",
    ]
    if ev.selected:
        lines.append(f"- Gate passed for `{ev.selected}`; paper orders are allowed if G5 holds.")
    else:
        lines.append(
            "- **No signal passed the validation gate. The paper strategy stays in shadow mode.**"
        )
    n_pass_p = sum(r.passes for r in ev.lead)
    lines += [
        f"- Family P (primary lead-lag): {n_pass_p} of {len(ev.lead)} tests pass after Holm "
        "and the permutation check.",
        f"- Family E (event study): {sum(r.passes for r in ev.events)} of {len(ev.events)} pass; "
        f"events per GPU and horizon range from {min(r.n_events for r in ev.events)} to "
        f"{max(r.n_events for r in ev.events)} (minimum for inference: {c4.min_events}).",
        f"- Family W (walk-forward): {sum(r.passes for r in ev.wf)} of {len(ev.wf)} pass; at most "
        f"{max(r.n_oos for r in ev.wf)} out-of-sample forecasts (minimum: {c4.min_oos_forecasts}).",
        f"- Family S (bucket baskets, secondary): {sum(r.passes for r in ev.buckets)} of "
        f"{len(ev.buckets)} pass at a false discovery rate of {c4.fdr_q:.0%}.",
        "",
        "## Sample and power",
        "",
    ]
    prows = []
    for h, info in ev.sample.items():
        n = info["n"]
        prows.append(
            {
                "horizon (sessions)": h,
                "windows": n,
                "first": info["first"],
                "last": info["last"],
                "MDE |rho|, alpha 0.05": cs.mde_correlation(n, c4.alpha),
                "MDE |rho|, Holm first step": cs.mde_correlation(n, c4.alpha / len(ev.lead)),
            }
        )
    lines += [
        frame_to_md(pd.DataFrame(prows), 2),
        "",
        "MDE: smallest correlation detectable with 80% power (Fisher z). Windows overlap for h > 1, "
        "so the effective sample is smaller still. Realistic predictive correlations for daily "
        "returns are 0.1 or less; detecting 0.1 after Holm needs about "
        f"{cs.n_for_correlation(0.10, c4.alpha / len(ev.lead)):,} sessions.",
        "",
        "## Family P: lead-lag, basket minus benchmark (primary)",
        "",
        "Slope: excess return in % for a signal change of 0.01. rho: Pearson correlation with a 95% "
        "block-bootstrap interval. p HAC: Newey-West t-test; p Holm: adjusted over the 18 tests; "
        "p perm: circular-shift permutation.",
        "",
    ]
    lines.append(frame_to_md(_leadlag_table(ev.lead), 3))
    lines += ["", "## Family E: event study on index moves of 2% or more", ""]
    et = pd.DataFrame(
        [
            {
                "GPU": r.gpu,
                "h": r.horizon,
                "events": r.n_events,
                "mean signed CAR %": 100 * r.mean_signed_car,
                "95% CI %": _ci(100 * r.ci_lo, 100 * r.ci_hi),
                "p sign-flip": r.p_sign_flip,
                "p Holm": r.p_adj,
                "passes": r.passes,
                "note": r.note,
            }
            for r in ev.events
        ]
    )
    lines += [frame_to_md(et, 3), ""]
    lines += [
        "## Family W: walk-forward forecasts against naive baselines",
        "",
        "Baselines: B0 zero excess return; B1 expanding mean. R2 OS: out-of-sample R-squared of "
        "the model relative to each baseline. CW p: Clark-West one-sided p-value; Holm over the "
        "18 models uses the larger of the two.",
        "",
    ]
    wt = pd.DataFrame(
        [
            {
                "signal": r.signal,
                "h": r.horizon,
                "OOS": r.n_oos,
                "R2 OS vs B0": r.r2_vs_b0,
                "R2 OS vs B1": r.r2_vs_b1,
                "CW p B0": r.cw_p_b0,
                "CW p B1": r.cw_p_b1,
                "hit rate": r.hit_rate,
                "p Holm": r.p_adj,
                "passes": r.passes,
                "note": r.note,
            }
            for r in ev.wf
        ]
    )
    lines += [frame_to_md(wt, 3), ""]
    lines += [
        "## Gate G3: long-short strategy on the walk-forward forecasts, net of costs",
        "",
        "Trades only when the forecast exceeds the round-trip cost. Mean net return per window "
        "in %, by cost multiple. Costs are assumptions (docs/claim4_plan.md section 7): "
        f"{c4.costs.stock_side_bps:g} bps per side for stocks, {c4.costs.benchmark_side_bps:g} bps "
        f"for {c4.benchmark}, {c4.costs.sell_fee_bps:g} bp fees on sells, borrow "
        f"{c4.costs.stock_borrow_annual:.1%} a year on short stocks and "
        f"{c4.costs.benchmark_borrow_annual:.1%} on the short benchmark.",
        "",
    ]
    st_rows = []
    for r in ev.strategies:
        row = {
            "signal": r.signal,
            "h": r.horizon,
            "windows": r.n_windows,
            "trades": r.n_trades,
            "Sharpe": r.sharpe,
            "95% CI": _ci(r.sharpe_lo, r.sharpe_hi),
            "passes": r.passes,
        }
        row.update({k: 100 * v for k, v in r.by_multiplier.items()})
        st_rows.append(row)
    lines += [frame_to_md(pd.DataFrame(st_rows), 3), ""]
    lines += [
        "## Gate",
        "",
        frame_to_md(
            pd.DataFrame(
                [
                    {
                        "pair": f"{r.signal}|h{r.horizon}",
                        "G1": r.g1_leadlag,
                        "G2": r.g2_walkforward,
                        "G3": r.g3_strategy,
                        "G4": r.g4_sufficiency,
                        "validated": r.validated,
                    }
                    for r in ev.gate_rows
                ]
            )
        ),
        "",
        "## Family S: bucket baskets (secondary; cannot open the gate)",
        "",
        "p adj: Benjamini-Hochberg over the 54 tests.",
        "",
        frame_to_md(_leadlag_table(ev.buckets, with_target=True), 3),
        "",
        "## Diagnostic: cross-correlogram (descriptive, not a test)",
        "",
        "corr(signal at session t, basket excess return of session t+k). k < 0: returns realized "
        "before the signal was known; k = 0 is the predictive test.",
        "",
        frame_to_md(_crosscorr_table(ev.crosscorr), 2),
        "",
    ]
    return "\n".join(lines) + "\n"


def _ci(lo: float, hi: float) -> str:
    if not (np.isfinite(lo) and np.isfinite(hi)):
        return "n/a"
    return f"[{lo:.2f}, {hi:.2f}]"


def _leadlag_table(items: list[an.LeadLag], with_target: bool = False) -> pd.DataFrame:
    rows = []
    for r in items:
        row: dict[str, object] = {}
        if with_target:
            row["target"] = r.target
        row.update(
            {
                "signal": r.signal,
                "h": r.horizon,
                "n": r.n,
                "non-zero": r.n_nonzero,
                "slope": r.slope,
                "rho": r.rho,
                "rho 95% CI": _ci(r.rho_lo, r.rho_hi),
                "p HAC": r.p_hac,
                "p adj": r.p_adj,
                "p perm": r.p_perm,
                "passes": r.passes,
                "note": r.note,
            }
        )
        rows.append(row)
    return pd.DataFrame(rows)


def _crosscorr_table(cc: pd.DataFrame) -> pd.DataFrame:
    if cc.empty:
        return cc
    t = cc.assign(
        cell=[
            f"{r:.2f} {_ci(lo, hi)}" if np.isfinite(r) else "n/a"
            for r, lo, hi in zip(cc["rho"], cc["lo"], cc["hi"], strict=True)
        ]
    )
    return t.pivot_table(index="k", columns="signal", values="cell", aggfunc="first").reset_index()


# ---------------------------------------------------------------------------
# Daily cycle
# ---------------------------------------------------------------------------
@dataclass
class Decision:
    run_at: pd.Timestamp
    target_session: Any
    target_open: pd.Timestamp
    window_start: pd.Timestamp
    window_end: pd.Timestamp
    deciding: bool
    already_logged: bool = False
    mode: str = "deferred"
    selected: str | None = None
    forecasts: dict[str, float] = field(default_factory=dict)
    signals: dict[str, float] = field(default_factory=dict)
    asof: dict[str, str] = field(default_factory=dict)
    index_ok: bool = True
    index_notes: list[str] = field(default_factory=list)
    risk: RiskState | None = None
    orders: list[dict[str, Any]] = field(default_factory=list)
    order_notes: list[str] = field(default_factory=list)
    gate_reasons: list[str] = field(default_factory=list)


def decision_window(
    sessions: pd.DataFrame, now: pd.Timestamp, cfg: Claim4Config
) -> tuple[Any, pd.Timestamp, pd.Timestamp, pd.Timestamp]:
    """Next session, its open, and the window in which a run may decide for it.

    The window opens at the daily cutoff on the UTC day before the session's
    open and closes ``open_buffer_minutes`` before the open, so only the last
    scheduled run before a session decides for it.
    """
    s = sessions.sort_values("open_utc")
    nxt = s.loc[pd.to_datetime(s["open_utc"], utc=True) > now].iloc[0]
    open_utc = pd.Timestamp(nxt["open_utc"])
    hh, mm = (int(x) for x in cfg.daily_cutoff_utc.split(":"))
    start = open_utc.normalize() - pd.Timedelta(days=1) + pd.Timedelta(hours=hh, minutes=mm)
    end = open_utc - pd.Timedelta(minutes=cfg.open_buffer_minutes)
    return nxt["session"], open_utc, start, end


def read_predictions(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=list(PRED_FIELDS))
    return pd.read_csv(path, dtype=str)


def append_rows(path: Path, fields: tuple[str, ...], rows: list[Mapping[str, Any]]) -> None:
    """Append-only CSV log; the header is written once."""
    path.parent.mkdir(parents=True, exist_ok=True)
    new = not path.exists()
    with path.open("a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(fields))
        if new:
            w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})


def _load_validation(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"selected": None, "pairs": {}}
    return json.loads(path.read_text())


def _directions(
    df: pd.DataFrame, signal: str, h: int, now: pd.Timestamp, cfg: Claim4Config, target: Any
) -> list[int]:
    """Cohort directions for the ``h`` sessions ending at ``target`` (older first)."""
    fc = an.walk_forward(df, signal, h, now, cfg)
    by = {r.session: r.forecast for r in fc.itertuples()}
    order = list(df.sort_values("open_utc")["session"])
    i = order.index(target)
    out = []
    for s in order[max(0, i - h + 1) : i + 1]:
        f = by.get(s)
        d = 0 if f is None or not np.isfinite(f) else int(np.sign(f))
        if d != 0 and abs(f) <= an.round_trip_cost(d, h, cfg):
            d = 0
        out.append(d)
    return out


def _current_qty(positions: list[dict[str, Any]]) -> dict[str, float]:
    out = {}
    for p in positions:
        q = float(p.get("qty", 0) or 0)
        if str(p.get("side", "long")) == "short" and q > 0:
            q = -q
        out[str(p["symbol"])] = q
    return out


def _submit(
    paper: AlpacaPaperClient, orders: list[Order], session: str, run_stamp: str
) -> list[dict[str, Any]]:
    out = []
    for o in orders:
        body = o.payload(session, run_stamp)
        try:
            resp = paper.submit_order(body)
            status = str(resp.get("status", "submitted"))
        except Exception as exc:  # every failure is recorded; none stops the run
            status = f"rejected: {type(exc).__name__}"
        out.append(
            {
                **{k: body[k] for k in ("symbol", "side", "qty", "client_order_id")},
                "reason": o.reason,
                "status": status,
            }
        )
    return out


def _cancel_open_claim4_orders(paper: AlpacaPaperClient) -> int:
    n = 0
    for o in paper.orders(status="open"):
        if str(o.get("client_order_id", "")).startswith(f"{CLIENT_PREFIX}-"):
            paper.cancel_order(str(o["id"]))
            n += 1
    return n


def env_check(paper: AlpacaPaperClient, data: AlpacaDataClient) -> list[str]:
    """Read-only check: account status and one daily-bar request. Prints no value."""
    lines = []
    acct = paper.account()
    lines.append(
        f"account: status {acct.get('status')}, paper prefix "
        f"{str(acct.get('account_number', '')).startswith('PA')}, "
        f"trading_blocked {acct.get('trading_blocked')}"
    )
    clock = paper.clock()
    lines.append(f"clock: market open {clock.get('is_open')}, next open {clock.get('next_open')}")
    bars = data.daily_bars(["SPY"], "2026-09-01", "2026-09-30")
    lines.append(f"market data: {len(bars.get('SPY', []))} SPY daily bars for 2026-09")
    return lines


def run_daily(
    cfg: Config,
    now: pd.Timestamp | None = None,
    paper: AlpacaPaperClient | None = None,
    data: AlpacaDataClient | None = None,
    observations: pd.DataFrame | None = None,
    env: Mapping[str, str] | None = None,
) -> Path:
    claim4_cfg(cfg)
    now = now or pd.Timestamp(utc_now())
    p = paths(cfg)
    own_p, own_d = paper is None, data is None
    paper = paper or AlpacaPaperClient()
    data = data or AlpacaDataClient()
    try:
        ctx = build_context(cfg, now, paper, data, observations, refresh=False)
        dec = _decide(ctx, cfg, paper, env)
    finally:
        if own_p:
            paper.close()
        if own_d:
            data.close()
    out = p["daily"] / f"{now.date().isoformat()}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_daily(dec, cfg))
    return out


ORDER_FIELDS = (
    "run_at_utc",
    "session",
    "symbol",
    "side",
    "qty",
    "client_order_id",
    "reason",
    "status",
)


def _fill_inputs(dec: Decision, df: pd.DataFrame, now: pd.Timestamp, c4: Claim4Config) -> None:
    """Signals, index freshness (G5) and walk-forward forecasts for the target session."""
    row = df.loc[df["session"] == dec.target_session].iloc[0]
    dec.signals = {s: float(row[s]) if pd.notna(row[s]) else float("nan") for s in SIGNAL_NAMES}
    dec.asof = {g: str(row[f"asof_{g}"]) for g in ("h100", "b200")}
    for g in ("h100", "b200"):
        d = row[f"asof_{g}"]
        if d is None or pd.isna(d):
            dec.index_ok = False
            dec.index_notes.append(f"{g.upper()}: no covered index day")
            continue
        age = (pd.Timestamp(dec.target_session) - pd.Timestamp(d)).days
        if age > c4.max_index_age_days:
            dec.index_ok = False
            dec.index_notes.append(f"{g.upper()}: index day {d} is {age} days old")
    for s in c4.signals:
        for h in c4.horizons:
            fc = an.walk_forward(df, s, h, now, c4)
            hit = fc.loc[fc["session"] == dec.target_session, "forecast"]
            dec.forecasts[f"{s}|h{h}"] = float(hit.iloc[0]) if len(hit) else float("nan")


def _paper_orders(
    dec: Decision, ctx: Context, c4: Claim4Config, paper: AlpacaPaperClient, run_stamp: str
) -> None:
    """Rebalance the claim-4 pair toward the cohort target, within the hard limits."""
    managed = [*c4.universe.members(), c4.benchmark]
    sig, h_txt = str(dec.selected).split("|h")
    h = int(h_txt)
    dirs = _directions(ctx.dataset, sig, h, ctx.now, c4, dec.target_session)
    assets = {s: paper.asset(s) for s in managed}
    shortable = {s: bool(a.get("shortable")) for s, a in assets.items()}
    fractionable = {s: bool(a.get("fractionable")) for s, a in assets.items()}
    scaled = apply_limits(cohort_target(dirs, h, c4, shortable), c4)
    last = ctx.bars.sort_values("session").groupby("symbol").tail(1)
    price = dict(zip(last["symbol"], last["close"], strict=True))
    cur = _current_qty(paper.positions())
    orders, notes = orders_for_targets(scaled.target, cur, price, fractionable, managed)
    dec.order_notes += [*scaled.notes, *notes, f"cohort directions (older first): {dirs}"]
    _cancel_open_claim4_orders(paper)
    dec.orders = _submit(paper, orders, str(dec.target_session), run_stamp)


def _flatten(dec: Decision, c4: Claim4Config, paper: AlpacaPaperClient, run_stamp: str) -> None:
    managed = [*c4.universe.members(), c4.benchmark]
    cur = _current_qty(paper.positions())
    _cancel_open_claim4_orders(paper)
    dec.orders = _submit(paper, flatten_orders(cur, managed), str(dec.target_session), run_stamp)
    dec.mode = "flatten"


def _log(dec: Decision, p: dict[str, Path]) -> None:
    now, target = dec.run_at, str(dec.target_session)
    if dec.orders:
        rows = [{"run_at_utc": now.isoformat(), "session": target, **o} for o in dec.orders]
        append_rows(p["orders"], ORDER_FIELDS, rows)
    if dec.already_logged:
        return
    forecasts = {k: (round(v, 6) if np.isfinite(v) else None) for k, v in dec.forecasts.items()}
    append_rows(
        p["predictions"],
        PRED_FIELDS,
        [
            {
                "decided_at_utc": now.isoformat(),
                "target_session": target,
                "asof_h100": dec.asof["h100"],
                "asof_b200": dec.asof["b200"],
                **{k: f"{v:.6f}" for k, v in dec.signals.items()},
                "selected_pair": dec.selected or "",
                "action": dec.mode,
                "forecasts_json": json.dumps(forecasts, sort_keys=True),
            }
        ],
    )


def _decide(
    ctx: Context, cfg: Config, paper: AlpacaPaperClient, env: Mapping[str, str] | None
) -> Decision:
    c4 = claim4_cfg(cfg)
    p = paths(cfg)
    target, t_open, w_start, w_end = decision_window(ctx.sessions, ctx.now, c4)
    dec = Decision(ctx.now, target, t_open, w_start, w_end, w_start <= ctx.now <= w_end)
    _fill_inputs(dec, ctx.dataset, ctx.now, c4)
    dec.selected = _load_validation(p["validation"]).get("selected")
    if not dec.selected:
        dec.gate_reasons.append("no signal validated (var/claim4_validation.json)")
    acct = paper.account()
    hist = paper.portfolio_history(period="1A", timeframe="1D")
    dec.risk = evaluate_risk(acct, hist, c4, env)
    preds = read_predictions(p["predictions"])
    traded_before = bool((preds.get("action", pd.Series(dtype=str)) == "paper").any())
    logged = preds.get("target_session", pd.Series(dtype=str)) == str(target)
    dec.already_logged = bool(logged.any())
    if not dec.deciding:
        dec.mode = "deferred"
        return dec
    can_trade = bool(dec.selected) and dec.index_ok and not dec.risk.blocks_new_positions
    dec.mode = "paper" if can_trade else "shadow"
    run_stamp = ctx.now.strftime("%Y%m%dT%H%M%S")
    if dec.mode == "paper":
        _paper_orders(dec, ctx, c4, paper, run_stamp)
    elif traded_before and (dec.risk.requires_flatten or not dec.selected):
        _flatten(dec, c4, paper, run_stamp)
    _log(dec, p)
    return dec


def render_daily(dec: Decision, cfg: Config) -> str:
    c4 = claim4_cfg(cfg)
    mode = {
        "shadow": "SHADOW: prediction logged, no orders sent",
        "paper": "PAPER: gated orders sent to the Alpaca paper account",
        "flatten": "FLATTEN: closing claim-4 paper positions",
        "deferred": "DEFERRED: a later scheduled run decides for the next session",
    }[dec.mode]
    lines = [
        f"# Claim 4 daily cycle, {dec.run_at.date().isoformat()}",
        "",
        f"Run at {dec.run_at.isoformat()}. **Mode: {mode}.**",
        "",
        f"- Next session: {dec.target_session} (opens {dec.target_open.isoformat()}).",
        f"- Decision window: {dec.window_start.isoformat()} to {dec.window_end.isoformat()}.",
    ]
    if dec.already_logged and dec.deciding:
        lines.append("- A prediction for this session was already logged; the first one stands.")
    lines += [
        f"- Index days used: H100 {dec.asof.get('h100')}, B200 {dec.asof.get('b200')}. "
        + ("Coverage and freshness OK." if dec.index_ok else "; ".join(dec.index_notes)),
        "",
        "## Signals for the next session",
        "",
        frame_to_md(pd.DataFrame([{"signal": k, "value": v} for k, v in dec.signals.items()]), 5),
        "",
        "## Walk-forward forecasts of basket excess return (%), fitted on data known now",
        "",
    ]
    rows = []
    for s in c4.signals:
        row: dict[str, object] = {"signal": s}
        for h in c4.horizons:
            v = dec.forecasts.get(f"{s}|h{h}", float("nan"))
            row[f"h={h}"] = 100 * v if np.isfinite(v) else float("nan")
        rows.append(row)
    lines += [
        frame_to_md(pd.DataFrame(rows), 3),
        "",
        "n/a: fewer than "
        f"{c4.min_train} training windows. Forecasts are logged for later evaluation; none is "
        "validated.",
        "",
        "## Gate",
        "",
        f"- Selected pair: {dec.selected or 'none'}.",
        *[f"- {r}" for r in dec.gate_reasons],
        "",
        "## Risk checks (percentages only; balances are not stored, D29)",
        "",
    ]
    r = dec.risk
    if r is not None:
        lines += [
            f"- Kill switch: {'ON' if r.kill_switch else 'off'}.",
            f"- Drawdown latch: {'ON' if r.drawdown_latched else 'off'} "
            f"(current drawdown {fmt(r.drawdown_pct, 2)}%).",
            f"- Daily P&L: {fmt(r.daily_pnl_pct, 2)}%; daily loss breach today: "
            f"{'yes' if r.daily_breach_today else 'no'}; halted after a recent breach: "
            f"{'yes' if r.halted_after_breach else 'no'}.",
            *[f"- {n}" for n in r.notes],
        ]
    lines += ["", "## Orders", ""]
    if dec.orders:
        lines.append(frame_to_md(pd.DataFrame(dec.orders)))
    else:
        lines.append("None.")
    lines += [*[f"- {n}" for n in dec.order_notes], ""]
    lines += [
        f"Costs assumed: docs/claim4_plan.md section 7. Tests declared for claim 4: "
        f"{variants.count_tests('claim4')}.",
        "",
    ]
    return "\n".join(lines) + "\n"
