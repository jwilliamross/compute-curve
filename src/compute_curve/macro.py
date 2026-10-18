"""Claim 11: do AI-economy signals lead GPU rental prices? (docs/macro_drivers_plan.md).

Research only, no orders. Target: the provider-equal mean 4-week log change of
GetDeploying H100 on-demand prices (round-7 panel). Predictors: 20-session excess
returns of equity baskets over SPY, and the 20-session change in the 2-year yield,
all taken at the last close on or before the Friday before each Monday.
"""

from __future__ import annotations

import io
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from compute_curve.explore.round6 import ols_slope_test
from compute_curve.explore.round7 import MIN_CS, _slope_ci, trim_start, weekly_panel
from compute_curve.statarb.power import holm

H = 4
WINDOW = 20
LAG = 6
LEADS = 8
GRANGER_LAG = 4
ALPHA = 0.05
MARKET = "SPY"
HYPERSCALERS = ["MSFT", "GOOGL", "AMZN", "META", "ORCL"]
BARS_START = date(2024, 6, 3)
LAST_FRIDAY = date(2026, 10, 9)  # the Friday before the panel's last Monday (2026-10-12)
FRED_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS2"
# NVIDIA quarterly results dates in the window, verified against NVIDIA/SEC releases
# (2026-10-18). Q3 FY25 (2024-11-20) and Q1 FY26 (2025-05-28) were not verified: dropped.
NVDA_EARNINGS = [
    date(2024, 8, 28),
    date(2025, 2, 26),
    date(2025, 8, 27),
    date(2025, 11, 19),
    date(2026, 2, 25),
    date(2026, 5, 20),
    date(2026, 8, 26),
]
TESTS = ("MD-1", "MD-2", "MD-3", "MD-4", "MD-5")
LABELS = {
    "MD-1": "AI-hardware basket excess return",
    "MD-2": "Neocloud basket excess return",
    "MD-3": "Hyperscaler basket excess return",
    "MD-4": "Change in the 2-year Treasury yield (pp)",
    "MD-5": "Power and capacity basket excess return",
}


# ---------------------------------------------------------------------------
# Target
# ---------------------------------------------------------------------------
def forward_change(panel: pd.DataFrame, h: int = H, min_cs: int = MIN_CS) -> pd.Series:
    """y(t): provider-equal mean of p(i, t+h) - p(i, t), at least ``min_cs`` providers."""
    fut = panel.shift(-h)
    both = panel.notna() & fut.notna()
    ch = (fut - panel).where(both)
    return ch.mean(axis=1).where(both.sum(axis=1) >= min_cs)


def weekly_change(panel: pd.DataFrame, min_cs: int = MIN_CS) -> pd.Series:
    """Provider-equal mean one-week log change (for the descriptive correlogram)."""
    both = panel.notna() & panel.shift(1).notna()
    return panel.diff().where(both).mean(axis=1).where(both.sum(axis=1) >= min_cs)


# ---------------------------------------------------------------------------
# Predictors
# ---------------------------------------------------------------------------
def basket_excess(
    closes: pd.DataFrame, names: list[str], market: str = MARKET, window: int = WINDOW
) -> pd.Series:
    """Equal-weight mean of the names' ``window``-session log returns minus the market's."""
    lr = np.log(closes).diff(window)
    cols = [n for n in names if n in lr.columns]
    basket = lr[cols].mean(axis=1, skipna=True)
    return (basket - lr[market]).where(lr[cols].notna().any(axis=1))


def level_change(series: pd.Series, window: int = WINDOW) -> pd.Series:
    return series.dropna().diff(window)


def asof_friday(daily: pd.Series, mondays: pd.DatetimeIndex) -> pd.Series:
    """Value at the last observation on or before the Friday before each Monday."""
    d = daily.dropna().sort_index()
    out = []
    for m in mondays:
        cut = pd.Timestamp(m) - pd.Timedelta(days=3)
        s = d.loc[:cut]
        out.append(float(s.iloc[-1]) if len(s) else np.nan)
    return pd.Series(out, index=mondays)


# ---------------------------------------------------------------------------
# Tests and descriptives
# ---------------------------------------------------------------------------
def md_test(x: pd.Series, y: pd.Series, seed: int) -> dict[str, Any]:
    """One-sided (+) HAC slope test of y on x, with a block-bootstrap slope CI."""
    j = pd.concat([x.rename("x"), y.rename("y")], axis=1).dropna()
    xs, ys = j["x"].to_numpy(float), j["y"].to_numpy(float)
    res = ols_slope_test(xs, ys, lag=LAG, sign=1)
    if "slope" in res:
        res["ci95"] = _slope_ci(xs, ys, seed)
    return res


def finish(tests: dict[str, dict[str, Any]]) -> None:
    ids = [k for k in TESTS if "p_one_sided" in tests[k]]
    adj = holm([tests[k]["p_one_sided"] for k in ids]) if ids else []
    for k, p in zip(ids, adj, strict=True):
        tests[k]["p_holm"] = float(p)
        ok = p <= ALPHA and tests[k]["slope"] > 0
        tests[k]["verdict"] = "confirmed" if ok else "not confirmed"


def correlogram(x: pd.Series, y: pd.Series, leads: int = LEADS) -> dict[int, float]:
    """corr(x(t), y(t+k)) for k in -leads..leads; k > 0 means x leads y."""
    out: dict[int, float] = {}
    for k in range(-leads, leads + 1):
        j = pd.concat([x, y.shift(-k)], axis=1).dropna()
        out[k] = float(j.corr().iloc[0, 1]) if len(j) > 10 else float("nan")
    return out


def granger(x: pd.Series, y: pd.Series, lag: int = GRANGER_LAG) -> dict[str, float]:
    """F-test p-values, x -> y and y -> x (predictive 'cause' only)."""
    from statsmodels.tsa.stattools import grangercausalitytests  # noqa: PLC0415

    j = pd.concat([y.rename("y"), x.rename("x")], axis=1).dropna()
    if len(j) < 5 * lag:
        return {"x_to_y": float("nan"), "y_to_x": float("nan"), "n": float(len(j))}
    a = grangercausalitytests(j[["y", "x"]].to_numpy(), [lag])
    b = grangercausalitytests(j[["x", "y"]].to_numpy(), [lag])
    return {
        "x_to_y": float(a[lag][0]["ssr_ftest"][1]),
        "y_to_x": float(b[lag][0]["ssr_ftest"][1]),
        "n": float(len(j)),
    }


def event_windows(y: pd.Series, events: list[date]) -> dict[str, Any]:
    """y at the first Monday after each event (decided with data after it) vs all other weeks."""
    yy = y.dropna()
    hits: list[tuple[str, float]] = []
    for e in events:
        after = yy.loc[yy.index > pd.Timestamp(e)]
        if len(after) and (after.index[0] - pd.Timestamp(e)).days <= 7:
            hits.append((str(e), float(after.iloc[0])))
    hit_idx = {pd.Timestamp(d) for d, _ in hits}
    rest = yy.loc[[t for t in yy.index if not any(0 < (t - h).days <= 7 for h in hit_idx)]]
    vals = np.array([v for _, v in hits])
    return {
        "events": hits,
        "mean_after": float(vals.mean()) if vals.size else float("nan"),
        "mean_other": float(rest.mean()) if len(rest) else float("nan"),
        "share_up_after": float((vals > 0).mean()) if vals.size else float("nan"),
        "share_up_other": float((rest > 0).mean()) if len(rest) else float("nan"),
    }


def predictors(
    closes: pd.DataFrame, dgs2: pd.Series, buckets: dict[str, list[str]], mondays: pd.DatetimeIndex
) -> dict[str, pd.Series]:
    daily = {
        "MD-1": basket_excess(closes, buckets["gpu_semis"]),
        "MD-2": basket_excess(closes, buckets["neocloud"]),
        "MD-3": basket_excess(closes, HYPERSCALERS),
        "MD-4": level_change(dgs2),
        "MD-5": basket_excess(closes, buckets["power_capacity"]),
    }
    return {k: asof_friday(v, mondays) for k, v in daily.items()}


def weekly_excess(closes: pd.DataFrame, names: list[str], mondays: pd.DatetimeIndex) -> pd.Series:
    """Basket 5-session excess return as of the Friday before each Monday (correlogram)."""
    return asof_friday(basket_excess(closes, names, window=5), mondays)


def analyse(
    panels: dict[str, pd.DataFrame],
    closes: pd.DataFrame,
    dgs2: pd.Series,
    buckets: dict[str, list[str]],
    seed: int,
) -> dict[str, Any]:
    h100 = trim_start(panels["H100"])
    y = forward_change(h100)
    x = predictors(closes, dgs2, buckets, h100.index)
    tests = {k: md_test(x[k], y, seed) for k in TESTS}
    finish(tests)
    wk = weekly_change(h100)
    wx = weekly_excess(closes, buckets["gpu_semis"], h100.index)
    out: dict[str, Any] = {
        "weeks": [str(h100.index[0].date()), str(h100.index[-1].date())],
        "tests": tests,
        "y_summary": {
            "n": int(y.notna().sum()),
            "mean": float(y.mean()),
            "sd": float(y.std()),
            "share_zero": float((y.abs() < 1e-9).mean()),
        },
        "correlogram_md1": correlogram(wx, wk),
        "granger_md1": granger(wx, wk),
        "nvda_earnings": event_windows(y, NVDA_EARNINGS),
    }
    if "B200" in panels:
        b200 = trim_start(panels["B200"], min_cs=4)
        yb = forward_change(b200, min_cs=4)
        xb = predictors(closes, dgs2, buckets, b200.index)
        out["b200_descriptive"] = {k: md_test(xb[k], yb, seed) for k in TESTS}
    return out


# ---------------------------------------------------------------------------
# Rendering and the one-shot run
# ---------------------------------------------------------------------------
def _f(v: Any, nd: int = 3) -> str:
    return f"{v:.{nd}f}" if isinstance(v, float) and np.isfinite(v) else "n/a"


def render(r: dict[str, Any]) -> str:
    lines = [
        "# Claim 11 results: AI-economy signals vs GPU rental prices",
        "",
        f"Plan: docs/macro_drivers_plan.md. H100 weeks {r['weeks'][0]} to {r['weeks'][1]} "
        "(GetDeploying API, aggregates only; credit: GetDeploying). One shot, Holm over 5. "
        "No trade is simulated, so no cost assumption applies.",
        "",
        "| Test | Predictor | n | Slope | 95% CI | corr | HAC p | Holm p | Verdict |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for k in TESTS:
        t = r["tests"][k]
        ci = t.get("ci95", [float("nan")] * 2)
        lines.append(
            f"| {k} | {LABELS[k]} | {t['n']} | {_f(t.get('slope', float('nan')), 4)} | "
            f"[{_f(ci[0], 4)}, {_f(ci[1], 4)}] | {_f(t.get('corr', float('nan')), 2)} | "
            f"{_f(t.get('p_one_sided', float('nan')))} | {_f(t.get('p_holm', float('nan')))} | "
            f"{t.get('verdict', '')} |"
        )
    ys = r["y_summary"]
    lines += [
        "",
        f"Target: 4-week provider-mean log change, n {ys['n']}, mean {_f(ys['mean'], 4)}, "
        f"sd {_f(ys['sd'], 4)}, exactly zero in {ys['share_zero']:.0%} of weeks.",
        "",
        "## Descriptive (exploratory)",
        "",
        "Lead-lag: corr(AI-hardware weekly excess return at t, H100 weekly change at t+k).",
        "",
        "| k (weeks) | " + " | ".join(str(k) for k in r["correlogram_md1"]) + " |",
        "|---|" + "---|" * len(r["correlogram_md1"]),
        "| corr | " + " | ".join(_f(v, 2) for v in r["correlogram_md1"].values()) + " |",
        "",
        f"Granger (lag {GRANGER_LAG}, n {int(r['granger_md1']['n'])}): AI hardware -> H100 "
        f"p {_f(r['granger_md1']['x_to_y'])}; H100 -> AI hardware p "
        f"{_f(r['granger_md1']['y_to_x'])}.",
        "",
    ]
    ev = r["nvda_earnings"]
    lines += [
        f"NVIDIA earnings ({len(ev['events'])} verified dates): mean H100 4-week change from "
        f"the next Monday {_f(ev['mean_after'], 4)} vs {_f(ev['mean_other'], 4)} in other "
        f"weeks; share up {_f(ev['share_up_after'], 2)} vs {_f(ev['share_up_other'], 2)}.",
    ]
    if "b200_descriptive" in r:
        lines += ["", "B200 (descriptive only):", ""]
        nan = float("nan")
        for k in TESTS:
            t = r["b200_descriptive"][k]
            lines.append(
                f"- {k}: n {t['n']}, slope {_f(t.get('slope', nan), 4)}, corr "
                f"{_f(t.get('corr', nan), 2)}, HAC p {_f(t.get('p_one_sided', nan))}"
            )
    return "\n".join(lines) + "\n"


def fetch_dgs2(cfg: Any, cache: Path) -> pd.Series:  # pragma: no cover - network
    """DGS2 from FRED (public domain), cached under var/."""
    from compute_curve.http import PoliteClient  # noqa: PLC0415

    if not cache.exists():
        with PoliteClient(
            user_agent=cfg.http.user_agent, min_interval_s=cfg.http.min_interval_s
        ) as client:
            resp = client.get(FRED_URL + f"&cosd={BARS_START.isoformat()}")
            resp.raise_for_status()
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(resp.text)
    df = pd.read_csv(io.StringIO(cache.read_text()), na_values=".")
    s = pd.Series(
        pd.to_numeric(df.iloc[:, 1], errors="coerce").to_numpy(),
        index=pd.to_datetime(df.iloc[:, 0]),
    )
    return s.loc[: pd.Timestamp(LAST_FRIDAY)]


def run_claim11(cfg: Any) -> Path:  # pragma: no cover - reads git-ignored data, runs once
    import json  # noqa: PLC0415

    from compute_curve.claim4.alpaca import AlpacaDataClient  # noqa: PLC0415
    from compute_curve.claim4.market_data import fetch_bars_cached  # noqa: PLC0415
    from compute_curve.collectors import getdeploying_api as gd  # noqa: PLC0415

    out = cfg.path("reports") / "macro"
    out.mkdir(parents=True, exist_ok=True)
    done = out / "claim11.json"
    if done.exists():
        raise RuntimeError(f"{done} exists; claim 11 runs once")
    vint = gd.latest_vintage(cfg.path("var") / "getdeploying_api")
    if vint is None:
        raise RuntimeError("no GetDeploying API download in var/getdeploying_api/")
    hist = gd.load_history(vint)
    panels = {"H100": weekly_panel(hist, "nvidia-h100"), "B200": weekly_panel(hist, "nvidia-b200")}
    c4 = cfg.claim4
    buckets = {k: list(v) for k, v in c4.universe.buckets().items()}
    symbols = sorted({*c4.universe.members(), *HYPERSCALERS, MARKET})
    end = LAST_FRIDAY + timedelta(days=1)
    with AlpacaDataClient() as client:
        bars = fetch_bars_cached(
            client,
            symbols,
            BARS_START.isoformat(),
            LAST_FRIDAY.isoformat(),
            cfg.path("var") / "market_data",
            feed=c4.feed,
            end_param=f"{end.isoformat()}T00:00:00Z",
        )
    b = bars.assign(session=pd.to_datetime(bars["session"]))
    closes = b.pivot_table(index="session", columns="symbol", values="close", aggfunc="last")
    dgs2 = fetch_dgs2(cfg, cfg.path("var") / "fred" / "DGS2.csv")
    res = analyse(panels, closes.sort_index(), dgs2, buckets, cfg.project.seed)
    res["vintage"] = vint.name
    done.write_text(json.dumps(res, indent=2, default=float))
    path = out / "claim11.md"
    path.write_text(render(res))
    return path
