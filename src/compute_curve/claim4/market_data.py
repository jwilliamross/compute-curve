"""Equity sessions, daily bars and window returns for claim 4.

Alpaca bars are cached under ``var/market_data/`` only and never committed
(docs/decisions.md D29). A manifest (symbols, dates, feed, row counts and a
SHA-256 of the canonical bar table) is committed so a later re-fetch can be
checked against what a result used.

Timing (no look-ahead):

* a session's official open and close come from Alpaca's trading calendar,
  in New York time, converted to UTC;
* a daily bar for session ``t`` is usable from its close plus
  ``BAR_DELAY`` (the free plan withholds the latest 15 minutes of
  consolidated data; 5 minutes are added as margin);
* the window return ``R(t, h)`` runs from the open of ``t`` to the close of
  ``t + h - 1`` and is known only after that close plus ``BAR_DELAY``.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

NEW_YORK = ZoneInfo("America/New_York")
BAR_DELAY = timedelta(minutes=20)
BAR_COLUMNS = ("symbol", "session", "open", "high", "low", "close", "volume", "vwap", "n_trades")


def sessions_from_calendar(rows: Sequence[Mapping[str, Any]]) -> pd.DataFrame:
    """Alpaca calendar rows -> ``session``, ``open_utc``, ``close_utc`` (aware UTC)."""
    out: list[dict[str, object]] = []
    for r in rows:
        d = date.fromisoformat(str(r["date"]))
        o = time.fromisoformat(str(r["open"]))
        c = time.fromisoformat(str(r["close"]))
        out.append(
            {
                "session": d,
                "open_utc": pd.Timestamp(datetime.combine(d, o, tzinfo=NEW_YORK)).tz_convert("UTC"),
                "close_utc": pd.Timestamp(datetime.combine(d, c, tzinfo=NEW_YORK)).tz_convert(
                    "UTC"
                ),
            }
        )
    df = pd.DataFrame(out, columns=["session", "open_utc", "close_utc"])
    return df.sort_values("session").reset_index(drop=True)


def bars_frame(raw: Mapping[str, Sequence[Mapping[str, Any]]]) -> pd.DataFrame:
    """Alpaca bar JSON -> tidy frame. ``t`` (midnight New York, as UTC) labels the session."""
    rows: list[dict[str, object]] = []
    for sym, bars in raw.items():
        for b in bars:
            ts = pd.Timestamp(str(b["t"])).tz_convert(NEW_YORK)
            rows.append(
                {
                    "symbol": sym,
                    "session": ts.date(),
                    "open": float(b["o"]),
                    "high": float(b["h"]),
                    "low": float(b["l"]),
                    "close": float(b["c"]),
                    "volume": float(b["v"]),
                    "vwap": float(b.get("vw", np.nan)),
                    "n_trades": float(b.get("n", np.nan)),
                }
            )
    df = pd.DataFrame(rows, columns=list(BAR_COLUMNS))
    return df.sort_values(["symbol", "session"]).reset_index(drop=True)


def content_hash(bars: pd.DataFrame) -> str:
    """SHA-256 of the canonical CSV of the bar table (sorted, fixed float format)."""
    canon = bars.sort_values(["symbol", "session"])[list(BAR_COLUMNS)]
    payload = canon.to_csv(index=False, float_format="%.6f").encode()
    return hashlib.sha256(payload).hexdigest()


def manifest(bars: pd.DataFrame, start: str, end: str, feed: str, adjustment: str) -> dict:
    """What was fetched, without any price: counts, first and last session, hash."""
    per = (
        bars.groupby("symbol")["session"].agg(["count", "min", "max"]).reset_index()
        if not bars.empty
        else pd.DataFrame(columns=["symbol", "count", "min", "max"])
    )
    return {
        "provider": "Alpaca market data API (data.alpaca.markets)",
        "feed": feed,
        "adjustment": adjustment,
        "start": start,
        "end": end,
        "rows": len(bars),
        "sha256": content_hash(bars) if not bars.empty else None,
        "symbols": {
            str(r.symbol): {"bars": int(r.count), "first": str(r.min), "last": str(r.max)}
            for r in per.itertuples(index=False)
        },
        "note": "Prices are not stored in the repository (docs/decisions.md D29).",
    }


def cache_path(cache_dir: Path, symbols: Sequence[str], start: str, end: str, feed: str) -> Path:
    key = hashlib.sha256(",".join(sorted(symbols)).encode()).hexdigest()[:12]
    return cache_dir / f"alpaca_bars_{feed}_{start}_{end}_{key}.parquet"


def fetch_bars_cached(
    client: Any,
    symbols: Sequence[str],
    start: str,
    end: str,
    cache_dir: Path,
    feed: str = "sip",
    adjustment: str = "all",
    refresh: bool = False,
) -> pd.DataFrame:
    """Daily bars from the local ``var`` cache, or from Alpaca (then cached locally)."""
    path = cache_path(cache_dir, symbols, start, end, feed)
    if path.exists() and not refresh:
        return _read_duckdb(path)
    raw = client.daily_bars(list(symbols), start, end, feed=feed, adjustment=adjustment)
    df = bars_frame(raw)
    cache_dir.mkdir(parents=True, exist_ok=True)
    _write_duckdb(df, path)
    return df


def _write_duckdb(df: pd.DataFrame, path: Path) -> None:
    import duckdb  # noqa: PLC0415

    con = duckdb.connect()
    try:
        con.register("bars_df", df)
        con.execute(f"COPY bars_df TO '{path.as_posix()}' (FORMAT PARQUET)")
    finally:
        con.close()


def _read_duckdb(path: Path) -> pd.DataFrame:
    import duckdb  # noqa: PLC0415

    con = duckdb.connect()
    try:
        # The path is built by cache_path() from a hash, never from user input.
        df = con.execute(f"SELECT * FROM read_parquet('{path.as_posix()}')").df()  # noqa: S608
    finally:
        con.close()
    df["session"] = pd.to_datetime(df["session"]).dt.date
    return df


def window_returns(
    bars: pd.DataFrame, sessions: pd.DataFrame, horizon: int
) -> tuple[pd.DataFrame, pd.Series]:
    """Simple returns from the open of ``t`` to the close of ``t + horizon - 1``.

    Returns (wide frame indexed by session with one column per symbol, and
    the UTC time each window's outcome becomes known). A symbol missing a
    bar at either end of a window gets NaN for that window.
    """
    if horizon < 1:
        raise ValueError("horizon must be >= 1")
    sess = sessions.sort_values("session").reset_index(drop=True)
    order = pd.Index(sess["session"])
    o = bars.pivot_table(index="session", columns="symbol", values="open", aggfunc="first")
    c = bars.pivot_table(index="session", columns="symbol", values="close", aggfunc="first")
    o, c = o.reindex(order), c.reindex(order)
    end_close = c.shift(-(horizon - 1))
    ret = end_close / o - 1.0
    known = pd.Series(
        pd.to_datetime(sess["close_utc"], utc=True).shift(-(horizon - 1)).to_numpy(),
        index=order,
    ) + pd.Timedelta(BAR_DELAY)
    return ret, known


def basket_excess(
    ret: pd.DataFrame, members: Sequence[str], benchmark: str, min_coverage: float = 0.5
) -> pd.Series:
    """Equal-weight basket simple return minus the benchmark's, per window.

    Windows where fewer than ``min_coverage`` of members have a return, or
    the benchmark has none, are NaN.
    """
    cols = [m for m in members if m in ret.columns]
    if not cols or benchmark not in ret.columns:
        return pd.Series(np.nan, index=ret.index)
    sub = ret[cols]
    enough = sub.notna().sum(axis=1) >= max(1, int(np.ceil(min_coverage * len(members))))
    basket = sub.mean(axis=1, skipna=True).where(enough)
    return basket - ret[benchmark]


def liquidity_screen(
    bars: pd.DataFrame,
    start: date,
    end: date,
    min_median_dollar_volume: float,
    min_price: float,
    min_sessions: int,
) -> pd.DataFrame:
    """Pre-sample liquidity check per symbol: pass or fail only, no price is reported.

    Dollar volume uses ``volume * vwap``. The price test uses the last close
    in the window.
    """
    w = bars.loc[(bars["session"] >= start) & (bars["session"] <= end)].copy()
    w["dollar_volume"] = w["volume"] * w["vwap"]
    rows = []
    for sym, grp in w.groupby("symbol"):
        g = grp.sort_values("session")
        med = float(g["dollar_volume"].median())
        rows.append(
            {
                "symbol": sym,
                "sessions": len(g),
                "passes_sessions": len(g) >= min_sessions,
                "passes_dollar_volume": med >= min_median_dollar_volume,
                "passes_price": float(g["close"].iloc[-1]) >= min_price,
            }
        )
    out = pd.DataFrame(
        rows,
        columns=["symbol", "sessions", "passes_sessions", "passes_dollar_volume", "passes_price"],
    )
    out["passes"] = out[["passes_sessions", "passes_dollar_volume", "passes_price"]].all(axis=1)
    return out


def write_manifest(path: Path, info: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(info, indent=2, sort_keys=True, default=str) + "\n")
