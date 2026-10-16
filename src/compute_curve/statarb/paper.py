"""SA2-M on the Alpaca PAPER account (fake money; D63, docs/statarb_paper_readiness.md).

The owner overrode the forward-test precondition on 2026-10-16 for paper
trading only. Everything here goes through ``claim4.alpaca.AlpacaPaperClient``,
which hard-fails unless ``APCA_API_BASE_URL`` is exactly the paper endpoint.

Each nightly run, after the close:

1. checks that the market is closed and the data ends on the last session;
2. checks the kill criteria from Alpaca's own history (stateless) and a
   committed kill marker; if any is hit, it flattens and stops for good;
3. builds the frozen SA2-M book (``statarb.signals.target_book``), dropping
   shorts that Alpaca cannot borrow;
4. sends market day orders that move the account to the book at the next
   open.

Reports carry percentages and counts only (D29); raw fills stay in ``var/``.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import numpy as np

from compute_curve.claim4.risk import KILL_ENV, equity_series
from compute_curve.claim4.strategy import Order, flatten_orders, orders_for_targets
from compute_curve.config import StatArbPaperConfig

PREFIX = "sa2"


@dataclass
class PaperRisk:
    drawdown_usd: float = 0.0
    return_pct: float = 0.0
    sessions: int = 0
    daily_breaches: int = 0
    bad_fill_share: float = float("nan")
    n_fills: int = 0
    kill: list[str] = field(default_factory=list)


def assess(
    history: Mapping[str, Any],
    account: Mapping[str, Any],
    pc: StatArbPaperConfig,
    slippage_bps: Sequence[float],
    env: Mapping[str, str],
) -> PaperRisk:
    """Kill criteria 1-5 of the readiness doc, recomputed from Alpaca's own history."""
    eq, pl = equity_series(history, pc.paper_start)
    try:
        now = float(account.get("equity", "nan"))
    except (TypeError, ValueError):
        now = float("nan")
    if np.isfinite(now) and now > 0:
        eq = np.append(eq, now)
    r = PaperRisk(sessions=int(max(len(eq) - 1, 0)))
    if eq.size:
        peak = np.maximum.accumulate(eq)
        r.drawdown_usd = float((peak - eq).max())
        r.return_pct = float(100 * (eq[-1] / eq[0] - 1))
        if r.drawdown_usd >= pc.max_drawdown_usd:
            r.kill.append(f"drawdown reached USD {pc.max_drawdown_usd:,.0f}")
    recent = pl[-pc.breach_window_sessions :] if pl.size else np.array([])
    r.daily_breaches = int(np.sum(recent[np.isfinite(recent)] <= -pc.daily_loss_limit_usd))
    if r.daily_breaches >= pc.max_daily_breaches:
        r.kill.append(
            f"daily loss limit breached {r.daily_breaches} times "
            f"in {pc.breach_window_sessions} sessions"
        )
    if r.sessions >= 60 and r.return_pct < 0:
        r.kill.append("cumulative return below zero after 60 paper sessions")
    s = np.asarray(slippage_bps, dtype=float)
    r.n_fills = int(s.size)
    if s.size:
        r.bad_fill_share = float(np.mean(s > 3 * pc.fill_cost_bps))
        if s.size >= pc.min_fills_for_check and r.bad_fill_share > pc.bad_fill_share:
            r.kill.append(f"{r.bad_fill_share:.0%} of fills worse than 3x the assumed cost")
    if env.get(KILL_ENV, "") == "1":
        r.kill.append(f"kill switch set by {KILL_ENV}")
    return r


def scale_targets(weights: Mapping[str, float], pc: StatArbPaperConfig) -> dict[str, float]:
    """Dollar targets at ``capital_usd``, scaled down together to respect the hard limits."""
    usd = {k: w * pc.capital_usd for k, w in weights.items() if abs(w) > 1e-12}
    if not usd:
        return {}
    factor = 1.0
    biggest = max(abs(v) for v in usd.values())
    gross = sum(abs(v) for v in usd.values())
    if biggest > pc.max_position_usd:
        factor = min(factor, pc.max_position_usd / biggest)
    if gross > pc.max_gross_usd:
        factor = min(factor, pc.max_gross_usd / gross)
    return {k: v * factor for k, v in usd.items()}


def payload(o: Order, session: str, stamp: str) -> dict[str, str]:
    q = f"{o.qty:.6f}".rstrip("0").rstrip(".") if o.qty != int(o.qty) else str(int(o.qty))
    return {
        "symbol": o.symbol,
        "qty": q,
        "side": o.side,
        "type": "market",
        "time_in_force": "day",
        "client_order_id": f"{PREFIX}-{session}-{o.symbol}-{stamp}",
    }


def slippage_bps(side: str, fill: float, open_px: float) -> float:
    """Positive = worse than the session open."""
    sign = 1.0 if side == "buy" else -1.0
    return float(sign * (fill - open_px) / open_px * 1e4)


def no_short_set(assets: Mapping[str, Mapping[str, Any]]) -> frozenset[str]:
    return frozenset(
        s for s, a in assets.items() if not (a.get("shortable") and a.get("easy_to_borrow"))
    )


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------
HEAD = "# SA2-M paper trading (Alpaca PAPER, fake money)"


def _fills(paper: Any, opens: Any, since: date) -> list[float]:  # pragma: no cover - Alpaca
    out = []
    for o in paper.orders(status="closed", limit=500):
        if not str(o.get("client_order_id", "")).startswith(f"{PREFIX}-"):
            continue
        if o.get("status") != "filled" or not o.get("filled_avg_price"):
            continue
        day = datetime.fromisoformat(str(o["filled_at"]).replace("Z", "+00:00")).date()
        ts = [t for t in opens.index if t.date() == day]
        sym = o["symbol"]
        if day < since or not ts or sym not in opens.columns:
            continue
        px = float(opens.loc[ts[0], sym])
        if np.isfinite(px) and px > 0:
            out.append(slippage_bps(o["side"], float(o["filled_avg_price"]), px))
    return out


def _write(out: Path, body: list[str], row: dict[str, Any]) -> Path:  # pragma: no cover - IO
    import pandas as pd  # noqa: PLC0415

    out.mkdir(parents=True, exist_ok=True)
    md = out / "status.md"
    stamp = row.get("run_utc", "")
    md.write_text("\n".join([HEAD, "", f"Run {stamp} UTC. D63.", *body]) + "\n")
    log = out / "log.csv"
    old = pd.read_csv(log) if log.exists() else pd.DataFrame()
    pd.concat([old, pd.DataFrame([row])]).to_csv(log, index=False)
    return md


def _preflight(cfg: Any, out: Path) -> str | None:  # pragma: no cover - reads local files
    """A reason not to trade at all, or None."""
    from compute_curve.claim4.pipeline import paths as c4paths  # noqa: PLC0415
    from compute_curve.claim4.pipeline import read_predictions  # noqa: PLC0415

    pc = cfg.statarb.paper
    if pc is None or not pc.enabled:
        return "disabled in config"
    if (out / "killed.json").exists():
        return f"stopped earlier: {(out / 'killed.json').read_text().strip()}"
    preds = read_predictions(c4paths(cfg)["predictions"])
    if "action" in preds and (preds["action"] == "paper").any():
        return "claim 4 has traded this account; refusing to share it"
    return None


def _target_session(paper: Any, last_session: date) -> tuple[str | None, str]:  # pragma: no cover
    """The next session if the market is closed and the data ends on the session before it."""
    clock = paper.clock()
    if clock.get("is_open"):
        return None, "market open; orders are only sent after the close"
    nxt = datetime.fromisoformat(str(clock["next_open"])).date()
    sessions = sorted(
        date.fromisoformat(c["date"]) for c in paper.calendar(str(last_session), str(nxt))
    )
    later = [d for d in sessions if d > last_session]
    if not later or later[0] != nxt:
        return None, f"data end {last_session} is not the session before {nxt}"
    return str(nxt), ""


def _kill(  # pragma: no cover - Alpaca paper account
    paper: Any,
    risk: PaperRisk,
    positions: dict[str, float],
    managed: list[str],
    target: str,
    stamp: str,
    out: Path,
) -> list[str]:
    orders = flatten_orders(positions, managed)
    for o in orders:
        paper.submit_order(payload(o, target, stamp))
    (out / "killed.json").write_text(json.dumps({"date": target, "reasons": risk.kill}))
    return [f"- **KILLED**: {'; '.join(risk.kill)}. Flattening {len(orders)} positions; stopped."]


def _summary(risk: PaperRisk, pc: StatArbPaperConfig) -> list[str]:
    bad = "n/a" if not np.isfinite(risk.bad_fill_share) else f"{risk.bad_fill_share:.0%}"
    dd = 100 * risk.drawdown_usd / pc.capital_usd
    kill_at = 100 * pc.max_drawdown_usd / pc.capital_usd
    return [
        f"- Since {pc.paper_start}: return {risk.return_pct:+.2f}% of account equity; worst "
        f"drawdown {dd:.1f}% of capital (kill at {kill_at:.0f}%); daily-loss breaches "
        f"{risk.daily_breaches}.",
        f"- Fills checked: {risk.n_fills}; share worse than 3x the assumed cost: {bad}.",
    ]


def run_paper(cfg: Any) -> Path:  # pragma: no cover - Alpaca paper account and market data
    import os  # noqa: PLC0415

    from compute_curve.claim4.alpaca import AlpacaPaperClient  # noqa: PLC0415
    from compute_curve.statarb.signals import latest_prices, target_book  # noqa: PLC0415

    pc = cfg.statarb.paper
    out = cfg.path("reports") / "statarb" / "paper"
    raw = cfg.path("var") / "statarb_paper"
    raw.mkdir(parents=True, exist_ok=True)
    now = datetime.now(UTC)
    row: dict[str, Any] = {"run_utc": now.isoformat(timespec="seconds")}
    reason = _preflight(cfg, out)
    if reason:
        return _write(out, [f"- {reason}. No orders."], row | {"mode": "no-orders"})
    prices = latest_prices(cfg)
    managed = [*cfg.claim4.universe.members(), cfg.claim4.benchmark]
    stamp = now.strftime("%Y%m%dT%H%M%S")
    with AlpacaPaperClient() as paper:
        target, why = _target_session(paper, prices.closes.index[-1].date())
        if target is None:
            return _write(out, [f"- {why}. No orders."], row | {"mode": "skipped"})
        row["target"] = target
        if any(
            str(o.get("client_order_id", "")).startswith(f"{PREFIX}-{target}-")
            for o in paper.orders(status="all", limit=500)
        ):
            return _write(out, [f"- Orders for {target} already sent."], row | {"mode": "done"})
        risk = assess(
            paper.portfolio_history(period="1A", timeframe="1D"),
            paper.account(),
            pc,
            _fills(paper, prices.opens, pc.paper_start),
            os.environ,
        )
        row |= {
            "return_pct": round(risk.return_pct, 3),
            "daily_breaches": risk.daily_breaches,
            "drawdown_pct_of_capital": round(100 * risk.drawdown_usd / pc.capital_usd, 3),
        }
        positions = {p["symbol"]: float(p["qty"]) for p in paper.positions()}
        if risk.kill:
            body = _kill(paper, risk, positions, managed, target, stamp, out)
            return _write(out, body + _summary(risk, pc), row | {"mode": "killed"})
        assets = {s: paper.asset(s) for s in managed}
        pooled, _ = target_book(prices.signal_logp, cfg.statarb, no_short=no_short_set(assets))
        tgt = scale_targets(pooled, pc)
        last_px = {
            s: float(prices.closes[s].dropna().iloc[-1]) for s in managed if s in prices.closes
        }
        frac = {s: bool(a.get("fractionable")) for s, a in assets.items()}
        orders, notes = orders_for_targets(tgt, positions, last_px, frac, managed)
        sent = [paper.submit_order(payload(o, target, stamp)) for o in orders]
    (raw / f"orders_{target}.json").write_text(json.dumps({"targets_usd": tgt, "orders": sent}))
    gross = sum(abs(v) for v in tgt.values()) / pc.capital_usd
    stocks = sum(1 for s in tgt if s != cfg.claim4.benchmark)
    body = [
        f"- Mode: **PAPER**. Orders for the open of {target}: {len(sent)} sent.",
        f"- Book: {stocks} stocks plus the XLK hedge; gross {gross:.2f} of capital "
        f"(USD {pc.capital_usd:,.0f}, fake money).",
        *_summary(risk, pc),
        *[f"- Note: {n}" for n in notes],
    ]
    return _write(
        out, body, row | {"mode": "paper", "n_orders": len(sent), "gross": round(gross, 3)}
    )
