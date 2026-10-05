"""Snapshot runner tests with an in-memory HTTP transport (no network)."""

import json
from datetime import UTC, date, datetime

import httpx

from compute_curve.config import load_config
from compute_curve.http import PoliteClient
from compute_curve.snapshot import (
    BACKFILL_SOURCE,
    backfill_gpurentalprices,
    collect_one,
    registry,
    run_snapshot,
)

LATEST = {
    "date": "2026-10-05",
    "generated_at": "2026-10-05T08:00:00Z",
    "offers": [
        {
            "provider": "lambda",
            "gpu": "h100-sxm",
            "usd_hr": 3.0,
            "kind": "on-demand",
            "fetched_at": "2026-10-05T08:00:00Z",
        }
    ],
}


def handler(request: httpx.Request) -> httpx.Response:
    path = request.url.path
    if path == "/robots.txt":
        if request.url.host == "blocked.example":
            return httpx.Response(200, text="User-agent: *\nDisallow: /")
        return httpx.Response(404)
    if request.url.host == "gpurentalprices.com":
        return httpx.Response(200, json=LATEST)
    if request.url.host == "raw.githubusercontent.com":
        day = path.rsplit("/", 1)[-1].removesuffix(".json")
        if day == "2026-07-20":
            return httpx.Response(404)
        snap = dict(LATEST, generated_at=f"{day}T23:00:00Z")
        snap["offers"] = [dict(LATEST["offers"][0], fetched_at=f"{day}T23:00:00Z")]
        return httpx.Response(200, json=snap)
    return httpx.Response(500)


def client(sleeps=None):
    return PoliteClient(
        user_agent="test",
        min_interval_s=1.0,
        transport=httpx.MockTransport(handler),
        sleep=(sleeps.append if sleeps is not None else (lambda s: None)),
    )


def cfg_in(tmp_path):
    cfg = load_config()
    return cfg.model_copy(
        update={"project": cfg.project.model_copy(update={"data_dir": tmp_path / "data"})}
    )


def test_snapshot_is_idempotent_and_logged(tmp_path):
    cfg = cfg_in(tmp_path)
    c = client()
    first = run_snapshot(cfg, ["gpurentalprices"], client=c)
    second = run_snapshot(cfg, ["gpurentalprices"], client=c)
    assert first[0].status == "written" and first[0].n_listings == 1
    assert second[0].status == "skipped_exists"
    files = list((tmp_path / "data" / "raw" / "listings").rglob("*.parquet"))
    assert len(files) == 1
    log = [
        json.loads(x) for x in (tmp_path / "data" / "collection_log.jsonl").read_text().splitlines()
    ]
    assert [x["status"] for x in log] == ["written"]  # skips make no request; not logged
    assert not any("authorization" in json.dumps(x).lower() for x in log)


def test_vast_refused_without_licence(tmp_path):
    cfg = cfg_in(tmp_path)
    out = collect_one(registry(cfg)["vast"], client(), tmp_path, datetime.now(tz=UTC))
    assert out.status == "refused_licence"


def test_robots_disallow_is_respected(tmp_path):
    c = client()
    assert not c.robots_allows("https://blocked.example/pricing")
    assert c.robots_allows("https://gpurentalprices.com/api/latest.json")


def test_rate_limit_between_requests_to_same_host():
    sleeps: list[float] = []
    c = client(sleeps)
    c.get("https://gpurentalprices.com/api/latest.json")
    c.get("https://gpurentalprices.com/api/latest.json")
    assert sleeps and all(s > 0 for s in sleeps)


def test_backfill_writes_each_day_once(tmp_path):
    cfg = cfg_in(tmp_path)
    c = client()
    out = backfill_gpurentalprices(cfg, date(2026, 7, 19), date(2026, 7, 21), client=c)
    assert [o.status for o in out] == ["written", "empty", "written"]
    again = backfill_gpurentalprices(cfg, date(2026, 7, 19), date(2026, 7, 21), client=c)
    assert [o.status for o in again] == ["skipped_exists", "empty", "skipped_exists"]
    files = sorted((tmp_path / "data" / "raw" / "listings" / BACKFILL_SOURCE).rglob("*.parquet"))
    assert [f.name for f in files] == [
        "gpurentalprices_hist_20260719T230000Z.parquet",
        "gpurentalprices_hist_20260721T230000Z.parquet",
    ]
