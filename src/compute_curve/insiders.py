"""Insider-buying tracker: SEC EDGAR Form 4 open-market purchases, daily (D69).

Reads EDGAR's daily form index, fetches each Form 4, keeps open-market purchases
(transaction code P), and flags:

- **clusters:** several insiders of one issuer buying within a window;
- **C-suite buys:** a CEO/CFO/President/Chair buying at least a set dollar amount;
- **large buys:** any insider buying at least a larger set amount.

Data is public US government data (SEC EDGAR). SEC's fair-access rules apply: a
declared User-Agent with a contact email (``SEC_USER_AGENT``), and at most 10
requests a second (we use about 8). Owner addresses are never stored.

Research and alerts only: nothing here trades.
"""

from __future__ import annotations

import os
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

ARCHIVES = "https://www.sec.gov/Archives/"
INDEX_URL = ARCHIVES + "edgar/daily-index/{y}/QTR{q}/form.{d}.idx"
MIN_INTERVAL_S = 0.125  # 8 requests a second, under SEC's 10/s limit
SOURCE = "insiders"
C_SUITE = re.compile(
    r"\b(ceo|cfo|chief executive|chief financial|president|chair(man|woman)?)\b", re.I
)
LINE = re.compile(r"^(4)\s+(.+?)\s+(\d+)\s+(\d{8})\s+(edgar/data/\S+\.txt)\s*$")
COLUMNS = {
    "filed_date": "object",
    "accession": "object",
    "ts_observed": "datetime64[ns, UTC]",
    "issuer_cik": "object",
    "issuer_name": "object",
    "ticker": "object",
    "owner_cik": "object",
    "owner_name": "object",
    "is_director": "bool",
    "is_officer": "bool",
    "is_ten_pct": "bool",
    "officer_title": "object",
    "transaction_date": "object",
    "shares": "float64",
    "price": "float64",
    "value_usd": "float64",
    "shares_after": "float64",
    "direct": "bool",
    "plan_10b5_1": "bool",
    "url": "object",
}


@dataclass(frozen=True)
class Rules:
    window_days: int = 14
    cluster_min_insiders: int = 3
    pair_min_insiders: int = 2
    min_value_usd: float = 25_000.0
    c_suite_min_usd: float = 100_000.0
    large_min_usd: float = 1_000_000.0
    min_price: float = 1.0


# ---------------------------------------------------------------------------
# Parsing (pure)
# ---------------------------------------------------------------------------
def parse_index(text: str) -> list[dict[str, str]]:
    """Form 4 rows of an EDGAR daily form index, one per accession (filers are listed twice)."""
    seen: dict[str, dict[str, str]] = {}
    for line in text.splitlines():
        m = LINE.match(line)
        if not m:
            continue
        path = m.group(5)
        acc = path.rsplit("/", 1)[-1].removesuffix(".txt")
        seen.setdefault(acc, {"accession": acc, "path": path, "filed": m.group(4)})
    return list(seen.values())


def extract_xml(submission: str) -> str | None:
    """The ownershipDocument XML inside a full-text EDGAR submission."""
    m = re.search(r"<XML>\s*(.*?)\s*</XML>", submission, re.S | re.I)
    body = m.group(1) if m else submission
    start = body.find("<ownershipDocument")
    if start < 0:
        return None
    end = body.find("</ownershipDocument>", start)
    return body[start : end + len("</ownershipDocument>")] if end > 0 else None


def _text(node: ET.Element | None, path: str) -> str:
    if node is None:
        return ""
    el = node.find(path)
    if el is None:
        return ""
    v = el.find("value")
    return ((v.text if v is not None else el.text) or "").strip()


def _flag(node: ET.Element | None, path: str) -> bool:
    return _text(node, path).lower() in ("1", "true")


def _num(s: str) -> float:
    try:
        return float(s.replace(",", ""))
    except ValueError:
        return float("nan")


def parse_form4(
    xml: str, accession: str, filed: str, url: str, ts: datetime
) -> list[dict[str, Any]]:
    """Open-market purchases (code P, acquired) in one Form 4, one row per owner x transaction."""
    if "<!DOCTYPE" in xml or "<!ENTITY" in xml:
        return []  # never parse documents that declare entities
    root = ET.fromstring(xml)  # noqa: S314 - see above
    issuer = root.find("issuer")
    owners = root.findall("reportingOwner")
    plan = _flag(root, "aff10b5One")
    rows: list[dict[str, Any]] = []
    for tx in root.findall("nonDerivativeTable/nonDerivativeTransaction"):
        if _text(tx, "transactionCoding/transactionCode") != "P":
            continue
        if _text(tx, "transactionAmounts/transactionAcquiredDisposedCode") != "A":
            continue
        shares = _num(_text(tx, "transactionAmounts/transactionShares"))
        price = _num(_text(tx, "transactionAmounts/transactionPricePerShare"))
        for o in owners:
            rel = o.find("reportingOwnerRelationship")
            rows.append(
                {
                    "filed_date": f"{filed[:4]}-{filed[4:6]}-{filed[6:]}",
                    "accession": accession,
                    "ts_observed": ts,
                    "issuer_cik": _text(issuer, "issuerCik"),
                    "issuer_name": _text(issuer, "issuerName"),
                    "ticker": _text(issuer, "issuerTradingSymbol").upper(),
                    "owner_cik": _text(o, "reportingOwnerId/rptOwnerCik"),
                    "owner_name": _text(o, "reportingOwnerId/rptOwnerName"),
                    "is_director": _flag(rel, "isDirector"),
                    "is_officer": _flag(rel, "isOfficer"),
                    "is_ten_pct": _flag(rel, "isTenPercentOwner"),
                    "officer_title": _text(rel, "officerTitle"),
                    "transaction_date": _text(tx, "transactionDate"),
                    "shares": shares,
                    "price": price,
                    "value_usd": shares * price,
                    "shares_after": _num(
                        _text(tx, "postTransactionAmounts/sharesOwnedFollowingTransaction")
                    ),
                    "direct": _text(tx, "ownershipNature/directOrIndirectOwnership") == "D",
                    "plan_10b5_1": plan,
                    "url": url,
                }
            )
    return rows


def frame(rows: list[dict[str, Any]]) -> pd.DataFrame:
    df = pd.DataFrame(rows, columns=list(COLUMNS))
    return df.astype({k: v for k, v in COLUMNS.items() if not v.startswith("datetime")})


# ---------------------------------------------------------------------------
# Signals (pure)
# ---------------------------------------------------------------------------
def is_c_suite(title: str) -> bool:
    return bool(C_SUITE.search(title or ""))


def qualifying(p: pd.DataFrame, rules: Rules) -> pd.DataFrame:
    """Purchases that count: not 10b5-1 plans, price >= min_price."""
    if p.empty:
        return p
    return p.loc[~p["plan_10b5_1"] & (p["price"] >= rules.min_price) & (p["value_usd"] > 0)]


def alerts(history: pd.DataFrame, new_filed: set[str], rules: Rules) -> pd.DataFrame:
    """Issuers with a new qualifying filing (filed on ``new_filed`` days) that meet a rule.

    The window looks back ``window_days`` calendar days of transaction dates from the
    latest new filing's transaction date; filings after the processed days never enter.
    """
    q = qualifying(history, rules)
    cols = [
        "ticker", "issuer_name", "tier", "insiders", "total_usd", "top_buyer", "top_title",
        "top_usd", "avg_price", "holding_increase_pct", "filings",
    ]  # fmt: skip
    if q.empty:
        return pd.DataFrame(columns=cols)
    q = q.assign(tdate=pd.to_datetime(q["transaction_date"], errors="coerce"))
    out = []
    for cik, g in q.groupby("issuer_cik"):
        fresh = g.loc[g["filed_date"].isin(new_filed)]
        if fresh.empty:
            continue
        end = fresh["tdate"].max()
        w = g.loc[(g["tdate"] > end - timedelta(days=rules.window_days)) & (g["tdate"] <= end)]
        per = w.groupby("owner_cik").agg(
            usd=("value_usd", "sum"),
            shares=("shares", "sum"),
            after=("shares_after", "max"),
            name=("owner_name", "first"),
            title=("officer_title", "first"),
        )
        per = per.loc[per["usd"] >= rules.min_value_usd]
        if per.empty:
            continue
        n = len(per)
        top = per.sort_values("usd", ascending=False).iloc[0]
        c_suite = per.loc[[is_c_suite(t) for t in per["title"]]]
        tier = ""
        if n >= rules.cluster_min_insiders:
            tier = f"cluster ({n} insiders)"
        elif (c_suite["usd"] >= rules.c_suite_min_usd).any():
            tier = "C-suite buy"
        elif n >= rules.pair_min_insiders:
            tier = "pair (2 insiders)"
        elif top["usd"] >= rules.large_min_usd:
            tier = "large buy"
        if not tier:
            continue
        before = per["after"] - per["shares"]
        inc = (per["shares"] / before.where(before > 0)).median()
        out.append(
            {
                "ticker": g["ticker"].iloc[-1],
                "issuer_name": g["issuer_name"].iloc[-1],
                "tier": tier,
                "insiders": n,
                "total_usd": float(per["usd"].sum()),
                "top_buyer": top["name"],
                "top_title": top["title"] or ("director" if g["is_director"].any() else ""),
                "top_usd": float(top["usd"]),
                "avg_price": float(w["value_usd"].sum() / w["shares"].sum()),
                "holding_increase_pct": float(inc * 100) if pd.notna(inc) else float("nan"),
                "filings": sorted(set(w["url"])),
                "issuer_cik": cik,
            }
        )
    rank = {"cluster": 0, "C-suite": 1, "pair": 2, "large": 3}
    df = pd.DataFrame(out)
    if df.empty:
        return pd.DataFrame(columns=cols)
    df["_r"] = [rank[t.split(" ")[0]] for t in df["tier"]]
    return df.sort_values(["_r", "total_usd"], ascending=[True, False]).drop(columns="_r")


def render(al: pd.DataFrame, purchases: pd.DataFrame, days: list[str], rules: Rules) -> str:
    lines = [
        f"# Insider buying: filings of {', '.join(days)}",
        "",
        "Open-market purchases (Form 4, code P) from SEC EDGAR. Excluded: 10b5-1 plan "
        f"trades and prices under USD {rules.min_price:.0f}. An insider counts if they bought "
        f"at least USD {rules.min_value_usd:,.0f} in the {rules.window_days}-day window. "
        "Not investment advice: research signal only (docs/insider_tracker.md).",
        "",
        f"## Alerts ({len(al)})",
        "",
    ]
    if al.empty:
        lines.append("No issuer met a rule today.")
    else:
        lines += [
            "| Ticker | Company | Signal | Insiders | Total bought | Biggest buyer | Avg price |"
            " Holding increase (median) | Filing |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
        for r in al.itertuples():
            inc = f"{r.holding_increase_pct:.0f}%" if pd.notna(r.holding_increase_pct) else "n/a"
            who = f"{r.top_buyer} ({r.top_title})" if r.top_title else str(r.top_buyer)
            lines.append(
                f"| {r.ticker or '?'} | {r.issuer_name} | {r.tier} | {r.insiders} | "
                f"${r.total_usd:,.0f} | {who}, ${r.top_usd:,.0f} | ${r.avg_price:,.2f} | {inc} | "
                f"[link]({r.filings[-1]}) |"
            )
    q = qualifying(purchases, rules)
    lines += [
        "",
        f"## All qualifying purchases filed ({len(q)}; top 25 by value)",
        "",
        "| Ticker | Insider | Title | Shares | Price | Value |",
        "|---|---|---|---|---|---|",
    ]
    for r in q.sort_values("value_usd", ascending=False).head(25).itertuples():
        title = r.officer_title or (
            "Director" if r.is_director else "10% owner" if r.is_ten_pct else ""
        )
        lines.append(
            f"| {r.ticker} | {r.owner_name} | {title} | {r.shares:,.0f} | ${r.price:,.2f} | "
            f"${r.value_usd:,.0f} |"
        )
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Fetching and the daily run
# ---------------------------------------------------------------------------
def index_url(d: date) -> str:
    return INDEX_URL.format(y=d.year, q=(d.month - 1) // 3 + 1, d=f"{d:%Y%m%d}")


def user_agent(env: dict[str, str] | None = None) -> str:
    """SEC requires a declared User-Agent with a contact email; refuse to run without one."""
    ua = (env if env is not None else os.environ).get("SEC_USER_AGENT", "").strip()
    if "@" not in ua:
        raise RuntimeError(
            "SEC_USER_AGENT must be set to 'Name email@example.com' (SEC fair-access policy); "
            "set it as a repository variable for the workflow"
        )
    return ua


def done_days(raw_dir: Path) -> set[str]:
    return {
        p.name.split("_")[1][:8]
        for p in (raw_dir / SOURCE).glob("*/*/*.parquet")
        if p.name.startswith(f"{SOURCE}_")
    }


def pending_days(today: date, done: set[str], back: int = 5) -> list[date]:
    """Weekdays in the last ``back`` calendar days before today not yet processed."""
    out = []
    for k in range(back, 0, -1):
        d = today - timedelta(days=k)
        if d.weekday() < 5 and f"{d:%Y%m%d}" not in done:
            out.append(d)
    return out


def fetch_day(client: Any, d: date) -> pd.DataFrame | None:  # pragma: no cover - network
    """All purchases filed on ``d``; None if the index is not published yet."""
    r = client.get(index_url(d))
    if r.status_code == 404:
        return None
    r.raise_for_status()
    rows: list[dict[str, Any]] = []
    for f in parse_index(r.text):
        url = ARCHIVES + f["path"]
        s = client.get(url)
        if s.status_code != 200:
            continue
        xml = extract_xml(s.text)
        if xml:
            try:
                rows += parse_form4(xml, f["accession"], f["filed"], url, datetime.now(UTC))
            except ET.ParseError:
                continue
    return frame(rows)


def load_history(raw_dir: Path, since: date) -> pd.DataFrame:
    from compute_curve.storage.raw_store import read_snapshot  # noqa: PLC0415

    frames = []
    for p in sorted((raw_dir / SOURCE).glob("*/*/*.parquet")):
        stamp = p.name.split("_")[1][:8]
        day = date(int(stamp[:4]), int(stamp[4:6]), int(stamp[6:8]))
        if day >= since:
            frames.append(read_snapshot(p))
    frames = [f for f in frames if not f.empty]
    return pd.concat(frames, ignore_index=True) if frames else frame([])


def run(cfg: Any, today: date | None = None) -> Path | None:  # pragma: no cover - network
    """Process pending filing days, write raw purchases, the report and (if any) alert.md."""
    from compute_curve.http import PoliteClient  # noqa: PLC0415
    from compute_curve.storage.raw_store import write_snapshot  # noqa: PLC0415

    today = today or datetime.now(UTC).date()
    raw = cfg.path("data") / "raw"
    rules = Rules()
    new_days: list[str] = []
    with PoliteClient(user_agent=user_agent(), min_interval_s=MIN_INTERVAL_S, timeout_s=60) as cl:
        for d in pending_days(today, done_days(raw)):
            df = fetch_day(cl, d)
            if df is None:
                continue
            write_snapshot(raw, SOURCE, datetime(d.year, d.month, d.day, tzinfo=UTC), df)
            new_days.append(f"{d:%Y-%m-%d}")
    out = cfg.path("reports") / "insiders"
    out.mkdir(parents=True, exist_ok=True)
    alert_file = out / "alert.md"
    alert_file.unlink(missing_ok=True)
    if not new_days:
        return None
    hist = load_history(raw, today - timedelta(days=60))
    al = alerts(hist, set(new_days), rules)
    fresh = hist.loc[hist["filed_date"].isin(new_days)]
    md = render(al, fresh, new_days, rules)
    (out / "latest.md").write_text(md)
    (out / f"insiders_{new_days[-1].replace('-', '')}.md").write_text(md)
    if not al.empty:
        alert_file.write_text(md + "\n---\n_Generated by the compute-curve insider tracker._\n")
    return out / "latest.md"
