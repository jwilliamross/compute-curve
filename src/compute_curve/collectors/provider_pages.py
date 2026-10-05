"""Direct list-price collectors for neocloud pricing pages.

Each class reads one public pricing page that the audit approved
(docs/data_sources.md): robots.txt allows the path and the site terms do not
prohibit reading it. Parsers are deliberately strict: if the expected
structure is not found they return no rows and a note, rather than guessing.

All prices are on-demand (or spot/reserved where the page labels them) list
prices in USD per GPU-hour; instance prices are divided by the GPU count.
"""

from __future__ import annotations

import re
from datetime import UTC, date, datetime
from typing import Any

from compute_curve.collectors.base import CollectedBatch, html_to_lines, parse_usd
from compute_curve.http import PoliteClient
from compute_curve.schema import (
    Availability,
    GpuModel,
    PriceObservation,
    Term,
    canonical_gpu_model,
    gpu_variant,
)


def _obs(
    *,
    provider: str,
    source: str,
    name: str,
    price: float,
    term: Term,
    ts_observed: datetime,
    snapshot_id: str,
    url: str,
    gpus: int | None,
    region: str | None,
    config: str | None = None,
    variant: str | None = None,
) -> PriceObservation:
    model = canonical_gpu_model(name)
    return PriceObservation(
        ts_observed=ts_observed,
        provider=provider,
        gpu_model=model,
        config=config or (f"{gpus}x {name}" if gpus else name),
        price_usd_per_gpu_hour=price,
        term=term,
        region=region,
        availability=Availability.UNKNOWN,
        source=source,
        snapshot_id=snapshot_id,
        gpu_variant=variant or gpu_variant(name),
        gpus_per_instance=gpus,
        listing_id=f"{provider}:{config or name}:{gpus or ''}:{term.value}",
        source_url=url,
        price_basis="gpu_hour_list",
    )


def _relevant(name: str) -> bool:
    return canonical_gpu_model(name) in (GpuModel.H100, GpuModel.H200, GpuModel.B200)


class _PageCollector:
    source_id = ""
    url = ""
    terms_url = ""
    attribution = ""

    def fetch(self, client: PoliteClient) -> Any:
        resp = client.get(self.url)
        resp.raise_for_status()
        return resp.text


# ---------------------------------------------------------------------------
# Nebius (Markdown docs page)
# ---------------------------------------------------------------------------
_NEB_SECTION = re.compile(r"^####\s+(?P<title>.+)$", re.MULTILINE)
_NEB_REGION = re.compile(r"available in the `(?P<r>[a-z0-9-]+)`")
_NEB_HEADER = re.compile(
    r"\|\s*\*\*Item(?:\s+—\s+(?P<when>from|before)\s+(?P<date>[A-Za-z]+ \d{1,2}, \d{4}))?\*\*"
)
_NEB_ROW = re.compile(
    r"^\s*\|\s*(?P<item>[^|]+?)\s*\|\s*\\?\$(?P<price>[0-9.,]+)\s*\|\s*1 GPU hour\s*\|",
    re.MULTILINE,
)


def nebius_region(code: str | None) -> str | None:
    if not code:
        return None
    prefix = code.split("-")[0]
    return {"us": "US", "eu": "EU", "me": "ME", "uk": "UK"}.get(prefix, prefix.upper())


class NebiusCollector(_PageCollector):
    source_id = "nebius"
    url = "https://docs.nebius.com/compute/resources/pricing.md"
    terms_url = "https://nebius.com/legal/terms-of-use"
    attribution = "Nebius pricing documentation"

    def __init__(self, today: date | None = None) -> None:
        self.today = today

    def normalize(self, payload: Any, ts_observed: datetime, snapshot_id: str) -> CollectedBatch:
        text = str(payload or "")
        today = self.today or ts_observed.date()
        rows: list[PriceObservation] = []
        heads = list(_NEB_SECTION.finditer(text))
        for i, h in enumerate(heads):
            title = h.group("title").replace("®", "").replace("™", "").strip()
            gpu_name = title.split(",")[0].strip()
            if not _relevant(gpu_name):
                continue
            body = text[h.end() : heads[i + 1].start() if i + 1 < len(heads) else len(text)]
            usd = body.split('<Tab title="ILS">')[0]
            region_m = _NEB_REGION.search(body)
            region = nebius_region(region_m.group("r") if region_m else None)
            block = _effective_block(usd, today)
            for m in _NEB_ROW.finditer(block):
                item = m.group("item").replace("®", "").strip()
                term = Term.SPOT if item.lower().startswith("preemptible") else Term.ON_DEMAND
                rows.append(
                    _obs(
                        provider="nebius",
                        source=self.source_id,
                        name=gpu_name,
                        price=float(m.group("price").replace(",", "")),
                        term=term,
                        ts_observed=ts_observed,
                        snapshot_id=snapshot_id,
                        url=self.url,
                        gpus=1,
                        region=region,
                        config=title,
                        variant="SXM",  # Nebius "NVLink" platforms are HGX (SXM) boards
                    )
                )
        notes = [] if rows else ["no H100/B200 rows parsed; page layout may have changed"]
        return CollectedBatch(listings=rows, notes=notes)


def _effective_block(usd_tab: str, today: date) -> str:
    """The price table in force on ``today`` when a page lists before/from dates."""
    marks = list(_NEB_HEADER.finditer(usd_tab))
    if not marks:
        return usd_tab
    chosen = 0
    for k, m in enumerate(marks):
        when, d = m.group("when"), m.group("date")
        if when is None:
            chosen = k
            break
        eff = datetime.strptime(d, "%B %d, %Y").replace(tzinfo=UTC).date()
        if (when == "from" and today >= eff) or (when == "before" and today < eff):
            chosen = k
            break
    start = marks[chosen].end()
    end = marks[chosen + 1].start() if chosen + 1 < len(marks) else len(usd_tab)
    return usd_tab[start:end]


# ---------------------------------------------------------------------------
# Lambda (HTML)
# ---------------------------------------------------------------------------
class LambdaCollector(_PageCollector):
    source_id = "lambda"
    url = "https://lambda.ai/pricing"
    terms_url = "https://lambda.ai/legal/terms-of-service"
    attribution = "Lambda public pricing page"
    SIZES = (8, 4, 2, 1)

    def normalize(self, payload: Any, ts_observed: datetime, snapshot_id: str) -> CollectedBatch:
        lines = html_to_lines(str(payload or ""))
        rows: list[PriceObservation] = []
        notes: list[str] = []
        start = next(
            (
                k
                for k in range(len(lines) - 3)
                if lines[k : k + 4] == ["8x", "4x", "2x", "1x"] or lines[k] == "8x4x2x1x"
            ),
            None,
        )
        if start is None:
            return CollectedBatch(notes=["instance size tabs not found"])
        table = -1
        i = start
        while i < len(lines) and table < len(self.SIZES):
            line = lines[i]
            if line == "PRICE/GPU/HR*":
                table += 1
            elif table >= 0 and line.startswith("NVIDIA ") and _relevant(line):
                price = next(
                    (parse_usd(x) for x in lines[i + 1 : i + 7] if x.startswith("$")), None
                )
                if price is not None and table < len(self.SIZES):
                    rows.append(
                        _obs(
                            provider="lambda",
                            source=self.source_id,
                            name=line.removeprefix("NVIDIA "),
                            price=price,
                            term=Term.ON_DEMAND,
                            ts_observed=ts_observed,
                            snapshot_id=snapshot_id,
                            url=self.url,
                            gpus=self.SIZES[table],
                            region=None,
                        )
                    )
            elif line.startswith("* plus applicable") and table == len(self.SIZES) - 1:
                break
            i += 1
        if table != len(self.SIZES) - 1:
            notes.append(f"expected {len(self.SIZES)} instance tables, saw {table + 1}")
            rows = []
        return CollectedBatch(listings=rows, notes=notes)


# ---------------------------------------------------------------------------
# CoreWeave (HTML)
# ---------------------------------------------------------------------------
_CW_NAME = re.compile(r"^NVIDIA HGX (H100|H200|B200)$")


class CoreWeaveCollector(_PageCollector):
    source_id = "coreweave"
    url = "https://www.coreweave.com/pricing"
    terms_url = "https://docs.coreweave.com/policies/terms-of-service/terms-of-use"
    attribution = "CoreWeave public pricing page"

    def normalize(self, payload: Any, ts_observed: datetime, snapshot_id: str) -> CollectedBatch:
        lines = html_to_lines(str(payload or ""))
        try:
            start = lines.index("On-demand GPU instances")
        except ValueError:
            return CollectedBatch(notes=["GPU instance section not found"])
        end = next(
            (k for k in range(start, len(lines)) if lines[k] == "On-demand CPU instances"),
            len(lines),
        )
        region: str | None = None
        rows: list[PriceObservation] = []
        seen: set[tuple[str, str | None, str]] = set()
        for k in range(start, end):
            line = lines[k]
            if line.upper().startswith("REGION:"):
                r = line.split(":", 1)[1].strip().upper()
                region = {"NORTH AMERICA": "NA", "EUROPE": "EU"}.get(r, r)
                continue
            m = _CW_NAME.match(line)
            if not m or k + 2 >= end or not lines[k + 1].startswith("On-Demand Price:"):
                continue
            gpus = _gpu_count(lines, k)
            if gpus is None:
                continue
            card = lines[k + 1 : k + 9]
            for label, term in (("On-Demand Price:", Term.ON_DEMAND), ("Spot Price:", Term.SPOT)):
                idx = next((j for j, x in enumerate(card) if x.startswith(label)), None)
                if idx is None:
                    continue
                # The amount is either on the label line or on the next one.
                price = parse_usd(card[idx]) or (
                    parse_usd(card[idx + 1]) if idx + 1 < len(card) else None
                )
                key = (m.group(1), region, term.value)
                if price is None or key in seen:
                    continue
                seen.add(key)
                rows.append(
                    _obs(
                        provider="coreweave",
                        source=self.source_id,
                        name=f"HGX {m.group(1)}",
                        price=price / gpus,
                        term=term,
                        ts_observed=ts_observed,
                        snapshot_id=snapshot_id,
                        url=self.url,
                        gpus=gpus,
                        region=region,
                        variant="SXM",
                    )
                )
        return CollectedBatch(listings=rows, notes=[] if rows else ["no HGX H100/B200 rows parsed"])


def _gpu_count(lines: list[str], k: int) -> int | None:
    """GPU count printed just before the 'GPU Count' label after a price card."""
    for j in range(k + 1, min(k + 15, len(lines))):
        if lines[j] == "GPU Count" and lines[j - 1].isdigit():
            return int(lines[j - 1])
    return None


# ---------------------------------------------------------------------------
# Hyperstack (HTML)
# ---------------------------------------------------------------------------
class HyperstackCollector(_PageCollector):
    source_id = "hyperstack"
    url = "https://www.hyperstack.cloud/gpu-pricing"
    terms_url = "https://www.hyperstack.cloud/terms-and-conditions"
    attribution = "Hyperstack public pricing page"

    def normalize(self, payload: Any, ts_observed: datetime, snapshot_id: str) -> CollectedBatch:
        lines = html_to_lines(str(payload or ""))
        rows: list[PriceObservation] = []
        term = Term.ON_DEMAND
        seen: set[tuple[str, str]] = set()
        for k, line in enumerate(lines):
            if line == "Reservation Pricing" or (
                line == "Reservation" and k + 1 < len(lines) and lines[k + 1] == "Pricing"
            ):
                term = Term.RESERVED
                continue
            if not (line.startswith("NVIDIA ") and _relevant(line)) or "GB200" in line:
                continue
            window = lines[k + 1 : k + 6]
            # On-demand rows are: name, VRAM, vCPU, RAM, $price. Reserved: name, $price.
            price_line = next((x for x in window if x.startswith("$")), None)
            if price_line is None:
                continue
            if term is Term.ON_DEMAND and not window[0].isdigit():
                continue  # navigation/menu text, not a price row
            key = (line, term.value)
            if key in seen:
                continue
            seen.add(key)
            price = parse_usd(price_line)
            if price is None:
                continue
            rows.append(
                _obs(
                    provider="hyperstack",
                    source=self.source_id,
                    name=line.removeprefix("NVIDIA "),
                    price=price,
                    term=term,
                    ts_observed=ts_observed,
                    snapshot_id=snapshot_id,
                    url=self.url,
                    gpus=1,
                    region=None,
                    config=line + (" (reserved, starting from)" if term is Term.RESERVED else ""),
                )
            )
        return CollectedBatch(listings=rows, notes=[] if rows else ["no H100/B200 rows parsed"])


# ---------------------------------------------------------------------------
# Verda, formerly DataCrunch (HTML)
# ---------------------------------------------------------------------------
_VERDA_ROW = re.compile(r"^(?P<n>\d+)x (?P<name>(?:H100|H200|B200)\S*(?: \S+)*?)\s*(?P<mem>\d+GB)$")


class VerdaCollector(_PageCollector):
    source_id = "verda"
    url = "https://verda.com/pricing"
    terms_url = "https://verda.com/terms"
    attribution = "Verda (formerly DataCrunch) public pricing page"

    def normalize(self, payload: Any, ts_observed: datetime, snapshot_id: str) -> CollectedBatch:
        lines = html_to_lines(str(payload or ""))
        rows: list[PriceObservation] = []
        seen: set[tuple[int, str, str]] = set()
        for k, line in enumerate(lines):
            m = _VERDA_ROW.match(line.strip())
            if not m:
                continue
            prices = [
                x
                for x in lines[k + 1 : k + 9]
                if x.strip().startswith("$") and x.strip().endswith("/h")
            ]
            if not prices:
                continue
            n = int(m.group("n"))
            name = m.group("name")
            for p_text, term in zip(prices[:2], (Term.ON_DEMAND, Term.SPOT), strict=False):
                price = parse_usd(p_text)
                key = (n, name, term.value)
                if price is None or key in seen:
                    continue
                seen.add(key)
                rows.append(
                    _obs(
                        provider="verda",
                        source=self.source_id,
                        name=name,
                        price=price / n,
                        term=term,
                        ts_observed=ts_observed,
                        snapshot_id=snapshot_id,
                        url=self.url,
                        gpus=n,
                        region=None,  # the page does not state a region per price
                        config=f"{n}x {name} {m.group('mem')}",
                        variant="SXM" if "SXM" in name.upper() else None,
                    )
                )
        return CollectedBatch(listings=rows, notes=[] if rows else ["no H100/B200 rows parsed"])
