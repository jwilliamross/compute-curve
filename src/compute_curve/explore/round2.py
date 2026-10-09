"""Exploration round 2 (docs/exploration_round2_plan.md).

R2-01 replicates H01 once, with its frozen round-1 specification, on the
listings confirmation set. R2-02, R2-03, R2-04 and R2-06 are exploratory and
run on round 1's exploration sets, with Benjamini-Hochberg across the four.
Every exploration number is exploratory.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from compute_curve.claim4 import stats as cs
from compute_curve.config import Claim4Config, Config, ExplorationConfig, Round2Config
from compute_curve.explore.data import Round1Data, load_round1
from compute_curve.explore.hypotheses import (
    EPS,
    Built,
    Spec,
    _frame,
    aws_change,
    aws_log_wide,
    cgi_hourly,
    gd_series,
    h01,
)
from compute_curve.explore.run import (
    Result,
    confirm_one,
    finish_confirmation,
    freeze,
    ranked_survivors,
    ts_test,
)

LABEL = "EXPLORATORY"
EMPTY = ["t", "x", "y", "ctrl"]

R2_SPECS: dict[str, Spec] = {
    s.hid: s
    for s in (
        Spec(
            "R2-02",
            "ts",
            "C",
            "CGI H100 past 6-hour change x (provider count changed in window)",
            "CGI H100 next 6-hour change, controlling for the past change",
            "6 hours",
            6,
            12,
            12,
            -1,
            False,
        ),
        Spec(
            "R2-03",
            "ts",
            "C",
            "CGI B200 past 6-hour change",
            "CGI B200 next 6-hour change",
            "6 hours",
            6,
            12,
            12,
            -1,
            False,
        ),
        Spec(
            "R2-04",
            "walkforward",
            "A",
            "AWS H100 spot 7-day change (expanding-window OLS forecast)",
            "AWS H100 spot next 7-day change",
            "7 days",
            7,
            14,
            14,
            1,
            False,
        ),
        Spec(
            "R2-06",
            "ts",
            "G",
            "GetDeploying H100 on-demand premium over 12-month reservation, weekly change",
            "GetDeploying H100 on-demand next-week change",
            "1 week",
            1,
            2,
            5,
            -1,
            True,
        ),
    )
}


# ---------------------------------------------------------------------------
# Builders
# ---------------------------------------------------------------------------
def cgi_hourly_providers(cgi: pd.DataFrame, gpu: str, max_age_minutes: int) -> pd.Series:
    """CGI provider count at each full hour, aligned with :func:`cgi_hourly`."""
    c = cgi.loc[cgi["gpu_model"] == gpu].sort_values("as_of")
    if c.empty or "n_providers" not in c.columns:
        return pd.Series(dtype=float)
    grid = pd.DataFrame(
        {"t": pd.date_range(c["as_of"].min().ceil("h"), c["as_of"].max().floor("h"), freq="h")}
    )
    m = pd.merge_asof(
        grid,
        c[["as_of", "n_providers"]],
        left_on="t",
        right_on="as_of",
        direction="backward",
        tolerance=pd.Timedelta(minutes=max_age_minutes),
    )
    return pd.Series(m["n_providers"].to_numpy(dtype=float), index=pd.DatetimeIndex(m["t"]))


def cgi_reversal(data: Round1Data, gpu: str, max_age_minutes: int) -> Built:
    """Past 6-hour log change against the next 6-hour log change, hourly."""
    v = cgi_hourly(data.cgi, gpu, max_age_minutes)
    if v.empty:
        return Built(pd.DataFrame(columns=EMPTY), 0)
    v = v.asfreq("h")
    frame = _frame(v - v.shift(6), v.shift(-6) - v, None)
    if frame.empty:
        return Built(frame, 0)
    one = (v - v.shift(1)).dropna()
    lo, hi = frame["t"].min() - pd.Timedelta(hours=5), frame["t"].max()
    one = one.loc[(one.index >= lo) & (one.index <= hi)]
    return Built(frame, int((one.abs() > EPS).sum()))


def r2_02(data: Round1Data, ecfg: ExplorationConfig) -> tuple[Built, int]:
    """Interaction ``x * D`` (D = provider count changed over the window), control ``x``.

    Returns the built frame (``x`` = interaction, ``ctrl`` = past change) and
    the number of windows with ``D = 1``.
    """
    v = cgi_hourly(data.cgi, "H100", ecfg.cgi_max_age_minutes)
    npv = cgi_hourly_providers(data.cgi, "H100", ecfg.cgi_max_age_minutes)
    if v.empty or npv.empty:
        return Built(pd.DataFrame(columns=EMPTY), 0), 0
    v, npv = v.asfreq("h"), npv.reindex(v.asfreq("h").index)
    past = v - v.shift(6)
    changed = (npv != npv.shift(6)) & npv.notna() & npv.shift(6).notna()
    frame = _frame(past * changed.astype(float), v.shift(-6) - v, past)
    frame = frame.dropna(subset=["ctrl"])
    d_windows = int((frame["x"].abs() > EPS).sum())
    one = (npv != npv.shift(1)) & npv.notna() & npv.shift(1).notna()
    if frame.empty:
        return Built(frame, 0), d_windows
    lo, hi = frame["t"].min() - pd.Timedelta(hours=5), frame["t"].max()
    events = int(one.loc[(one.index >= lo) & (one.index <= hi)].sum())
    return Built(frame, events), d_windows


def r2_04(data: Round1Data, ecfg: ExplorationConfig) -> Built:
    w = aws_log_wide(data.aws, "H100")
    frame = _frame(aws_change(w, 7, ecfg.min_pools), aws_change(w, -7, ecfg.min_pools), None)
    one = aws_change(w, 1, ecfg.min_pools)
    if frame.empty:
        return Built(frame, 0)
    lo, hi = frame["t"].min() - pd.Timedelta(days=6), frame["t"].max()
    return Built(frame, int((one.loc[(one.index >= lo) & (one.index <= hi)].abs() > EPS).sum()))


def r2_06(data: Round1Data) -> Built:
    od = gd_series(data.gd, "H100", "on_demand", "value")
    r12 = gd_series(data.gd, "H100", "reserved_12m", "value")
    if od.empty or r12.empty:
        return Built(pd.DataFrame(columns=EMPTY), 0)
    grid = od.index.union(r12.index)
    od, r12 = od.reindex(grid), r12.reindex(grid)
    prem = od - r12
    frame = _frame(prem - prem.shift(1), od.shift(-1) - od, od - od.shift(1))
    return Built(frame, int((frame["x"].abs() > EPS).sum()))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def residualize(frame: pd.DataFrame) -> pd.DataFrame:
    """Frisch-Waugh-Lovell: ``x`` and ``y`` net of a constant and ``ctrl``."""
    d = frame.dropna(subset=["x", "y", "ctrl"]).copy()
    if len(d) < 3:
        return d.assign(ctrl=np.nan)
    z = np.column_stack([np.ones(len(d)), d["ctrl"].to_numpy(float)])
    for col in ("x", "y"):
        beta, *_ = np.linalg.lstsq(z, d[col].to_numpy(float), rcond=None)
        d[col] = d[col].to_numpy(float) - z @ beta
    return d.assign(ctrl=np.nan)


def walk_forward(frame: pd.DataFrame, horizon: pd.Timedelta, min_train: int) -> pd.DataFrame:
    """Expanding-window OLS forecasts using only pairs whose outcome is known at ``t``.

    A pair at ``t'`` is known at ``t' + horizon``. Returns rows with ``y``,
    ``forecast`` (model), ``mean`` (training mean) for every ``t`` that had at
    least ``min_train`` known pairs.
    """
    d = frame.dropna(subset=["x", "y"]).sort_values("t").reset_index(drop=True)
    t = pd.to_datetime(d["t"])
    rows = []
    for i in range(len(d)):
        known = t + horizon <= t.iloc[i]
        if int(known.sum()) < min_train:
            continue
        xs, ys = d.loc[known, "x"].to_numpy(float), d.loc[known, "y"].to_numpy(float)
        b, a = np.polyfit(xs, ys, 1) if np.ptp(xs) > 0 else (0.0, float(ys.mean()))
        rows.append(
            {
                "t": d.loc[i, "t"],
                "y": float(d.loc[i, "y"]),
                "forecast": float(a + b * d.loc[i, "x"]),
                "mean": float(ys.mean()),
                "slope": float(b),
            }
        )
    return pd.DataFrame(rows, columns=["t", "y", "forecast", "mean", "slope"])


def oos_r2(y: np.ndarray, pred: np.ndarray, base: np.ndarray) -> float:
    den = float(np.sum((y - base) ** 2))
    return float(1.0 - np.sum((y - pred) ** 2) / den) if den > 0 else float("nan")


def wf_test(
    built: Built, spec: Spec, ecfg: ExplorationConfig, r2cfg: Round2Config
) -> tuple[Result, pd.DataFrame]:
    """Clark-West (one-sided) of the walk-forward forecast against zero change."""
    res = Result(spec.hid, spec.kind)
    res.n_events = built.n_events
    fc = walk_forward(built.frame, pd.Timedelta(days=7), r2cfg.min_train)
    res.n = len(fc)
    res.n_nonzero = int(np.sum(np.abs(built.frame["x"].to_numpy(float)) > EPS))
    if fc.empty:
        res.notes.append("no out-of-sample forecasts")
        return res, fc
    y, f = fc["y"].to_numpy(float), fc["forecast"].to_numpy(float)
    cw = cs.clark_west(y, f, np.zeros_like(y), spec.lag)
    res.p_hac = cw.p_value if cw is not None else float("nan")
    res.t_stat = cw.stat if cw is not None else float("nan")
    res.slope = float(fc["slope"].iloc[-1])
    res.y_mean = float(np.mean(y))
    r2_zero = oos_r2(y, f, np.zeros_like(y))
    r2_mean = oos_r2(y, f, fc["mean"].to_numpy(float))
    res.ci_lo, res.ci_hi = r2_zero, r2_mean  # reported as OOS R2 vs zero and vs mean
    res.p_perm = 0.0 if (r2_zero > 0 and r2_mean > 0) else 1.0
    res.sufficient = bool(
        res.n >= r2cfg.min_oos
        and res.n_nonzero >= ecfg.min_nonzero
        and res.n_events >= ecfg.min_events
        and np.isfinite(res.p_hac)
    )
    res.notes.append(f"OOS R2 vs zero {r2_zero:.3f}, vs running mean {r2_mean:.3f}")
    return res, fc


def explore2(
    data: Round1Data, ecfg: ExplorationConfig, r2cfg: Round2Config, seed: int
) -> tuple[list[Result], dict[str, Any]]:
    """R2-02, R2-03, R2-04, R2-06 on the exploration sets, then BH across the four."""
    exp = data.restrict(ecfg, "explore")
    extra: dict[str, Any] = {}
    out: list[Result] = []
    b02, d_windows = r2_02(exp, ecfg)
    r = ts_test(Built(residualize(b02.frame), b02.n_events), R2_SPECS["R2-02"], ecfg, seed)
    extra["R2-02_D_windows"] = d_windows
    if d_windows < r2cfg.min_provider_change_windows:
        r.sufficient = False
        r.notes.append(f"only {d_windows} windows with a provider-count change")
    out.append(r)
    out.append(
        ts_test(cgi_reversal(exp, "B200", ecfg.cgi_max_age_minutes), R2_SPECS["R2-03"], ecfg, seed)
    )
    r04, fc = wf_test(r2_04(exp, ecfg), R2_SPECS["R2-04"], ecfg, r2cfg)
    extra["R2-04_n_oos"] = len(fc)
    out.append(r04)
    out.append(ts_test(r2_06(exp), R2_SPECS["R2-06"], ecfg, seed))
    return apply_round2(out, ecfg), extra


def apply_round2(results: list[Result], ecfg: ExplorationConfig) -> list[Result]:
    """BH across round 2's exploratory tests; survival as round 1 (S1 to S4)."""
    pvals = [r.p_hac if r.sufficient and np.isfinite(r.p_hac) else 1.0 for r in results]
    for r, q in zip(results, cs.benjamini_hochberg(pvals), strict=True):
        r.q = float(q)
        r.mde = cs.mde_correlation(max(r.n, 0), ecfg.fdr_q / len(results))
        spec = R2_SPECS[r.hid]
        echo_ok = not spec.echo or bool(
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
    return results


def replicate_h01(
    data: Round1Data, h01_explore: dict[str, Any], ecfg: ExplorationConfig
) -> dict[str, Any]:
    """R2-01: H01's frozen round-1 specification, once, on the listings confirmation set."""
    r = Result(**{k: (float("nan") if v is None else v) for k, v in h01_explore.items()})
    fz = freeze(r)
    conf = data.restrict(ecfg, "confirm")
    built = h01(conf, ecfg)
    row = finish_confirmation([confirm_one(built, fz, ecfg)], ecfg)[0]
    out = asdict(row)
    out["frozen"] = fz
    days = pd.to_datetime(built.frame["t"]) if not built.frame.empty else pd.Series(dtype=object)
    out["window"] = [str(days.min()), str(days.max())] if len(days) else []
    return out


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------
def _cfgs(cfg: Config) -> tuple[ExplorationConfig, Round2Config, Claim4Config]:
    if cfg.exploration is None or cfg.exploration2 is None or cfg.claim4 is None:
        raise RuntimeError("config needs [exploration], [exploration2] and [claim4]")
    return cfg.exploration, cfg.exploration2, cfg.claim4


def paths(cfg: Config) -> dict[str, Path]:
    rep = cfg.path("reports") / "exploration"
    return {
        "dir": rep,
        "explore_json": rep / "round2_exploration.json",
        "explore_md": rep / "round2_exploration.md",
        "replication_json": rep / "round2_replication.json",
        "frozen": rep / "round2_frozen.json",
        "round1_json": rep / "round1_exploration.json",
    }


def _clean(v: Any) -> Any:
    if isinstance(v, float) and not np.isfinite(v):
        return None
    if isinstance(v, dict):
        return {k: _clean(x) for k, x in v.items()}
    if isinstance(v, list):
        return [_clean(x) for x in v]
    return v


def _f(v: float | None, nd: int = 3) -> str:
    return "n/a" if v is None or not np.isfinite(v) else f"{v:.{nd}f}"


def _p(v: float | None) -> str:
    if v is None or not np.isfinite(v):
        return "n/a"
    return "<0.001" if v < 0.001 else f"{v:.3f}"


def render_exploration2(results: list[Result], extra: dict[str, Any]) -> str:
    lines = [
        f"# Exploration round 2: exploration-set results ({LABEL})",
        "",
        f"Generated {datetime.now(UTC):%Y-%m-%d %H:%M} UTC. Exploration sets of round 1 only",
        "(docs/exploration_round2_plan.md). Benjamini-Hochberg across the 4 tests at q = 0.10.",
        "",
        "| ID | n | Non-zero signal | Distinct changes | Slope | Correlation (95% CI) | p | "
        "Robustness p | q (BH) | Echo t | Status |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        if r.kind == "walkforward":
            corr = f"OOS R² {_f(r.ci_lo)} vs zero, {_f(r.ci_hi)} vs mean"
            rob = "both R² > 0" if r.p_perm == 0 else "an R² ≤ 0"
        else:
            corr = f"{_f(r.rho, 2)} ({_f(r.ci_lo, 2)} to {_f(r.ci_hi, 2)})"
            rob = _p(r.p_perm)
        status = (
            "not testable"
            if not r.sufficient
            else (
                "survivor"
                if r.survives
                else ("not significant" if r.q > 0.10 else "fails a filter")
            )
        )
        echo = _f(r.echo_t, 2) if R2_SPECS[r.hid].echo else "n/a"
        lines.append(
            f"| {r.hid} | {r.n} | {r.n_nonzero} | {r.n_events} | {_f(r.slope, 4)} | {corr} | "
            f"{_p(r.p_hac)} | {rob} | {_p(r.q)} | {echo} | {status} |"
        )
    lines += ["", "## Hypotheses", ""]
    for r in results:
        s = R2_SPECS[r.hid]
        lines.append(
            f"- **{r.hid}**: {s.signal} → {s.target} ({s.horizon}); expected sign "
            f"{'+' if s.expected_sign > 0 else '−'}."
            + (f" Notes: {'; '.join(r.notes)}." if r.notes else "")
        )
    lines += ["", f"Extra counts: {json.dumps(extra)}.", ""]
    surv = [r.hid for r in results if r.survives]
    lines.append(f"Survivors: {', '.join(surv) if surv else 'none'}.")
    return "\n".join(lines) + "\n"


def run_exploration2(cfg: Config) -> Path:  # pragma: no cover - reads local data
    ecfg, r2cfg, _ = _cfgs(cfg)
    p = paths(cfg)
    results, extra = explore2(load_round1(cfg), ecfg, r2cfg, cfg.project.seed)
    p["dir"].mkdir(parents=True, exist_ok=True)
    payload = {
        "label": LABEL,
        "generated": datetime.now(UTC).isoformat(),
        "results": [r.as_dict() for r in results],
        "extra": extra,
        "survivors": [r.hid for r in ranked_survivors(results, ecfg.max_confirm)],
    }
    p["explore_json"].write_text(json.dumps(_clean(payload), indent=2, default=str))
    p["explore_md"].write_text(render_exploration2(results, extra))
    return p["explore_md"]


def run_replicate(cfg: Config) -> Path:  # pragma: no cover - reads local data
    ecfg, _, _ = _cfgs(cfg)
    p = paths(cfg)
    if p["replication_json"].exists():
        raise FileExistsError(f"{p['replication_json']} exists; the replication is one shot")
    r1 = json.loads(p["round1_json"].read_text())
    h01_res = next(r for r in r1["results"] if r["hid"] == "H01")
    out = replicate_h01(load_round1(cfg), h01_res, ecfg)
    out["generated"] = datetime.now(UTC).isoformat()
    p["replication_json"].write_text(json.dumps(_clean(out), indent=2, default=str))
    return p["replication_json"]


# ---------------------------------------------------------------------------
# One-shot confirmation of the frozen survivors (future data)
# ---------------------------------------------------------------------------
N_SURVIVORS = 2  # R2-03 and R2-04; each p is multiplied by 2 (Bonferroni, D46)
AWS_CONFIRM = (pd.Timestamp("2026-10-01"), pd.Timestamp("2026-12-31"))


def cgi_window_complete(r2cfg: Round2Config, now: pd.Timestamp) -> bool:
    end = pd.Timestamp(r2cfg.cgi_confirm[1])
    return bool(now >= end + pd.Timedelta(hours=6, minutes=10))


def confirm_cgi(
    values: pd.DataFrame, frozen: dict[str, Any], ecfg: ExplorationConfig, r2cfg: Round2Config
) -> dict[str, Any]:
    """R2-03 on point-in-time CGI B200 values inside the round-2 window only."""
    a, b = (pd.Timestamp(x) for x in r2cfg.cgi_confirm)
    inside = values.loc[(values["as_of"] >= a) & (values["as_of"] <= b)]
    data = Round1Data(
        listings=pd.DataFrame(),
        cgi=inside,
        gd=pd.DataFrame(),
        aws=pd.DataFrame(),
        bars=pd.DataFrame(),
    )
    built = cgi_reversal(data, "B200", ecfg.cgi_max_age_minutes)
    row = confirm_one(built, frozen, ecfg, spec=R2_SPECS["R2-03"])
    row.p_holm = min(1.0, row.p_one_sided * N_SURVIVORS) if np.isfinite(row.p_one_sided) else 1.0
    row.c1 = bool(row.p_holm <= ecfg.confirm_alpha)
    row.confirmed = row.c1 and row.c2
    row.verdict = "confirmed: candidate" if row.confirmed else "not confirmed"
    out = asdict(row)
    out["window"] = (
        [str(built.frame["t"].min()), str(built.frame["t"].max())] if len(built.frame) else []
    )
    return out


def aws_window_complete(aws: pd.DataFrame) -> bool:
    return bool(len(aws)) and pd.Timestamp(max(aws["day"])) >= AWS_CONFIRM[1]


def confirm_aws(aws: pd.DataFrame, ecfg: ExplorationConfig, r2cfg: Round2Config) -> dict[str, Any]:
    """R2-04: the frozen walk-forward procedure; forecasts whose outcome ends in Oct to Dec."""
    data = Round1Data(
        listings=pd.DataFrame(), cgi=pd.DataFrame(), gd=pd.DataFrame(), aws=aws, bars=pd.DataFrame()
    )
    fc = walk_forward(r2_04(data, ecfg).frame, pd.Timedelta(days=7), r2cfg.min_train)
    t = pd.to_datetime(fc["t"])
    sel = fc.loc[(t >= AWS_CONFIRM[0]) & (t + pd.Timedelta(days=7) <= AWS_CONFIRM[1])]
    y, f = sel["y"].to_numpy(float), sel["forecast"].to_numpy(float)
    cw = cs.clark_west(y, f, np.zeros_like(y), 7) if len(sel) else None
    p = cw.p_value if cw is not None else float("nan")
    p_adj = min(1.0, p * N_SURVIVORS) if np.isfinite(p) else 1.0
    r2z = oos_r2(y, f, np.zeros_like(y)) if len(sel) else float("nan")
    r2m = oos_r2(y, f, sel["mean"].to_numpy(float)) if len(sel) else float("nan")
    c1 = bool(p_adj <= ecfg.confirm_alpha)
    c2 = bool(np.isfinite(r2z) and np.isfinite(r2m) and r2z > 0 and r2m > 0)
    return {
        "hid": "R2-04",
        "n": len(sel),
        "clark_west_p": p,
        "p_adjusted": p_adj,
        "oos_r2_zero": r2z,
        "oos_r2_mean": r2m,
        "c1": c1,
        "c2": c2,
        "confirmed": c1 and c2,
        "verdict": "confirmed: candidate" if c1 and c2 else "not confirmed",
    }


def run_confirmation2(cfg: Config, now: pd.Timestamp | None = None) -> Path:  # pragma: no cover
    """Each survivor once, only when its future data window is complete."""
    from compute_curve.claim5.pipeline import paths as c5paths  # noqa: PLC0415
    from compute_curve.claim5.pipeline import read_pool_daily  # noqa: PLC0415
    from compute_curve.explore import forward as fw  # noqa: PLC0415
    from compute_curve.explore.pipeline import _cgi_vintages  # noqa: PLC0415

    ecfg, r2cfg, _ = _cfgs(cfg)
    p = paths(cfg)
    now = now or pd.Timestamp.now(tz="UTC")
    frozen = {f["hid"]: f for f in json.loads(p["frozen"].read_text())["frozen"]}
    lines = [
        "# Exploration round 2: confirmation status",
        "",
        f"Checked {now:%Y-%m-%d %H:%M} UTC.",
        "",
    ]
    for hid in ("R2-03", "R2-04"):
        out_path = p["dir"] / f"round2_confirmation_{hid}.json"
        if out_path.exists():
            res = json.loads(out_path.read_text())
            lines.append(f"- {hid}: done earlier; {res['verdict']}.")
            continue
        if hid == "R2-03":
            if not cgi_window_complete(r2cfg, now):
                lines.append(f"- R2-03: waiting for CGI data to {r2cfg.cgi_confirm[1]:%Y-%m-%d}.")
                continue
            fwd_lag = (
                cfg.exploration.forward["H05"].max_publish_lag_minutes if cfg.exploration else 15
            )
            values, counts = fw.point_in_time(_cgi_vintages(cfg), "B200", fwd_lag)
            res = confirm_cgi(values, frozen["R2-03"], ecfg, r2cfg)
            res["point_in_time"] = counts
        else:
            aws = read_pool_daily(c5paths(cfg)["pool_daily"])
            if not aws_window_complete(aws):
                lines.append(
                    "- R2-04: waiting for the AWS 2026-12 month (add it to [claim5].months)."
                )
                continue
            res = confirm_aws(aws, ecfg, r2cfg)
        res["generated"] = now.isoformat()
        out_path.write_text(json.dumps(_clean(res), indent=2, default=str))
        lines.append(f"- {hid}: {res['verdict']}.")
    out = p["dir"] / "round2_confirmation.md"
    out.write_text("\n".join(lines) + "\n")
    return out
