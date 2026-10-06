"""Claim 5: AWS spot data access, daily series and signals. Hand-built fixtures; no network."""

from __future__ import annotations

import hashlib
from datetime import date

import duckdb
import httpx
import numpy as np
import pandas as pd
import pytest

from compute_curve.claim4.market_data import sessions_from_calendar
from compute_curve.claim5 import aws_spot as aw
from compute_curve.claim5.signals import build_signals, session_days
from compute_curve.synthetic import synthetic_weekday_calendar

ZENODO_ROBOTS = """User-agent: *
Disallow: /search
Disallow: /api
Disallow: /administration
Disallow: /records/*/preview
Allow: /api/records/*/files
Disallow: /api/records/*/files-archive
Crawl-delay: 10
"""


def test_robots_follow_rfc9309_longest_match():
    rules = aw.parse_robots(ZENODO_ROBOTS)
    assert aw.robots_allows(rules, "/records/23082767/files/2024-10.tsv.zst")
    assert aw.robots_allows(rules, "/api/records/23082767/files")
    assert not aw.robots_allows(rules, "/api/records/23082767")
    assert not aw.robots_allows(rules, "/api/records/23082767/files-archive")
    assert not aw.robots_allows(rules, "/records/23082767/preview/x.tsv")
    assert not aw.robots_allows(rules, "/search")


def _records(rows: list[tuple[str, str, float, str]]) -> pd.DataFrame:
    # Hand-built fixture rows in the dataset's layout; not market data.
    df = pd.DataFrame(rows, columns=["az_id", "instance_type", "price", "ts"])
    df["ts"] = pd.to_datetime(df["ts"], utc=True)
    df["product"] = "Linux/UNIX"
    df["month"] = df["ts"].dt.strftime("%Y-%m")
    return df


def test_price_in_effect_at_the_cutoff_per_gpu_hour():
    rec = _records(
        [
            ("use1-az1", "p5.48xlarge", 40.0, "2025-01-01 00:00"),
            ("use1-az1", "p5.48xlarge", 48.0, "2025-01-01 23:45"),
            ("use1-az2", "p5.4xlarge", 5.0, "2025-01-01 00:00"),
        ]
    )
    p = aw.pool_daily(rec).set_index(["day", "az_id"])
    assert p.loc[(date(2025, 1, 1), "use1-az1"), "price_per_gpu_hour"] == pytest.approx(5.0)
    assert p.loc[(date(2025, 1, 2), "use1-az1"), "price_per_gpu_hour"] == pytest.approx(6.0)
    assert p.loc[(date(2025, 1, 1), "use1-az2"), "price_per_gpu_hour"] == pytest.approx(5.0)
    assert (p["gpu"] == "H100").all()


def test_a_pool_missing_from_a_months_file_is_not_offered_that_month():
    rec = _records(
        [
            ("use1-az1", "p4d.24xlarge", 16.0, "2025-01-01 00:00"),
            ("use1-az2", "p4d.24xlarge", 16.0, "2025-01-01 00:00"),
            ("use1-az2", "p4d.24xlarge", 17.0, "2025-02-01 00:00"),
        ]
    )
    p = aw.pool_daily(rec)
    feb = p.loc[pd.to_datetime(p["day"]).dt.month == 2]
    assert set(feb["az_id"]) == {"use1-az2"}
    assert len(p.loc[p["az_id"] == "use1-az1"]) == 31


def _pools(prices: dict[str, list[float]], start: date) -> pd.DataFrame:
    rows = []
    for pool, series in prices.items():
        az, it = pool.split("|")
        for i, v in enumerate(series):
            if not np.isnan(v):
                rows.append((start + pd.Timedelta(days=i), az, it, "A100", v))
    df = pd.DataFrame(rows, columns=["day", "az_id", "instance_type", "gpu", "price_per_gpu_hour"])
    df["day"] = pd.to_datetime(df["day"]).dt.date
    return df


def _c5(cfg):
    return cfg.claim5.model_copy(update={"gpu_classes": ["A100"]})


def test_level_is_matched_pool_median_change_and_ignores_new_pools(cfg):
    nan = float("nan")
    start = date(2025, 3, 2)  # Sunday
    pools = _pools(
        {
            "use1-az1|p4d.24xlarge": [2.0, 2.0, 2.2, 2.2],
            "use1-az2|p4d.24xlarge": [2.0, 2.0, 2.2, 2.2],
            "use1-az3|p4d.24xlarge": [2.0, 2.0, 2.0, 2.0],
            "use1-az4|p4d.24xlarge": [nan, nan, 9.0, 9.0],  # new, expensive pool
        },
        start,
    )
    s = sessions_from_calendar(synthetic_weekday_calendar(date(2025, 3, 3), date(2025, 3, 6)))
    sig = build_signals(pools, s, _c5(cfg)).set_index("session")
    # Tuesday's session sees Monday (2.0 everywhere) vs Sunday: no change.
    assert sig.loc[date(2025, 3, 4), "level_a100"] == pytest.approx(0.0)
    # Wednesday sees Tuesday vs Monday: two of three matched pools up 10%; the new pool is ignored.
    assert sig.loc[date(2025, 3, 5), "level_a100"] == pytest.approx(np.log(1.1))
    assert sig.loc[date(2025, 3, 5), "asof_a100"] == date(2025, 3, 4)


def test_too_few_matched_pools_or_a_gap_gives_no_signal(cfg):
    start = date(2025, 3, 2)
    two = _pools({"a|p4d.24xlarge": [2.0] * 5, "b|p4d.24xlarge": [2.0] * 5}, start)
    s = sessions_from_calendar(synthetic_weekday_calendar(date(2025, 3, 3), date(2025, 3, 6)))
    assert build_signals(two, s, _c5(cfg))["level_a100"].isna().all()
    nan = float("nan")
    gap = _pools({p: [2.0, 2.0, nan, nan, 2.0, 2.0] for p in ("a|x", "b|x", "c|x")}, start)
    gap["instance_type"] = "p4d.24xlarge"
    s2 = sessions_from_calendar(synthetic_weekday_calendar(date(2025, 3, 3), date(2025, 3, 9)))
    sig = build_signals(gap, s2, _c5(cfg)).set_index("session")
    assert np.isnan(sig.loc[date(2025, 3, 5), "level_a100"])  # its day (03-04) is missing
    assert np.isnan(sig.loc[date(2025, 3, 6), "level_a100"])  # 03-05 is also missing
    assert np.isnan(sig.loc[date(2025, 3, 7), "level_a100"])  # previous session had no day


def test_a_days_price_reaches_the_market_at_the_next_open(cfg):
    s = sessions_from_calendar(synthetic_weekday_calendar(date(2025, 3, 3), date(2025, 3, 7)))
    days = [date(2025, 3, 2), date(2025, 3, 3), date(2025, 3, 4)]
    d = session_days(days, s, "23:30", 60, 5, 1)
    by = dict(zip(s["session"], d, strict=True))
    assert by[date(2025, 3, 3)] == date(2025, 3, 2)
    assert by[date(2025, 3, 4)] == date(2025, 3, 3)
    assert by[date(2025, 3, 5)] == date(2025, 3, 4)
    assert by[date(2025, 3, 6)] is None  # 03-05 missing; 03-04 is two days old


def _transport(body: bytes):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text=ZENODO_ROBOTS)
        return httpx.Response(200, content=body)

    return httpx.MockTransport(handler)


def test_download_verifies_md5_and_never_overwrites(tmp_path):
    body = b"fixture bytes"
    good = hashlib.md5(body, usedforsecurity=False).hexdigest()
    client = httpx.Client(transport=_transport(body))
    log = aw.download_files({"x.tsv.zst": good}, tmp_path, "test-agent", client, delay_s=0)
    assert log[0]["status"] == "downloaded" and (tmp_path / "x.tsv.zst").read_bytes() == body
    log2 = aw.download_files({"x.tsv.zst": good}, tmp_path, "test-agent", client, delay_s=0)
    assert log2[0]["status"] == "exists"
    with pytest.raises(RuntimeError, match="md5"):
        aw.download_files({"y.tsv.zst": "0" * 32}, tmp_path, "test-agent", client, delay_s=0)
    assert not (tmp_path / "y.tsv.zst").exists()
    with pytest.raises(RuntimeError, match="exists with md5"):
        aw.download_files({"x.tsv.zst": "0" * 32}, tmp_path, "test-agent", client, delay_s=0)


def test_filter_keeps_gpu_types_us_zones_and_linux(tmp_path):
    raw = tmp_path / "2025-01.tsv.zst"
    rows = [
        ("use1-az1", "p5.48xlarge", "Linux/UNIX", 40.0, "2025-01-01T00:00:00+00:00"),
        ("euc1-az1", "p5.48xlarge", "Linux/UNIX", 40.0, "2025-01-01T00:00:00+00:00"),
        ("use1-az1", "p5.48xlarge", "SUSE Linux", 40.0, "2025-01-01T00:00:00+00:00"),
        ("usw2-az1", "m5.large", "Linux/UNIX", 0.05, "2025-01-01T00:00:00+00:00"),
        ("usw2-az3", "p4d.24xlarge", "Linux/UNIX", 16.0, "2025-01-01T01:00:00+00:00"),
    ]
    con = duckdb.connect()
    con.execute("CREATE TABLE t(a VARCHAR, b VARCHAR, c VARCHAR, d DOUBLE, e VARCHAR)")
    con.executemany("INSERT INTO t VALUES (?, ?, ?, ?, ?)", rows)
    con.execute(
        f"COPY t TO '{raw.as_posix()}' (FORMAT CSV, DELIMITER '\t', HEADER false, COMPRESSION zstd)"
    )
    con.close()
    n = aw.filter_file(raw, tmp_path / "out.parquet")
    assert n == 2
    kept = aw.load_filtered([tmp_path / "out.parquet"])
    assert set(kept["az_id"]) == {"use1-az1", "usw2-az3"}
    assert (kept["month"] == "2025-01").all()
