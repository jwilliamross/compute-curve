"""Collector interface.

A collector has two parts:

* ``fetch(client)``: performs the HTTP request(s) and returns the parsed
  payload. This is the only part that touches the network.
* ``normalize(payload, ts_observed, snapshot_id)``: a pure function from the
  payload to validated :class:`PriceObservation` rows. Tests exercise it with
  recorded fixtures.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol

from compute_curve.http import PoliteClient
from compute_curve.schema import PriceObservation


@dataclass(frozen=True)
class CollectorResult:
    source: str
    ts_observed: datetime
    observations: list[PriceObservation]
    n_raw_records: int
    n_dropped: int
    notes: list[str] = field(default_factory=list)


class Collector(Protocol):
    source_id: str
    terms_url: str

    def fetch(self, client: PoliteClient) -> Any: ...

    def normalize(
        self, payload: Any, ts_observed: datetime, snapshot_id: str
    ) -> tuple[list[PriceObservation], int]:
        """Return (observations, number of raw records dropped)."""
        ...
