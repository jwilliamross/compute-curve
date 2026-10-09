"""Round-1 tests, false-discovery control, survival, freezing and confirmation.

Statistics come from :mod:`compute_curve.claim4.stats` and
:mod:`compute_curve.backtest.bootstrap` (docs/exploration_plan.md sections
7 and 8). Every exploration result is exploratory.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats as st

from compute_curve.backtest.bootstrap import block_bootstrap_ci
from compute_curve.claim4 import stats as cs
from compute_curve.config import ExplorationConfig
from compute_curve.explore.hypotheses import EPS, SPECS, Built, Spec


@dataclass
class Result:
    hid: str
    kind: str
    n: int = 0
    n_nonzero: int = 0
    n_events: int = 0
    n_cross_sections: int = 0
    intercept: float = float("nan")
    slope: float = float("nan")
    slope_se: float = float("nan")
    t_stat: float = float("nan")
    p_hac: float = float("nan")
    rho: float = float("nan")
    ci_lo: float = float("nan")  # correlation (time series) or mean slope (panel)
    ci_hi: float = float("nan")
    p_perm: float = float("nan")
    n_perm: int = 0
    echo_slope: float = float("nan")
    echo_t: float = float("nan")
    y_mean: float = float("nan")
    mde: float = float("nan")
    sufficient: bool = False
    q: float = float("nan")
    survives: bool = False
    notes: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Single tests
# ---------------------------------------------------------------------------
def _echo(frame: pd.DataFrame, lag: int) -> tuple[float, float]:
    """Slope and t of y on x after partialling out ``ctrl`` (Frisch-Waugh-Lovell)."""
    d = frame.dropna(subset=["x", "y", "ctrl"])
    if len(d) < 5 or np.ptp(d["ctrl"].to_numpy(float)) == 0:
        return float("nan"), float("nan")
    z = np.column_stack([np.ones(len(d)), d["ctrl"].to_numpy(float)])

    def resid(v: np.ndarray) -> np.ndarray:
        beta, *_ = np.linalg.lstsq(z, v, rcond=None)
        return v - z @ beta

    fit = cs.ols_hac(resid(d["x"].to_numpy(float)), resid(d["y"].to_numpy(float)), lag)
    return (fit.slope, fit.t_stat) if fit is not None else (float("nan"), float("nan"))


def ts_test(built: Built, spec: Spec, ecfg: ExplorationConfig, seed: int) -> Result:
    """Predictive OLS with Newey-West errors, circular-shift check, bootstrap CI."""
    res = Result(spec.hid, spec.kind)
    d = built.frame.dropna(subset=["x", "y"]).sort_values("t")
    x, y = d["x"].to_numpy(float), d["y"].to_numpy(float)
    res.n, res.n_events = len(d), built.n_events
    res.n_nonzero = int(np.sum(np.abs(x) > EPS))
    res.y_mean = float(y.mean()) if y.size else float("nan")
    res.mde = cs.mde_correlation(res.n, ecfg.fdr_q / len(SPECS))
    fit = cs.ols_hac(x, y, spec.lag)
    res.rho = cs.pearson(x, y)
    if fit is None:
        res.notes.append(
            "too few observations for the Newey-West lag"
            if not cs.enough_for_hac(res.n, spec.lag)
            else "no variation in the signal"
        )
    else:
        res.intercept, res.slope, res.slope_se = fit.intercept, fit.slope, fit.slope_se
        res.t_stat, res.p_hac = fit.t_stat, fit.p_value
        res.ci_lo, res.ci_hi = cs.block_bootstrap_corr_ci(
            x, y, block_length=spec.block, n_boot=ecfg.n_boot, seed=seed
        )
        res.p_perm, res.n_perm = cs.circular_shift_pvalue(x, y, min_shift=spec.min_shift)
        if spec.echo:
            res.echo_slope, res.echo_t = _echo(d, spec.lag)
    res.sufficient = bool(
        fit is not None
        and cs.enough_for_hac(res.n, spec.lag)
        and res.n_nonzero >= ecfg.min_nonzero
        and res.n_events >= ecfg.min_events
    )
    if fit is not None and not res.sufficient:
        res.notes.append(
            f"insufficient: {res.n_nonzero} non-zero signal values (need {ecfg.min_nonzero}), "
            f"{res.n_events} distinct changes (need {ecfg.min_events})"
        )
    return res


def daily_slopes(frame: pd.DataFrame, min_providers: int) -> pd.DataFrame:
    """Cross-sectional OLS of ``y`` on ``x`` per day ``t`` (Fama-MacBeth first stage)."""
    rows = []
    for t, g in frame.dropna(subset=["x", "y"]).groupby("t", sort=True):
        xs, ys = g["x"].to_numpy(float), g["y"].to_numpy(float)
        if xs.size < min_providers or np.ptp(xs) == 0:
            continue
        b, a = np.polyfit(xs, ys, 1)
        rows.append({"t": t, "a": float(a), "b": float(b), "n": int(xs.size)})
    return pd.DataFrame(rows, columns=["t", "a", "b", "n"])


def panel_test(built: Built, spec: Spec, ecfg: ExplorationConfig, seed: int) -> Result:
    """Fama-MacBeth mean slope: Newey-West t, exact sign-flip check, block bootstrap."""
    res = Result(spec.hid, spec.kind)
    f = built.frame.dropna(subset=["x", "y"])
    slopes = daily_slopes(f, ecfg.min_cs_providers)
    res.n = len(f)
    res.n_events = built.n_events
    res.n_cross_sections = len(slopes)
    res.n_nonzero = int(np.sum(np.abs(f["y"].to_numpy(float)) > EPS))
    res.y_mean = float(f["y"].mean()) if len(f) else float("nan")
    res.rho = cs.pearson(f["x"].to_numpy(float), f["y"].to_numpy(float))
    b = slopes["b"].to_numpy(float)
    if b.size >= 2:
        res.intercept, res.slope = float(slopes["a"].mean()), float(b.mean())
        res.slope_se = cs.hac_mean_se(b, spec.lag)
        if np.isfinite(res.slope_se) and res.slope_se > 0:
            res.t_stat = res.slope / res.slope_se
            res.p_hac = float(2 * st.t.sf(abs(res.t_stat), df=b.size - 1))
        res.ci_lo, res.ci_hi = block_bootstrap_ci(
            b, np.mean, n_boot=ecfg.n_boot, block_length=spec.block, seed=seed
        )
        res.p_perm = cs.sign_flip_pvalue(b[:: spec.lag], seed=seed)
        res.n_perm = int(b[:: spec.lag].size)
    else:
        res.notes.append("fewer than two daily cross-sections")
    res.mde = cs.mde_correlation(max(res.n_cross_sections, 0), ecfg.fdr_q / len(SPECS))
    res.sufficient = bool(
        res.n_cross_sections >= ecfg.min_cross_sections
        and res.n_nonzero >= ecfg.min_nonzero
        and res.n_events >= ecfg.min_events
        and np.isfinite(res.p_hac)
    )
    if not res.sufficient:
        res.notes.append(
            f"insufficient: {res.n_cross_sections} cross-sections (need "
            f"{ecfg.min_cross_sections}), {res.n_nonzero} non-zero provider changes (need "
            f"{ecfg.min_nonzero}), {res.n_events} change days (need {ecfg.min_events})"
        )
    return res


def run_test(built: Built, spec: Spec, ecfg: ExplorationConfig, seed: int) -> Result:
    return (panel_test if spec.kind == "panel" else ts_test)(built, spec, ecfg, seed)


# ---------------------------------------------------------------------------
# The round: BH across all hypotheses, survival, ranking
# ---------------------------------------------------------------------------
def apply_round(results: list[Result], ecfg: ExplorationConfig) -> list[Result]:
    """Benjamini-Hochberg across the round (not testable counts as p = 1), then S1 to S4."""
    pvals = [r.p_hac if r.sufficient and np.isfinite(r.p_hac) else 1.0 for r in results]
    qs = cs.benjamini_hochberg(pvals)
    for r, q in zip(results, qs, strict=True):
        r.q = float(q)
        spec = SPECS[r.hid]
        echo_ok = True
        if spec.echo:
            echo_ok = bool(
                np.isfinite(r.echo_t)
                and np.sign(r.echo_slope) == np.sign(r.slope)
                and abs(r.echo_t) >= ecfg.echo_min_t
            )
        r.survives = bool(
            r.sufficient
            and r.q <= ecfg.fdr_q
            and np.isfinite(r.p_perm)
            and r.p_perm <= ecfg.perm_alpha
            and echo_ok
        )
        if r.sufficient and r.q <= ecfg.fdr_q and not r.survives:
            r.notes.append("passes the false-discovery screen but fails a robustness filter")
    return results


def ranked_survivors(results: list[Result], k: int) -> list[Result]:
    surv = [r for r in results if r.survives]
    return sorted(surv, key=lambda r: (r.q, r.p_hac))[:k]


# ---------------------------------------------------------------------------
# Freezing and the one-shot confirmation
# ---------------------------------------------------------------------------
def freeze(r: Result) -> dict[str, Any]:
    spec = SPECS[r.hid]
    return {
        "hid": r.hid,
        "spec": asdict(spec),
        "direction": int(np.sign(r.slope)),
        "intercept": r.intercept,
        "slope": r.slope,
        "slope_se_explore": r.slope_se,
        "n_explore": r.n_cross_sections if spec.kind == "panel" else r.n,
        "rho_explore": r.rho,
        "y_mean_explore": r.y_mean,
    }


@dataclass
class Confirmation:
    hid: str
    n: int = 0
    slope: float = float("nan")
    slope_se: float = float("nan")
    t_stat: float = float("nan")
    p_one_sided: float = float("nan")
    p_holm: float = float("nan")
    oos_r2_zero: float = float("nan")
    oos_r2_mean: float = float("nan")
    power: float = float("nan")
    c1: bool = False
    c2: bool = False
    confirmed: bool = False
    verdict: str = ""
    notes: list[str] = field(default_factory=list)


def _oos_r2(y: np.ndarray, pred: np.ndarray, base: np.ndarray) -> float:
    den = float(np.sum((y - base) ** 2))
    return float(1.0 - np.sum((y - pred) ** 2) / den) if den > 0 else float("nan")


def confirm_one(
    built: Built, frozen: dict[str, Any], ecfg: ExplorationConfig, spec: Spec | None = None
) -> Confirmation:
    """Frozen specification on the confirmation sample: C1 (one-sided) and C2 (OOS R2)."""
    spec = spec or SPECS[frozen["hid"]]
    out = Confirmation(frozen["hid"])
    sign = int(frozen["direction"])
    a, b = float(frozen["intercept"]), float(frozen["slope"])
    f = built.frame.dropna(subset=["x", "y"])
    x, y = f["x"].to_numpy(float), f["y"].to_numpy(float)
    if spec.kind == "panel":
        slopes = daily_slopes(f, ecfg.min_cs_providers)
        bs = slopes["b"].to_numpy(float)
        out.n = int(bs.size)
        if bs.size >= 2:
            out.slope, out.slope_se = float(bs.mean()), cs.hac_mean_se(bs, spec.lag)
            if np.isfinite(out.slope_se) and out.slope_se > 0:
                out.t_stat = out.slope / out.slope_se
                out.p_one_sided = float(st.t.sf(sign * out.t_stat, df=bs.size - 1))
        n_exp = max(int(frozen["n_explore"]), 1)
        se_c = float(frozen["slope_se_explore"]) * np.sqrt(n_exp / max(out.n, 1))
        z = abs(b) / se_c if se_c > 0 else float("nan")
    else:
        out.n = int(x.size)
        fit = cs.ols_hac(x, y, spec.lag)
        if fit is not None:
            out.slope, out.slope_se, out.t_stat = fit.slope, fit.slope_se, fit.t_stat
            out.p_one_sided = float(st.t.sf(sign * fit.t_stat, df=x.size - 2))
        rho = abs(float(frozen["rho_explore"]))
        z = np.arctanh(min(rho, 0.999)) * np.sqrt(max(out.n - 3, 0))
    out.power = (
        float(st.norm.cdf(z - st.norm.ppf(1 - ecfg.confirm_alpha))) if np.isfinite(z) else 0.0
    )
    if x.size:
        pred = a + b * x
        out.oos_r2_zero = _oos_r2(y, pred, np.zeros_like(y))
        out.oos_r2_mean = _oos_r2(y, pred, np.full_like(y, float(frozen["y_mean_explore"])))
    out.c2 = bool(
        np.isfinite(out.oos_r2_zero)
        and np.isfinite(out.oos_r2_mean)
        and out.oos_r2_zero > 0
        and out.oos_r2_mean > 0
    )
    return out


def finish_confirmation(rows: list[Confirmation], ecfg: ExplorationConfig) -> list[Confirmation]:
    """Holm across the confirmed hypotheses, then the verdicts."""
    p = [r.p_one_sided if np.isfinite(r.p_one_sided) else 1.0 for r in rows]
    adj = cs.holm(p) if rows else []
    for r, pa in zip(rows, adj, strict=True):
        r.p_holm = float(pa)
        r.c1 = bool(np.isfinite(pa) and pa <= ecfg.confirm_alpha)
        r.confirmed = r.c1 and r.c2
        if r.confirmed:
            r.verdict = "confirmed: candidate for the forward test"
        elif r.power < 0.5:
            r.verdict = "not confirmed (underpowered)"
        else:
            r.verdict = "not confirmed"
    return rows
