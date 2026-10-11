"""GPU Price Tracker (Hugging Face) backfill: offline, hand-made Parquet files."""

import json
from datetime import UTC, date, datetime
from pathlib import Path

import duckdb
import httpx
import pandas as pd

from compute_curve.collectors import gpuprices_hf as hf
from compute_curve.config import load_config
from compute_curve.http import PoliteClient
from compute_curve.snapshot import HF_SOURCE, backfill_gpuprices_hf, make_hf_client
from compute_curve.storage.raw_store import read_snapshot

# provider, instance_type, gpu_type, gpu_count, region, price_per_hour, is_spot,
# available, quality, country
ROWS = [
    ("lambdalabs", "gpu_8x_h100_sxm5", "H100", 8, "us-east-1", 31.92, False, True, "ok", "US"),
    ("datacrunch", "1B200.30V", "B200", 1, "FIN-01", 3.708, True, None, "ok", None),
    ("azure", "Standard_NC40ads_H100_v5", "H100NVL", 1, "eastus", 6.98, False, True, "ok", "US"),
    ("vastai", "50255932", "H100", 2, "us-oregon", 4.0, False, True, "ok", "US"),
    ("runpod", "NVIDIA H200", "H200", 8, "US-CA-2", 28.0, False, True, "ok", "US"),
    ("oci", "BM.GPU.H100.8", "H100", 8, "us-ashburn-1", 80.0, False, True, "ok", "US"),
    ("vultr", "vcg-h100", "H100", 1, "ewr", 2.99, False, True, "ok", "US"),
    (
        "nebius",
        "gpu-h100-sxm 8gpu",
        "H100",
        8,
        "eu-north1",
        36.0,
        False,
        False,
        "missing_memory",
        "FI",
    ),
    ("aws", "p4d.24xlarge", "A100", 8, "us-east-1", 32.77, False, True, "ok", "US"),
    ("gcp", "a4x-highgpu-4g", "GB200", 4, "us-central1", 40.0, False, True, "ok", "US"),
]


def _parquet(tmp: Path, stamp: str, rows: list[tuple]) -> bytes:
    """One snapshot file in the publisher's schema, written with DuckDB."""
    df = pd.DataFrame(
        rows,
        columns=[
            "provider",
            "instance_type",
            "gpu_type",
            "gpu_count",
            "region",
            "price_per_hour",
            "is_spot",
            "available",
            "quality",
            "country",
        ],
    )
    df.insert(0, "timestamp", pd.Timestamp(stamp, tz="UTC"))
    df = df.assign(
        gpu_memory_gb=80,
        vcpus=26,
        ram_gb=225.0,
        availability_zone=None,
        region_canonical=None,
        region_lat=None,
        region_lon=None,
        region_group=None,
    )
    df["available"] = df["available"].astype("boolean")
    path = tmp / f"{stamp}.parquet"
    con = duckdb.connect()
    try:
        con.register("snap", df)
        con.execute(f"COPY (SELECT * FROM snap) TO '{path.as_posix()}' (FORMAT PARQUET)")  # noqa: S608
    finally:
        con.close()
    return path.read_bytes()


F_MAR = "prices/dt=2026-03-09/snapshot_20260309T094314Z.parquet"
F_A = "prices/dt=2026-05-08/snapshot_20260508T090003Z.parquet"
F_B = "prices/dt=2026-05-08/snapshot_20260508T102007Z.parquet"
F_LATE = "prices/dt=2026-05-08/snapshot_20260508T210002Z.parquet"
F_C = "prices/dt=2026-05-10/snapshot_20260510T090002Z.parquet"
# (commit time, id, files the repository holds after it), oldest first
COMMITS = [
    ("2026-05-07T20:26:07Z", "c1", [F_MAR]),
    ("2026-05-09T10:00:00Z", "c2", [F_MAR, F_A, F_B]),
    ("2026-05-10T12:00:00Z", "c3", [F_MAR, F_A, F_B, F_C]),
    ("2026-07-08T22:31:30Z", "c4", [F_MAR, F_A, F_B, F_C, F_LATE]),  # F_LATE uploaded late
]


def _files(tmp: Path) -> dict[str, bytes]:
    one = [ROWS[0]]
    return {
        F_MAR: _parquet(tmp, "2026-03-09T09:43:14Z", one),
        F_A: _parquet(tmp, "2026-05-08T09:00:03.6Z", ROWS),
        F_B: _parquet(tmp, "2026-05-08T10:20:07Z", one),
        F_LATE: _parquet(tmp, "2026-05-08T21:00:02Z", one),
        F_C: _parquet(tmp, "2026-05-10T09:00:02Z", one),
    }


def _tree(paths: list[str]) -> list[dict[str, object]]:
    dirs = sorted({p.rsplit("/", 1)[0] for p in paths})
    tree: list[dict[str, object]] = [{"type": "directory", "path": d, "size": 0} for d in dirs]
    return tree + [{"type": "file", "path": p, "size": 1} for p in paths]


def _client(files: dict[str, bytes], calls: list[str]) -> PoliteClient:
    api = "/api/datasets/afhubbard/gpu-prices"
    history = [{"id": i, "title": "sync", "date": t} for t, i, _ in reversed(COMMITS)]

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        calls.append(str(request.url))
        if path == f"{api}/tree/main/prices":
            return httpx.Response(200, json=_tree(list(files)))
        if path == f"{api}/commits/main":  # two pages, linked like the hub does
            if request.url.params.get("p") == "0":
                nxt = f"https://huggingface.co{api}/commits/main?p=1&limit=50"
                return httpx.Response(
                    200, json=history[:2], headers={"Link": f'<{nxt}>; rel="next"'}
                )
            return httpx.Response(200, json=history[2:])
        for _, rev, held in COMMITS:
            prefix = f"{api}/tree/{rev}/prices/dt="
            if path.startswith(prefix):
                day = path.removeprefix(prefix)
                inside = [p for p in held if p.startswith(f"prices/dt={day}/")]
                return httpx.Response(200, json=_tree(inside)) if inside else httpx.Response(404)
        rel = path.removeprefix("/datasets/afhubbard/gpu-prices/resolve/main/")
        return httpx.Response(200, content=files[rel]) if rel in files else httpx.Response(404)

    return PoliteClient(
        user_agent="test", transport=httpx.MockTransport(handler), sleep=lambda s: None
    )


def _cfg(tmp_path: Path):
    cfg = load_config()
    return cfg.model_copy(
        update={"project": cfg.project.model_copy(update={"data_dir": tmp_path / "data"})}
    )


def _stored(tmp_path: Path) -> list[Path]:
    return sorted((tmp_path / "data" / "raw" / "listings" / HF_SOURCE).rglob("*.parquet"))


def test_backfill_filters_maps_and_is_idempotent(tmp_path):
    files = _files(tmp_path)
    calls: list[str] = []
    c = _client(files, calls)
    cfg = _cfg(tmp_path)
    t0 = datetime.now(tz=UTC)
    out = backfill_gpuprices_hf(
        cfg, date(2026, 3, 9), date(2026, 5, 11), c, today=date(2026, 5, 11)
    )
    by_day = {
        json.loads(o.detail)["day"] if o.detail.startswith("{") else o.detail[:10]: o for o in out
    }
    assert by_day["2026-03-09"].status == "skipped_unverified"  # first upload months later
    assert by_day["2026-05-09"].status == "empty"
    assert by_day["2026-05-11"].status == "skipped_incomplete"
    written = [o for o in out if o.status == "written"]
    assert [json.loads(o.detail)["day"] for o in written] == ["2026-05-08", "2026-05-10"]
    may8 = json.loads(written[0].detail)
    assert may8["provider:vast"] == 1 and may8["provider:runpod"] == 1
    assert may8["provider:oci"] == 1 and may8["provider:vultr"] == 1
    assert may8["quality_not_ok"] == 1
    assert may8["skipped_unverified"] == 1  # the 21:00 file reached the hub months later
    assert written[0].n_listings == 4  # 3 kept rows + 1 from the 10:20 file
    downloads = [u for u in calls if "/resolve/" in u]
    assert sorted(u.rsplit("/", 1)[-1] for u in downloads) == [
        F_A.rsplit("/", 1)[-1],
        F_B.rsplit("/", 1)[-1],
        F_C.rsplit("/", 1)[-1],
    ]  # unverified files are never downloaded
    assert any("/tree/c2/prices/dt=2026-05-08" in u for u in calls)
    assert any("/tree/c3/prices/dt=2026-05-10" in u for u in calls)

    paths = _stored(tmp_path)
    assert [p.name for p in paths] == [
        "gpuprices_hf_20260508T102007Z.parquet",  # stamped with the day's latest snapshot
        "gpuprices_hf_20260510T090002Z.parquet",
    ]
    df = read_snapshot(paths[0])
    assert set(df["provider"]) == {"lambda", "verda", "azure"}
    assert not set(df["provider"]) & {"vast", "runpod", "oci", "vultr", "vastai"}
    assert set(df["gpu_model"]) == {"H100", "B200"}  # A100 and GB200 out of scope
    lam = df.loc[(df["provider"] == "lambda") & (df["gpus_per_instance"] == 8)]
    assert lam["price_usd_per_gpu_hour"].round(4).tolist() == [3.99, 3.99]
    assert set(lam["gpu_variant"]) == {"SXM"}
    nvl = df.loc[df["provider"] == "azure"].iloc[0]
    assert (nvl["gpu_model"], nvl["gpu_variant"], nvl["region"]) == ("H100", "NVL", "US")
    verda = df.loc[df["provider"] == "verda"].iloc[0]
    assert verda["term"] == "spot" and verda["availability"] == "unknown"
    assert verda["region"] == "FIN-01"
    # ts_source is the publisher's snapshot time; ts_observed is when we fetched it
    assert set(df["snapshot_id"]) == {
        "gpuprices_hf_20260508T090003Z",
        "gpuprices_hf_20260508T102007Z",
    }
    first = df.loc[df["snapshot_id"] == "gpuprices_hf_20260508T090003Z"]
    assert (first["ts_source"] == pd.Timestamp("2026-05-08T09:00:03.6Z")).all()
    assert (df["ts_observed"] >= t0).all()
    assert json.loads(first["raw_json"].iloc[0])["hf_path"].startswith("prices/dt=2026-05-08/")

    n = len(calls)
    again = backfill_gpuprices_hf(
        cfg, date(2026, 5, 8), date(2026, 5, 10), c, today=date(2026, 5, 11)
    )
    assert [o.status for o in again] == ["skipped_exists", "empty", "skipped_exists"]
    assert len(calls) == n + 3  # tree and commit history, for the empty day only
    stored_only = backfill_gpuprices_hf(
        cfg, date(2026, 5, 8), date(2026, 5, 8), c, today=date(2026, 5, 11)
    )
    assert [o.status for o in stored_only] == ["skipped_exists"]
    assert len(calls) == n + 3  # nothing to do, so no request at all
    log = (tmp_path / "data" / "collection_log.jsonl").read_text().splitlines()
    assert any(json.loads(x)["source"] == HF_SOURCE for x in log)


def test_partition_files_and_stamps():
    tree = [
        {"type": "directory", "path": "prices/dt=2026-05-08"},
        {"type": "file", "path": "prices/dt=2026-05-08/snapshot_20260508T210002Z.parquet"},
        {"type": "file", "path": "prices/dt=2026-05-08/snapshot_20260508T090003Z.parquet"},
        {"type": "file", "path": "prices/README.md"},
    ]
    files = hf.partition_files(tree)
    assert list(files) == [date(2026, 5, 8)]
    assert files[date(2026, 5, 8)][0].endswith("090003Z.parquet")
    assert hf.file_stamp(files[date(2026, 5, 8)][0]) == datetime(2026, 5, 8, 9, 0, 3, tzinfo=UTC)
    commits = hf.commit_times(
        [{"id": "b", "date": "2026-05-09T10:00:00Z"}, {"id": "a", "date": "2026-05-07T20:26:07Z"}]
    )
    assert [sha for _, sha in commits] == ["a", "b"]
    assert hf.publication_cutoff(date(2026, 5, 8)) == datetime(2026, 5, 10, tzinfo=UTC)
    assert hf.revision_at(commits, hf.publication_cutoff(date(2026, 5, 8))) == "b"
    assert hf.revision_at(commits, hf.publication_cutoff(date(2026, 5, 7))) == "a"
    assert hf.revision_at(commits, hf.publication_cutoff(date(2026, 3, 9))) is None


def test_hf_client_waits_at_least_three_seconds(tmp_path):
    assert make_hf_client(_cfg(tmp_path)).min_interval_s >= 3.0
