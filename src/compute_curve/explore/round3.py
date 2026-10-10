"""Exploration round 3: what drives the CGI reversal (docs/exploration_round3_plan.md).

Four channels of the past 6-hour CGI move are tested once each on future
CGI data, with Holm across the four. The model is
``y = a + b * past + c * x``; ``c`` is tested by Frisch-Waugh-Lovell with
Newey-West errors. The exploration window only freezes coefficients for C2,
and every statistic on it is labelled exploratory and contaminated (D49).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import scipy.stats as st

from compute_curve.claim4 import stats as cs
from compute_curve.config import Config, ExplorationConfig, Round3Config
from compute_curve.explore.hypotheses import EPS, Spec
from compute_curve.explore.round2 import oos_r2, residualize

LABEL = "EXPLORATORY (contaminated: the window was looked at before the plan)"
STEPS = 24  # 15-minute stamps in 6 hours
HORIZON = pd.Timedelta(hours=6)
BAND_KEY = "stability_band_usd_gpu_hr"


@dataclass(frozen=True)
class R3:
    spec: Spec
    gpu: str
    channel: str  # "np", "jump" or "edge"


def _spec(hid: str, gpu: str, signal: str, sign: int) -> Spec:
    return Spec(
        hid, "ts", "C", signal, f"CGI {gpu} next 6-hour change", "6 hours", 12, 12, 12, sign, False
    )


R3_TESTS: dict[str, R3] = {
    t.spec.hid: t
    for t in (
        R3(_spec("R3-01", "H100", "past 6h move made at n_passing changes", -1), "H100", "np"),
        R3(_spec("R3-02", "H100", "past 6h move in 15-min jumps >= threshold", -1), "H100", "jump"),
        R3(_spec("R3-03", "B200", "past 6h move in 15-min jumps >= threshold", -1), "B200", "jump"),
        R3(_spec("R3-04", "H100", "6h change of the lower band edge", 1), "H100", "edge"),
    )
}


# ---------------------------------------------------------------------------
# Data: point-in-time 15-minute grid
# ---------------------------------------------------------------------------
def point_in_time_full(rows: pd.DataFrame, gpu: str, max_lag_minutes: int) -> pd.DataFrame:
    """First-observed vintage per stamp, published within ``max_lag``; keeps n, version, band."""
    cols = ["as_of", "value", "n_providers", "methodology_id", "band"]
    r = rows.loc[rows["gpu_model"] == gpu].copy()
    if r.empty:
        return pd.DataFrame(columns=cols)
    r["as_of"] = pd.to_datetime(r["as_of"], utc=True)
    r["ts_observed"] = pd.to_datetime(r["ts_observed"], utc=True)
    first = r.sort_values(["as_of", "ts_observed"]).drop_duplicates("as_of", keep="first")
    meta = first["raw_json"].map(lambda s: json.loads(s) if s else {})
    gen = pd.to_datetime(meta.map(lambda m: m.get("generated_at")), utc=True)
    lag = gen - first["as_of"]
    first = first.assign(band=meta.map(lambda m: m.get(BAND_KEY)).astype(float))
    ok = lag.notna() & (lag <= pd.Timedelta(minutes=max_lag_minutes))
    return first.loc[ok, cols].reset_index(drop=True)


def within(pit: pd.DataFrame, window: tuple[Any, Any]) -> pd.DataFrame:
    """Truncate to the window *before* anything is computed."""
    a, b = (pd.Timestamp(x) for x in window)
    return pit.loc[(pit["as_of"] >= a) & (pit["as_of"] <= b)].reset_index(drop=True)


def grid15(pit: pd.DataFrame) -> pd.DataFrame:
    """Values on the full 15-minute grid (missing stamps are NaN)."""
    if pit.empty:
        return pd.DataFrame(columns=["v", "n", "mid", "edge"])
    p = pit.set_index("as_of").sort_index()
    idx = pd.date_range(p.index.min(), p.index.max(), freq="15min")
    p = p.reindex(idx)
    lower = p["value"] - p["band"]
    return pd.DataFrame(
        {
            "v": np.log(p["value"].astype(float)),
            "n": p["n_providers"].astype(float),
            "mid": p["methodology_id"],
            "edge": np.log(lower.where(lower > 0)),
        },
        index=idx,
    )


def channels(g: pd.DataFrame, threshold: float) -> pd.DataFrame:
    """Hourly decision points with ``y``, ``past`` and the three channels (plan section 3)."""
    out_cols = ["t", "y", "past", "x_np", "x_jump", "x_edge", "f_np", "f_jump", "f_edge"]
    if len(g) <= 2 * STEPS:
        return pd.DataFrame(columns=out_cols)
    v, n = g["v"], g["n"]
    r = v.diff()
    np_flag = (n != n.shift()).astype(float).where(n.notna() & n.shift().notna())
    jump_flag = (r.abs() >= threshold).astype(float).where(r.notna())
    edge_step = g["edge"].diff()

    def rsum(s: pd.Series) -> pd.Series:
        return s.rolling(STEPS, min_periods=STEPS).sum()

    codes = pd.Series(pd.factorize(g["mid"].fillna("?"))[0], index=g.index, dtype=float)
    codes = codes.where(g["mid"].notna())
    full = 2 * STEPS + 1
    present = v.notna().astype(float).rolling(full).sum().shift(-STEPS) == full
    one_version = (codes.rolling(full).max() == codes.rolling(full).min()).shift(-STEPS) == 1
    frame = pd.DataFrame(
        {
            "t": g.index,
            "y": v.shift(-STEPS) - v,
            "past": v - v.shift(STEPS),
            "x_np": rsum(r * np_flag),
            "x_jump": rsum(r * jump_flag),
            "x_edge": g["edge"] - g["edge"].shift(STEPS),
            "f_np": np_flag,
            "f_jump": jump_flag,
            "f_edge": (edge_step.abs() > EPS).astype(float).where(edge_step.notna()),
        },
        index=g.index,
    )
    keep = present.fillna(False) & one_version.fillna(False) & (g.index.minute == 0)
    return frame.loc[keep, out_cols].reset_index(drop=True)


def model_frame(ch: pd.DataFrame, channel: str) -> pd.DataFrame:
    """``t, x, y, ctrl`` for one channel; rows missing the channel are dropped."""
    f = ch.rename(columns={f"x_{channel}": "x", "past": "ctrl"})[["t", "x", "y", "ctrl"]]
    return f.dropna().reset_index(drop=True)


def n_events(ch: pd.DataFrame, g: pd.DataFrame, channel: str, threshold: float) -> int:
    """Distinct 15-minute stamps where the channel fired, inside the frame's span."""
    if ch.empty:
        return 0
    lo, hi = ch["t"].min() - HORIZON, ch["t"].max()
    s = g.loc[(g.index > lo) & (g.index <= hi)]
    if channel == "np":
        flag = (s["n"] != s["n"].shift()) & s["n"].notna() & s["n"].shift().notna()
    elif channel == "jump":
        flag = s["v"].diff().abs() >= threshold
    else:
        flag = s["edge"].diff().abs() > EPS
    return int(flag.sum())


def channel_windows(frame: pd.DataFrame) -> int:
    """Non-overlapping 6-hour windows (decision hours 0, 6, 12, 18 UTC) with a non-zero channel."""
    t = pd.to_datetime(frame["t"])
    return int(((t.dt.hour % 6 == 0) & (frame["x"].abs() > EPS)).sum())


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
@dataclass
class R3Result:
    hid: str
    gpu: str
    channel: str
    n: int = 0
    n_events: int = 0
    n_channel_windows: int = 0
    c: float = float("nan")
    c_se: float = float("nan")
    t_stat: float = float("nan")
    p_one_sided: float = float("nan")
    p_perm: float = float("nan")
    ci_lo: float = float("nan")
    ci_hi: float = float("nan")
    b_past_only: float = float("nan")
    sufficient: bool = False
    p_holm: float = float("nan")
    oos_r2_vs_past: float = float("nan")
    oos_r2_vs_zero: float = float("nan")
    c1: bool = False
    c2: bool = False
    confirmed: bool = False
    verdict: str = ""
    notes: list[str] = field(default_factory=list)


def fit_models(frame: pd.DataFrame) -> dict[str, float]:
    """OLS coefficients of the two-regressor and the past-only model (frozen for C2)."""
    y = frame["y"].to_numpy(float)
    one = np.ones(len(frame))
    z2 = np.column_stack([one, frame["ctrl"].to_numpy(float), frame["x"].to_numpy(float)])
    z1 = z2[:, :2]
    (a, b, c), *_ = np.linalg.lstsq(z2, y, rcond=None)
    (a1, b1), *_ = np.linalg.lstsq(z1, y, rcond=None)
    return {"a": float(a), "b": float(b), "c": float(c), "a1": float(a1), "b1": float(b1)}


def test_channel(
    frame: pd.DataFrame,
    test: R3,
    ecfg: ExplorationConfig,
    r3cfg: Round3Config,
    events: int,
    seed: int,
) -> R3Result:
    """One-sided HAC test of ``c`` (FWL), circular shift and block-bootstrap CI."""
    res = R3Result(test.spec.hid, test.gpu, test.channel)
    res.n, res.n_events = len(frame), events
    res.n_channel_windows = channel_windows(frame) if len(frame) else 0
    if len(frame) >= 3:
        res.b_past_only = fit_models(frame)["b1"]
    d = residualize(frame)
    x, y = d["x"].to_numpy(float), d["y"].to_numpy(float)
    varies = len(frame) > 0 and np.ptp(frame["x"].to_numpy(float)) > EPS and np.ptp(x) > EPS
    fit = cs.ols_hac(x, y, test.spec.lag) if varies else None
    if fit is None:
        res.notes.append("too few observations or no variation in the channel")
        return res
    res.c, res.c_se, res.t_stat = fit.slope, fit.slope_se, fit.t_stat
    res.p_one_sided = float(st.t.sf(test.spec.expected_sign * fit.t_stat, df=x.size - 2))
    res.p_perm, _ = cs.circular_shift_pvalue(x, y, min_shift=test.spec.min_shift)
    res.ci_lo, res.ci_hi = cs.block_bootstrap_corr_ci(
        x, y, block_length=test.spec.block, n_boot=ecfg.n_boot, seed=seed
    )
    nonzero = int(np.sum(np.abs(frame["x"].to_numpy(float)) > EPS))
    res.sufficient = bool(
        res.n >= r3cfg.min_points
        and res.n_channel_windows >= r3cfg.min_channel_windows
        and nonzero >= ecfg.min_nonzero
        and res.n_events >= ecfg.min_events
    )
    if not res.sufficient:
        res.notes.append(
            f"insufficient: n {res.n} (need {r3cfg.min_points}), channel windows "
            f"{res.n_channel_windows} (need {r3cfg.min_channel_windows}), non-zero {nonzero}, "
            f"events {res.n_events}"
        )
    return res


def build_all(
    rows: pd.DataFrame, window: tuple[Any, Any], threshold: float, max_lag: int
) -> dict[str, tuple[pd.DataFrame, int]]:
    """Model frame and event count for each round-3 test, inside ``window`` only."""
    out: dict[str, tuple[pd.DataFrame, int]] = {}
    grids: dict[str, pd.DataFrame] = {}
    for hid, t in R3_TESTS.items():
        if t.gpu not in grids:
            grids[t.gpu] = grid15(within(point_in_time_full(rows, t.gpu, max_lag), window))
        g = grids[t.gpu]
        ch = channels(g, threshold)
        out[hid] = (model_frame(ch, t.channel), n_events(ch, g, t.channel, threshold))
    return out


def explore3(
    rows: pd.DataFrame, ecfg: ExplorationConfig, r3cfg: Round3Config, max_lag: int, seed: int
) -> tuple[list[R3Result], dict[str, dict[str, float]], dict[str, Any]]:
    """Exploration window: contaminated statistics, frozen coefficients, descriptive thresholds."""
    built = build_all(rows, r3cfg.explore, r3cfg.jump_threshold, max_lag)
    results, frozen = [], {}
    for hid, (frame, events) in built.items():
        results.append(test_channel(frame, R3_TESTS[hid], ecfg, r3cfg, events, seed))
        if len(frame) >= 3:
            frozen[hid] = fit_models(frame) | {"n_explore": float(len(frame))}
    desc: dict[str, Any] = {}
    for thr in r3cfg.descriptive_thresholds:
        alt = build_all(rows, r3cfg.explore, thr, max_lag)
        for hid in ("R3-02", "R3-03"):
            frame, events = alt[hid]
            r = test_channel(frame, R3_TESTS[hid], ecfg, r3cfg, events, seed)
            desc[f"{hid}@{thr:g}"] = {"n": r.n, "c": r.c, "t": r.t_stat, "events": events}
    return results, frozen, desc


def confirm3(
    rows: pd.DataFrame,
    frozen: dict[str, dict[str, float]],
    ecfg: ExplorationConfig,
    r3cfg: Round3Config,
    max_lag: int,
    seed: int,
) -> list[R3Result]:
    """Each test once on the confirmation window: C1 (Holm over 4) and C2 (frozen models)."""
    built = build_all(rows, r3cfg.confirm, r3cfg.jump_threshold, max_lag)
    results = []
    for hid, (frame, events) in built.items():
        r = test_channel(frame, R3_TESTS[hid], ecfg, r3cfg, events, seed)
        fz = frozen.get(hid)
        if fz is not None and len(frame):
            y = frame["y"].to_numpy(float)
            past, x = frame["ctrl"].to_numpy(float), frame["x"].to_numpy(float)
            pred2 = fz["a"] + fz["b"] * past + fz["c"] * x
            pred1 = fz["a1"] + fz["b1"] * past
            r.oos_r2_vs_past = oos_r2(y, pred2, pred1)
            r.oos_r2_vs_zero = oos_r2(y, pred2, np.zeros_like(y))
        else:
            r.notes.append("no frozen coefficients")
        r.c2 = bool(
            np.isfinite(r.oos_r2_vs_past)
            and np.isfinite(r.oos_r2_vs_zero)
            and r.oos_r2_vs_past > 0
            and r.oos_r2_vs_zero > 0
        )
        results.append(r)
    pvals = [r.p_one_sided if r.sufficient and np.isfinite(r.p_one_sided) else 1.0 for r in results]
    for r, pa in zip(results, cs.holm(pvals), strict=True):
        r.p_holm = float(pa)
        r.c1 = bool(r.sufficient and pa <= ecfg.confirm_alpha)
        r.confirmed = r.c1 and r.c2
        r.verdict = "confirmed" if r.confirmed else "not confirmed"
    return results


def confirm_window_complete(r3cfg: Round3Config, now: pd.Timestamp) -> bool:
    return bool(now >= pd.Timestamp(r3cfg.confirm[1]) + HORIZON + pd.Timedelta(minutes=10))


# ---------------------------------------------------------------------------
# Reports and entry points
# ---------------------------------------------------------------------------
def paths(cfg: Config) -> dict[str, Path]:
    d = cfg.path("reports") / "exploration"
    d.mkdir(parents=True, exist_ok=True)
    return {
        "dir": d,
        "exploration": d / "round3_exploration.json",
        "exploration_md": d / "round3_exploration.md",
        "frozen": d / "round3_frozen.json",
        "confirmation": d / "round3_confirmation.json",
        "confirmation_md": d / "round3_confirmation.md",
    }


def _clean(v: Any) -> Any:
    if isinstance(v, float) and not np.isfinite(v):
        return None
    if isinstance(v, dict):
        return {k: _clean(x) for k, x in v.items()}
    if isinstance(v, list):
        return [_clean(x) for x in v]
    return v


def _f(v: float, nd: int = 3) -> str:
    return "n/a" if not np.isfinite(v) else f"{v:.{nd}f}"


def render_exploration3(results: list[R3Result], desc: dict[str, Any], thr: float) -> str:
    lines = [
        "# Exploration round 3: exploration window",
        "",
        f"**{LABEL}.** These numbers count for nothing; every test is decided once",
        "on future CGI data (docs/exploration_round3_plan.md, D49). They are shown",
        "because the frozen coefficients for C2 come from this window.",
        "",
        f"Jump threshold {thr:g} (log). One-sided p in the pre-registered direction;",
        "c is the slope on the channel net of the past 6-hour move (Frisch-Waugh-Lovell,",
        "Newey-West lag 12). CI is the block-bootstrap 95% CI of corr(x, y) after FWL.",
        "",
        "| ID | GPU | channel | n | events | channel windows | c | t | p (one-sided) "
        "| circular-shift p | corr CI | past-only slope |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        lines.append(
            f"| {r.hid} | {r.gpu} | {r.channel} | {r.n} | {r.n_events} | {r.n_channel_windows} "
            f"| {_f(r.c)} | {_f(r.t_stat, 2)} | {_f(r.p_one_sided)} | {_f(r.p_perm)} "
            f"| [{_f(r.ci_lo, 2)}, {_f(r.ci_hi, 2)}] | {_f(r.b_past_only)} |"
        )
    lines += ["", "Descriptive jump thresholds (not tested):", ""]
    for k, d in desc.items():
        lines.append(f"- {k}: n {d['n']}, c {_f(d['c'])}, t {_f(d['t'], 2)}, events {d['events']}")
    return "\n".join(lines) + "\n"


def _rows_and_lag(cfg: Config) -> tuple[pd.DataFrame, int]:  # pragma: no cover - local data
    from compute_curve.explore.pipeline import _cgi_vintages  # noqa: PLC0415

    lag = cfg.exploration.forward["H05"].max_publish_lag_minutes if cfg.exploration else 15
    return _cgi_vintages(cfg), lag


def _cfgs(cfg: Config) -> tuple[ExplorationConfig, Round3Config]:
    if cfg.exploration is None or cfg.exploration3 is None:
        raise RuntimeError("[exploration] and [exploration3] config are required")
    return cfg.exploration, cfg.exploration3


def run_exploration3(cfg: Config) -> Path:  # pragma: no cover - reads local data
    ecfg, r3cfg = _cfgs(cfg)
    p = paths(cfg)
    if p["frozen"].exists():
        raise RuntimeError(f"{p['frozen']} exists; round-3 coefficients are frozen once")
    rows, lag = _rows_and_lag(cfg)
    results, frozen, desc = explore3(rows, ecfg, r3cfg, lag, cfg.project.seed)
    p["exploration"].write_text(
        json.dumps(
            _clean({"label": LABEL, "results": [asdict(r) for r in results], "descriptive": desc}),
            indent=2,
            default=str,
        )
    )
    p["frozen"].write_text(json.dumps(_clean({"frozen": frozen}), indent=2))
    p["exploration_md"].write_text(render_exploration3(results, desc, r3cfg.jump_threshold))
    return p["exploration_md"]


def run_confirmation3(
    cfg: Config, now: pd.Timestamp | None = None
) -> Path:  # pragma: no cover - reads local data
    """Once the window is complete: the one-shot confirmation. Before: data counts only."""
    ecfg, r3cfg = _cfgs(cfg)
    p = paths(cfg)
    now = now or pd.Timestamp.now(tz="UTC")
    lines = ["# Exploration round 3: confirmation status", "", f"Checked {now:%Y-%m-%d %H:%M} UTC."]
    if p["confirmation"].exists():
        lines.append("\nDone earlier; see round3_confirmation.json.")
    elif not confirm_window_complete(r3cfg, now):
        rows, lag = _rows_and_lag(cfg)
        lines.append(f"\nWaiting for CGI data to {r3cfg.confirm[1]:%Y-%m-%d %H:%M} UTC.")
        lines.append("No statistic is computed on the window before then. Stamps so far:")
        for gpu in ("H100", "B200"):
            n = len(within(point_in_time_full(rows, gpu, lag), r3cfg.confirm))
            lines.append(f"- {gpu}: {n} point-in-time 15-minute stamps")
    else:
        rows, lag = _rows_and_lag(cfg)
        frozen = json.loads(p["frozen"].read_text())["frozen"]
        results = confirm3(rows, frozen, ecfg, r3cfg, lag, cfg.project.seed)
        p["confirmation"].write_text(
            json.dumps(
                _clean({"generated": now.isoformat(), "results": [asdict(r) for r in results]}),
                indent=2,
                default=str,
            )
        )
        lines.append("")
        lines += [f"- {r.hid}: {r.verdict} (p Holm {_f(r.p_holm)})" for r in results]
    p["confirmation_md"].write_text("\n".join(lines) + "\n")
    return p["confirmation_md"]
