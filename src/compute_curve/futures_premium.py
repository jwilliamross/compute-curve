"""Claim 7: the GPU1/GPU2 futures risk premium (docs/futures_premium_plan.md).

Shadow log and one-shot evaluation only. Reads manual CME settlements and
(optionally) published index values; writes derived numbers only (D59).
Never sends an order and never contacts an exchange or broker.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from compute_curve.config import Config, ContractSpec, CostConfig
from compute_curve.contracts import last_trading_day
from compute_curve.statarb import evaluate as ev
from compute_curve.statarb.power import holm
from compute_curve.timeutil import add_months, month_days, month_start

INDEX_NAMES = {"GPU1": "SDH100RT", "GPU2": "SDB200RT"}
STRATEGIES = ("FP-A", "FP-B")


@dataclass(frozen=True)
class Rules:
    thr_a: float = 0.05
    thr_b: float = 0.03
    min_obs: int = 12
    deadline: date = date(2028, 1, 1)
    alpha: float = 0.05
    hac_lag: int = 1
    stress: float = 2.0


RULES = Rules()


def first_business_day(month: date) -> date:
    return month_days(month, business_days_only=True)[0]


def decision_days(start: date, end: date) -> list[date]:
    out, m = [], month_start(start)
    while m <= end:
        d = first_business_day(m)
        if start <= d <= end:
            out.append(d)
        m = add_months(m, 1)
    return out


def _cutoff(t: date) -> pd.Timestamp:
    return pd.Timestamp(datetime(t.year, t.month, t.day, tzinfo=UTC))


def curve_before(settle: pd.DataFrame, product: str, t: date) -> dict[str, float]:
    """Latest usable settlement per contract month at 00:00 UTC on ``t``."""
    s = settle.loc[(settle["product"] == product) & (settle["ts_available"] < _cutoff(t))]
    if s.empty:
        return {}
    last = s.sort_values("trade_date").groupby("contract_month").tail(1)
    return {str(r.contract_month): float(r.settle_price) for r in last.itertuples()}


def index_before(pub: pd.DataFrame, name: str, t: date) -> float | None:
    p = pub.loc[(pub["index_name"] == name) & (pub["ts_available"] <= _cutoff(t))]
    if p.empty:
        return None
    return float(p.sort_values("as_of_date")["value"].iloc[-1])


def realized(settle: pd.DataFrame, product: str, month: date) -> float | None:
    """Final settlement: the settle price on the contract's last trading day (assumption)."""
    ltd = last_trading_day(month)
    r = settle.loc[
        (settle["product"] == product)
        & (settle["contract_month"] == f"{month:%Y-%m}")
        & (settle["trade_date"] == ltd)
    ]
    return None if r.empty else float(r["settle_price"].iloc[-1])


def leg_cost(spec: ContractSpec, costs: CostConfig, mult: float = 1.0) -> float:
    """USD per contract per leg: entry spread and slippage, exchange, broker, cash settlement."""
    ticks = (costs.half_spread_ticks + costs.slippage_ticks) * spec.tick_size
    fees = (
        spec.exchange_fee_per_contract
        + costs.broker_clearing_fee_per_contract
        + spec.cash_settlement_fee_per_contract
    )
    return mult * (ticks * spec.gpu_hours_per_contract + fees)


def decide(log_gap: float, thr: float) -> int:
    """Sell a rich leg (gap above thr) and buy a cheap one: returns the position in the rich leg."""
    if log_gap > thr:
        return -1
    if log_gap < -thr:
        return 1
    return 0


def _codes(t: date) -> tuple[date, date]:
    m = month_start(t)
    return add_months(m, 1), add_months(m, 2)


def observations(
    settle: pd.DataFrame, pub: pd.DataFrame, cfg: Config, through: date, rules: Rules = RULES
) -> list[dict[str, Any]]:
    """Every decision day up to ``through``: signals, positions, and net P&L once settled."""
    rows: list[dict[str, Any]] = []
    if settle.empty:
        return rows
    first = min(settle["trade_date"])
    for t in decision_days(first, through):
        m1, m2 = _codes(t)
        for product, spec in cfg.contracts.items():
            curve = curve_before(settle, product, t)
            f1, f2 = curve.get(f"{m1:%Y-%m}"), curve.get(f"{m2:%Y-%m}")
            s_idx = index_before(pub, INDEX_NAMES.get(product, ""), t)
            base = {"product": product, "decision_day": str(t)}
            if f1 is not None and s_idx is not None:
                gap = float(np.log(f1) - np.log(s_idx))
                pos = decide(gap, rules.thr_a)
                a1 = realized(settle, product, m1)
                row = base | {"strategy": "FP-A", "signal": gap, "position": pos}
                if pos != 0 and a1 is not None:
                    gross = pos * (a1 - f1) * spec.gpu_hours_per_contract
                    row |= {
                        "pnl": gross - leg_cost(spec, cfg.costs),
                        "pnl_stress": gross - leg_cost(spec, cfg.costs, rules.stress),
                    }
                rows.append(row)
            if f1 is not None and f2 is not None:
                gap = float(np.log(f2) - np.log(f1))
                pos2 = decide(gap, rules.thr_b)  # position in M2; M1 is the opposite
                a1, a2 = realized(settle, product, m1), realized(settle, product, m2)
                row = base | {"strategy": "FP-B", "signal": gap, "position": pos2}
                if pos2 != 0 and a1 is not None and a2 is not None:
                    h = spec.gpu_hours_per_contract
                    gross = pos2 * ((a2 - f2) - (a1 - f1)) * h
                    row |= {
                        "pnl": gross - 2 * leg_cost(spec, cfg.costs),
                        "pnl_stress": gross - 2 * leg_cost(spec, cfg.costs, rules.stress),
                    }
                rows.append(row)
    return rows


def evaluate(rows: list[dict[str, Any]], today: date, rules: Rules = RULES) -> dict[str, Any]:
    """Pre-registered C1/C2 per strategy, Holm over both; 'waiting' until the trigger."""
    settled = {
        k: sorted(
            (r for r in rows if r["strategy"] == k and "pnl" in r), key=lambda r: r["decision_day"]
        )
        for k in STRATEGIES
    }
    due = today >= rules.deadline or any(len(v) >= rules.min_obs for v in settled.values())
    out: dict[str, Any] = {"due": due, "strategies": {}}
    for k, v in settled.items():
        out["strategies"][k] = {"n_settled": len(v)}
    if not due:
        return out
    ps = []
    for k, v in settled.items():
        res = out["strategies"][k]
        if len(v) < rules.min_obs:
            res["verdict"] = "too little history to conclude"
            ps.append(1.0)
            continue
        pnl = np.array([r["pnl"] for r in v], dtype=float)
        stress = np.array([r["pnl_stress"] for r in v], dtype=float)
        p = ev.hac_p_one_sided(pnl, rules.hac_lag)
        res |= {
            "mean_pnl_usd": float(pnl.mean()),
            "mean_pnl_stress_usd": float(stress.mean()),
            "p_one_sided": p,
        }
        ps.append(p if np.isfinite(p) else 1.0)
    for (_k, res), pa in zip(out["strategies"].items(), holm(ps), strict=True):
        if "p_one_sided" in res:
            res["p_holm"] = float(pa)
            ok = pa <= rules.alpha and res["mean_pnl_usd"] > 0 and res["mean_pnl_stress_usd"] > 0
            res["verdict"] = "pass" if ok else "not confirmed"
    return out


def premia_today(
    settle: pd.DataFrame, pub: pd.DataFrame, cfg: Config, day: date
) -> list[dict[str, Any]]:
    """Descriptive log premia for ``day`` (no position implied)."""
    m1, m2 = _codes(day)
    out = []
    for product in cfg.contracts:
        curve = curve_before(settle, product, day)
        f1, f2 = curve.get(f"{m1:%Y-%m}"), curve.get(f"{m2:%Y-%m}")
        s_idx = index_before(pub, INDEX_NAMES.get(product, ""), day)
        out.append(
            {
                "date": str(day),
                "product": product,
                "pi_outright": float(np.log(f1 / s_idx)) if f1 and s_idx else None,
                "slope_m2_m1": float(np.log(f2 / f1)) if f1 and f2 else None,
            }
        )
    return out


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------
def run_shadow(cfg: Config, today: date) -> Path:  # pragma: no cover - reads local manual files
    from compute_curve.pipeline import paths as ppaths  # noqa: PLC0415
    from compute_curve.storage import warehouse as wh  # noqa: PLC0415

    p = ppaths(cfg)
    settle = wh.load_settlement_csvs(p["manual_settle"])
    pub = wh.load_published_index_csvs(p["manual_index"], cfg.nowcast.publication_lag_days)
    out = cfg.path("reports") / "futures_premium"
    out.mkdir(parents=True, exist_ok=True)
    md = out / "status.md"
    if settle.empty:
        md.write_text(
            "# Claim 7 futures premium: shadow\n\n"
            f"{today}: no CME settlements in data/manual/cme_settlements/ yet "
            "(GPU1/GPU2 not listed, B8). Nothing computed. No orders.\n"
        )
        return md
    rows = observations(settle, pub, cfg, today)
    log = out / "premia_log.csv"
    new = pd.DataFrame(premia_today(settle, pub, cfg, today))
    if log.exists():
        old = pd.read_csv(log)
        new = pd.concat([old, new]).drop_duplicates(["date", "product"], keep="first")
    new.to_csv(log, index=False)
    pd.DataFrame(
        [
            {
                k: r.get(k)
                for k in (
                    "product",
                    "decision_day",
                    "strategy",
                    "signal",
                    "position",
                    "pnl",
                    "pnl_stress",
                )
            }
            for r in rows
        ]
    ).to_csv(out / "decisions.csv", index=False)
    result = out / "claim7_result.json"
    ev_ = evaluate(rows, today)
    lines = ["# Claim 7 futures premium: shadow", "", f"As of {today}. Derived numbers only (D59)."]
    for k, v in ev_["strategies"].items():
        lines.append(f"- {k}: {v['n_settled']} settled traded decisions.")
    if ev_["due"] and not result.exists():
        result.write_text(json.dumps(ev_, indent=2, default=float))
        lines.append("- Evaluation ran (once): see claim7_result.json.")
    elif result.exists():
        lines.append("- Evaluated earlier: see claim7_result.json.")
    else:
        lines.append(f"- Evaluation waits for {RULES.min_obs} settled trades or {RULES.deadline}.")
    md.write_text("\n".join(lines) + "\n")
    return md
