"""AWS GPU spot prices from the Zenodo "AWS Spot Price History" dataset.

Source: Eric Pauley (University of Wisconsin-Madison), "AWS Spot Price
History", Zenodo, version 2026-09, DOI 10.5281/zenodo.23082767, licence
CC BY 4.0. Each monthly file is a zstd-compressed TSV in the format of AWS
``describe-spot-price-history`` (availability zone ID, instance type,
product description, USD per instance-hour, timestamp). Each month's file
starts with the price in effect at 00:00 UTC on the 1st.

Access rules (docs/claim5_plan.md section 1):

* robots.txt is read once and obeyed with RFC 9309 semantics (wildcards,
  longest match wins); Zenodo's ``Crawl-delay: 10`` is honoured between
  requests;
* only the monthly files the pre-registered sample needs are downloaded;
* raw files are immutable: written once under ``var/aws_spot/raw/``
  (git-ignored), verified against Zenodo's MD5, never overwritten.

Daily series: for each pool (availability zone ID x instance type), the
price in effect at the daily cutoff (23:30 UTC) is the latest record at or
before the cutoff in that month's file, divided by the instance's GPU count.
"""

from __future__ import annotations

import hashlib
import re
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

import duckdb
import httpx
import numpy as np
import pandas as pd

RECORD_ID = 23082767
DOI = "10.5281/zenodo.23082767"
VERSION = "2026-09"
ATTRIBUTION = (
    'Eric Pauley (University of Wisconsin-Madison), "AWS Spot Price History", Zenodo, '
    "version 2026-09, https://doi.org/10.5281/zenodo.23082767, CC BY 4.0"
)
ZENODO = "https://zenodo.org"
CRAWL_DELAY_S = 10.0

# GPU instance types with data-center training GPUs (A100 generation or newer).
# GPU counts per instance from AWS instance-type documentation.
GPU_TYPES: dict[str, tuple[str, int]] = {
    "p4d.24xlarge": ("A100", 8),
    "p4de.24xlarge": ("A100", 8),
    "p5.48xlarge": ("H100", 8),
    "p5.4xlarge": ("H100", 1),
    "p5e.48xlarge": ("H200", 8),
    "p5en.48xlarge": ("H200", 8),
    "p6-b200.48xlarge": ("B200", 8),
    "p6-b300.48xlarge": ("B300", 8),
}
# Audited Zenodo files (record 23082767, version 2026-09): key -> md5.
AUDITED_FILES: dict[str, str] = {
    "2022.tsv.zst": "a3a66a5fe06979807a724fe8799c39c9",
    "2023.tsv.zst": "568f377074918f324be0d03f401c1b6b",
    "2024-01.tsv.zst": "06aa4e023dc893f4a5dcd87d7cf03f22",
    "2024-02.tsv.zst": "454d6e264e79991d8d589ecdb90df737",
    "2024-03.tsv.zst": "72032275103b4ac80e970397ea16847a",
    "2024-04.tsv.zst": "bda3872ee305bccdfc0fff1ef3e79557",
    "2024-05.tsv.zst": "e49d14807b9f618f0edda9ddc69ab78c",
    "2024-06.tsv.zst": "ff058dadb8a41cf2b28e85d51de1d30e",
    "2024-07.tsv.zst": "9f82ac0fc36ec6852f113cbb0f50eec6",
    "2024-08.tsv.zst": "c809438eff3ee2f9e8656b82f1afd68d",
    "2024-09.tsv.zst": "ec7b7477f9644132527e9aa729d6cc7a",
    "2024-10.tsv.zst": "598dd828a0df79e43cabf62f86a66d12",
    "2024-11.tsv.zst": "5983e7a1f3510d0358943de6f8f0b058",
    "2024-12.tsv.zst": "e0f97d23fa53402ac1ebe2503dd91caf",
    "2025-01.tsv.zst": "d763724350584924e1a2aab5d6527ba8",
    "2025-02.tsv.zst": "2a5866bc86181f56afe8e07dec7ef554",
    "2025-03.tsv.zst": "afec0f26cfcf8145ea73f489f3bcbf1a",
    "2025-04.tsv.zst": "55d955b13863e60a78a80ab24530a700",
    "2025-05.tsv.zst": "c7e29d6598f3a22e61d37fdf4a3b3f76",
    "2025-06.tsv.zst": "3025fab72d86b6bde368514c8d1ac2ec",
    "2025-07.tsv.zst": "b1ca4fb49eae076d0fe25946c648e5bb",
    "2025-08.tsv.zst": "0485510fa57641bd25c661504683e252",
    "2025-09.tsv.zst": "abae8bac2a2fa2942693631b286b8f80",
    "2025-10.tsv.zst": "de4c915f9484ebfb8ce9ace376afe224",
    "2025-11.tsv.zst": "e523e2e217950590fb7e0b5cce5919e4",
    "2025-12.tsv.zst": "9fd092622892e64a139715280dc64845",
    "2026-01.tsv.zst": "4019e436e8ed0cc562f651be76104688",
    "2026-02.tsv.zst": "1dbb9ac0a93164d09eb0971a9402f832",
    "2026-07.tsv.zst": "29a172eb2ec02c2860ab634d42b140fc",
    "2026-08.tsv.zst": "e45475d16af7e68f81335162f1dd65fd",
    "2026-09.tsv.zst": "0c7b9bc02224a6fb12f3f544c4f53950",
}
US_AZ_PREFIXES = ("use1-", "use2-", "usw1-", "usw2-")
PRODUCT = "Linux/UNIX"
FILTERED_COLUMNS = ("az_id", "instance_type", "product", "price", "ts_epoch", "month")


# ---------------------------------------------------------------------------
# robots.txt (RFC 9309: longest matching rule wins, Allow wins ties)
# ---------------------------------------------------------------------------
def parse_robots(text: str, agent: str = "*") -> list[tuple[bool, str]]:
    """Allow/Disallow rules for ``agent`` (falls back to ``*``)."""
    groups: dict[str, list[tuple[bool, str]]] = {}
    current: list[str] = []
    in_rules = False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        key, val = (s.strip() for s in line.split(":", 1))
        key = key.lower()
        if key == "user-agent":
            if in_rules:
                current, in_rules = [], False
            current.append(val.lower())
            for a in current:
                groups.setdefault(a, [])
        elif key in ("allow", "disallow") and current:
            in_rules = True
            if val:
                for a in current:
                    groups[a].append((key == "allow", val))
    return groups.get(agent.lower(), groups.get("*", []))


def _pattern_regex(pattern: str) -> re.Pattern[str]:
    anchored = pattern.endswith("$")
    body = re.escape(pattern.rstrip("$")).replace(r"\*", ".*")
    return re.compile("^" + body + ("$" if anchored else ""))


def robots_allows(rules: Sequence[tuple[bool, str]], path: str) -> bool:
    best: tuple[int, bool] | None = None
    for allow, pattern in rules:
        if _pattern_regex(pattern).match(path):
            key = (len(pattern), allow)
            if best is None or key > best:
                best = key
    return True if best is None else best[1]


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------
def file_url(key: str) -> str:
    return f"{ZENODO}/records/{RECORD_ID}/files/{key}?download=1"


def md5_of(path: Path) -> str:
    h = hashlib.md5(usedforsecurity=False)
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download_files(
    files: Mapping[str, str],
    raw_dir: Path,
    user_agent: str,
    client: httpx.Client | None = None,
    delay_s: float = CRAWL_DELAY_S,
) -> list[dict[str, object]]:
    """Download ``{key: md5}`` into ``raw_dir``; verified, never overwritten."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    own = client is None
    client = client or httpx.Client(
        headers={"User-Agent": user_agent}, timeout=120.0, follow_redirects=True
    )
    log: list[dict[str, object]] = []
    try:
        rules = parse_robots(client.get(f"{ZENODO}/robots.txt").text, user_agent)

        def guard(request: httpx.Request) -> None:
            if request.url.host == "zenodo.org" and not robots_allows(rules, request.url.path):
                raise PermissionError(f"robots.txt disallows {request.url.path}")

        client.event_hooks["request"] = [guard]
        for key, expected in files.items():
            dest = raw_dir / key
            if dest.exists():
                got = md5_of(dest)
                if got != expected:
                    raise RuntimeError(f"{dest} exists with md5 {got}, expected {expected}")
                log.append({"key": key, "status": "exists", "bytes": dest.stat().st_size})
                continue
            time.sleep(delay_s)
            tmp = dest.with_suffix(dest.suffix + ".part")
            h = hashlib.md5(usedforsecurity=False)
            with client.stream("GET", file_url(key)) as r:
                r.raise_for_status()
                with tmp.open("wb") as fh:
                    for chunk in r.iter_bytes(1 << 20):
                        fh.write(chunk)
                        h.update(chunk)
            if h.hexdigest() != expected:
                tmp.unlink()
                raise RuntimeError(f"{key}: md5 mismatch")
            tmp.rename(dest)
            dest.chmod(0o444)
            log.append({"key": key, "status": "downloaded", "bytes": dest.stat().st_size})
    finally:
        if own:
            client.close()
    return log


# ---------------------------------------------------------------------------
# Filter (DuckDB reads zstd TSV directly)
# ---------------------------------------------------------------------------
def month_of(key: str) -> str:
    """'2024-10.tsv.zst' -> '2024-10'."""
    return key.split(".", 1)[0]


def filter_file(raw_path: Path, out_path: Path, types: Sequence[str] = tuple(GPU_TYPES)) -> int:
    """Keep GPU instance types, US availability zones and Linux/UNIX; write Parquet."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    month = month_of(raw_path.name)
    type_list = ", ".join(f"'{t}'" for t in types)
    az_cond = " OR ".join(f"az_id LIKE '{p}%'" for p in US_AZ_PREFIXES)
    # Paths and literals are built by this module from constants, never from input.
    sql = f"""
        COPY (
            SELECT az_id, instance_type, product, price,
                   epoch(CAST(ts AS TIMESTAMPTZ)) AS ts_epoch, '{month}' AS month
            FROM read_csv('{raw_path.as_posix()}', delim='\t', header=false,
                          compression='zstd', quote='', escape='',
                          columns={{'az_id': 'VARCHAR', 'instance_type': 'VARCHAR',
                                    'product': 'VARCHAR', 'price': 'DOUBLE',
                                    'ts': 'VARCHAR'}})
            WHERE instance_type IN ({type_list}) AND product = '{PRODUCT}' AND ({az_cond})
        ) TO '{out_path.as_posix()}' (FORMAT PARQUET)
    """  # noqa: S608
    con = duckdb.connect()
    try:
        con.execute(sql)
        n = con.execute(f"SELECT count(*) FROM read_parquet('{out_path.as_posix()}')").fetchone()  # noqa: S608
    finally:
        con.close()
    return int(n[0]) if n else 0


def load_filtered(paths: Sequence[Path]) -> pd.DataFrame:
    if not paths:
        return pd.DataFrame(columns=list(FILTERED_COLUMNS))
    files = ", ".join(f"'{p.as_posix()}'" for p in paths)
    con = duckdb.connect()
    try:
        df = con.execute(f"SELECT * FROM read_parquet([{files}])").df()  # noqa: S608
    finally:
        con.close()
    df["ts"] = pd.to_datetime(df["ts_epoch"], unit="s", utc=True)
    return df


# ---------------------------------------------------------------------------
# Daily series
# ---------------------------------------------------------------------------
def pool_daily(
    records: pd.DataFrame,
    cutoff_utc: str = "23:30",
    types: Mapping[str, tuple[str, int]] = GPU_TYPES,
) -> pd.DataFrame:
    """Price in effect per pool at the daily cutoff, per GPU-hour.

    Only records from the same month's file are used, so a pool that the
    month-start snapshot omits is treated as not offered that month.
    """
    cols = ["day", "az_id", "instance_type", "gpu", "price_per_gpu_hour", "ts_record"]
    if records.empty:
        return pd.DataFrame(columns=cols)
    hh, mm = (int(x) for x in cutoff_utc.split(":"))
    out = []
    for month, grp in records.groupby("month", sort=True):
        start = pd.Timestamp(f"{month}-01", tz="UTC")
        days = pd.date_range(start, start + pd.offsets.MonthEnd(0), freq="D")
        cut = days + pd.Timedelta(hours=hh, minutes=mm)
        g = grp.sort_values("ts")
        for (az, it), pool in g.groupby(["az_id", "instance_type"], sort=True):
            idx = np.searchsorted(pool["ts"].to_numpy(), cut.to_numpy(), side="right") - 1
            ok = idx >= 0
            if not ok.any():
                continue
            gpu, n = types[str(it)]
            prices = pool["price"].to_numpy()[idx[ok]]
            out.append(
                pd.DataFrame(
                    {
                        "day": days[ok].date,
                        "az_id": az,
                        "instance_type": it,
                        "gpu": gpu,
                        "price_per_gpu_hour": prices / n,
                        "ts_record": pool["ts"].to_numpy()[idx[ok]],
                    }
                )
            )
    if not out:
        return pd.DataFrame(columns=cols)
    df = pd.concat(out, ignore_index=True)
    return df.loc[df["price_per_gpu_hour"] > 0, cols].reset_index(drop=True)


def iqr(x: np.ndarray) -> float:
    if x.size < 2:
        return float("nan")
    q75, q25 = np.percentile(x, [75, 25])
    return float(q75 - q25)


def class_daily(pools: pd.DataFrame) -> pd.DataFrame:
    """Per day and GPU class: pools offered, median price per GPU-hour, IQR of log price."""
    rows = []
    for (day, gpu), g in pools.groupby(["day", "gpu"], sort=True):
        p = g["price_per_gpu_hour"].to_numpy(float)
        rows.append(
            {
                "day": day,
                "gpu": gpu,
                "n_pools": len(p),
                "median_usd_per_gpu_hour": float(np.median(p)),
                "iqr_log_price": iqr(np.log(p)),
            }
        )
    return pd.DataFrame(
        rows, columns=["day", "gpu", "n_pools", "median_usd_per_gpu_hour", "iqr_log_price"]
    )


@dataclass(frozen=True)
class Coverage:
    month: str
    rows_kept: int
    pools: int
    types: tuple[str, ...]


def coverage(records: pd.DataFrame) -> list[Coverage]:
    out = []
    for month, g in records.groupby("month", sort=True):
        out.append(
            Coverage(
                str(month),
                len(g),
                int(g.groupby(["az_id", "instance_type"]).ngroups),
                tuple(sorted(g["instance_type"].unique())),
            )
        )
    return out


def url_path(url: str) -> str:
    return urlsplit(url).path
