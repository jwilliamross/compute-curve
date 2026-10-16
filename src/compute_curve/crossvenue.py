"""FP-K: GPU1 against Kalshi's H100 monthly-average market (docs/crossvenue_plan.md).

Shadow decisions and one-shot evaluation only; never sends an order to CME
or Kalshi.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from compute_curve.config import Config
from compute_curve.futures_premium import curve_before, decision_days, leg_cost, realized
from compute_curve.statarb import evaluate as ev
from compute_curve.timeutil import add_months, month_start

SERIES = "KXH100MS"


@dataclass(frozen=True)
class KRules:
    band: float = 0.08
    max_age_days: int = 3
    min_obs: int = 12
    deadline: date = date(2028, 7, 1)
    alpha: float = 0.05
    gate_alpha: float = 0.10
    stress: float = 2.0


RULES = KRules()


def kalshi_quote(curve: pd.DataFrame, month: str, t: date, rules: KRules = RULES) -> float | None:
    """Latest implied median for ``month`` logged before ``t`` and at most 3 days old."""
    if curve.empty:
        return None
    c = curve.loc[(curve["series"] == SERIES) & (curve["month"] == month)].copy()
    c["d"] = pd.to_datetime(c["date"]).dt.date
    c = c.loc[(c["d"] < t) & (c["d"] >= t - timedelta(days=rules.max_age_days))]
    return None if c.empty else float(c.sort_values("d")["implied_median"].iloc[-1])


def decide(f: float, q: float, band: float = RULES.band) -> int:
    g = float(np.log(f / q))
    if g > band:
        return -1
    if g < -band:
        return 1
    return 0


def observations(
    settle: pd.DataFrame, curve: pd.DataFrame, cfg: Config, through: date, rules: KRules = RULES
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if settle.empty:
        return rows
    spec = cfg.contracts["GPU1"]
    for t in decision_days(min(settle["trade_date"]), through):
        m1 = add_months(month_start(t), 1)
        code = f"{m1:%Y-%m}"
        f = curve_before(settle, "GPU1", t).get(code)
        q = kalshi_quote(curve, code, t, rules)
        if f is None or q is None:
            continue
        pos = decide(f, q, rules.band)
        row: dict[str, Any] = {
            "decision_day": str(t),
            "month": code,
            "futures": f,
            "kalshi": q,
            "position": pos,
        }
        s = realized(settle, "GPU1", m1)
        if s is not None:
            row["settlement"] = s
            if pos != 0:
                gross = pos * (s - f) * spec.gpu_hours_per_contract
                row["pnl"] = gross - leg_cost(spec, cfg.costs)
                row["pnl_stress"] = gross - leg_cost(spec, cfg.costs, rules.stress)
        rows.append(row)
    return rows


def gate_p(rows: list[dict[str, Any]]) -> float:
    """Diebold-Mariano one-sided p that Kalshi's quote beats the futures as a forecast."""
    r = [x for x in rows if "settlement" in x]
    if len(r) < 5:
        return float("nan")
    s = np.log([x["settlement"] for x in r])
    d = (s - np.log([x["futures"] for x in r])) ** 2 - (s - np.log([x["kalshi"] for x in r])) ** 2
    return ev.hac_p_one_sided(d, 1)


def evaluate(rows: list[dict[str, Any]], today: date, rules: KRules = RULES) -> dict[str, Any]:
    done = [r for r in rows if "pnl" in r]
    due = today >= rules.deadline or len(done) >= rules.min_obs
    out: dict[str, Any] = {"due": due, "n_settled_trades": len(done)}
    if not due:
        return out
    if len(done) < rules.min_obs:
        return out | {"verdict": "too little history to conclude"}
    pnl = np.array([r["pnl"] for r in done])
    stress = np.array([r["pnl_stress"] for r in done])
    p = ev.hac_p_one_sided(pnl, 1)
    g = gate_p(rows)
    ok = np.isfinite(g) and g <= rules.gate_alpha and p <= rules.alpha and stress.mean() > 0
    return out | {
        "gate_p": g,
        "mean_pnl_usd": float(pnl.mean()),
        "mean_pnl_stress_usd": float(stress.mean()),
        "p_one_sided": p,
        "verdict": "pass" if ok else "not confirmed",
    }


def run_shadow(cfg: Config, today: date) -> Path:  # pragma: no cover - reads local files
    from compute_curve.pipeline import paths as ppaths  # noqa: PLC0415
    from compute_curve.storage import warehouse as wh  # noqa: PLC0415

    out = cfg.path("reports") / "crossvenue"
    out.mkdir(parents=True, exist_ok=True)
    curve_csv = cfg.path("reports") / "kalshi" / "implied_curve.csv"
    curve = pd.read_csv(curve_csv) if curve_csv.exists() else pd.DataFrame()
    n_h100 = int((curve["series"] == SERIES).sum()) if not curve.empty else 0
    lines = [
        "# FP-K GPU1 vs Kalshi H100 monthly average: shadow",
        "",
        f"As of {today}. Plan: docs/crossvenue_plan.md. No orders.",
        f"- Kalshi implied-curve rows logged for {SERIES}: {n_h100}.",
    ]
    settle = wh.load_settlement_csvs(ppaths(cfg)["manual_settle"])
    if settle.empty:
        lines.append("- No CME settlements yet (GPU1 not listed, B8). Waiting.")
    else:
        rows = observations(settle, curve, cfg, today)
        pd.DataFrame(rows).to_csv(out / "decisions.csv", index=False)
        res = evaluate(rows, today)
        lines.append(f"- {res['n_settled_trades']} settled traded decisions.")
        result = out / "fpk_result.json"
        if res["due"] and not result.exists():
            result.write_text(json.dumps(res, indent=2, default=float))
    md = out / "status.md"
    md.write_text("\n".join(lines) + "\n")
    return md
