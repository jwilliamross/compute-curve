"""Collector interface and shared helpers.

A collector has two parts:

* ``fetch(client)``: performs the HTTP request(s) and returns the payload.
  This is the only part that touches the network.
* ``normalize(payload, ts_observed, snapshot_id)``: a pure function from the
  payload to validated rows. Tests exercise it with hand-written fixtures.

Every collector declares the terms URL it was approved under
(``docs/data_sources.md``) and the attribution string its licence requires.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from html.parser import HTMLParser
from typing import Any, Protocol

from compute_curve.http import PoliteClient
from compute_curve.schema import IndexObservation, PriceObservation

# Providers whose own terms prohibit automated collection or index construction
# from their prices (docs/data_sources.md). Rows for them are dropped even when
# they arrive through a third-party aggregator.
DEFAULT_EXCLUDED_PROVIDERS: frozenset[str] = frozenset({"vast", "runpod"})

_ALIASES = {
    "vastai": "vast",
    "datacrunch": "verda",
    "lambdalabs": "lambda",
    "lambdacloud": "lambda",
    "massedcompute": "massedcompute",
    "voltagepark": "voltagepark",
    "googlecloud": "gcp",
    "google": "gcp",
    "microsoftazure": "azure",
    "amazonwebservices": "aws",
    "oraclecloud": "oci",
    "oracle": "oci",
}


def canonical_provider(name: str) -> str:
    """Lowercase alphanumeric provider id with known aliases folded."""
    key = re.sub(r"[^a-z0-9]", "", name.lower())
    return _ALIASES.get(key, key)


@dataclass(frozen=True)
class CollectedBatch:
    listings: list[PriceObservation] = field(default_factory=list)
    indices: list[IndexObservation] = field(default_factory=list)
    n_dropped: int = 0
    notes: list[str] = field(default_factory=list)


class Collector(Protocol):
    source_id: str
    terms_url: str
    attribution: str

    def fetch(self, client: PoliteClient) -> Any: ...

    def normalize(
        self, payload: Any, ts_observed: datetime, snapshot_id: str
    ) -> CollectedBatch: ...


class _TextExtractor(HTMLParser):
    """Visible text of an HTML document, one text node per line."""

    _SKIP = frozenset({"script", "style", "noscript", "svg", "template"})

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self._SKIP:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in self._SKIP and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0:
            text = " ".join(data.split())
            if text:
                self.parts.append(text)


def html_to_lines(html: str) -> list[str]:
    """Visible text nodes of ``html`` in document order."""
    parser = _TextExtractor()
    parser.feed(html)
    parser.close()
    return parser.parts


def parse_usd(text: str) -> float | None:
    """First USD amount in ``text`` (e.g. '$3.99', '$68.80 / Hour'), or None."""
    m = re.search(r"\$\s*([0-9][0-9,]*\.?[0-9]*)", text)
    if not m:
        return None
    try:
        return float(m.group(1).replace(",", ""))
    except ValueError:
        return None
