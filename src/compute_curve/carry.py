"""FP-D: long the backwardation on GPU1/GPU2 (docs/carry_plan.md).

Shadow decisions and one-shot evaluation only; never sends an order.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from compute_curve.config import Config
from compute_curve.futures_premium import (
    INDEX_NAMES,
    curve_before,
    decision_days,
    index_before,
    leg_cost,
    realized,
)
from compute_curve.statarb import evaluate as ev
from compute_curve.statarb.power import holm
from compute_curve.timeutil import add_months, month_start

VARIANTS = ("FP-D-I", "FP-D-F")


@dataclass(frozen=True)
class CarryRules:
    gap: float = 0.05
    horizon_months: int = 3
    min_obs: int = 12
    deadline: date = date(2028, 7, 1)
    alpha: float = 0.05
    hac_lag: int = 2
    stress: float = 2.0


RULES = CarryRules()


def go_long(f3: float, ref: float, gap: float = RULES.gap) -> bool:
    return bool(np.log(f3 / ref) < -gap)


def observations(
    settle: pd.DataFrame, pub: pd.DataFrame, cfg: Config, through: date, rules: CarryRules = RULES
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if settle.empty:
        return rows
    for t in decision_days(min(settle["trade_date"]), through):
        m1 = add_months(month_start(t), 1)
        m3 = add_months(month_start(t), rules.horizon_months)
        for product, spec in cfg.contracts.items():
            curve = curve_before(settle, product, t)
            f3 = curve.get(f"{m3:%Y-%m}")
            if f3 is None:
                continue
            refs = {
                "FP-D-I": index_before(pub, INDEX_NAMES.get(product, ""), t)
                if not pub.empty
                else None,
                "FP-D-F": curve.get(f"{m1:%Y-%m}"),
            }
            s3 = realized(settle, product, m3)
            for variant, ref in refs.items():
                if ref is None:
                    continue
                row: dict[str, Any] = {
                    "variant": variant,
                    "product": product,
                    "decision_day": str(t),
                    "contract_month": f"{m3:%Y-%m}",
                    "log_gap": float(np.log(f3 / ref)),
                    "long": go_long(f3, ref, rules.gap),
                }
                if s3 is not None:
                    row["realized_premium"] = float(np.log(s3 / f3))
                    if row["long"]:
                        gross = (s3 - f3) * spec.gpu_hours_per_contract
                        row["pnl"] = gross - leg_cost(spec, cfg.costs)
                        row["pnl_stress"] = gross - leg_cost(spec, cfg.costs, rules.stress)
                rows.append(row)
    return rows


def evaluate(rows: list[dict[str, Any]], today: date, rules: CarryRules = RULES) -> dict[str, Any]:
    traded = {v: [r for r in rows if r["variant"] == v and "pnl" in r] for v in VARIANTS}
    due = today >= rules.deadline or any(len(x) >= rules.min_obs for x in traded.values())
    out: dict[str, Any] = {
        "due": due,
        "variants": {v: {"n_settled_trades": len(x)} for v, x in traded.items()},
    }
    prem = [r["realized_premium"] for r in rows if "realized_premium" in r]
    out["mean_realized_premium"] = float(np.mean(prem)) if prem else None
    if not due:
        return out
    ps = []
    for v in VARIANTS:
        res, x = out["variants"][v], traded[v]
        if len(x) < rules.min_obs:
            res["verdict"] = "too little history to conclude"
            ps.append(1.0)
            continue
        pnl = np.array([r["pnl"] for r in x])
        stress = np.array([r["pnl_stress"] for r in x])
        p = ev.hac_p_one_sided(pnl, rules.hac_lag)
        res |= {
            "mean_pnl_usd": float(pnl.mean()),
            "mean_pnl_stress_usd": float(stress.mean()),
            "p_one_sided": p,
        }
        ps.append(p if np.isfinite(p) else 1.0)
    for v, pa in zip(VARIANTS, holm(ps), strict=True):
        res = out["variants"][v]
        if "p_one_sided" in res:
            res["p_holm"] = float(pa)
            ok = pa <= rules.alpha and res["mean_pnl_stress_usd"] > 0
            res["verdict"] = "pass" if ok else "not confirmed"
    return out


def run_shadow(cfg: Config, today: date) -> Path:  # pragma: no cover - reads local files
    from compute_curve.pipeline import paths as ppaths  # noqa: PLC0415
    from compute_curve.storage import warehouse as wh  # noqa: PLC0415

    p = ppaths(cfg)
    out = cfg.path("reports") / "carry"
    out.mkdir(parents=True, exist_ok=True)
    settle = wh.load_settlement_csvs(p["manual_settle"])
    lines = [
        "# FP-D long-the-backwardation: shadow",
        "",
        f"As of {today}. Plan: docs/carry_plan.md. No orders.",
    ]
    if settle.empty:
        lines.append("- No CME settlements yet (GPU1/GPU2 not listed, B8). Waiting.")
    else:
        pub = wh.load_published_index_csvs(p["manual_index"], cfg.nowcast.publication_lag_days)
        rows = observations(settle, pub, cfg, today)
        pd.DataFrame(rows).to_csv(out / "decisions.csv", index=False)
        res = evaluate(rows, today)
        for v, r in res["variants"].items():
            lines.append(f"- {v}: {r['n_settled_trades']} settled long trades.")
        result = out / "fpd_result.json"
        if res["due"] and not result.exists():
            result.write_text(json.dumps(res, indent=2, default=float))
            lines.append("- Evaluation ran (once): see fpd_result.json.")
    md = out / "status.md"
    md.write_text("\n".join(lines) + "\n")
    return md
