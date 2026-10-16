"""Today's SA2-M target book: what the frozen strategy would hold at the next open.

For learning and hand paper-trading only. It never sends an order. The
paper-trading preconditions in docs/statarb_paper_readiness.md are not met
(the forward test is still running), so this is practice, not a signal to
trade real money.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from compute_curve.config import StatArbConfig
from compute_curve.statarb.pipeline import ETF, REGIONS_6C
from compute_curve.statarb.strategies import residual_trades, s_scores


@dataclass(frozen=True)
class BookLine:
    symbol: str
    weight: float  # fraction of capital; + long, - short
    cells_long: int
    cells_short: int


def with_next_session(logp: pd.DataFrame) -> pd.DataFrame:
    """Append a placeholder row for the next session so signals at the last close can enter."""
    nxt = logp.iloc[[-1]].copy()
    nxt.index = [logp.index[-1] + pd.offsets.BDay(1)]
    return pd.concat([logp, nxt])


def target_book(
    signal_logp: pd.DataFrame, sa: StatArbConfig, region: list[list[float]] | None = None
) -> tuple[dict[str, float], dict[str, list[int]]]:
    """Pooled weights held into the next session across the frozen SA2-M cells."""
    region = region or REGIONS_6C["SA2-M"]
    lp = with_next_session(signal_logp)
    n = len(lp)
    pooled: dict[str, float] = {}
    votes: dict[str, list[int]] = {}
    for window, entry in region:
        trades = residual_trades(
            lp,
            ETF,
            int(window),
            entry,
            sa.residual,
            sa.max_positions,
            sa.max_hold,
            int(window),
            n - 2,
        )
        for tr in trades:
            if tr.end != n:  # closed at or before the next open: not held
                continue
            for sym, w in tr.weights.items():
                pooled[sym] = pooled.get(sym, 0.0) + w / len(region)
                if sym != ETF:
                    v = votes.setdefault(sym, [0, 0])
                    v[0 if w > 0 else 1] += 1
    return pooled, votes


def scores_today(signal_logp: pd.DataFrame, window: int = 60) -> dict[str, float]:
    rets = signal_logp.diff()
    return {k: v[0] for k, v in s_scores(rets, ETF, len(rets) - 1, window).items()}


def book_lines(pooled: dict[str, float], votes: dict[str, list[int]]) -> list[BookLine]:
    lines = [
        BookLine(s, w, votes.get(s, [0, 0])[0], votes.get(s, [0, 0])[1])
        for s, w in pooled.items()
        if abs(w) > 1e-9
    ]
    return sorted(lines, key=lambda x: -abs(x.weight))


def render(lines: list[BookLine], scores: dict[str, float], asof: str, capital: float) -> str:
    out = [
        f"# SA2-M practice sheet for the session after {asof}",
        "",
        "Practice only: paper-trade by hand or in a simulator, never with real money. "
        "The forward test that would allow paper trading is still running "
        "(docs/statarb_paper_readiness.md).",
        "",
        "How to use it: at the next open, hold these positions (dollar amounts for a "
        f"USD {capital:,.0f} practice account). Hold until the sheet drops the name. "
        "XLK is the hedge leg. Write every trade in your journal.",
        "",
        "| Symbol | Side | Weight | Practice dollars | Cells long / short (of 12) |",
        "|---|---|---|---|---|",
    ]
    for b in lines:
        side = "LONG" if b.weight > 0 else "SHORT"
        cells = "hedge" if b.symbol == ETF else f"{b.cells_long} / {b.cells_short}"
        out.append(
            f"| {b.symbol} | {side} | {b.weight:+.3f} | {b.weight * capital:+,.0f} | {cells} |"
        )
    if not lines:
        out.append("| (no positions) | | | | |")
    stocks = sum(abs(b.weight) for b in lines if b.symbol != ETF)
    out += [
        "",
        f"Gross stock exposure {stocks:.2f} of capital; positions are 0.1 of capital per "
        "position per cell, averaged over the 12 frozen cells (windows 40/60/90 days; "
        "entries 1.0-2.0).",
        "",
        "## Today's 60-day s-scores (how stretched each stock is against XLK)",
        "",
        "Below -1.25: cheap, a long candidate. Above +1.25: rich, a short candidate.",
        "",
        "| Symbol | s-score |",
        "|---|---|",
    ]
    out += [f"| {s} | {v:+.2f} |" for s, v in sorted(scores.items(), key=lambda x: x[1])]
    return "\n".join(out) + "\n"


def run_signals(cfg: Any, capital: float = 10_000.0) -> Path:  # pragma: no cover - Alpaca data
    from datetime import timedelta  # noqa: PLC0415

    from compute_curve.claim4.alpaca import AlpacaDataClient  # noqa: PLC0415
    from compute_curve.claim4.market_data import fetch_bars_cached  # noqa: PLC0415
    from compute_curve.claim5.pipeline import claim5_cfg  # noqa: PLC0415
    from compute_curve.statarb.pipeline import wide_prices  # noqa: PLC0415
    from compute_curve.timeutil import utc_now  # noqa: PLC0415

    sa, c4, c5 = cfg.statarb, cfg.claim4, claim5_cfg(cfg)
    symbols = [*c4.universe.members(), c4.benchmark]
    last = utc_now().date() - timedelta(days=1)
    with AlpacaDataClient() as client:
        bars = fetch_bars_cached(
            client,
            symbols,
            c5.bars_start.isoformat(),
            last.isoformat(),
            cfg.path("var") / "market_data",
            feed=c4.feed,
            end_param=f"{last.isoformat()}T23:59:00Z",
        )
    prices = wide_prices(bars, symbols, dict(c5.member_start), sa.min_history)
    pooled, votes = target_book(prices.signal_logp, sa)
    asof = str(prices.closes.index[-1].date())
    md = render(book_lines(pooled, votes), scores_today(prices.signal_logp), asof, capital)
    out = cfg.path("reports") / "statarb" / "practice"  # weights and scores only, no prices (D29)
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"sa2m_sheet_{asof}.md"
    path.write_text(md)
    (out / "latest.md").write_text(md)
    return path
