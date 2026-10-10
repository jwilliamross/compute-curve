"""Idempotent daily snapshot of all approved sources, plus history backfill.

For each enabled collector: if a snapshot for today's UTC date already
exists, skip it (unless ``force``, which appends another immutable
snapshot). Listings go to ``data/raw/listings/<source>/`` and index values to
``data/raw/indices/<source>/``. Every attempt is appended to
``data/collection_log.jsonl``; errors record the exception type and HTTP
status only, never headers or secrets.
"""

from __future__ import annotations

import hashlib
import io
import json
import logging
import re
import zipfile
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import httpx

from compute_curve.collectors.azure_retail import AzureRetailCollector
from compute_curve.collectors.base import CollectedBatch, Collector
from compute_curve.collectors.cgi import SKUS as CGI_SKUS
from compute_curve.collectors.cgi import CgiCollector, fetch_history, normalize_history
from compute_curve.collectors.fastgpu import FastGpuCollector
from compute_curve.collectors.getdeploying import GetDeployingCollector
from compute_curve.collectors.gpurentalprices import (
    GpuRentalPricesCollector,
    normalize_snapshot,
    snapshot_generated_at,
    snapshot_url,
)
from compute_curve.collectors.lium import LiumCollector
from compute_curve.collectors.provider_pages import (
    CoreWeaveCollector,
    HyperstackCollector,
    LambdaCollector,
    NebiusCollector,
    VerdaCollector,
)
from compute_curve.collectors.vast import VastCollector
from compute_curve.config import Config
from compute_curve.http import PoliteClient, RobotsDisallowedError
from compute_curve.storage.raw_store import (
    INDICES,
    LISTINGS,
    index_observations_to_frame,
    observations_to_frame,
    snapshot_id,
    snapshot_path,
    snapshots_for_day,
    write_snapshot,
)
from compute_curve.timeutil import ensure_utc, utc_now

log = logging.getLogger(__name__)

# Sources whose terms require a data licence before any automated collection.
LICENCE_REQUIRED: frozenset[str] = frozenset({"vast"})


@dataclass(frozen=True)
class SnapshotOutcome:
    source: str
    status: str  # written | skipped_exists | error | empty | refused_licence
    paths: tuple[str, ...]
    n_listings: int
    n_indices: int
    n_dropped: int
    detail: str


def registry(cfg: Config) -> dict[str, Collector]:
    """All implemented collectors keyed by source id."""
    excluded = frozenset(cfg.collectors.excluded_providers)
    collectors: list[Collector] = [
        CgiCollector(excluded),
        GetDeployingCollector(),
        GpuRentalPricesCollector(excluded),
        LiumCollector(),
        NebiusCollector(),
        LambdaCollector(),
        CoreWeaveCollector(),
        HyperstackCollector(),
        VerdaCollector(),
        AzureRetailCollector(),
        FastGpuCollector(excluded),
        VastCollector(),
    ]
    return {c.source_id: c for c in collectors}


def make_client(cfg: Config) -> PoliteClient:
    return PoliteClient(
        user_agent=cfg.http.user_agent,
        min_interval_s=cfg.http.min_interval_s,
        timeout_s=cfg.http.timeout_s,
        max_retries=cfg.http.max_retries,
    )


def append_log(log_path: Path, entry: dict[str, object]) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, sort_keys=True, default=str) + "\n")


def write_batch(raw_dir: Path, source: str, ts: datetime, batch: CollectedBatch) -> list[Path]:
    """Write a batch's listings and index values as immutable snapshots."""
    paths: list[Path] = []
    if batch.listings:
        paths.append(
            write_snapshot(raw_dir / LISTINGS, source, ts, observations_to_frame(batch.listings))
        )
    if batch.indices:
        paths.append(
            write_snapshot(
                raw_dir / INDICES, source, ts, index_observations_to_frame(batch.indices)
            )
        )
    return paths


def already_collected(raw_dir: Path, source: str, day: date) -> list[Path]:
    return snapshots_for_day(raw_dir / LISTINGS, source, day) + snapshots_for_day(
        raw_dir / INDICES, source, day
    )


def collect_one(
    collector: Collector,
    client: PoliteClient,
    raw_dir: Path,
    now: datetime,
    force: bool = False,
    licensed: frozenset[str] = frozenset(),
) -> SnapshotOutcome:
    now = ensure_utc(now)
    src = collector.source_id
    if src in LICENCE_REQUIRED and src not in licensed:
        return SnapshotOutcome(
            src, "refused_licence", (), 0, 0, 0, "terms require a data licence (docs/blockers.md)"
        )
    existing = already_collected(raw_dir, src, now.date())
    if existing and not force:
        return SnapshotOutcome(
            src, "skipped_exists", tuple(map(str, existing)), 0, 0, 0, "already collected today"
        )
    try:
        payload = collector.fetch(client)
        ts_obs = utc_now()  # time the response was received
        batch = collector.normalize(payload, ts_obs, snapshot_id(src, ts_obs))
    except RobotsDisallowedError as exc:
        return SnapshotOutcome(src, "error", (), 0, 0, 0, f"robots.txt disallows {exc}")
    except httpx.HTTPStatusError as exc:
        return SnapshotOutcome(src, "error", (), 0, 0, 0, f"HTTP {exc.response.status_code}")
    except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
        return SnapshotOutcome(src, "error", (), 0, 0, 0, type(exc).__name__)
    if not batch.listings and not batch.indices:
        return SnapshotOutcome(
            src, "empty", (), 0, 0, batch.n_dropped, "; ".join(batch.notes) or "no usable rows"
        )
    paths = write_batch(raw_dir, src, ts_obs, batch)
    return SnapshotOutcome(
        src,
        "written",
        tuple(map(str, paths)),
        len(batch.listings),
        len(batch.indices),
        batch.n_dropped,
        "; ".join(batch.notes),
    )


def _log_outcome(
    cfg: Config, reg: dict[str, Collector], out: SnapshotOutcome, now: datetime
) -> None:
    root = cfg.path("data").parent
    append_log(
        cfg.path("data") / "collection_log.jsonl",
        {
            "ts": now.isoformat(),
            "source": out.source,
            "status": out.status,
            "paths": [
                Path(p).relative_to(root).as_posix() if Path(p).is_absolute() else p
                for p in out.paths
            ],
            "n_listings": out.n_listings,
            "n_indices": out.n_indices,
            "n_dropped": out.n_dropped,
            "detail": out.detail,
            "terms_url": reg[out.source].terms_url if out.source in reg else None,
        },
    )


def run_snapshot(
    cfg: Config,
    sources: list[str] | None = None,
    force: bool = False,
    client: PoliteClient | None = None,
) -> list[SnapshotOutcome]:
    reg = registry(cfg)
    enabled = sources or cfg.collectors.enabled
    unknown = set(enabled) - set(reg)
    if unknown:
        raise ValueError(f"unknown sources: {sorted(unknown)}")
    raw_dir = cfg.path("data") / "raw"
    own_client = client is None
    client = client or make_client(cfg)
    outcomes: list[SnapshotOutcome] = []
    try:
        for src in enabled:
            now = utc_now()
            out = collect_one(
                reg[src], client, raw_dir, now, force, frozenset(cfg.collectors.licensed)
            )
            outcomes.append(out)
            _log_outcome(cfg, reg, out, now)
            log.info(
                "%s: %s (%d listings, %d index rows)",
                src,
                out.status,
                out.n_listings,
                out.n_indices,
            )
    finally:
        if own_client:
            client.close()
    return outcomes


# ---------------------------------------------------------------------------
# Backfill: gpurentalprices.com daily snapshots (CC BY 4.0)
# ---------------------------------------------------------------------------
BACKFILL_SOURCE = "gpurentalprices_hist"


def backfill_gpurentalprices(
    cfg: Config,
    start: date,
    end: date,
    client: PoliteClient | None = None,
) -> list[SnapshotOutcome]:
    """Fetch the publisher's archived daily snapshots for ``start..end``.

    Each archived day is written once, stamped with the publisher's
    ``generated_at`` so the file path is unique and re-runs are no-ops.
    Rows keep the publisher's ``fetched_at`` as ``ts_source``.
    """
    raw_dir = cfg.path("data") / "raw"
    reg = registry(cfg)
    own_client = client is None
    client = client or make_client(cfg)
    excluded = frozenset(cfg.collectors.excluded_providers)
    outcomes: list[SnapshotOutcome] = []
    try:
        d = start
        while d <= end:
            outcomes.append(_backfill_day(client, raw_dir, d, excluded))
            _log_outcome(cfg, reg, outcomes[-1], utc_now())
            d += timedelta(days=1)
    finally:
        if own_client:
            client.close()
    return outcomes


def _backfill_day(
    client: PoliteClient, raw_dir: Path, d: date, excluded: frozenset[str]
) -> SnapshotOutcome:
    src = BACKFILL_SOURCE
    if _stored(raw_dir, d):
        return SnapshotOutcome(src, "skipped_exists", (), 0, 0, 0, f"{d} already stored")
    try:
        resp = client.get(snapshot_url(d))
        if resp.status_code == 404:
            return SnapshotOutcome(src, "empty", (), 0, 0, 0, f"{d} not in archive (404)")
        resp.raise_for_status()
        payload = resp.json()
    except RobotsDisallowedError as exc:
        return SnapshotOutcome(src, "error", (), 0, 0, 0, f"robots.txt disallows {exc}")
    except (httpx.HTTPError, ValueError) as exc:
        return SnapshotOutcome(src, "error", (), 0, 0, 0, type(exc).__name__)
    return _store_day(raw_dir, d, payload, excluded)


def _stored(raw_dir: Path, d: date) -> bool:
    folder = raw_dir / LISTINGS / BACKFILL_SOURCE / f"{d:%Y}" / f"{d:%m}"
    return folder.exists() and any(folder.glob(f"{BACKFILL_SOURCE}_{d:%Y%m%d}T*.parquet"))


def _store_day(raw_dir: Path, d: date, payload: Any, excluded: frozenset[str]) -> SnapshotOutcome:
    """Write one archived daily snapshot, stamped with its ``generated_at``."""
    src = BACKFILL_SOURCE
    gen = snapshot_generated_at(payload)
    if gen is None or gen.date() != d:
        return SnapshotOutcome(src, "error", (), 0, 0, 0, f"{d}: unexpected generated_at {gen}")
    ts_obs = utc_now()
    batch = normalize_snapshot(payload, ts_obs, snapshot_id(src, gen), src, excluded)
    if not batch.listings:
        return SnapshotOutcome(src, "empty", (), 0, 0, batch.n_dropped, f"{d}: no rows")
    path = snapshot_path(raw_dir / LISTINGS, src, gen)
    write_snapshot(raw_dir / LISTINGS, src, gen, observations_to_frame(batch.listings))
    return SnapshotOutcome(
        src, "written", (str(path),), len(batch.listings), 0, batch.n_dropped, str(d)
    )


# The publisher's frozen quarterly archive on Zenodo (CC BY 4.0). It holds the
# first days of the series, 2026-07-05..07-18, which the GitHub mirror no
# longer serves (D48). One request; Zenodo asks for a 10-second crawl delay.
ZENODO_ARCHIVE = (
    "https://zenodo.org/records/21435395/files/gpu-rental-prices-2026-07-19.zip?download=1"
)
ZENODO_MD5 = "57f098ba77a6dc38b900f3a0245040dd"
_ZIP_SNAPSHOT = re.compile(r"data/snapshots/(\d{4}-\d{2}-\d{2})\.json$")


def archive_snapshots(blob: bytes, md5: str = ZENODO_MD5) -> dict[date, Any]:
    """Daily snapshot payloads in a Zenodo archive, keyed by date (md5-checked)."""
    digest = hashlib.md5(blob, usedforsecurity=False).hexdigest()
    if digest != md5:
        raise ValueError(f"archive md5 {digest} does not match the Zenodo record")
    out: dict[date, Any] = {}
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        for name in z.namelist():
            m = _ZIP_SNAPSHOT.search(name)
            if m:
                out[date.fromisoformat(m.group(1))] = json.loads(z.read(name))
    return dict(sorted(out.items()))


def backfill_gpurentalprices_zenodo(
    cfg: Config,
    start: date,
    end: date,
    client: PoliteClient | None = None,
    md5: str = ZENODO_MD5,
) -> list[SnapshotOutcome]:
    """Import the archive's days in ``start..end`` that are not stored yet."""
    raw_dir = cfg.path("data") / "raw"
    src = BACKFILL_SOURCE
    reg = registry(cfg)
    excluded = frozenset(cfg.collectors.excluded_providers)
    days = [start + timedelta(days=i) for i in range((end - start).days + 1)]
    todo = [d for d in days if not _stored(raw_dir, d)]
    outcomes = [
        SnapshotOutcome(src, "skipped_exists", (), 0, 0, 0, f"{d} already stored")
        for d in days
        if d not in todo
    ]
    if not todo:
        return outcomes
    own_client = client is None
    client = client or make_client(cfg)
    try:
        resp = client.get(ZENODO_ARCHIVE)
        resp.raise_for_status()
        snaps = archive_snapshots(resp.content, md5)
    except RobotsDisallowedError as exc:
        return [*outcomes, SnapshotOutcome(src, "error", (), 0, 0, 0, f"robots: {exc}")]
    except (httpx.HTTPError, ValueError) as exc:
        return [*outcomes, SnapshotOutcome(src, "error", (), 0, 0, 0, str(exc)[:200])]
    finally:
        if own_client:
            client.close()
    for d in todo:
        if d in snaps:
            outcomes.append(_store_day(raw_dir, d, snaps[d], excluded))
        else:
            outcomes.append(SnapshotOutcome(src, "empty", (), 0, 0, 0, f"{d} not in archive"))
        _log_outcome(cfg, reg, outcomes[-1], utc_now())
    return outcomes


def backfill_cgi(
    cfg: Config, start: datetime, end: datetime, client: PoliteClient | None = None
) -> list[SnapshotOutcome]:
    """Import Computable GPU Index history (15-minute values) as one vintage per SKU."""
    raw_dir = cfg.path("data") / "raw"
    reg = registry(cfg)
    own_client = client is None
    client = client or make_client(cfg)
    outcomes: list[SnapshotOutcome] = []
    try:
        for sku in CGI_SKUS:
            src = "cgi_hist"
            try:
                values = fetch_history(client, sku, ensure_utc(start), ensure_utc(end))
            except (httpx.HTTPError, ValueError, RobotsDisallowedError) as exc:
                outcomes.append(
                    SnapshotOutcome(src, "error", (), 0, 0, 0, f"{sku}: {type(exc).__name__}")
                )
                continue
            ts_obs = utc_now()
            batch = normalize_history(
                sku, values, ts_obs, snapshot_id(f"{src}_{sku.lower()}", ts_obs)
            )
            if not batch.indices:
                outcomes.append(SnapshotOutcome(src, "empty", (), 0, 0, batch.n_dropped, sku))
                continue
            paths = write_batch(raw_dir, f"{src}_{sku.lower()}", ts_obs, batch)
            outcomes.append(
                SnapshotOutcome(
                    src,
                    "written",
                    tuple(map(str, paths)),
                    0,
                    len(batch.indices),
                    batch.n_dropped,
                    sku,
                )
            )
            _log_outcome(cfg, reg, outcomes[-1], ts_obs)
    finally:
        if own_client:
            client.close()
    return outcomes
