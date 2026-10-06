"""Round-1 commands: exploration, freeze, confirmation (docs/exploration_plan.md).

Outputs go to ``reports/exploration/``. The confirmation is one shot: it
refuses to run when its result file exists. No Alpaca price is written;
reports hold statistics only (D29).
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from compute_curve.backtest import variants
from compute_curve.config import Claim4Config, Config, ExplorationConfig
from compute_curve.explore.data import Round1Data, Which, load_round1
from compute_curve.explore.hypotheses import SPECS, Built, build
from compute_curve.explore.run import (
    Confirmation,
    Result,
    apply_round,
    confirm_one,
    finish_confirmation,
    freeze,
    ranked_survivors,
    run_test,
)

LABEL = "EXPLORATORY"


def _cfgs(cfg: Config) -> tuple[ExplorationConfig, Claim4Config]:
    if cfg.exploration is None or cfg.claim4 is None:
        raise RuntimeError("config needs [exploration] and [claim4] sections")
    return cfg.exploration, cfg.claim4


def paths(cfg: Config) -> dict[str, Path]:
    ecfg, _ = _cfgs(cfg)
    rep = cfg.path("reports") / "exploration"
    k = f"round{ecfg.round}"
    return {
        "dir": rep,
        "explore_json": rep / f"{k}_exploration.json",
        "explore_md": rep / f"{k}_exploration.md",
        "frozen": rep / f"{k}_frozen.json",
        "confirm_json": rep / f"{k}_confirmation.json",
        "confirm_md": rep / f"{k}_confirmation.md",
    }


def _window(built: Built) -> tuple[str, str]:
    t = built.frame["t"] if "t" in built.frame else pd.Series(dtype=object)
    if t.empty:
        return "", ""
    return str(pd.Timestamp(t.min())), str(pd.Timestamp(t.max()))


def _clean(v: Any) -> Any:
    if isinstance(v, float) and not np.isfinite(v):
        return None
    if isinstance(v, dict):
        return {k: _clean(x) for k, x in v.items()}
    if isinstance(v, list):
        return [_clean(x) for x in v]
    return v


def explore(
    data: Round1Data, ecfg: ExplorationConfig, c4: Claim4Config, seed: int
) -> tuple[list[Result], dict[str, tuple[str, str]]]:
    """Every hypothesis on the exploration set only, then the round's BH and filters."""
    exp = data.restrict(ecfg, "explore")
    results, windows = [], {}
    for hid, spec in SPECS.items():
        built = build(hid, exp, ecfg, c4)
        windows[hid] = _window(built)
        results.append(run_test(built, spec, ecfg, seed))
    return apply_round(results, ecfg), windows


def confirm(
    data: Round1Data, frozen: list[dict[str, Any]], ecfg: ExplorationConfig, c4: Claim4Config
) -> tuple[list[Confirmation], dict[str, tuple[str, str]]]:
    """Each frozen specification once on the confirmation set only."""
    conf = data.restrict(ecfg, "confirm")
    rows, windows = [], {}
    for fz in frozen:
        built = build(fz["hid"], conf, ecfg, c4)
        windows[fz["hid"]] = _window(built)
        rows.append(confirm_one(built, fz, ecfg))
    return finish_confirmation(rows, ecfg), windows


def _status(r: Result) -> str:
    if not r.sufficient:
        return "not testable"
    if r.survives:
        return "survivor"
    return "not significant" if r.q > 0.10 else "fails a robustness filter"


def _f(v: float, nd: int = 3) -> str:
    return "n/a" if v is None or not np.isfinite(v) else f"{v:.{nd}f}"


def _p(v: float) -> str:
    if v is None or not np.isfinite(v):
        return "n/a"
    return "<0.001" if v < 0.001 else f"{v:.3f}"


def render_exploration(
    results: list[Result], windows: dict[str, tuple[str, str]], ecfg: ExplorationConfig
) -> str:
    gen = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# Exploration round {ecfg.round}: exploration-set results ({LABEL})",
        "",
        f"Generated {gen}. Every number here is **exploratory**: it comes from the",
        "exploration set only (docs/exploration_plan.md section 2) and is not a finding.",
        f"{len(results)} hypotheses, one test each; Benjamini-Hochberg across the round at q = "
        f"{ecfg.fdr_q}. Project-wide declared tests and evaluations: {variants.count_tests()}.",
        "",
        "| ID | Data | Sample (first to last t) | n | Non-zero signal | Distinct changes | Slope | "
        "Correlation (95% CI) | p (Newey-West) | p (permutation) | q (BH) | Echo t | Status |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        spec = SPECS[r.hid]
        first, last = windows.get(r.hid, ("", ""))
        span = f"{first[:16]} to {last[:16]}" if first else "none"
        if spec.kind == "panel":
            corr = f"pooled {_f(r.rho, 2)}; mean slope CI {_f(r.ci_lo)} to {_f(r.ci_hi)}"
            n = f"{r.n} provider-days, {r.n_cross_sections} days"
        else:
            corr = f"{_f(r.rho, 2)} ({_f(r.ci_lo, 2)} to {_f(r.ci_hi, 2)})"
            n = str(r.n)
        lines.append(
            f"| {r.hid} | {spec.data} | {span} | {n} | {r.n_nonzero} | {r.n_events} | "
            f"{_f(r.slope, 4)} | {corr} | {_p(r.p_hac)} | {_p(r.p_perm)} | {_p(r.q)} | "
            f"{_f(r.echo_t, 2) if spec.echo else 'n/a'} | {_status(r)} |"
        )
    lines += ["", "## Hypotheses", ""]
    for r in results:
        spec = SPECS[r.hid]
        sign = "+" if spec.expected_sign > 0 else "−"
        obs = "n/a" if not np.isfinite(r.slope) else ("+" if r.slope > 0 else "−")
        lines.append(
            f"- **{r.hid}**: {spec.signal} → {spec.target} ({spec.horizon}). Expected sign {sign}, "
            f"observed {obs}. Smallest detectable correlation at this n: {_f(r.mde, 2)}."
            + (f" Notes: {'; '.join(r.notes)}." if r.notes else "")
        )
    surv = ranked_survivors(results, ecfg.max_confirm)
    lines += [
        "",
        "## Survivors",
        "",
        (
            "None. No hypothesis passes S1 to S4, so nothing goes to confirmation."
            if not surv
            else "Ranked by q, then p (at most "
            f"{ecfg.max_confirm} go to confirmation): " + ", ".join(r.hid for r in surv) + "."
        ),
        "",
    ]
    return "\n".join(lines)


def run_exploration(cfg: Config) -> Path:  # pragma: no cover - reads local data
    ecfg, c4 = _cfgs(cfg)
    p = paths(cfg)
    results, windows = explore(load_round1(cfg), ecfg, c4, cfg.project.seed)
    p["dir"].mkdir(parents=True, exist_ok=True)
    payload = {
        "label": LABEL,
        "generated": datetime.now(UTC).isoformat(),
        "round": ecfg.round,
        "fdr_q": ecfg.fdr_q,
        "results": [r.as_dict() for r in results],
        "windows": windows,
        "survivors": [r.hid for r in ranked_survivors(results, ecfg.max_confirm)],
        "all_survivors": [r.hid for r in results if r.survives],
    }
    p["explore_json"].write_text(json.dumps(_clean(payload), indent=2, default=str))
    p["explore_md"].write_text(render_exploration(results, windows, ecfg))
    return p["explore_md"]


def describe_survivors(
    data: Round1Data, hids: list[str], ecfg: ExplorationConfig, c4: Claim4Config
) -> str:
    """Descriptive stability checks on the exploration set only (not tests)."""
    exp = data.restrict(ecfg, "explore")
    lines = [
        f"# Exploration round {ecfg.round}: survivors, descriptive checks ({LABEL})",
        "",
        "Exploration set only. These are descriptive, post hoc and not tests; they change",
        "nothing in the frozen specifications.",
        "",
        "| ID | Correlation, all | First half | Second half | Without the 1% largest signals |",
        "|---|---|---|---|---|",
    ]
    for hid in hids:
        f = build(hid, exp, ecfg, c4).frame.dropna(subset=["x", "y"]).sort_values("t")
        x, y = f["x"].to_numpy(float), f["y"].to_numpy(float)
        half = len(f) // 2
        keep = np.abs(x) <= np.quantile(np.abs(x), 0.99)
        cells = [
            np.corrcoef(x, y)[0, 1],
            np.corrcoef(x[:half], y[:half])[0, 1],
            np.corrcoef(x[half:], y[half:])[0, 1],
            np.corrcoef(x[keep], y[keep])[0, 1],
        ]
        lines.append(f"| {hid} | " + " | ".join(_f(c, 2) for c in cells) + " |")
    return "\n".join(lines) + "\n"


def run_freeze(cfg: Config) -> Path:  # pragma: no cover - file glue
    ecfg, _ = _cfgs(cfg)
    p = paths(cfg)
    if p["frozen"].exists():
        raise FileExistsError(f"{p['frozen']} exists; a frozen specification is never rewritten")
    ex = json.loads(p["explore_json"].read_text())
    by_id = {r["hid"]: r for r in ex["results"]}
    frozen = []
    for hid in ex["survivors"][: ecfg.max_confirm]:
        r = Result(**{k: (float("nan") if v is None else v) for k, v in by_id[hid].items()})
        frozen.append(freeze(r))
    payload = {"frozen_at": datetime.now(UTC).isoformat(), "frozen": frozen}
    p["frozen"].write_text(json.dumps(_clean(payload), indent=2, default=str))
    if frozen:
        _, c4 = _cfgs(cfg)
        hids = [fz["hid"] for fz in frozen]
        text = describe_survivors(load_round1(cfg), hids, ecfg, c4)
        (p["dir"] / f"round{ecfg.round}_descriptive.md").write_text(text)
    return p["frozen"]


def render_confirmation(
    rows: list[Confirmation], windows: dict[str, tuple[str, str]], ecfg: ExplorationConfig
) -> str:
    gen = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# Exploration round {ecfg.round}: confirmation (one shot)",
        "",
        f"Generated {gen}. Frozen specifications from `round{ecfg.round}_frozen.json`, run once on",
        "the confirmation set only. C1: one-sided Newey-West test in the exploration direction,",
        f"Holm across the {len(rows)} confirmed, at {ecfg.confirm_alpha}. C2: the frozen forecast",
        "beats a zero change and the exploration mean out of sample (R² above 0 against both).",
        "",
    ]
    if not rows:
        lines.append("No survivor from exploration, so nothing was confirmed.")
        return "\n".join(lines) + "\n"
    lines += [
        "| ID | Sample | n | Slope | p one-sided | p Holm | OOS R² vs zero | OOS R² vs mean | "
        "Power | C1 | C2 | Verdict |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        first, last = windows.get(r.hid, ("", ""))
        lines.append(
            f"| {r.hid} | {first[:16]} to {last[:16]} | {r.n} | {_f(r.slope, 4)} | "
            f"{_p(r.p_one_sided)} | {_p(r.p_holm)} | {_f(r.oos_r2_zero)} | {_f(r.oos_r2_mean)} | "
            f"{_f(r.power, 2)} | {'yes' if r.c1 else 'no'} | {'yes' if r.c2 else 'no'} | "
            f"{r.verdict} |"
        )
    return "\n".join(lines) + "\n"


def run_confirmation(cfg: Config) -> Path:  # pragma: no cover - reads local data
    ecfg, c4 = _cfgs(cfg)
    p = paths(cfg)
    if p["confirm_json"].exists():
        raise FileExistsError(f"{p['confirm_json']} exists; the confirmation is one shot")
    if not p["frozen"].exists():
        raise FileNotFoundError("run `explore round1 freeze` first (and commit the frozen file)")
    frozen = json.loads(p["frozen"].read_text())["frozen"]
    rows, windows = confirm(load_round1(cfg), frozen, ecfg, c4)
    payload = {
        "generated": datetime.now(UTC).isoformat(),
        "rows": [r.__dict__ for r in rows],
        "windows": windows,
    }
    p["confirm_json"].write_text(json.dumps(_clean(payload), indent=2, default=str))
    p["confirm_md"].write_text(render_confirmation(rows, windows, ecfg))
    return p["confirm_md"]


def set_label(which: Which) -> str:
    return "exploration set" if which == "explore" else "confirmation set"
