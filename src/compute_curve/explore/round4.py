"""Exploration round 4: forward one-shot replication of H01 (docs/exploration_round4_plan.md).

H01's frozen round-1 specification runs once on listing days 2026-10-07 to
2026-12-31, which no test has used. Listings are truncated to the window
before anything is computed, so every 5-day outcome lies inside it.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, replace
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import scipy.stats as st

from compute_curve.claim4 import stats as cs
from compute_curve.config import Config, ExplorationConfig, Round4Config
from compute_curve.explore.data import Round1Data
from compute_curve.explore.hypotheses import h01
from compute_curve.explore.run import confirm_one, finish_confirmation

HID = "R4-01"


def in_window(listings: pd.DataFrame, window: tuple[date, date]) -> pd.DataFrame:
    d = pd.to_datetime(listings["as_of_date"]).dt.date
    return listings.loc[(d >= window[0]) & (d <= window[1])].reset_index(drop=True)


def window_complete(r4: Round4Config, today: date) -> bool:
    return today > r4.h01_forward[1]


def confirm_forward(
    data: Round1Data, frozen: dict[str, Any], ecfg: ExplorationConfig, r4: Round4Config
) -> dict[str, Any]:
    """H01 (frozen) on the forward window only: C1 one-sided, C2 out-of-sample R2."""
    fwd = replace(data, listings=in_window(data.listings, r4.h01_forward))
    built = h01(fwd, ecfg)
    row = finish_confirmation([confirm_one(built, frozen, ecfg)], ecfg)[0]
    out = asdict(row) | {"hid": HID, "replicates": "H01", "frozen": frozen}
    days = pd.to_datetime(built.frame["t"]) if not built.frame.empty else pd.Series(dtype=object)
    out["window"] = [str(days.min().date()), str(days.max().date())] if len(days) else []
    return out


def _clean(v: Any) -> Any:
    if isinstance(v, float) and math.isnan(v):
        return None
    if isinstance(v, dict):
        return {k: _clean(x) for k, x in v.items()}
    if isinstance(v, list):
        return [_clean(x) for x in v]
    return v


def run_confirmation4(cfg: Config, today: date | None = None) -> Path:  # pragma: no cover
    """Count days until the window closes; then run R4-01 once."""
    from compute_curve.explore.data import load_index_inputs  # noqa: PLC0415
    from compute_curve.timeutil import utc_now  # noqa: PLC0415

    ecfg, r4 = cfg.exploration, cfg.exploration4
    if ecfg is None or r4 is None:
        raise RuntimeError("[exploration] and [exploration4] config are required")
    d = cfg.path("reports") / "exploration"
    out_json, out_md = d / "round4_confirmation.json", d / "round4_confirmation.md"
    today = today or utc_now().date()
    lines = ["# Exploration round 4: R4-01 status", "", f"Checked {today} (UTC)."]
    if out_json.exists():
        lines.append("\nDone earlier; see round4_confirmation.json.")
    else:
        data = load_index_inputs(cfg)
        win = in_window(data.listings, r4.h01_forward)
        n_days = win["as_of_date"].nunique() if len(win) else 0
        if not window_complete(r4, today):
            lines += [
                "",
                f"Waiting for listings to {r4.h01_forward[1]} (runs from "
                f"{r4.h01_forward[1] + timedelta(days=1)}). No statistic is computed before then.",
                f"Listing days collected in the window so far: {n_days}.",
            ]
        else:
            rep = json.loads((d / "round2_replication.json").read_text())
            res = confirm_forward(data, rep["frozen"], ecfg, r4)
            res["generated"] = str(today)
            out_json.write_text(json.dumps(_clean(res), indent=2, default=str))
            lines += ["", f"- {HID} (H01 forward): {res['verdict']}, p {res['p_one_sided']:.3f}."]
    out_md.write_text("\n".join(lines) + "\n")
    return out_md


# ---------------------------------------------------------------------------
# R4-02: AWS H100 spot scarcity -> neocloud H100 prices (plan section 3)
# ---------------------------------------------------------------------------
H = 7
R402_EXPLORE = (date(2026, 7, 1), date(2026, 9, 30))
R402_CONFIRM = (date(2026, 10, 1), date(2026, 12, 24))
R402_TARGETS = ("cgi", "own_panel")


def log_series(values: pd.Series) -> pd.Series:
    """Daily log level indexed by date (exact dates only, nothing filled in)."""
    s = values.dropna()
    s = s[s > 0]
    out = pd.Series(np.log(s.to_numpy(float)), index=pd.to_datetime(s.index).date)
    return out[~out.index.duplicated(keep="last")].sort_index()


def lead_lag_pairs(x_log: pd.Series, y_log: pd.Series, window: tuple[date, date]) -> pd.DataFrame:
    """x = 7-day past change of the signal, y = next 7-day change of the target, t in window.

    Both series are truncated to [window start - 7 days, window end + 7 days]
    before anything is computed.
    """
    lo, hi = window[0] - timedelta(days=H), window[1] + timedelta(days=H)
    xs = x_log[(x_log.index >= lo) & (x_log.index <= hi)]
    ys = y_log[(y_log.index >= lo) & (y_log.index <= hi)]
    rows = []
    t = window[0]
    while t <= window[1]:
        b, f = t - timedelta(days=H), t + timedelta(days=H)
        if t in xs.index and b in xs.index and t in ys.index and f in ys.index:
            rows.append({"t": t, "x": xs[t] - xs[b], "y": ys[f] - ys[t]})
        t += timedelta(days=1)
    return pd.DataFrame(rows, columns=["t", "x", "y"])


def fit_r402(frame: pd.DataFrame) -> dict[str, Any]:
    """One-sided (b > 0) Newey-West test, lag 7, plus the OLS coefficients."""
    out: dict[str, Any] = {"n": len(frame), "n_nonzero_y": int((frame["y"].abs() > 1e-12).sum())}
    fit = (
        cs.ols_hac(frame["x"].to_numpy(float), frame["y"].to_numpy(float), H)
        if len(frame)
        else None
    )
    if fit is None:
        out.update(a=float("nan"), b=float("nan"), t=float("nan"), p_one_sided=float("nan"))
        return out
    p = float(st.t.sf(fit.t_stat, df=len(frame) - 2))
    out.update(a=fit.intercept, b=fit.slope, se=fit.slope_se, t=fit.t_stat, p_one_sided=p)
    return out


def confirm_r402(
    frames: dict[str, pd.DataFrame], frozen: dict[str, dict[str, Any]], alpha: float
) -> list[dict[str, Any]]:
    rows = []
    for name, frame in frames.items():
        r = fit_r402(frame) | {"target": name}
        fz = frozen.get(name, {})
        if len(frame) and np.isfinite(fz.get("a", np.nan)):
            y = frame["y"].to_numpy(float)
            pred = fz["a"] + fz["b"] * frame["x"].to_numpy(float)
            den = float(np.sum(y**2))
            r["oos_r2_zero"] = float(1 - np.sum((y - pred) ** 2) / den) if den > 0 else float("nan")
        else:
            r["oos_r2_zero"] = float("nan")
        rows.append(r)
    ps = [r["p_one_sided"] if np.isfinite(r["p_one_sided"]) else 1.0 for r in rows]
    for r, pa in zip(rows, cs.holm(ps), strict=True):
        r["p_holm"] = float(pa)
        r["c1"] = bool(pa <= alpha)
        r["c2"] = bool(np.isfinite(r["oos_r2_zero"]) and r["oos_r2_zero"] > 0)
        r["confirmed"] = r["c1"] and r["c2"]
        r["verdict"] = "confirmed" if r["confirmed"] else "not confirmed"
    return rows


def r402_inputs(cfg: Config) -> dict[str, pd.Series]:  # pragma: no cover - reads local data
    from compute_curve.explore.data import load_index_inputs  # noqa: PLC0415
    from compute_curve.fairvalue import daily_log_close  # noqa: PLC0415

    aws = pd.read_csv(cfg.path("reports") / "claim5" / "aws_spot_daily.csv")
    aws = aws.loc[aws["gpu"] == "H100"].set_index("day")["median_usd_per_gpu_hour"]
    own = pd.read_csv(cfg.path("reports") / "own_index.csv")
    own = own.loc[(own["series"] == "history_panel") & (own["gpu_model"] == "H100")]
    cgi = daily_log_close(load_index_inputs(cfg).cgi, "H100")
    return {
        "aws": log_series(aws),
        "cgi": pd.Series(cgi.to_numpy(float), index=list(cgi.index)).sort_index(),
        "own_panel": log_series(own.set_index("as_of_date")["value"]),
    }


def run_r402(cfg: Config) -> Path:  # pragma: no cover - reads local data
    """Exploration fits (once, frozen) and the one-shot confirmation when AWS 2026-12 exists."""
    ecfg = cfg.exploration
    if ecfg is None:
        raise RuntimeError("[exploration] config is required")
    d = cfg.path("reports") / "exploration"
    frozen_p, conf_p, md = (
        d / "round4_r402_frozen.json",
        d / "round4_r402_confirmation.json",
        d / "round4_r402.md",
    )
    s = r402_inputs(cfg)
    lines = ["# R4-02: AWS H100 spot scarcity -> neocloud H100 prices", ""]
    if not frozen_p.exists():
        fits = {t: fit_r402(lead_lag_pairs(s["aws"], s[t], R402_EXPLORE)) for t in R402_TARGETS}
        frozen_p.write_text(json.dumps(_clean(fits), indent=2))
    fits = json.loads(frozen_p.read_text())
    lines += [
        "## Exploration, AWS 2026-07..09 (EXPLORATORY, descriptive; coefficients frozen)",
        "",
        "| Target | Pairs | Non-zero target changes | Slope b | t | One-sided p |",
        "|---|---|---|---|---|---|",
    ]
    for t in R402_TARGETS:
        f = fits[t]
        lines.append(
            f"| {t} | {f['n']} | {f['n_nonzero_y']} | {_fmt(f.get('b'))} | {_fmt(f.get('t'), 2)} "
            f"| {_fmt(f.get('p_one_sided'))} |"
        )
    aws_last = max(s["aws"].index) if len(s["aws"]) else None
    if conf_p.exists():
        lines += ["", "Confirmation done earlier; see round4_r402_confirmation.json."]
    elif aws_last is None or aws_last < date(2026, 12, 31):
        lines += ["", f"Confirmation waits for AWS data through 2026-12-31 (latest: {aws_last})."]
    else:
        frames = {t: lead_lag_pairs(s["aws"], s[t], R402_CONFIRM) for t in R402_TARGETS}
        rows = confirm_r402(frames, fits, ecfg.confirm_alpha)
        conf_p.write_text(json.dumps(_clean({"rows": rows}), indent=2, default=str))
        lines += [
            "",
            *[f"- {r['target']}: {r['verdict']} (p Holm {r['p_holm']:.3f})" for r in rows],
        ]
    md.write_text("\n".join(lines) + "\n")
    return md


def _fmt(v: Any, nd: int = 3) -> str:
    try:
        x = float(v)
    except (TypeError, ValueError):
        return "n/a"
    return "n/a" if math.isnan(x) else f"{x:.{nd}f}"
