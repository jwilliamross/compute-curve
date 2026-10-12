"""Claude-assisted extraction of GPU list prices from archived pricing pages (D58).

The model only proposes rows. Every row must carry a verbatim quote from the
page that contains its price; ``collectors.wayback.verify_row`` drops any row
whose quote is not on the page, whose price is not in the quote, or whose GPU
is not named nearby. Spend is metered per call into an append-only ledger
(``data/llm_spend.jsonl``) and capped per run and in total.

Needs ``ANTHROPIC_API_KEY`` in the environment. It is never logged or stored.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel

SYSTEM = (
    "You read the visible text of an archived cloud GPU pricing page and list its "
    "published prices for NVIDIA H100, H200 and B200 GPUs only (any form factor: SXM, "
    "PCIe, NVL). Ignore every other GPU, including GH200, GB200, B300 and A100. "
    "For each price give: the GPU name as written; how many GPUs the priced unit has; "
    "the price in US dollars; whether it is per GPU-hour or per instance-hour; the term "
    "(on_demand, spot or reserved; a commitment or contract price is reserved); and "
    "`quote`, an exact, contiguous copy of the shortest page text that contains the "
    "price. Copy the quote character for character; never paraphrase, reformat or "
    "combine separate lines. If a price is ambiguous, not in US dollars, 'contact "
    "sales', or you are unsure which GPU it belongs to, leave it out. An empty list "
    "is a correct answer for a page without such prices."
)


class PriceRow(BaseModel):
    gpu_name: str
    gpus_per_unit: int
    price_usd: float
    unit: Literal["per_gpu_hour", "per_instance_hour"]
    term: Literal["on_demand", "spot", "reserved"]
    quote: str


class PageExtraction(BaseModel):
    rows: list[PriceRow]


@dataclass(frozen=True)
class Pricing:
    """USD per million tokens (docs/decisions.md D58; check before changing models)."""

    input_per_mtok: float
    output_per_mtok: float

    def cost(self, input_tokens: int, output_tokens: int) -> float:
        return (input_tokens * self.input_per_mtok + output_tokens * self.output_per_mtok) / 1e6


@dataclass(frozen=True)
class SpendEntry:
    ts: str
    run_id: str
    provider: str
    capture: str
    digest: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    n_proposed: int
    n_kept: int
    truncated: bool
    status: str


def read_ledger(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def append_ledger(path: Path, entry: SpendEntry) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(asdict(entry), sort_keys=True) + "\n")


def spent(entries: list[dict[str, Any]], run_id: str | None = None) -> float:
    return float(sum(e["cost_usd"] for e in entries if run_id is None or e.get("run_id") == run_id))


def done_digests(entries: list[dict[str, Any]]) -> set[tuple[str, str]]:
    """(provider, digest) pairs already settled: extracted, or no GPU text to send."""
    return {
        (e["provider"], e["digest"]) for e in entries if e.get("status") in ("ok", "no_gpu_text")
    }


def within_budget(
    entries: list[dict[str, Any]], run_id: str, worst_case: float, total: float, per_run: float
) -> bool:
    """True if one more call costing at most ``worst_case`` stays within both caps."""
    return spent(entries) + worst_case <= total and spent(entries, run_id) + worst_case <= per_run


def user_prompt(provider: str, url: str, captured: datetime, text: str) -> str:
    return (
        f"Provider: {provider}\nPage: {url}\nArchived: {captured:%Y-%m-%d %H:%M} UTC\n\n"
        f"<page_text>\n{text}\n</page_text>"
    )


def extract(  # pragma: no cover - calls the Claude API
    client: Any,
    model: str,
    effort: str,
    max_tokens: int,
    prompt: str,
) -> tuple[PageExtraction | None, int, int, str]:
    """(parsed rows or None, input tokens, output tokens, status) for one page."""
    import anthropic  # noqa: PLC0415

    try:
        resp = client.messages.parse(
            model=model,
            max_tokens=max_tokens,
            system=SYSTEM,
            output_config={"effort": effort},
            messages=[{"role": "user", "content": prompt}],
            output_format=PageExtraction,
        )
    except anthropic.BadRequestError as exc:
        return None, 0, 0, f"bad_request: {exc.message[:120]}"
    usage = resp.usage
    # Conservative: cache writes and reads are metered at the full input price.
    n_in = (
        int(usage.input_tokens or 0)
        + int(usage.cache_creation_input_tokens or 0)
        + int(usage.cache_read_input_tokens or 0)
    )
    n_out = int(usage.output_tokens or 0)
    if resp.stop_reason == "refusal":
        return None, n_in, n_out, "refusal"
    if resp.stop_reason == "max_tokens":
        return None, n_in, n_out, "max_tokens"
    return resp.parsed_output, n_in, n_out, "ok"
