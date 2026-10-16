"""Claim 9: GPU price binaries on Kalshi, favourite-longshot test (docs/kalshi_plan.md).

Public market data only (no key, no account, no orders). Raw responses stay
in git-ignored ``var/kalshi/`` (D62); reports carry derived numbers only.
"""

from __future__ import annotations

import json
import math
import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from compute_curve.backtest.bootstrap import circular_block_indices
from compute_curve.claim4 import stats as cs

BASE = "https://api.elections.kalshi.com/trade-api/v2"
SERIES = (
    "KXH100WS",
    "KXB200WS",
    "KXH200WS",
    "KXA100WS",
    "KXH100MS",
    "KXB200MS",
    "KXH200MS",
    "KXA100MS",
)
USER_AGENT = "compute-curve-research/0.1 (non-commercial research)"
RETRO_END = datetime(2026, 10, 16, 23, 59, 59, tzinfo=UTC)
FORWARD_START = datetime(2026, 10, 17, tzinfo=UTC)
FORWARD_DEADLINE = date(2027, 4, 1)
LEAD_S = 48 * 3600

GetJson = Callable[[str, dict[str, Any]], dict[str, Any]]


@dataclass(frozen=True)
class Rules:
    long_lo: float = 0.03
    long_hi: float = 0.20
    fav_lo: float = 0.80
    fav_hi: float = 0.97
    fee_rate: float = 0.07
    stress_fee_mult: float = 2.0
    stress_slip: float = 0.01
    min_dates_retro: int = 10
    min_dates_forward: int = 30
    alpha: float = 0.05
    block: int = 2
    n_boot: int = 2000


RULES = Rules()


# ---------------------------------------------------------------------------
# Download (polite, cached)
# ---------------------------------------------------------------------------
def make_get(min_interval_s: float = 2.5, max_tries: int = 8) -> GetJson:  # pragma: no cover
    import httpx  # noqa: PLC0415

    client = httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=30)
    last = [0.0]

    def get(path: str, params: dict[str, Any]) -> dict[str, Any]:
        for attempt in range(max_tries):
            wait = min_interval_s - (time.monotonic() - last[0])
            if wait > 0:
                time.sleep(wait)
            last[0] = time.monotonic()
            r = client.get(BASE + path, params=params)
            if r.status_code == 429:
                time.sleep(10 * (attempt + 1))
                continue
            r.raise_for_status()
            return r.json()  # type: ignore[no-any-return]
        raise RuntimeError(f"{path}: rate limited after {max_tries} tries")

    return get


def fetch_markets(get: GetJson, series: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    cursor = None
    while True:
        params: dict[str, Any] = {"series_ticker": series, "limit": 1000}
        if cursor:
            params["cursor"] = cursor
        d = get("/markets", params)
        rows += d.get("markets", [])
        cursor = d.get("cursor")
        if not cursor:
            return rows


def _ts(iso: str) -> int:
    return int(datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp())


def fetch_candles(get: GetJson, series: str, m: dict[str, Any]) -> list[dict[str, Any]]:
    d = get(
        f"/series/{series}/markets/{m['ticker']}/candlesticks",
        {"start_ts": _ts(m["open_time"]), "end_ts": _ts(m["close_time"]), "period_interval": 1440},
    )
    return list(d.get("candlesticks", []))


def fetch_candles_batch(get: GetJson, markets: list[dict[str, Any]]) -> dict[str, list[Any]]:
    """Daily candles for up to 50 markets in one request."""
    d = get(
        "/markets/candlesticks",
        {
            "market_tickers": ",".join(m["ticker"] for m in markets),
            "start_ts": min(_ts(m["open_time"]) for m in markets),
            "end_ts": max(_ts(m["close_time"]) for m in markets),
            "period_interval": 1440,
        },
    )
    return {x["market_ticker"]: list(x.get("candlesticks", [])) for x in d.get("markets", [])}


def download(
    root: Path, get: GetJson, series: Iterable[str] = SERIES
) -> dict[str, int]:  # pragma: no cover
    """Refresh market lists; fetch candles once for each finalized market (cached)."""
    counts: dict[str, int] = {}
    for s in series:
        markets = fetch_markets(get, s)
        (root / "markets").mkdir(parents=True, exist_ok=True)
        (root / "markets" / f"{s}.json").write_text(json.dumps(markets))
        cdir = root / "candles" / s
        cdir.mkdir(parents=True, exist_ok=True)
        todo = [
            m
            for m in markets
            if m.get("status") == "finalized" and not (cdir / f"{m['ticker']}.json").exists()
        ]
        for i in range(0, len(todo), 50):
            got = fetch_candles_batch(get, todo[i : i + 50])
            for ticker, candles in got.items():
                (cdir / f"{ticker}.json").write_text(json.dumps(candles))
        counts[s] = len(todo)
    return counts


# ---------------------------------------------------------------------------
# Rules
# ---------------------------------------------------------------------------
def fee(price: float, rate: float = RULES.fee_rate) -> float:
    """Kalshi taker fee for one contract, rounded up to the cent."""
    return math.ceil(round(rate * price * (1 - price) * 100, 9)) / 100


def _f(x: Any) -> float | None:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v


def decision_quote(candles: list[dict[str, Any]], close_ts: int) -> dict[str, float] | None:
    """yes bid/ask closes of the last daily candle ending at least 48 h before close."""
    ok = [c for c in candles if int(c["end_period_ts"]) <= close_ts - LEAD_S]
    if not ok:
        return None
    c = max(ok, key=lambda x: int(x["end_period_ts"]))
    bid = _f((c.get("yes_bid") or {}).get("close_dollars"))
    ask = _f((c.get("yes_ask") or {}).get("close_dollars"))
    if bid is None or ask is None or not (0 < bid <= ask < 1):
        return None
    return {"bid": bid, "ask": ask, "ts": float(c["end_period_ts"])}


def trade(quote: dict[str, float], result: str, rules: Rules = RULES) -> dict[str, Any] | None:
    """KB-1: buy NO on longshots, YES on favourites; P&L at normal and stress costs."""
    bid, ask = quote["bid"], quote["ask"]
    if rules.long_lo <= bid <= rules.long_hi:
        side, price, win = "no", 1 - bid, result == "no"
    elif rules.fav_lo <= ask <= rules.fav_hi:
        side, price, win = "yes", ask, result == "yes"
    else:
        return None
    payoff = 1.0 if win else 0.0
    f = fee(price)
    return {
        "side": side,
        "price": price,
        "win": win,
        "pnl": payoff - price - f,
        "pnl_stress": payoff - price - rules.stress_fee_mult * f - rules.stress_slip,
    }


def build_trades(root: Path, rules: Rules = RULES) -> pd.DataFrame:  # pragma: no cover - reads var/
    rows = []
    for s in SERIES:
        f = root / "markets" / f"{s}.json"
        if not f.exists():
            continue
        for m in json.loads(f.read_text()):
            cf = root / "candles" / s / f"{m['ticker']}.json"
            if (
                m.get("status") != "finalized"
                or m.get("result") not in ("yes", "no")
                or not cf.exists()
            ):
                continue
            q = decision_quote(json.loads(cf.read_text()), _ts(m["close_time"]))
            row = {
                "series": s,
                "event": m["event_ticker"],
                "ticker": m["ticker"],
                "close_time": m["close_time"],
                "result": m["result"],
                "has_quote": q is not None,
            }
            if q is not None:
                row |= {"bid": q["bid"], "ask": q["ask"], "decision_ts": q["ts"]}
                t = trade(q, m["result"], rules)
                if t is not None:
                    row |= t
            rows.append(row)
    return pd.DataFrame(rows)


def date_pnl(trades: pd.DataFrame, col: str = "pnl") -> pd.Series:
    t = trades.dropna(subset=[col])
    if t.empty:
        return pd.Series(dtype=float)
    d = pd.to_datetime(t["close_time"]).dt.date
    return t.groupby(d)[col].sum().sort_index()


def kb1_test(
    trades: pd.DataFrame, min_dates: int, seed: int, rules: Rules = RULES
) -> dict[str, Any]:
    by_date = date_pnl(trades)
    res: dict[str, Any] = {
        "n_trades": int(trades["pnl"].notna().sum()) if "pnl" in trades else 0,
        "n_dates": len(by_date),
    }
    if len(by_date) < min_dates:
        res["verdict"] = "too little history to conclude"
        return res
    x = by_date.to_numpy(float)
    stress = date_pnl(trades, "pnl_stress").to_numpy(float)
    se = cs.hac_mean_se(x, 1)
    t = float(x.mean() / se) if se > 0 else float("nan")
    from scipy import stats as st  # noqa: PLC0415

    p = float(st.t.sf(t, df=len(x) - 1)) if np.isfinite(t) else 1.0
    rng = np.random.default_rng(seed)
    boots = [
        x[circular_block_indices(len(x), rules.block, rng)].mean() for _ in range(rules.n_boot)
    ]
    tr = trades.dropna(subset=["pnl"])
    ok = p <= rules.alpha and stress.mean() > 0
    return res | {
        "mean_pnl_per_date": float(x.mean()),
        "mean_pnl_per_trade": float(tr["pnl"].mean()),
        "mean_pnl_stress_per_date": float(stress.mean()),
        "hit_rate": float(tr["win"].mean()),
        "by_side": {
            s: {"n": len(g), "mean_pnl": float(g["pnl"].mean()), "hit": float(g["win"].mean())}
            for s, g in tr.groupby("side")
        },
        "t_hac": t,
        "p_one_sided": p,
        "ci95_per_date": [float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))],
        "verdict": "pass" if ok else "not confirmed",
    }


def calibration(trades: pd.DataFrame) -> dict[str, Any]:
    q = trades.dropna(subset=["bid", "ask"]).copy()
    if q.empty:
        return {"n": 0}
    q["mid"] = (q["bid"] + q["ask"]) / 2
    q["y"] = (q["result"] == "yes").astype(float)
    q["bucket"] = np.clip((q["mid"] * 10).astype(int), 0, 9)
    table = [
        {
            "bucket": f"{b / 10:.1f}-{(b + 1) / 10:.1f}",
            "n": len(g),
            "mid": float(g["mid"].mean()),
            "yes_rate": float(g["y"].mean()),
        }
        for b, g in q.groupby("bucket")
    ]
    brier = float(((q["mid"] - q["y"]) ** 2).mean())
    out: dict[str, Any] = {"n": len(q), "brier": brier, "brier_coin": 0.25, "table": table}
    p = np.clip(q["mid"].to_numpy(), 0.01, 0.99)
    x = np.log(p / (1 - p))
    if len(np.unique(q["y"])) == 2 and np.ptp(x) > 0:
        import statsmodels.api as sm  # noqa: PLC0415

        try:
            fit = sm.Logit(q["y"].to_numpy(), np.column_stack([np.ones_like(x), x])).fit(disp=0)
            out |= {"logit_slope": float(fit.params[1]), "logit_slope_se": float(fit.bse[1])}
        except (np.linalg.LinAlgError, ValueError):
            out["logit_slope"] = None
    return out


MONTHLY = ("KXH100MS", "KXB200MS", "KXH200MS", "KXA100MS")
MAX_SPREAD = 0.20


def implied_median(
    markets: list[dict[str, Any]], max_spread: float = MAX_SPREAD
) -> dict[str, Any] | None:
    """Strike where the YES mid of 'greater than K' markets crosses 0.5 (crossvenue plan)."""
    pts = []
    for m in markets:
        if m.get("strike_type") != "greater":
            continue
        bid, ask = _f(m.get("yes_bid_dollars")), _f(m.get("yes_ask_dollars"))
        k = _f(m.get("floor_strike"))
        if bid is None or ask is None or k is None or not (0 < ask < 1) or bid <= 0:
            continue
        if ask - bid > max_spread:
            continue
        pts.append((k, (bid + ask) / 2, ask - bid))
    if len(pts) < 3:
        return None
    pts.sort()
    strikes = np.array([x[0] for x in pts])
    mids = np.minimum.accumulate(np.array([x[1] for x in pts]))
    if not (mids.max() >= 0.5 >= mids.min()):
        return None
    med = float(np.interp(0.5, mids[::-1], strikes[::-1]))
    return {
        "implied_median": med,
        "n_strikes": len(pts),
        "median_spread": float(np.median([x[2] for x in pts])),
    }


def implied_curve(root: Path, day: date) -> pd.DataFrame:  # pragma: no cover - reads var/
    rows = []
    for s in MONTHLY:
        f = root / "markets" / f"{s}.json"
        if not f.exists():
            continue
        markets = [m for m in json.loads(f.read_text()) if m.get("status") == "active"]
        for ev in sorted({m["event_ticker"] for m in markets}):
            res = implied_median([m for m in markets if m["event_ticker"] == ev])
            if res is not None:
                month = pd.to_datetime(ev.split("-")[-1], format="%y%b").strftime("%Y-%m")
                rows.append({"date": str(day), "series": s, "month": month} | res)
    return pd.DataFrame(
        rows, columns=["date", "series", "month", "implied_median", "n_strikes", "median_spread"]
    )


def append_curve(path: Path, new: pd.DataFrame) -> None:  # pragma: no cover - file IO
    if new.empty:
        return
    old = pd.read_csv(path) if path.exists() else pd.DataFrame(columns=new.columns)
    out = pd.concat([old, new]).drop_duplicates(["date", "series", "month"], keep="first")
    out.to_csv(path, index=False)


def split(trades: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if trades.empty:
        return trades, trades
    close = pd.to_datetime(trades["close_time"], utc=True)
    dec = pd.to_datetime(
        trades.get("decision_ts", pd.Series(np.nan, index=trades.index)), unit="s", utc=True
    )
    retro = trades.loc[close <= pd.Timestamp(RETRO_END)]
    fwd = trades.loc[dec > pd.Timestamp(FORWARD_START)]
    return retro, fwd


def _summary_line(r: dict[str, Any]) -> str:
    return (
        f"- Trades {r.get('n_trades', 0)} over {r.get('n_dates', 0)} close dates; "
        f"verdict: **{r.get('verdict', 'waiting')}**."
    )


def _detail_lines(r: dict[str, Any]) -> list[str]:
    if "mean_pnl_per_date" not in r:
        return []
    lo, hi = r["ci95_per_date"]
    out = [
        f"- Mean P&L per close date ${r['mean_pnl_per_date']:.3f} (95% CI [{lo:.3f}, {hi:.3f}]); "
        f"per trade ${r['mean_pnl_per_trade']:.4f}; stress ${r['mean_pnl_stress_per_date']:.3f} "
        f"per date; hit rate {r['hit_rate']:.2f}; HAC t {r['t_hac']:.2f}; "
        f"one-sided p {r['p_one_sided']:.3f}."
    ]
    for s, v in r["by_side"].items():
        out.append(
            f"  - {s.upper()}: {v['n']} trades, mean ${v['mean_pnl']:.4f}, hit {v['hit']:.2f}"
        )
    return out


def render(res: dict[str, Any]) -> str:
    lines = [
        "# Claim 9: Kalshi GPU price binaries (favourite-longshot)",
        "",
        "Plan: docs/kalshi_plan.md (pre-registered before any price was read). Ornn GPU indices, "
        "weekly and monthly-average contracts. Costs: Kalshi taker fee rounded up to the cent; "
        "stress 2x fee + 1 cent. Variants: 3 (project total 333). Research only.",
        "",
    ]
    for key, label in (("kb1r", "KB-1R retrospective"), ("kb1f", "KB-1F forward")):
        lines += [f"## {label}", "", _summary_line(res.get(key, {}))]
        lines += _detail_lines(res.get(key, {}))
        lines.append("")
    c = res.get("kb2", {})
    lines += ["## KB-2 calibration (descriptive)", ""]
    if c.get("n"):
        slope = ""
        if c.get("logit_slope") is not None:
            slope = (
                f"; logit slope {c['logit_slope']:.2f} (SE {c['logit_slope_se']:.2f}; "
                "above 1 = under-confident)"
            )
        lines.append(f"- {c['n']} market quotes; Brier {c['brier']:.4f} (coin 0.25){slope}")
        lines += ["", "| Mid bucket | n | Mean mid | YES rate |", "|---|---|---|---|"]
        lines += [
            f"| {r['bucket']} | {r['n']} | {r['mid']:.2f} | {r['yes_rate']:.2f} |"
            for r in c["table"]
        ]
    return "\n".join(lines) + "\n"


def run(cfg: Any, refresh: bool = True) -> Path:  # pragma: no cover - network and var/
    root = cfg.path("var") / "kalshi"
    if refresh:
        download(root, make_get())
    trades = build_trades(root)
    retro, fwd = split(trades)
    out = cfg.path("reports") / "kalshi"
    out.mkdir(parents=True, exist_ok=True)
    append_curve(out / "implied_curve.csv", implied_curve(root, datetime.now(UTC).date()))
    seed = cfg.project.seed
    res: dict[str, Any] = {"kb2": calibration(retro)}
    retro_file = out / "kb1r.json"
    if retro_file.exists():
        res["kb1r"] = json.loads(retro_file.read_text())
    else:
        res["kb1r"] = kb1_test(retro, RULES.min_dates_retro, seed)
        retro_file.write_text(json.dumps(res["kb1r"], indent=2))
    fwd_res = kb1_test(fwd, RULES.min_dates_forward, seed)
    due = (
        fwd_res["n_dates"] >= RULES.min_dates_forward
        or datetime.now(UTC).date() >= FORWARD_DEADLINE
    )
    fwd_file = out / "kb1f.json"
    if fwd_file.exists():
        res["kb1f"] = json.loads(fwd_file.read_text())
    elif due:
        res["kb1f"] = fwd_res
        fwd_file.write_text(json.dumps(fwd_res, indent=2))
    else:
        res["kb1f"] = {
            "n_trades": fwd_res["n_trades"],
            "n_dates": fwd_res["n_dates"],
            "verdict": f"waiting ({fwd_res['n_dates']}/30 close dates)",
        }
    md = out / "status.md"
    md.write_text(render(res))
    return md
