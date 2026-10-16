"""Claim 8: GPU2/GPU1 relative value on the B200/H100 ratio (docs/spread_plan.md).

Shadow decisions and one-shot evaluation only. Reads manual CME settlements
and licensed published-index CSVs (D59); writes derived numbers only. Never
sends an order and never contacts an exchange or broker.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from compute_curve.claim4 import stats as cs
from compute_curve.config import Config
from compute_curve.futures_premium import (
    INDEX_NAMES,
    _cutoff,
    curve_before,
    decision_days,
    leg_cost,
    realized,
)
from compute_curve.statarb import evaluate as ev
from compute_curve.statarb.power import holm
from compute_curve.timeutil import add_months, month_start

STRATEGIES = ("SP-I", "SP-F")


@dataclass(frozen=True)
class SpreadRules:
    phi: float = 0.5
    theta: float = 0.05
    min_index_days: int = 40
    min_futures_days: int = 60
    min_obs: int = 12
    deadline: date = date(2028, 7, 1)
    alpha: float = 0.05
    hac_lag: int = 1
    stress: float = 2.0
    sp0_min_prior: int = 20
    sp0_horizon: int = 40
    sp0_min_forecasts: int = 60
    sp0_date: date = date(2027, 7, 1)


RULES = SpreadRules()


def forecast(r_now: float, r_bar: float, phi: float = RULES.phi) -> float:
    """Partial reversion of the log ratio towards its running mean."""
    return r_bar + phi * (r_now - r_bar)


def notional_k(f2: float, f1: float) -> int:
    """GPU1 contracts per GPU2 contract, roughly notional-neutral, in {1, 2, 3}."""
    return int(min(3, max(1, round(f2 / f1))))


def decide(g: float, theta: float = RULES.theta) -> int:
    """Position in GPU2: +1 when the market ratio is too low, -1 when too high."""
    if g > theta:
        return 1
    if g < -theta:
        return -1
    return 0


def spread_pnl(
    pos: int, k: int, f1: float, f2: float, s1: float, s2: float, hours: float, cost: float
) -> float:
    return pos * ((s2 - f2) - k * (s1 - f1)) * hours - (1 + k) * cost


def index_ratio_history(pub: pd.DataFrame, t: date) -> pd.Series:
    """ln(B200 index / H100 index) on days with both values usable at 00:00 UTC on t."""
    p = pub.loc[pub["ts_available"] <= _cutoff(t)]
    if p.empty:
        return pd.Series(dtype=float)
    wide = p.pivot_table(index="as_of_date", columns="index_name", values="value", aggfunc="last")
    need = [INDEX_NAMES["GPU1"], INDEX_NAMES["GPU2"]]
    if not set(need) <= set(wide.columns):
        return pd.Series(dtype=float)
    both = wide[need].dropna().sort_index()
    return np.log(both[need[1]]) - np.log(both[need[0]])


def front_ratio_history(settle: pd.DataFrame, t: date) -> pd.Series:
    """Daily ln(F2/F1) on each trade date's front contract month, usable before t."""
    s = settle.loc[settle["ts_available"] < _cutoff(t)]
    out = {}
    for d, g in s.groupby("trade_date"):
        front = f"{month_start(d):%Y-%m}"
        p = g.loc[g["contract_month"] == front].set_index("product")["settle_price"]
        if {"GPU1", "GPU2"} <= set(p.index):
            out[d] = float(np.log(p["GPU2"]) - np.log(p["GPU1"]))
    return pd.Series(out, dtype=float).sort_index()


def _levels(
    variant: str, settle: pd.DataFrame, pub: pd.DataFrame, t: date
) -> tuple[float, float] | None:
    if variant == "SP-I":
        hist, need = index_ratio_history(pub, t), RULES.min_index_days
    else:
        hist, need = front_ratio_history(settle, t), RULES.min_futures_days
    if len(hist) < need + 1:
        return None
    return float(hist.iloc[-1]), float(hist.iloc[:-1].mean())


def observations(
    settle: pd.DataFrame, pub: pd.DataFrame, cfg: Config, through: date, rules: SpreadRules = RULES
) -> list[dict[str, Any]]:
    """Every decision day up to ``through``, both variants: forecast, market, position, P&L."""
    rows: list[dict[str, Any]] = []
    if settle.empty:
        return rows
    spec1, spec2 = cfg.contracts["GPU1"], cfg.contracts["GPU2"]
    hours = spec1.gpu_hours_per_contract
    for t in decision_days(min(settle["trade_date"]), through):
        m2 = add_months(month_start(t), 2)
        code = f"{m2:%Y-%m}"
        f1 = curve_before(settle, "GPU1", t).get(code)
        f2 = curve_before(settle, "GPU2", t).get(code)
        if f1 is None or f2 is None:
            continue
        s1, s2 = realized(settle, "GPU1", m2), realized(settle, "GPU2", m2)
        for variant in STRATEGIES:
            lv = _levels(variant, settle, pub, t)
            if lv is None:
                continue
            r_now, r_bar = lv
            r_hat = forecast(r_now, r_bar, rules.phi)
            f = float(np.log(f2) - np.log(f1))
            pos = decide(r_hat - f, rules.theta)
            k = notional_k(f2, f1)
            row: dict[str, Any] = {
                "strategy": variant,
                "decision_day": str(t),
                "contract_month": code,
                "forecast": r_hat,
                "random_walk": r_now,
                "market": f,
                "signal": r_hat - f,
                "position": pos,
                "k": k,
            }
            if s1 is not None and s2 is not None:
                row["realized"] = float(np.log(s2) - np.log(s1))
                if pos != 0:
                    c = leg_cost(spec2, cfg.costs)
                    row["pnl"] = spread_pnl(pos, k, f1, f2, s1, s2, hours, c)
                    row["pnl_stress"] = spread_pnl(
                        pos, k, f1, f2, s1, s2, hours, leg_cost(spec2, cfg.costs, rules.stress)
                    )
            rows.append(row)
    return rows


def c0(rows: list[dict[str, Any]], lag: int = RULES.hac_lag) -> float:
    """Clark-West one-sided p: forecast vs random walk on realised settlement ratios."""
    r = [x for x in rows if "realized" in x]
    if len(r) < 3:
        return float("nan")
    y = np.array([x["realized"] for x in r])
    m = np.array([x["forecast"] for x in r])
    rw = np.array([x["random_walk"] for x in r])
    out = cs.clark_west(y - rw, m - rw, np.zeros_like(y), lag)
    return float(out.p_value) if out is not None else float("nan")


def evaluate(rows: list[dict[str, Any]], today: date, rules: SpreadRules = RULES) -> dict[str, Any]:
    """C0, C1 (Holm over SP-I and SP-F) and C2; 'waiting' until the trigger."""
    by = {k: [r for r in rows if r["strategy"] == k] for k in STRATEGIES}
    traded = {k: [r for r in v if "pnl" in r] for k, v in by.items()}
    due = today >= rules.deadline or any(len(v) >= rules.min_obs for v in traded.values())
    out: dict[str, Any] = {
        "due": due,
        "strategies": {k: {"n_settled_trades": len(v)} for k, v in traded.items()},
    }
    if not due:
        return out
    ps = []
    for k in STRATEGIES:
        res, v = out["strategies"][k], traded[k]
        if len(v) < rules.min_obs:
            res["verdict"] = "too little history to conclude"
            ps.append(1.0)
            continue
        pnl = np.array([r["pnl"] for r in v])
        stress = np.array([r["pnl_stress"] for r in v])
        p = ev.hac_p_one_sided(pnl, rules.hac_lag)
        res |= {
            "c0_p": c0(by[k]),
            "mean_pnl_usd": float(pnl.mean()),
            "mean_pnl_stress_usd": float(stress.mean()),
            "p_one_sided": p,
        }
        ps.append(p if np.isfinite(p) else 1.0)
    for k, pa in zip(STRATEGIES, holm(ps), strict=True):
        res = out["strategies"][k]
        if "p_one_sided" not in res:
            continue
        res["p_holm"] = float(pa)
        ok = (
            np.isfinite(res["c0_p"])
            and res["c0_p"] <= rules.alpha
            and pa <= rules.alpha
            and res["mean_pnl_stress_usd"] > 0
        )
        res["verdict"] = "pass" if ok else "not confirmed"
    return out


# ---------------------------------------------------------------------------
# SP-0: forward replication on our own index
# ---------------------------------------------------------------------------
def own_ratio(own: pd.DataFrame) -> pd.Series:
    """ln(B200/H100) of our own index on days where both meet coverage."""
    o = own.loc[(own["series"] == "history_panel") & own["meets_coverage"].astype(bool)]
    wide = o.pivot_table(index="as_of_date", columns="gpu_model", values="value", aggfunc="last")
    if not {"H100", "B200"} <= set(wide.columns):
        return pd.Series(dtype=float)
    both = wide[["H100", "B200"]].dropna()
    both.index = pd.to_datetime(both.index)
    return (np.log(both["B200"]) - np.log(both["H100"])).sort_index()


def sp0_forecasts(ratio: pd.Series, rules: SpreadRules = RULES) -> pd.DataFrame:
    """One forecast per day with enough history; the outcome once 40 business days have passed."""
    rows = []
    vals = ratio.to_numpy(float)
    idx = ratio.index
    for i in range(rules.sp0_min_prior, len(vals)):
        target = idx[i] + pd.offsets.BDay(rules.sp0_horizon)
        fut = ratio.loc[ratio.index >= target]
        rows.append(
            {
                "date": idx[i].date(),
                "ratio": vals[i],
                "forecast": forecast(vals[i], float(vals[:i].mean()), rules.phi),
                "outcome": float(fut.iloc[0]) if not fut.empty else np.nan,
            }
        )
    return pd.DataFrame(rows, columns=["date", "ratio", "forecast", "outcome"])


def sp0_evaluate(fc: pd.DataFrame, today: date, rules: SpreadRules = RULES) -> dict[str, Any]:
    done = fc.dropna(subset=["outcome"])
    res: dict[str, Any] = {"n_forecasts": len(fc), "n_with_outcome": len(done)}
    if today < rules.sp0_date:
        res["verdict"] = f"waiting until {rules.sp0_date}"
        return res
    if len(done) < rules.sp0_min_forecasts:
        res["verdict"] = "too little history to conclude"
        return res
    y = (done["outcome"] - done["ratio"]).to_numpy(float)
    m = (done["forecast"] - done["ratio"]).to_numpy(float)
    cw = cs.clark_west(y, m, np.zeros_like(y), rules.sp0_horizon)
    p = float(cw.p_value) if cw is not None else float("nan")
    res |= {
        "p_one_sided": p,
        "verdict": "pass" if np.isfinite(p) and p <= rules.alpha else "not confirmed",
    }
    return res


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------
def run_shadow(cfg: Config, today: date) -> Path:  # pragma: no cover - reads local files
    from compute_curve.pipeline import paths as ppaths  # noqa: PLC0415
    from compute_curve.storage import warehouse as wh  # noqa: PLC0415

    p = ppaths(cfg)
    out = cfg.path("reports") / "spread"
    out.mkdir(parents=True, exist_ok=True)
    own_csv = cfg.path("reports") / "own_index.csv"
    fc = sp0_forecasts(own_ratio(pd.read_csv(own_csv))) if own_csv.exists() else pd.DataFrame()
    if not fc.empty:
        fc.to_csv(out / "sp0_forecasts.csv", index=False)
    sp0 = sp0_evaluate(fc, today) if not fc.empty else {"verdict": "no own-index data"}
    lines = [
        "# Claim 8 GPU2/GPU1 spread: shadow",
        "",
        f"As of {today}. Plan: docs/spread_plan.md. Derived numbers only (D59). No orders.",
        "",
        f"- SP-0 (own-index forward replication of R7-04): {sp0.get('n_forecasts', 0)} forecasts, "
        f"{sp0.get('n_with_outcome', 0)} with a 40-business-day outcome; {sp0['verdict']}.",
    ]
    if not fc.empty:
        last = fc.iloc[-1]
        lines.append(
            f"- Latest own-index ratio ln(B200/H100) {last['ratio']:.3f}; forecast for 40 business "
            f"days ahead {last['forecast']:.3f} (B200 at {np.exp(last['forecast']):.2f}x H100)."
        )
    settle = wh.load_settlement_csvs(p["manual_settle"])
    if settle.empty:
        lines.append("- SP-I/SP-F: no CME settlements yet (GPU1/GPU2 not listed, B8). Waiting.")
    else:
        pub = wh.load_published_index_csvs(p["manual_index"], cfg.nowcast.publication_lag_days)
        rows = observations(settle, pub, cfg, today)
        pd.DataFrame(rows).to_csv(out / "decisions.csv", index=False)
        ev_ = evaluate(rows, today)
        for k, v in ev_["strategies"].items():
            lines.append(f"- {k}: {v['n_settled_trades']} settled traded decisions.")
        result = out / "claim8_result.json"
        if ev_["due"] and not result.exists():
            result.write_text(json.dumps(ev_, indent=2, default=float))
            lines.append("- Evaluation ran (once): see claim8_result.json.")
    if sp0.get("p_one_sided") is not None and not (out / "sp0_result.json").exists():
        (out / "sp0_result.json").write_text(json.dumps(sp0, indent=2, default=float))
    md = out / "status.md"
    md.write_text("\n".join(lines) + "\n")
    return md
