"""Claim-5 orchestration: fetch the AWS spot data and build the daily series.

``run_fetch`` downloads the pre-registered months (verified, immutable,
git-ignored), filters them to GPU instance types in US availability zones
on Linux/UNIX, and writes:

* ``var/aws_spot/pool_daily.parquet``: price in effect per pool per day
  (derived, rebuildable);
* ``reports/claim5/aws_spot_daily.csv``: per day and GPU class, pools
  offered, median USD per GPU-hour and IQR of log price (committed;
  CC BY 4.0, attribution in the file header of the manifest);
* ``reports/claim5/aws_spot_manifest.json``: record, DOI, files, checksums,
  rows kept and coverage.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import duckdb
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
from compute_curve.claim4.pipeline import (
    Evaluation,
    _ci,
    _crosscorr_table,
    _leadlag_table,
    last_final_session,
)
from compute_curve.claim5 import aws_spot as aw
from compute_curve.claim5.signals import build_signals
from compute_curve.config import Claim4Config, Claim5Config, Config
from compute_curve.reporting import frame_to_md
from compute_curve.timeutil import utc_now


def claim5_cfg(cfg: Config) -> Claim5Config:
    if cfg.claim5 is None:
        raise RuntimeError("config has no [claim5] section")
    return cfg.claim5


def paths(cfg: Config) -> dict[str, Path]:
    c5 = claim5_cfg(cfg)
    var = cfg.path("var") / "aws_spot"
    rep = cfg.path("reports") / "claim5"
    return {
        "raw": var / "raw" / str(c5.zenodo_record),
        "filtered": var / "filtered",
        "pool_daily": var / "pool_daily.parquet",
        "reports": rep,
        "daily_csv": rep / "aws_spot_daily.csv",
        "manifest": rep / "aws_spot_manifest.json",
        "signals": rep / "signals.csv",
        "evaluation": rep / "evaluation.md",
        "bars_manifest": rep / "data_manifest.json",
        "validation": cfg.path("var") / "claim5_validation.json",
        "cache": cfg.path("var") / "market_data",
    }


def _write_parquet(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    try:
        con.register("frame", df)
        con.execute(f"COPY frame TO '{path.as_posix()}' (FORMAT PARQUET)")
    finally:
        con.close()


def read_pool_daily(path: Path) -> pd.DataFrame:
    con = duckdb.connect()
    try:
        cols = "day, az_id, instance_type, gpu, price_per_gpu_hour"
        df = con.execute(f"SELECT {cols} FROM read_parquet('{path.as_posix()}')").df()  # noqa: S608
    finally:
        con.close()
    df["day"] = pd.to_datetime(df["day"]).dt.date
    return df


def run_fetch(cfg: Config) -> dict[str, Any]:
    c5 = claim5_cfg(cfg)
    p = paths(cfg)
    keys = {f"{m}.tsv.zst": aw.AUDITED_FILES[f"{m}.tsv.zst"] for m in c5.months}
    log = aw.download_files(keys, p["raw"], cfg.http.user_agent)
    kept = {}
    for key in keys:
        out = p["filtered"] / f"{aw.month_of(key)}.parquet"
        kept[key] = aw.filter_file(p["raw"] / key, out)
    records = aw.load_filtered(sorted(p["filtered"].glob("*.parquet")))
    records = records.loc[records["month"].isin(c5.months)]
    pools = aw.pool_daily(records, c5.cutoff_utc)
    _write_parquet(pools, p["pool_daily"])
    daily = aw.class_daily(pools)
    p["reports"].mkdir(parents=True, exist_ok=True)
    daily.to_csv(p["daily_csv"], index=False, float_format="%.6f")
    sizes = {e["key"]: e["bytes"] for e in log}
    manifest = {
        "source": aw.ATTRIBUTION,
        "zenodo_record": aw.RECORD_ID,
        "doi": aw.DOI,
        "version": aw.VERSION,
        "licence": "CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)",
        "changes": "Filtered to GPU instance types in US availability zones on Linux/UNIX; "
        "daily price in effect at the cutoff, divided by GPUs per instance.",
        "filters": {
            "instance_types": aw.GPU_TYPES,
            "az_prefixes": aw.US_AZ_PREFIXES,
            "product": aw.PRODUCT,
            "cutoff_utc": c5.cutoff_utc,
        },
        "files": {k: {"md5": keys[k], "bytes": sizes.get(k), "rows_kept": kept[k]} for k in keys},
        "coverage": [asdict(c) for c in aw.coverage(records)],
        "missing_months_in_dataset": ["2026-03", "2026-04", "2026-05", "2026-06"],
    }
    p["manifest"].write_text(json.dumps(manifest, indent=2, default=str) + "\n")
    return manifest


# ---------------------------------------------------------------------------
# Evaluation: claim 4's battery, unchanged, on the claim-5 signals
# ---------------------------------------------------------------------------
def battery_config(cfg: Config) -> Claim4Config:
    """Claim 4's settings with the claim-5 signals and sample start (the gate is unchanged)."""
    c4, c5 = cfg.claim4, claim5_cfg(cfg)
    if c4 is None:
        raise RuntimeError("config has no [claim4] section")
    return c4.model_copy(
        update={
            "signals": c5.signals,
            "first_session": c5.first_session,
            "bars_start": c5.bars_start,
        }
    )


def apply_member_start(bars: pd.DataFrame, starts: dict[str, date]) -> pd.DataFrame:
    """Drop a member's bars before its pre-registered start date."""
    keep = pd.Series(True, index=bars.index)
    for sym, start in starts.items():
        keep &= ~((bars["symbol"] == sym) & (bars["session"] < start))
    return bars.loc[keep]


@dataclass
class Context5:
    now: pd.Timestamp
    sessions: pd.DataFrame
    signals: pd.DataFrame
    bars: pd.DataFrame
    dataset: pd.DataFrame
    manifest: dict[str, Any]


def build_context(
    cfg: Config,
    now: pd.Timestamp,
    paper: AlpacaPaperClient,
    data: AlpacaDataClient,
    pools: pd.DataFrame | None = None,
    refresh: bool = True,
) -> Context5:
    c5, bc = claim5_cfg(cfg), battery_config(cfg)
    cal = paper.calendar(c5.bars_start.isoformat(), (now.date() + timedelta(days=14)).isoformat())
    sessions = sessions_from_calendar(cal)
    pools = read_pool_daily(paths(cfg)["pool_daily"]) if pools is None else pools
    signals = build_signals(pools, sessions, c5, bc.open_buffer_minutes)
    end = last_final_session(sessions, now)
    if end is None:
        raise RuntimeError("no completed session to fetch bars for")
    end_close = sessions.loc[sessions["session"] == end, "close_utc"].iloc[0]
    end_param = (pd.Timestamp(end_close) + BAR_DELAY).strftime("%Y-%m-%dT%H:%M:%SZ")
    symbols = [*bc.universe.members(), bc.benchmark]
    start = c5.bars_start.isoformat()
    bars = fetch_bars_cached(
        data,
        symbols,
        start,
        end.isoformat(),
        paths(cfg)["cache"],
        bc.feed,
        bc.adjustment,
        refresh,
        end_param=end_param,
    )
    bars = apply_member_start(bars.loc[bars["session"] <= end], c5.member_start)
    dataset = an.build_dataset(signals, bars, sessions, bc)
    man = manifest(bars, start, end.isoformat(), bc.feed, bc.adjustment)
    man["member_start"] = {k: str(v) for k, v in c5.member_start.items()}
    return Context5(now, sessions, signals, bars, dataset, man)


def evaluate(ctx: Context5, cfg: Config) -> Evaluation:
    c5, bc = claim5_cfg(cfg), battery_config(cfg)
    seed, nb = cfg.project.seed, cfg.bootstrap.n_boot
    df, now = ctx.dataset, ctx.now
    lead = an.lead_lag_family(df, now, bc, [an.BASKET], "P", "holm", bc.alpha, nb, seed)
    buckets = an.lead_lag_family(
        df, now, bc, list(bc.universe.buckets()), "S", "bh", bc.fdr_q, nb, seed
    )
    events = an.event_family(df, now, bc, nb, seed, gpus=c5.gpu_classes)
    wf, forecasts = an.walk_forward_family(df, now, bc)
    strategies = [
        an.evaluate_strategy(forecasts[(s, h)], s, h, bc, nb, seed)
        for s in bc.signals
        for h in bc.horizons
    ]
    rows, selected = an.gate(lead, wf, strategies, bc)
    levels = [s for s in bc.signals if s.startswith("level_")]
    cc = pd.concat(
        [an.cross_correlogram(df, s, now, n_boot=nb, seed=seed) for s in levels], ignore_index=True
    )
    sample = {}
    has_signal = df[list(bc.signals)].notna().any(axis=1)
    for h in bc.horizons:
        known = pd.to_datetime(df[f"known_h{h}"], utc=True) <= now
        m = df["in_sample"] & known & df[f"R_basket_h{h}"].notna() & has_signal
        sess = df.loc[m, "session"]
        sample[h] = {
            "n": int(m.sum()),
            "first": str(sess.min()) if len(sess) else None,
            "last": str(sess.max()) if len(sess) else None,
        }
    return Evaluation(
        now.isoformat(), lead, buckets, events, wf, strategies, rows, selected, cc, sample
    )


def member_history(bars: pd.DataFrame, members: list[str]) -> pd.DataFrame:
    first = bars.groupby("symbol")["session"].min()
    return pd.DataFrame(
        {"symbol": members, "first bar used": [str(first.get(s, "none")) for s in members]}
    )


def render(ev: Evaluation, ctx: Context5, cfg: Config) -> str:
    bc = battery_config(cfg)
    n_tests = variants.count_tests("claim5")
    holm_n = len(ev.lead)
    lines = [
        "# Claim 5 evaluation: do AWS GPU spot prices lead compute-linked equities?",
        "",
        f"Generated {ev.generated}. Pre-registration: `docs/claim5_plan.md`. Tests and evaluations "
        f"declared for claim 5: {n_tests}; variant entries project-wide: {variants.count()}.",
        "",
        f"Signal data: {aw.ATTRIBUTION}. Filtered to GPU instance types in US availability zones on "
        "Linux/UNIX (`reports/claim5/aws_spot_manifest.json`).",
        "",
        "Bars: Alpaca market data API, SIP feed, adjusted for splits and dividends; not stored "
        f"(D29). Manifest `reports/claim5/data_manifest.json`, SHA-256 "
        f"`{(ctx.manifest.get('sha256') or '')[:16]}...`. Outcome: claim 4's category-balanced "
        f"basket of {len(bc.universe.members())} stocks minus {bc.benchmark}, open after the "
        "signal to the close h sessions later. Aggregate statistics only.",
        "",
        "## Verdict",
        "",
        "- **Gate passed for `" + ev.selected + "`.**"
        if ev.selected
        else "- **No signal passed the validation gate (unchanged from claim 4).**",
        f"- Family P (primary lead-lag): {sum(r.passes for r in ev.lead)} of {len(ev.lead)} pass "
        "after Holm and the permutation check.",
        f"- Family E (event study): {sum(r.passes for r in ev.events)} of {len(ev.events)} pass; "
        f"events per GPU and horizon: {min(r.n_events for r in ev.events)} to "
        f"{max(r.n_events for r in ev.events)} (minimum for inference {bc.min_events}).",
        f"- Family W (walk-forward): {sum(r.passes for r in ev.wf)} of {len(ev.wf)} pass; up to "
        f"{max(r.n_oos for r in ev.wf)} out-of-sample forecasts (minimum {bc.min_oos_forecasts}).",
        f"- Family S (bucket baskets, secondary): {sum(r.passes for r in ev.buckets)} of "
        f"{len(ev.buckets)} pass at a false discovery rate of {bc.fdr_q:.0%}.",
        "",
        "## Sample and power",
        "",
    ]
    prows = [
        {
            "horizon (sessions)": h,
            "windows": info["n"],
            "first": info["first"],
            "last": info["last"],
            "MDE |rho|, alpha 0.05": cs.mde_correlation(info["n"], bc.alpha),
            "MDE |rho|, Holm first step": cs.mde_correlation(info["n"], bc.alpha / holm_n),
        }
        for h, info in ev.sample.items()
    ]
    lines += [frame_to_md(pd.DataFrame(prows), 2), "", "### Member history used", ""]
    lines += [frame_to_md(member_history(ctx.bars, bc.universe.members())), ""]
    lines += [
        "## Family P: lead-lag, basket minus benchmark (primary)",
        "",
        "Slope: excess return in % for a signal change of 0.01. p adj: Holm over the "
        f"{holm_n} tests. p perm: circular-shift permutation.",
        "",
        frame_to_md(_leadlag_table(ev.lead), 3),
        "",
        "## Family E: event study on spot moves of 2% or more",
        "",
    ]
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
    lines += [
        frame_to_md(et, 3),
        "",
        "## Family W: walk-forward forecasts against naive baselines",
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
    lines += [frame_to_md(wt, 3), "", "## Gate G3: long-short strategy, net of claim 4's costs", ""]
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
    lines += [frame_to_md(pd.DataFrame(st_rows), 3), "", "## Gate", ""]
    lines.append(
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
        )
    )
    lines += [
        "",
        "## Family S: bucket baskets (secondary; cannot open the gate)",
        "",
        f"p adj: Benjamini-Hochberg over the {len(ev.buckets)} tests.",
        "",
        frame_to_md(_leadlag_table(ev.buckets, with_target=True), 3),
        "",
        "## Diagnostic: cross-correlogram (descriptive, not a test)",
        "",
        "corr(signal at session t, basket excess return of session t+k); k < 0: returns before "
        "the signal was known.",
        "",
        frame_to_md(_crosscorr_table(ev.crosscorr), 2),
        "",
    ]
    return "\n".join(lines) + "\n"


def run_evaluation(
    cfg: Config,
    now: pd.Timestamp | None = None,
    paper: AlpacaPaperClient | None = None,
    data: AlpacaDataClient | None = None,
    pools: pd.DataFrame | None = None,
) -> Path:
    now = now or pd.Timestamp(utc_now())
    p = paths(cfg)
    own_p, own_d = paper is None, data is None
    paper = paper or AlpacaPaperClient()
    data = data or AlpacaDataClient()
    try:
        ctx = build_context(cfg, now, paper, data, pools)
    finally:
        if own_p:
            paper.close()
        if own_d:
            data.close()
    ev = evaluate(ctx, cfg)
    p["reports"].mkdir(parents=True, exist_ok=True)
    p["validation"].parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated": ev.generated,
        "plan": "docs/claim5_plan.md",
        "selected": ev.selected,
        "pairs": {
            f"{r.signal}|h{r.horizon}": {"validated": r.validated, "reasons": r.reasons}
            for r in ev.gate_rows
        },
    }
    p["validation"].write_text(json.dumps(payload, indent=2, default=str))
    write_manifest(p["bars_manifest"], ctx.manifest)
    bc = battery_config(cfg)
    cols = ["session", *[c for c in ctx.signals.columns if c.startswith("asof_")], *bc.signals]
    sig = ctx.signals.loc[ctx.signals["session"] >= bc.first_session, cols]
    sig.loc[pd.to_datetime(sig["session"]) <= pd.Timestamp(now.date())].to_csv(
        p["signals"], index=False, float_format="%.6f"
    )
    p["evaluation"].write_text(render(ev, ctx, cfg))
    return p["evaluation"]
