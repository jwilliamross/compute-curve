"""Balance-of-month fair value for GPU1/GPU2 and the FP-C rule (docs/bom_plan.md).

Descriptive sheet plus a shadow-only balance-of-month trade. Never sends an
order. Uses Silicon Data's published index when a licensed CSV is present,
otherwise our own index, labelled as a proxy.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from compute_curve.config import Config, ContractSpec
from compute_curve.contracts import settlement_days
from compute_curve.futures_premium import INDEX_NAMES, _cutoff, curve_before, leg_cost, realized
from compute_curve.statarb import evaluate as ev
from compute_curve.timeutil import add_months, month_start

Z90 = 1.645
SIGMA_WINDOW = 60
SIGMA_FLOOR = 0.001
OWN_NAMES = {"GPU1": "H100", "GPU2": "B200"}


@dataclass(frozen=True)
class BomRules:
    band_sd: float = 1.0
    cost_mult_band: float = 2.0
    min_obs: int = 12
    deadline: date = date(2028, 1, 1)
    alpha: float = 0.05
    stress: float = 2.0


RULES = BomRules()


def rw_average_sd(horizons: np.ndarray, sigma: float) -> float:
    """SD of the mean of a driftless random walk observed at ``horizons`` steps ahead."""
    h = np.asarray(horizons, dtype=float)
    if h.size == 0:
        return 0.0
    cov = np.minimum.outer(h, h)
    return float(sigma * np.sqrt(cov.sum()) / h.size)


def sigma_daily(series: pd.Series, window: int = SIGMA_WINDOW) -> tuple[float, int]:
    """SD of daily log changes over the last ``window`` observations, floored."""
    ch = np.log(series.sort_index().astype(float)).diff().dropna().iloc[-window:]
    if len(ch) < 2:
        return SIGMA_FLOOR, len(ch)
    return max(float(ch.std(ddof=1)), SIGMA_FLOOR), len(ch)


def _bday_gap(a: date, b: date) -> int:
    return int(np.busday_count(a, b))


def month_fair_value(
    index: pd.Series, spec: ContractSpec, month: date, today: date, sigma: float
) -> dict[str, Any]:
    """FV and 90% band of ``month``'s settlement average, seen from ``today``."""
    s = index.sort_index()
    s = s[s.index <= today]
    level = float(s.iloc[-1])
    days = settlement_days(spec, month)
    done = [d for d in days if d <= today]
    rest = [d for d in days if d > today]
    realized_vals = []
    for d in done:
        prior = s[s.index <= d]
        if not prior.empty:
            realized_vals.append(float(prior.iloc[-1]))
    k, m, n = len(realized_vals), len(rest), len(days)
    a_k = float(np.mean(realized_vals)) if realized_vals else None
    fv = ((k * a_k if a_k is not None else 0.0) + m * level) / max(k + m, 1)
    horizons = np.array([max(_bday_gap(today, d), 1) for d in rest])
    sd_rest = rw_average_sd(horizons, sigma)
    sd = sd_rest * (m / max(k + m, 1))
    return {
        "month": f"{month:%Y-%m}",
        "days_total": n,
        "days_realized": k,
        "realized_avg": a_k,
        "level": level,
        "fair_value": fv,
        "sd_log": sd,
        "low90": fv * float(np.exp(-Z90 * sd)),
        "high90": fv * float(np.exp(Z90 * sd)),
    }


def sheet(
    index: pd.Series, spec: ContractSpec, today: date, months_ahead: int = 3
) -> tuple[list[dict[str, Any]], float, int]:
    sigma, n_sigma = sigma_daily(index)
    m0 = month_start(today)
    rows = [
        month_fair_value(index, spec, add_months(m0, i), today, sigma)
        for i in range(months_ahead + 1)
    ]
    return rows, sigma, n_sigma


# ---------------------------------------------------------------------------
# FP-C
# ---------------------------------------------------------------------------
def decision_day(spec: ContractSpec, month: date) -> date:
    """First averaging day on which at least half the month's days are observed."""
    days = settlement_days(spec, month)
    return days[(len(days) + 1) // 2]


def fpc_decide(f: float, fv: float, band: float) -> int:
    if f > fv + band:
        return -1
    if f < fv - band:
        return 1
    return 0


def _index_before(pub: pd.DataFrame, name: str, t: date) -> pd.Series:
    p = pub.loc[(pub["index_name"] == name) & (pub["ts_available"] <= _cutoff(t))]
    return p.set_index("as_of_date")["value"].astype(float).sort_index()


def fpc_observations(
    settle: pd.DataFrame, pub: pd.DataFrame, cfg: Config, through: date, rules: BomRules = RULES
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if settle.empty or pub.empty:
        return rows
    m = month_start(min(settle["trade_date"]))
    while m <= month_start(through):
        for product, spec in cfg.contracts.items():
            t = decision_day(spec, m)
            if t > through:
                continue
            idx = _index_before(pub, INDEX_NAMES.get(product, ""), t)
            f = curve_before(settle, product, t).get(f"{m:%Y-%m}")
            if idx.empty or f is None:
                continue
            sigma, _ = sigma_daily(idx)
            # FV as seen with data usable at t: the last usable value is from before t.
            fvr = month_fair_value(idx, spec, m, idx.index.max(), sigma)
            cost = leg_cost(spec, cfg.costs)
            band = rules.cost_mult_band * cost / spec.gpu_hours_per_contract
            band += rules.band_sd * fvr["sd_log"] * fvr["fair_value"]
            pos = fpc_decide(f, fvr["fair_value"], band)
            row = {
                "product": product,
                "month": f"{m:%Y-%m}",
                "decision_day": str(t),
                "market": f,
                "fair_value": fvr["fair_value"],
                "band": band,
                "position": pos,
            }
            s = realized(settle, product, m)
            if pos != 0 and s is not None:
                gross = pos * (s - f) * spec.gpu_hours_per_contract
                row["pnl"] = gross - cost
                row["pnl_stress"] = gross - leg_cost(spec, cfg.costs, rules.stress)
            rows.append(row)
        m = add_months(m, 1)
    return rows


def fpc_evaluate(
    rows: list[dict[str, Any]], today: date, rules: BomRules = RULES
) -> dict[str, Any]:
    done = [r for r in rows if "pnl" in r]
    due = today >= rules.deadline or len(done) >= rules.min_obs
    out: dict[str, Any] = {"due": due, "n_settled_trades": len(done)}
    if not due:
        return out
    if len(done) < rules.min_obs:
        out["verdict"] = "too little history to conclude"
        return out
    pnl = np.array([r["pnl"] for r in done])
    stress = np.array([r["pnl_stress"] for r in done])
    p = ev.hac_p_one_sided(pnl, 1)
    ok = np.isfinite(p) and p <= rules.alpha and stress.mean() > 0
    return out | {
        "mean_pnl_usd": float(pnl.mean()),
        "mean_pnl_stress_usd": float(stress.mean()),
        "p_one_sided": p,
        "verdict": "pass" if ok else "not confirmed",
    }


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------
def _own_series(own: pd.DataFrame, gpu: str) -> pd.Series:
    o = own.loc[
        (own["series"] == "history_panel")
        & own["meets_coverage"].astype(bool)
        & (own["gpu_model"] == gpu)
    ]
    s = o.set_index(pd.to_datetime(o["as_of_date"]).dt.date)["value"].astype(float)
    return s[~s.index.duplicated(keep="last")].sort_index()


def _fmt_rows(
    product: str, source: str, rows: list[dict[str, Any]], market: dict[str, float]
) -> list[str]:
    out = [
        f"### {product} ({source})",
        "",
        "| Month | Days averaged | Realised avg | Fair value | 90% range | Market | Market - FV |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        ra = f"{r['realized_avg']:.3f}" if r["realized_avg"] is not None else "-"
        f = market.get(r["month"])
        mk = f"{f:.3f}" if f is not None else "-"
        gap = f"{f - r['fair_value']:+.3f}" if f is not None else "-"
        out.append(
            f"| {r['month']} | {r['days_realized']}/{r['days_total']} | {ra} | "
            f"{r['fair_value']:.3f} | {r['low90']:.3f}-{r['high90']:.3f} | {mk} | {gap} |"
        )
    return [*out, ""]


def run_sheet(cfg: Config, today: date) -> Path:  # pragma: no cover - reads local files
    from compute_curve.pipeline import paths as ppaths  # noqa: PLC0415
    from compute_curve.storage import warehouse as wh  # noqa: PLC0415

    p = ppaths(cfg)
    out = cfg.path("reports") / "fair_value"
    out.mkdir(parents=True, exist_ok=True)
    pub = wh.load_published_index_csvs(p["manual_index"], cfg.nowcast.publication_lag_days)
    settle = wh.load_settlement_csvs(p["manual_settle"])
    own_csv = cfg.path("reports") / "own_index.csv"
    own = pd.read_csv(own_csv) if own_csv.exists() else pd.DataFrame()
    lines = [
        "# GPU1/GPU2 balance-of-month fair value",
        "",
        f"As of {today}. Method: docs/bom_plan.md. Driftless random walk for the days not yet "
        "averaged; 90% range from the recent daily volatility. A **proxy** sheet uses our own "
        "index, not Silicon Data's: its level differs (basis risk). Research only; no orders.",
        "",
    ]
    csv_rows = []
    for product, spec in cfg.contracts.items():
        sd_idx = (
            _index_before(pub, INDEX_NAMES.get(product, ""), today)
            if not pub.empty
            else pd.Series()
        )
        if not sd_idx.empty:
            idx, source = sd_idx, "Silicon Data index"
        elif not own.empty:
            idx, source = _own_series(own, OWN_NAMES[product]), "proxy: our own index"
        else:
            continue
        if idx.empty:
            continue
        rows, sigma, n_sigma = sheet(idx, spec, today)
        market = curve_before(settle, product, today) if not settle.empty else {}
        lines += _fmt_rows(product, source, rows, market)
        lines.append(f"Daily volatility used: {sigma:.4f} ({n_sigma} daily changes).")
        lines.append("")
        csv_rows += [{"product": product, "source": source, **r} for r in rows]
    pd.DataFrame(csv_rows).to_csv(out / "sheet.csv", index=False)
    fpc_rows = fpc_observations(settle, pub, cfg, today)
    fpc = fpc_evaluate(fpc_rows, today)
    lines.append(
        f"FP-C (balance-of-month trade, needs licensed SD values): {fpc['n_settled_trades']} "
        "settled traded decisions."
        + ("" if not settle.empty else " No CME settlements yet; waiting.")
    )
    result = out / "fpc_result.json"
    if fpc["due"] and not result.exists():
        result.write_text(json.dumps(fpc, indent=2, default=float))
    md = out / "sheet.md"
    md.write_text("\n".join(lines) + "\n")
    return md
