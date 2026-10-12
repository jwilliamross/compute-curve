"""Archived provider pricing pages from the Wayback Machine (D58).

For each approved provider page, the CDX API lists captures with distinct
content (``collapse=digest``, HTTP 200 only). Each capture's original HTML
(``<timestamp>id_/<url>``) is reduced to visible text, Claude proposes the
H100/H200/B200 prices on it (``compute_curve.llm_extract``), and only rows
that pass ``verify_row`` are kept:

- the row's quote appears verbatim on the page (whitespace-normalized);
- the price appears as a number in that quote;
- the GPU is named in the quote or in the 400 characters before it.

``ts_observed`` is the capture time: the archive shows the price was public
then. Rows are research-only (stored under ``data/raw/archive``, outside the
listings the own index reads) until a pre-registered use says otherwise.
Providers: only pages whose live versions we already collect under their
terms (docs/data_sources.md). Never Vast.ai, RunPod or Together.
"""

from __future__ import annotations

import contextlib
import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlencode

from compute_curve.collectors.base import html_to_lines
from compute_curve.llm_extract import PriceRow
from compute_curve.schema import (
    Availability,
    GpuModel,
    PriceObservation,
    Term,
    canonical_gpu_model,
    gpu_variant,
)
from compute_curve.storage.raw_store import snapshot_id

CDX = "https://web.archive.org/cdx/search/cdx"
ARCHIVE = "https://web.archive.org/web/{ts}id_/{url}"
ARCHIVE_DIR = "archive"
FORBIDDEN = frozenset({"vast", "runpod", "together"})
KEEP = frozenset({GpuModel.H100, GpuModel.H200, GpuModel.B200})
WINDOW = 400
_NUM = re.compile(r"\d+(?:,\d{3})*(?:\.\d+)?")
_GPU_TOKEN = {GpuModel.H100: "H100", GpuModel.H200: "H200", GpuModel.B200: "B200"}
_HINT = re.compile(r"\$|H100|H200|B200|GPU|hour|/hr|\bhr\b", re.IGNORECASE)


@dataclass(frozen=True)
class Capture:
    ts: datetime
    original: str
    digest: str

    @property
    def stamp(self) -> str:
        return f"{self.ts:%Y%m%d%H%M%S}"

    @property
    def archive_url(self) -> str:
        return ARCHIVE.format(ts=self.stamp, url=self.original)


def source_name(provider: str) -> str:
    return f"wayback_{provider}"


def cdx_query(url: str, start: str, end: str) -> str:
    params = {
        "url": url,
        "from": start,
        "to": end,
        "output": "json",
        "fl": "timestamp,original,statuscode,digest",
        "filter": "statuscode:200",
        "collapse": "digest",
    }
    return f"{CDX}?{urlencode(params)}"


def parse_cdx(payload: Any) -> list[Capture]:
    """Captures from a CDX JSON reply (first row is the header); oldest first."""
    if not isinstance(payload, list) or len(payload) < 2:
        return []
    head = [str(h) for h in payload[0]]
    out = []
    for row in payload[1:]:
        rec = dict(zip(head, row, strict=False))
        if rec.get("statuscode") != "200":
            continue
        try:
            ts = datetime.strptime(str(rec["timestamp"]), "%Y%m%d%H%M%S").replace(tzinfo=UTC)
        except (KeyError, ValueError):
            continue
        out.append(Capture(ts, str(rec.get("original", "")), str(rec.get("digest", ""))))
    return sorted(out, key=lambda c: c.ts)


def page_text(html: str, max_chars: int) -> tuple[str, bool]:
    """Visible text; if longer than ``max_chars``, keep price-like lines and 3 neighbours.

    Returns (text, truncated). Truncation is recorded in the spend ledger.
    """
    lines = [ln.strip() for ln in html_to_lines(html) if ln.strip()]
    text = "\n".join(lines)
    if len(text) <= max_chars:
        return text, False
    keep = set()
    for i, ln in enumerate(lines):
        if _HINT.search(ln):
            keep.update(range(max(0, i - 3), min(len(lines), i + 4)))
    text = "\n".join(lines[i] for i in sorted(keep))
    return text[:max_chars], True


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def _supported(row: PriceRow, model: GpuModel, text: str) -> bool:
    """Quote on the page, price in the quote, GPU named in or just before the quote."""
    page, quote = _norm(text), _norm(row.quote)
    pos = page.find(quote)
    if len(quote) < 4 or pos < 0:
        return False
    nums = [float(n.replace(",", "")) for n in _NUM.findall(quote)]
    window = page[max(0, pos - WINDOW) : pos + len(quote)]
    return any(abs(n - row.price_usd) < 0.006 for n in nums) and (
        _GPU_TOKEN[model] in window.upper()
    )


def verify_row(row: PriceRow, text: str) -> tuple[GpuModel, float] | None:
    """(GPU family, USD per GPU-hour) if the row is supported by the page text, else None."""
    model = canonical_gpu_model(row.gpu_name)
    if model not in KEEP or row.gpus_per_unit < 1 or not _supported(row, model, text):
        return None
    per_gpu = row.price_usd / (row.gpus_per_unit if row.unit == "per_instance_hour" else 1)
    return (model, per_gpu) if 0.05 < per_gpu < 100 else None


def to_observation(
    row: PriceRow,
    model: GpuModel,
    per_gpu: float,
    provider: str,
    cap: Capture,
    extractor: str,
    extracted_at: datetime,
) -> PriceObservation:
    src = source_name(provider)
    term = {"on_demand": Term.ON_DEMAND, "spot": Term.SPOT, "reserved": Term.RESERVED}[row.term]
    return PriceObservation(
        ts_observed=cap.ts,
        provider=provider,
        gpu_model=model,
        config=f"{row.gpus_per_unit}x {row.gpu_name}",
        price_usd_per_gpu_hour=per_gpu,
        term=term,
        region=None,
        availability=Availability.UNKNOWN,
        source=src,
        snapshot_id=snapshot_id(src, cap.ts),
        ts_source=cap.ts,
        gpu_variant=gpu_variant(row.gpu_name),
        gpus_per_instance=row.gpus_per_unit,
        listing_id=f"{provider}:{row.gpu_name}:{row.gpus_per_unit}:{row.term}",
        source_url=cap.archive_url,
        price_basis=("instance_hour_list_div_gpus" if row.unit == "per_instance_hour" else "list"),
        raw_json=json.dumps(
            {
                "quote": row.quote,
                "unit": row.unit,
                "price_usd": row.price_usd,
                "digest": cap.digest,
                "extractor": extractor,
                "extracted_at": extracted_at.isoformat(),
            },
            sort_keys=True,
        ),
    )


# ---------------------------------------------------------------------------
# Runner (network and Claude API; run from the manual GitHub workflow)
# ---------------------------------------------------------------------------
def has_gpu_text(text: str) -> bool:
    up = text.upper()
    return any(tok in up for tok in _GPU_TOKEN.values())


@dataclass
class _Run:
    """State shared by one backfill run."""

    cfg: Any
    client: Any
    llm: Any
    run_id: str
    ledger: Any
    raw_dir: Any
    pricing: Any
    worst: float


def _captures(run: _Run, url: str, end: str) -> tuple[list[Capture], str]:  # pragma: no cover
    import httpx  # noqa: PLC0415

    from compute_curve.http import RobotsDisallowedError  # noqa: PLC0415

    try:
        resp = run.client.get(cdx_query(url, run.cfg.wayback.start, end))
        resp.raise_for_status()
        return parse_cdx(resp.json()), ""
    except RobotsDisallowedError:
        return [], "robots.txt disallowed or unreachable"
    except (httpx.HTTPError, ValueError) as exc:
        return [], f"CDX failed: {type(exc).__name__}"


def _extract_page(  # pragma: no cover - Claude API
    run: _Run, provider: str, cap: Capture, text: str
) -> tuple[str, int, int, int, list[PriceObservation]]:
    """(status, input tokens, output tokens, rows proposed, verified observations)."""
    from compute_curve import llm_extract as lx  # noqa: PLC0415
    from compute_curve.timeutil import utc_now  # noqa: PLC0415

    if not has_gpu_text(text):
        return "no_gpu_text", 0, 0, 0, []
    wb = run.cfg.wayback
    prompt = lx.user_prompt(provider, cap.original, cap.ts, text)
    parsed, n_in, n_out, status = lx.extract(run.llm, wb.model, wb.effort, wb.max_tokens, prompt)
    rows = parsed.rows if parsed else []
    now = utc_now()
    kept = []
    for r in rows:
        ok = verify_row(r, text)
        if ok is not None:
            kept.append(to_observation(r, ok[0], ok[1], provider, cap, wb.model, now))
    return status, n_in, n_out, len(rows), kept


def _store(run: _Run, provider: str, cap: Capture, kept: list[PriceObservation]) -> int:
    from compute_curve.storage.raw_store import (  # noqa: PLC0415
        ImmutableWriteError,
        observations_to_frame,
        write_snapshot,
    )

    uniq = {(o.listing_id, round(o.price_usd_per_gpu_hour, 4)): o for o in kept}
    if uniq:
        with contextlib.suppress(ImmutableWriteError):
            frame = observations_to_frame(list(uniq.values()))
            write_snapshot(run.raw_dir, source_name(provider), cap.ts, frame)
    return len(uniq)


def _process(
    run: _Run, provider: str, cap: Capture, row: dict[str, Any]
) -> None:  # pragma: no cover
    import httpx  # noqa: PLC0415

    from compute_curve import llm_extract as lx  # noqa: PLC0415
    from compute_curve.http import RobotsDisallowedError  # noqa: PLC0415
    from compute_curve.timeutil import utc_now  # noqa: PLC0415

    wb = run.cfg.wayback
    try:
        page = run.client.get(cap.archive_url)
    except (httpx.HTTPError, RobotsDisallowedError) as exc:
        row["note"] = f"some pages failed ({type(exc).__name__})"
        return
    if page.status_code != 200:
        return
    text, truncated = page_text(page.text, wb.max_chars)
    status, n_in, n_out, proposed, kept = _extract_page(run, provider, cap, text)
    row["pages_sent"] += int(status != "no_gpu_text")
    row["rows_kept"] += _store(run, provider, cap, kept)
    lx.append_ledger(
        run.ledger,
        lx.SpendEntry(
            ts=utc_now().isoformat(),
            run_id=run.run_id,
            provider=provider,
            capture=cap.stamp,
            digest=cap.digest,
            model=wb.model,
            input_tokens=n_in,
            output_tokens=n_out,
            cost_usd=round(run.pricing.cost(n_in, n_out), 6),
            n_proposed=proposed,
            n_kept=len(kept),
            truncated=truncated,
            status=status,
        ),
    )


def coverage_order(queues: list[list[Capture]]) -> list[tuple[int, Capture]]:
    """(target index, capture) in the order that spreads a fixed budget widely.

    First the earliest capture of each calendar month of every target, months
    oldest first and targets interleaved; then each month's second capture;
    and so on. A run stopped by the spend cap has covered every target and
    month it reached instead of one target in full.
    """
    keyed = []
    for i, caps in enumerate(queues):
        seen: dict[str, int] = {}
        for c in sorted(caps, key=lambda c: c.ts):
            month = f"{c.ts:%Y-%m}"
            rank = seen.get(month, 0)
            seen[month] = rank + 1
            keyed.append(((rank, month, i, c.ts), (i, c)))
    return [v for _, v in sorted(keyed, key=lambda kv: kv[0])]


def _list_target(
    run: _Run, provider: str, url: str, end: str
) -> tuple[dict[str, Any], list[Capture]]:  # pragma: no cover
    from compute_curve import llm_extract as lx  # noqa: PLC0415

    row: dict[str, Any] = {
        "provider": provider,
        "url": url,
        "captures": 0,
        "new": 0,
        "pages_sent": 0,
        "rows_kept": 0,
        "note": "",
    }
    caps, row["note"] = _captures(run, url, end)
    done = lx.done_digests(lx.read_ledger(run.ledger))
    todo = [c for c in caps if (provider, c.digest) not in done]
    row["captures"], row["new"] = len(caps), len(todo)
    return row, todo


def _drain(
    run: _Run, rows: list[dict[str, Any]], queues: list[list[Capture]]
) -> None:  # pragma: no cover
    from compute_curve import llm_extract as lx  # noqa: PLC0415

    wb = run.cfg.wayback
    for i, cap in coverage_order(queues):
        entries = lx.read_ledger(run.ledger)
        if not lx.within_budget(
            entries, run.run_id, run.worst, wb.budget_total_usd, wb.budget_run_usd
        ):
            for r in rows:
                if r["new"] > r["pages_sent"]:
                    r["note"] = "stopped: spend cap"
            return
        _process(run, rows[i]["provider"], cap, rows[i])


def backfill_wayback(  # pragma: no cover - network and Claude API
    cfg: Any, end: str, dry_run: bool = False, providers: frozenset[str] | None = None
) -> dict[str, Any]:
    """Extract archived prices for every configured target; stop at the spend caps."""
    import os  # noqa: PLC0415

    from compute_curve import llm_extract as lx  # noqa: PLC0415
    from compute_curve.http import PoliteClient  # noqa: PLC0415
    from compute_curve.timeutil import utc_now  # noqa: PLC0415

    wb = cfg.wayback
    if wb is None:
        raise RuntimeError("[wayback] config is required")
    llm = None
    if not dry_run:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        import anthropic  # noqa: PLC0415

        llm = anthropic.Anthropic()
    pricing = lx.Pricing(wb.input_per_mtok, wb.output_per_mtok)
    targets = [
        t
        for t in wb.targets
        if t.provider not in FORBIDDEN and (providers is None or t.provider in providers)
    ]
    ledger = cfg.path("data") / "llm_spend.jsonl"
    with PoliteClient(
        user_agent=cfg.http.user_agent,
        min_interval_s=max(cfg.http.min_interval_s, wb.min_interval_s),
        timeout_s=60.0,
        max_retries=cfg.http.max_retries,
    ) as client:
        run = _Run(
            cfg,
            client,
            llm,
            f"{utc_now():%Y%m%dT%H%M%SZ}",
            ledger,
            cfg.path("data") / "raw" / ARCHIVE_DIR,
            pricing,
            pricing.cost(wb.max_chars // 3, wb.max_tokens),
        )
        listed = [_list_target(run, t.provider, t.url, end) for t in targets]
        rows, queues = [r for r, _ in listed], [q for _, q in listed]
        if not dry_run:
            _drain(run, rows, queues)
    entries = lx.read_ledger(ledger)
    return {
        "run_id": run.run_id,
        "dry_run": dry_run,
        "targets": rows,
        "spent_run_usd": round(lx.spent(entries, run.run_id), 4),
        "spent_total_usd": round(lx.spent(entries), 4),
        "worst_case_per_page_usd": round(run.worst, 4),
    }


def render_summary(s: dict[str, Any]) -> str:
    lines = [
        f"# Wayback backfill, run {s['run_id']}{' (dry run)' if s['dry_run'] else ''}",
        "",
        "Archived pricing pages; Claude-proposed rows kept only if verified against the "
        "page text (D58, docs/wayback_backfill.md). Research-only data.",
        "",
        "| Provider | Page | Distinct captures | Not yet processed | Pages sent | Rows kept "
        "| Note |",
        "|---|---|---|---|---|---|---|",
    ]
    for t in s["targets"]:
        lines.append(
            f"| {t['provider']} | {t['url']} | {t['captures']} | {t['new']} | "
            f"{t['pages_sent']} | {t['rows_kept']} | {t['note']} |"
        )
    if "spent_total_usd" in s:
        lines += [
            "",
            f"Spend this run: USD {s['spent_run_usd']:.2f}; total: USD "
            f"{s['spent_total_usd']:.2f}. Worst case per page: USD "
            f"{s['worst_case_per_page_usd']:.2f}.",
        ]
    return "\n".join(lines) + "\n"
