"""GetDeploying weekly GPU price dataset.

Source: https://getdeploying.com/dataset/gpu-prices/<slug>.csv (CSV, keyless).
Licence: CC BY 4.0, attribution "GetDeploying, GPU rental price history,
https://getdeploying.com/gpus, CC BY 4.0".

Each row is a weekly aggregate (median, min, max across offerings) per
billing type. Rows are stored as :class:`IndexObservation`. The publisher
serves its whole history on every fetch; each fetch is stored as a vintage
so revisions stay visible. Note: early weeks (from 2025-10-06) repeat
identical values, which suggests back-filled rather than observed history
(docs/data_sources.md).
"""

from __future__ import annotations

import csv
import io
import json
from datetime import UTC, datetime
from typing import Any

from compute_curve.collectors.base import CollectedBatch
from compute_curve.http import PoliteClient
from compute_curve.schema import GpuModel, IndexObservation, Term

BASE = "https://getdeploying.com/dataset/gpu-prices"
SLUGS: dict[str, GpuModel] = {
    "nvidia-h100": GpuModel.H100,
    "nvidia-h200": GpuModel.H200,
    "nvidia-b200": GpuModel.B200,
}
TERMS = {
    "ON_DEMAND": Term.ON_DEMAND,
    "SPOT": Term.SPOT,
    "RESERVATION": Term.RESERVED,
}
ATTRIBUTION = "GetDeploying, GPU rental price history, https://getdeploying.com/gpus, CC BY 4.0"


class GetDeployingCollector:
    source_id = "getdeploying"
    terms_url = "https://getdeploying.com/dataset"
    attribution = ATTRIBUTION

    def fetch(self, client: PoliteClient) -> Any:
        out: dict[str, str] = {}
        for slug in SLUGS:
            resp = client.get(f"{BASE}/{slug}.csv")
            if resp.status_code == 404:
                continue
            resp.raise_for_status()
            out[slug] = resp.text
        return out

    def normalize(self, payload: Any, ts_observed: datetime, snapshot_id: str) -> CollectedBatch:
        rows: list[IndexObservation] = []
        dropped = 0
        for slug, text in (payload or {}).items():
            model = SLUGS.get(slug)
            if model is None:
                continue
            for rec in csv.DictReader(io.StringIO(text)):
                obs = _row(rec, slug, model, ts_observed, snapshot_id)
                if obs is None:
                    dropped += 1
                else:
                    rows.append(obs)
        return CollectedBatch(indices=rows, n_dropped=dropped)


def _f(x: str | None) -> float | None:
    try:
        return float(x) if x not in (None, "") else None
    except ValueError:
        return None


def _i(x: str | None) -> int | None:
    v = _f(x)
    return int(v) if v is not None else None


def _row(
    rec: dict[str, str], slug: str, model: GpuModel, ts_observed: datetime, snapshot_id: str
) -> IndexObservation | None:
    billing = (rec.get("billing_type") or "").upper()
    term = TERMS.get(billing)
    median = _f(rec.get("median_price"))
    if term is None or median is None or median <= 0:
        return None
    months = rec.get("reservation_months") or ""
    suffix = f" {months}m" if months else ""
    try:
        as_of = datetime.strptime(rec["date"], "%Y-%m-%d").replace(tzinfo=UTC)
    except (KeyError, ValueError):
        return None
    return IndexObservation(
        ts_observed=ts_observed,
        source="getdeploying",
        snapshot_id=snapshot_id,
        index_name=f"GetDeploying {slug} {billing}{suffix} weekly median",
        gpu_model=model,
        term=term,
        as_of=as_of,
        value=median,
        band_low=_f(rec.get("min_price")),
        band_high=_f(rec.get("max_price")),
        n_providers=_i(rec.get("provider_count")),
        n_listings=_i(rec.get("offering_count")),
        license="CC-BY-4.0",
        raw_json=json.dumps(
            {
                "provider_median_price": _f(rec.get("provider_median_price")),
                "attribution": ATTRIBUTION,
            },
            sort_keys=True,
        ),
    )
