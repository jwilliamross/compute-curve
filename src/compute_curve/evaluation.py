"""Claim tests on real data, validation gating, and backtest reports.

Every section first checks whether enough real data exists. When it does
not, the report says so and states what is missing; nothing is fitted.
Synthetic data appears only in the engine-validation report, which is
stamped as such and is never read by ``run_evaluation``.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from compute_curve.backtest import variants
from compute_curve.backtest.bootstrap import block_bootstrap_ci, paired_loss_difference_ci
from compute_curve.backtest.tearsheet import (
    cost_assumptions_md,
    cost_sensitivity,
    tearsheet,
    tearsheet_md,
)
from compute_curve.config import Config
from compute_curve.index.tracking import join_own_and_published, tracking_stats
from compute_curve.models import nowcast as nc
from compute_curve.models import relative_value as rv
from compute_curve.models import term_structure as ts_model
from compute_curve.models.schwartz_smith import SSParams, fit_spot_only
from compute_curve.paper.engine import AccountState, Key, Strategy, flat_strategy
from compute_curve.paper.market import MarketData, MarketView
from compute_curve.paper.runner import RunResult, run_backtest
from compute_curve.paper.signals import SignalBook, make_strategy
from compute_curve.pipeline import Inputs, load_inputs, paths
from compute_curve.reporting import fmt, frame_to_md
from compute_curve.synthetic import synthetic_config, synthetic_market
from compute_curve.timeutil import month_start, utc_now

MIN_TRACKING_DAYS = 20
MIN_NOWCAST_MONTHS = 6
MIN_RV_DAYS = 120


def _complete_months(published: pd.DataFrame, index_name: str) -> list[date]:
    p = published.loc[published["index_name"] == index_name]
    if p.empty:
        return []
    days = sorted(p["as_of_date"])
    first, last = days[0], days[-1]
    months = []
    m = month_start(first)
    if m < first:
        m = (m.replace(day=28) + timedelta(days=4)).replace(day=1)
    while m <= last:
        months.append(m)
        m = (m.replace(day=28) + timedelta(days=4)).replace(day=1)
    return months


def _covered(df: pd.DataFrame, gpu_model: str) -> pd.DataFrame:
    if df.empty:
        return df
    return df.loc[(df["gpu_model"] == gpu_model) & df["meets_coverage"].astype(bool)]


def data_sufficiency(cfg: Config, inp: Inputs) -> pd.DataFrame:
    rows = []
    for product, spec in cfg.contracts.items():
        own = _covered(inp.own_index, spec.gpu_model)
        hist = _covered(inp.own_index_hist, spec.gpu_model)
        pub = inp.published.loc[inp.published["index_name"] == spec.underlying_index]
        st = inp.settlements.loc[inp.settlements["product"] == product]
        rows.append(
            {
                "product": product,
                "own_headline_days": len(own),
                "own_panel_days": len(hist),
                "settlement_index_days": len(pub),
                "settlement_trade_days": st["trade_date"].nunique() if not st.empty else 0,
                "complete_published_months": len(
                    _complete_months(inp.published, spec.underlying_index)
                ),
            }
        )
    return pd.DataFrame(rows)


def eval_tracking(cfg: Config, inp: Inputs) -> list[str]:
    out = []
    for product, spec in cfg.contracts.items():
        j = join_own_and_published(
            inp.own_index, inp.published, spec.gpu_model, spec.underlying_index
        )
        ts = tracking_stats(
            j,
            spec.gpu_model,
            MIN_TRACKING_DAYS,
            cfg.bootstrap.n_boot,
            cfg.bootstrap.block_length,
            cfg.project.seed,
        )
        if ts is None:
            out.append(
                f"- {product} ({spec.gpu_model}): insufficient overlap ({len(j)} days with both our "
                f"index and the published index; need {MIN_TRACKING_DAYS}). No tracking error reported."
            )
        else:
            out.append(
                f"- {product}: {ts.n_days} days; mean log error {ts.mean_log_error:+.4f} "
                f"[{ts.mean_log_error_ci[0]:+.4f}, {ts.mean_log_error_ci[1]:+.4f}]; RMSE "
                f"{ts.rmse_log:.4f} [{ts.rmse_log_ci[0]:.4f}, {ts.rmse_log_ci[1]:.4f}]; "
                f"corr of daily changes {fmt(ts.corr_daily_changes, 3)}."
            )
    return out


def eval_nowcast(cfg: Config, inp: Inputs) -> tuple[list[str], dict[str, object]]:
    lines: list[str] = []
    verdicts: dict[str, object] = {}
    for product, spec in cfg.contracts.items():
        months = _complete_months(inp.published, spec.underlying_index)
        if len(months) < MIN_NOWCAST_MONTHS:
            lines.append(
                f"- {product}: insufficient data. {len(months)} complete months of published index "
                f"history with our index alongside; the pre-registered minimum is {MIN_NOWCAST_MONTHS}."
            )
            verdicts[product] = {
                "validated": False,
                "reason": "insufficient_data",
                "n_months": len(months),
            }
            continue
        errs = nc.evaluate(inp.market, spec, spec.gpu_model, months)
        mse = (errs.assign(se=errs["log_error"] ** 2)).groupby("method")["se"].mean()
        if "own_bridge" not in mse:
            lines.append(f"- {product}: our index has no coverage in the evaluation months.")
            verdicts[product] = {"validated": False, "reason": "no_own_index_coverage"}
            continue
        stronger = min(nc.BASELINES, key=lambda b: mse.get(b, np.inf))
        res = nc.cluster_bootstrap_diff(
            errs,
            "own_bridge",
            stronger,
            cfg.bootstrap.n_boot,
            cfg.bootstrap.confidence,
            cfg.project.seed,
        )
        ok = res.get("n_months", 0) >= MIN_NOWCAST_MONTHS and res.get("ci_high", 1.0) < 0
        lines.append(
            f"- {product}: {res.get('n_months')} months, {res.get('n_points')} decision points. "
            f"MSE(log) own_bridge {mse['own_bridge']:.6f} vs {stronger} {mse[stronger]:.6f}; "
            f"difference {res.get('mean_diff', float('nan')):+.6f} "
            f"[{res.get('ci_low', float('nan')):+.6f}, {res.get('ci_high', float('nan')):+.6f}]. "
            f"{'Beats' if ok else 'Does not beat'} the stronger baseline."
        )
        verdicts[product] = {"validated": ok, "reason": "tested", **res}
    return lines, verdicts


def eval_term_structure(cfg: Config, inp: Inputs) -> list[str]:
    lines = []
    for product, spec in cfg.contracts.items():
        pub = inp.published.loc[inp.published["index_name"] == spec.underlying_index]
        st = inp.settlements.loc[inp.settlements["product"] == product]
        n_settle_days = st["trade_date"].nunique() if not st.empty else 0
        if len(pub) < cfg.schwartz_smith.min_observations:
            lines.append(
                f"- {product}: spot-only fit skipped: {len(pub)} published index days, minimum "
                f"{cfg.schwartz_smith.min_observations}."
            )
        else:
            s = pub.set_index("as_of_date")["value"].sort_index()
            full = pd.Series(s, index=pd.date_range(s.index.min(), s.index.max()).date)
            fit = fit_spot_only(
                np.log(full.to_numpy(float)),
                cfg.schwartz_smith.dt_years,
                SSParams(),
                None,
                cfg.schwartz_smith.min_observations,
            )
            if fit is not None:
                p = fit.params
                lines.append(
                    f"- {product}: spot-only real-world fit on {fit.n_obs} days: kappa {p.kappa:.3f}, "
                    f"sigma_chi {p.sigma_chi:.3f}, sigma_xi {p.sigma_xi:.3f}, rho {p.rho:.3f}, "
                    f"mu_xi {p.mu_xi:+.3f}. Weakly identified from spot data alone "
                    "(docs/term_structure_model.md); descriptive only, not used for trading."
                )
        if n_settle_days < cfg.schwartz_smith.min_observations:
            lines.append(
                f"- {product}: model-versus-market test needs futures settlements and realized "
                f"final settlements. Available: {n_settle_days} settlement days, minimum "
                f"{cfg.schwartz_smith.min_observations}. Not testable yet."
            )
            continue
        base = SSParams(
            delta=cfg.schwartz_smith.depreciation_rate_prior,
            jump_mean=cfg.schwartz_smith.jump_mean_prior,
            jump_std=cfg.schwartz_smith.jump_std_prior,
        )
        rows = ts_model.walk_forward(
            inp.market, spec, cfg.launches, base, cfg.schwartz_smith.min_observations
        )
        if rows.empty:
            lines.append(f"- {product}: no forecast has a realized settlement yet.")
            continue
        for bl in ("futures", "random_walk"):
            lm = (np.log(rows["model"]) - np.log(rows["realized"])) ** 2
            lb = (np.log(rows[bl]) - np.log(rows["realized"])) ** 2
            mean, ci = paired_loss_difference_ci(
                lm.to_numpy(),
                lb.to_numpy(),
                cfg.bootstrap.n_boot,
                6,
                cfg.bootstrap.confidence,
                cfg.project.seed,
            )
            lines.append(
                f"- {product}: model vs {bl}, {len(rows)} forecasts over "
                f"{rows['contract_month'].nunique()} realized months: mean loss difference "
                f"{mean:+.5f} [{ci[0]:+.5f}, {ci[1]:+.5f}]."
            )
    return lines


def _series(df: pd.DataFrame, gpu_model: str) -> pd.Series:
    d = _covered(df, gpu_model)
    if d.empty:
        return pd.Series(dtype=float)
    return d.set_index("as_of_date")["value"].astype(float).sort_index()


def _ratio_verdict(ratio: float, cfg: Config) -> str:
    rc = cfg.relative_value
    central = "cheaper" if ratio < rc.perf_ratio_b200_over_h100 else "dearer"
    if ratio < rc.perf_ratio_low:
        robust = "cheaper across the whole assumed range"
    elif ratio > rc.perf_ratio_high:
        robust = "dearer across the whole assumed range"
    else:
        robust = "not robust: the break-even ratio lies inside the assumed range"
    return f"B200 is {central} per unit of compute at the central ratio; {robust}"


def eval_relative_value(cfg: Config, inp: Inputs) -> tuple[list[str], bool]:
    rc = cfg.relative_value
    lines = [
        f"Assumed B200/H100 throughput ratio {rc.perf_ratio_b200_over_h100} "
        f"(range {rc.perf_ratio_low}-{rc.perf_ratio_high}; docs/relative_value.md).",
        "",
    ]
    for label, frame in (("headline", inp.own_index), ("history panel", inp.own_index_hist)):
        h, b = _series(frame, "H100"), _series(frame, "B200")
        common = sorted(set(h.index) & set(b.index))
        if not common:
            lines.append(f"- {label}: no day with both series.")
            continue
        ratios = pd.Series([b[d] / h[d] for d in common], index=common)
        d = common[-1]
        lines.append(
            f"- {label}, {d}: H100 USD {h[d]:.3f}, B200 USD {b[d]:.3f} per GPU-hour; break-even "
            f"ratio {ratios.iloc[-1]:.2f} (min {ratios.min():.2f}, median {ratios.median():.2f}, "
            f"max {ratios.max():.2f} over {len(ratios)} days). {_ratio_verdict(ratios.iloc[-1], cfg)}."
        )
    ref = inp.reference
    for name_h, name_b, label in (
        ("Computable GPU Index H100", "Computable GPU Index B200", "Computable GPU Index"),
        (
            "GetDeploying nvidia-h100 ON_DEMAND weekly median",
            "GetDeploying nvidia-b200 ON_DEMAND weekly median",
            "GetDeploying weekly median",
        ),
    ):
        hh = _ref_daily(ref, name_h)
        bb = _ref_daily(ref, name_b)
        common = sorted(set(hh.index) & set(bb.index))
        if common:
            r = bb[common[-1]] / hh[common[-1]]
            lines.append(
                f"- {label}, {common[-1]}: break-even ratio {r:.2f}. {_ratio_verdict(r, cfg)}."
            )
    h, b = _series(inp.own_index_hist, "H100"), _series(inp.own_index_hist, "B200")
    spread = (
        rv.log_spread(b, h, rc.perf_ratio_b200_over_h100)
        if len(h) and len(b)
        else pd.Series(dtype=float)
    )
    lines.append("")
    if len(spread) < MIN_RV_DAYS:
        lines.append(
            f"- Spread mean-reversion test (H4): insufficient history ({len(spread)} days on the "
            f"fixed panel; minimum {MIN_RV_DAYS}). Not run."
        )
        return lines, False
    preds = rv.walk_forward_ar1(spread, horizon=5, min_train=60)
    ev = rv.evaluate_spread_forecast(
        preds, 5, cfg.bootstrap.n_boot, cfg.bootstrap.block_length, cfg.project.seed
    )
    ok = ev is not None and ev.ci[1] < 0
    if ev is not None:
        lines.append(
            f"- AR(1) vs random walk, 5-day spread change, {ev.n} forecasts: MSE {ev.mse_model:.6f} vs "
            f"{ev.mse_random_walk:.6f}; difference {ev.mean_diff:+.6f} [{ev.ci[0]:+.6f}, {ev.ci[1]:+.6f}]."
        )
    lines.append("- This tests the spot spread. A tradable test needs futures settlements.")
    return lines, ok


def _ref_daily(ref: pd.DataFrame, index_name: str) -> pd.Series:
    """Last value per UTC date of a reference index (latest vintage)."""
    if ref.empty:
        return pd.Series(dtype=float)
    r = ref.loc[ref["index_name"] == index_name].copy()
    if r.empty:
        return pd.Series(dtype=float)
    r["as_of"] = pd.to_datetime(r["as_of"], utc=True)
    r["d"] = r["as_of"].dt.date
    return r.sort_values("as_of").groupby("d")["value"].last().astype(float)


def _vol_ci(
    values: pd.Series, periods_per_year: float, cfg: Config
) -> tuple[float, tuple[float, float], float, int]:
    r = np.diff(np.log(values.to_numpy(float)))
    if r.size < 10:
        return float("nan"), (float("nan"), float("nan")), float("nan"), int(r.size)
    scale = float(np.sqrt(periods_per_year))
    vol = float(np.std(r, ddof=1) * scale)
    ci = block_bootstrap_ci(
        r,
        lambda x: float(np.std(x, ddof=1) * scale),
        cfg.bootstrap.n_boot,
        cfg.bootstrap.block_length,
        cfg.bootstrap.confidence,
        cfg.project.seed,
    )
    return vol, ci, float(np.mean(r == 0)), int(r.size)


def describe_series(cfg: Config, inp: Inputs) -> pd.DataFrame:
    """Descriptive statistics of every real price series held (no model, no test)."""
    rows = []
    specs = [
        ("own headline", _series(inp.own_index, "H100"), "H100", 365.0),
        ("own headline", _series(inp.own_index, "B200"), "B200", 365.0),
        ("own history panel", _series(inp.own_index_hist, "H100"), "H100", 365.0),
        ("own history panel", _series(inp.own_index_hist, "B200"), "B200", 365.0),
        (
            "Computable GPU Index (daily close)",
            _ref_daily(inp.reference, "Computable GPU Index H100"),
            "H100",
            365.0,
        ),
        (
            "Computable GPU Index (daily close)",
            _ref_daily(inp.reference, "Computable GPU Index B200"),
            "B200",
            365.0,
        ),
        (
            "GetDeploying weekly median",
            _ref_daily(inp.reference, "GetDeploying nvidia-h100 ON_DEMAND weekly median"),
            "H100",
            52.0,
        ),
        (
            "GetDeploying weekly median",
            _ref_daily(inp.reference, "GetDeploying nvidia-b200 ON_DEMAND weekly median"),
            "B200",
            52.0,
        ),
    ]
    for name, ser, gpu, ppy in specs:
        if ser.empty:
            continue
        vol, ci, zero, _n = _vol_ci(ser, ppy, cfg)
        rows.append(
            {
                "series": name,
                "gpu": gpu,
                "first": str(ser.index.min()),
                "last": str(ser.index.max()),
                "n_obs": len(ser),
                "last_value": float(ser.iloc[-1]),
                "share_unchanged": zero,
                "ann_vol": vol,
                "ann_vol_ci_low": ci[0],
                "ann_vol_ci_high": ci[1],
            }
        )
    return pd.DataFrame(rows)


def cross_check_reference(cfg: Config, inp: Inputs) -> list[str]:
    """Our fixed-panel index against the Computable GPU Index on overlapping days."""
    lines = []
    for gpu in ("H100", "B200"):
        own = _series(inp.own_index_hist, gpu)
        ref = _ref_daily(inp.reference, f"Computable GPU Index {gpu}")
        joined = pd.DataFrame({"as_of_date": list(own.index), "own": own.to_numpy()}).merge(
            pd.DataFrame({"as_of_date": list(ref.index), "published": ref.to_numpy()}),
            on="as_of_date",
        )
        ts = tracking_stats(
            joined,
            gpu,
            MIN_TRACKING_DAYS,
            cfg.bootstrap.n_boot,
            cfg.bootstrap.block_length,
            cfg.project.seed,
        )
        if ts is None:
            lines.append(
                f"- {gpu}: {len(joined)} overlapping days; fewer than {MIN_TRACKING_DAYS}."
            )
            continue
        lines.append(
            f"- {gpu}: {ts.n_days} overlapping days. Mean log difference (ours minus CGI) "
            f"{ts.mean_log_error:+.3f} [{ts.mean_log_error_ci[0]:+.3f}, {ts.mean_log_error_ci[1]:+.3f}]; "
            f"RMSE {ts.rmse_log:.3f}; correlation of daily changes {fmt(ts.corr_daily_changes, 2)}."
        )
    return lines


def run_evaluation(cfg: Config) -> Path:
    inp = load_inputs(cfg)
    suff = data_sufficiency(cfg, inp)
    track = eval_tracking(cfg, inp)
    now_lines, now_verdicts = eval_nowcast(cfg, inp)
    ts_lines = eval_term_structure(cfg, inp)
    rv_lines, rv_ok = eval_relative_value(cfg, inp)
    desc = describe_series(cfg, inp)
    xcheck = cross_check_reference(cfg, inp)
    has_futures = not inp.settlements.empty
    nowcast_ok = all(bool(v.get("validated")) for v in now_verdicts.values()) and bool(now_verdicts)
    validation = {
        "generated": utc_now().isoformat(),
        "signals": {
            "nowcast": {"validated": nowcast_ok and has_futures, "detail": now_verdicts},
            "relative_value": {
                "validated": False,
                "detail": "requires a futures-spread test; spot-spread result "
                + ("passed" if rv_ok else "did not pass or was not testable"),
            },
        },
    }
    p = paths(cfg)
    p["validation"].parent.mkdir(parents=True, exist_ok=True)
    p["validation"].write_text(json.dumps(validation, indent=2, default=str))
    lines = [
        "# Evaluation of the three claims (real data only)",
        "",
        f"Generated {validation['generated']}. Variants declared project-wide: {variants.count()}.",
        "No synthetic data is used in this report.",
        "",
        "## Bottom line",
        "",
        "None of the three claims can be tested on 2026-10-05. GPU1/GPU2 are not listed "
        "(CFTC review extended to 2026-11-09), so there are no futures prices. History of the "
        "settlement index cannot be stored without a licence. Everything below except the "
        "data-availability table is descriptive.",
        "",
        "## Data available",
        "",
        frame_to_md(suff),
        "",
        "## Descriptive statistics of the price series held",
        "",
        "Annualized volatility of log changes (calendar days for daily series, weeks for "
        "weekly), with a circular block-bootstrap 95% CI. `share_unchanged` is the share of "
        "periods with no change. Silicon Data reports realized volatility through 2026-08-14 "
        "of 26.2% (H100) and 30.2% (B200) for its own indices (cited, not computed here).",
        "",
        frame_to_md(desc, 3) if not desc.empty else "_no series_",
        "",
        "Computable GPU Index data: (c) 2026 Computable, CC BY-NC 4.0. GetDeploying data: "
        "CC BY 4.0. gpurentalprices.com data: CC BY 4.0.",
        "",
        "## Our index versus an independent index (Computable GPU Index)",
        "",
        "A construction cross-check, not a tracking error against the settlement index.",
        "",
        *xcheck,
        "",
        "## Our index versus the settlement index",
        "",
        *track,
        "",
        "## Claim 1: nowcast edge",
        "",
        *now_lines,
        "",
        "## Claim 2: model edge (term structure)",
        "",
        *ts_lines,
        "",
        "## Claim 3: survivability after costs",
        "",
        "Backtests on real futures history require CME settlements; see `reports/backtest_real.md`.",
        "",
        "### Relative value (descriptive)",
        "",
        *rv_lines,
        "",
        "## Cost assumptions",
        "",
        cost_assumptions_md(cfg),
        "",
        "## Validation status used by the paper account",
        "",
        f"- nowcast: {'VALIDATED' if validation['signals']['nowcast']['validated'] else 'not validated (shadow mode)'}",
        "- relative_value: not validated (shadow mode)",
    ]
    out = p["reports"] / "evaluation.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n")
    return out


# ----------------------------------------------------------------------------
# Backtests
# ----------------------------------------------------------------------------
SYNTHETIC_PARAMS = {
    "GPU1": SSParams(
        kappa=3.0,
        sigma_chi=0.4,
        sigma_xi=0.2,
        rho=0.2,
        mu_xi=-0.2,
        mu_xi_star=-0.25,
        lambda_chi=0.05,
    ),
    "GPU2": SSParams(
        kappa=2.5,
        sigma_chi=0.45,
        sigma_xi=0.25,
        rho=0.3,
        mu_xi=-0.3,
        mu_xi_star=-0.35,
        lambda_chi=0.05,
    ),
}


def _momentum_strategy(view: MarketView, state: AccountState) -> dict[Key, int]:
    """Toy rule for exercising the engine: follow the 5-day change of the second month."""
    s = view.settlements()
    out: dict[Key, int] = {}
    if s.empty:
        return out
    for product, grp in s.groupby("product"):
        days = sorted(set(grp["trade_date"]))
        if len(days) < 6:
            continue
        cur = grp.loc[grp["trade_date"] == days[-1]].sort_values("contract_month")
        if len(cur) < 2:
            continue
        cm = str(cur.iloc[1]["contract_month"])
        past = grp.loc[(grp["trade_date"] == days[-6]) & (grp["contract_month"] == cm)]
        if past.empty:
            continue
        chg = float(cur.iloc[1]["settle_price"]) - float(past["settle_price"].iloc[0])
        out[(str(product), cm)] = 2 if chg > 0 else -2
    return out


def synthetic_engine_check(cfg: Config) -> Path:
    scfg = synthetic_config(cfg)
    start, n = date(2024, 1, 1), 730
    frames_s, frames_p = [], []
    for i, (product, spec) in enumerate(scfg.contracts.items()):
        sm = synthetic_market(
            spec,
            start,
            n,
            SYNTHETIC_PARAMS[product],
            seed=cfg.project.seed + i,
            xi0=float(np.log(2.2 if product == "GPU1" else 5.5)),
        )
        frames_s.append(sm.settlements)
        frames_p.append(sm.published_index)
    md = MarketData.build(
        settlements=pd.concat(frames_s, ignore_index=True),
        published_index=pd.concat(frames_p, ignore_index=True),
    )
    end = start + timedelta(days=n - 1)

    # Same engine with loss stops and margin made non-binding: with them active
    # the trade path depends on costs (a stop fires earlier, or margin runs out,
    # when costs are higher), so PnL need not be monotone in costs. Holding
    # trades fixed isolates the cost model for the monotonicity check.
    nostop = scfg.model_copy(
        update={
            "risk": scfg.risk.model_copy(
                update={"daily_loss_limit": 1e12, "max_drawdown": 1e12, "starting_cash": 1e12}
            )
        }
    )

    def run(strategy: Strategy, name: str, c: Config = scfg) -> Callable[[float], RunResult]:
        def _go(m: float) -> RunResult:
            return run_backtest(md, strategy, start, end, c, f"{name}_x{m}", m, strategy_name=name)

        return _go

    flat = run(flat_strategy, "flat")(1.0)
    mom = run(_momentum_strategy, "momentum_toy")
    base: RunResult = mom(1.0)
    sens = cost_sensitivity(mom, scfg)
    sens_nostop = cost_sensitivity(run(_momentum_strategy, "momentum_nostop", nostop), nostop)
    book = SignalBook()
    sig = run_backtest(
        md,
        make_strategy(scfg, {"nowcast", "relative_value"}, book),
        start,
        end,
        scfg,
        "signals_x1.0",
        1.0,
    )
    checks = [
        ("Flat strategy has zero PnL and zero costs", abs(tearsheet(flat, scfg).total_pnl) < 1e-9),
        (
            "Cash-flow ledger sums to equity change",
            abs(
                base.cash_flows["amount"].sum()
                - (base.account["equity"].iloc[-1] - scfg.risk.starting_cash)
            )
            < 1e-6,
        ),
        (
            "PnL falls as costs rise (stops and margin non-binding, trades held fixed)",
            bool(np.all(np.diff(sens_nostop["total_pnl"].to_numpy()) < 0)),
        ),
        (
            "Gross position never exceeds limit",
            int(base.account["gross_contracts"].max()) <= scfg.risk.max_gross_contracts,
        ),
        ("Signals strategy ran end to end", len(sig.account) == n),
    ]
    lines = [
        "# Engine validation on SYNTHETIC data",
        "",
        "> **SYNTHETIC DATA - ENGINE VALIDATION ONLY - NOT A RESULT.** Prices are simulated from "
        "a Schwartz-Smith process with invented parameters. Nothing here says anything about the "
        "real GPU1/GPU2 market or about the three claims.",
        "",
        "## Engine checks",
        "",
        "| Check | Pass |",
        "|---|---|",
        *[f"| {c} | {'yes' if ok else 'NO'} |" for c, ok in checks],
        "",
        tearsheet_md(tearsheet(base, scfg), scfg, sens).replace(
            "# Tearsheet", "## Tearsheet (toy momentum rule)"
        ),
        "",
        "With loss stops and margin active, the trade path changes with costs, because a stop "
        "fires or margin runs out at different times. The sensitivity table above therefore "
        "need not be monotone. With stops and margin made non-binding, trades are identical "
        "across rows:",
        "",
        frame_to_md(sens_nostop, 2),
        "",
        "## Signals strategy on synthetic inputs",
        "",
        f"Shadow predictions logged: {len(book.rows)}. Fills: {len(sig.fills)}. "
        "The synthetic market has no own-index series, so the nowcast model cannot form a "
        "prediction and only the relative-value rule can act.",
    ]
    out = paths(cfg)["reports"] / "engine_validation_SYNTHETIC.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n")
    if not all(ok for _, ok in checks):
        raise RuntimeError("engine validation failed; see report")
    return out


def real_backtest(cfg: Config) -> Path:
    inp = load_inputs(cfg)
    out = paths(cfg)["reports"] / "backtest_real.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    if inp.settlements.empty:
        out.write_text(
            "# Backtest on real data\n\n"
            "Not run: there is no CME settlement history in `data/manual/cme_settlements/`. "
            "GPU1/GPU2 did not list on 2026-10-05: the CFTC extended its review to 2026-11-09 "
            "(docs/contract_specs.md, docs/blockers.md B8). Settlements must be added by hand "
            "because cmegroup.com may not be scripted (B2). No backtest result exists.\n\n"
            "Historical index data (our index, the Computable GPU Index, GetDeploying) cannot "
            "stand in for futures: trading it would require inventing a futures price. Those "
            "series are analysed descriptively in `reports/evaluation.md`. The engine itself is "
            "validated on labelled synthetic data in `reports/engine_validation_SYNTHETIC.md`.\n"
        )
        return out
    days = sorted(inp.settlements["trade_date"])
    start, end = days[0], days[-1]
    book = SignalBook()
    strat = make_strategy(cfg, {"nowcast", "relative_value"}, book)

    def run(m: float) -> RunResult:
        return run_backtest(
            inp.market, strat, start, end, cfg, f"real_signals_x{m}", m, strategy_name="signals"
        )

    sens = cost_sensitivity(run, cfg)
    ts = tearsheet(run(1.0), cfg)
    out.write_text(
        tearsheet_md(ts, cfg, sens)
        + "\nAll pre-registered signals traded ungated (validation status does not apply in backtests).\n"
    )
    return out


def run_backtests(cfg: Config, engine_check: bool = False) -> list[Path]:
    outs = []
    if engine_check:
        outs.append(synthetic_engine_check(cfg))
    outs.append(real_backtest(cfg))
    return outs
