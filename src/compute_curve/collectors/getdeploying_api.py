"""GetDeploying API: per-provider GPU price history (D60, docs/exploration_round7_plan.md).

Free research access granted by GetDeploying until 2026-12-14. Publishing
aggregate results with charts is allowed; raw rows are not redistributed.
Raw responses go to git-ignored ``var/getdeploying_api/<vintage>/``; the
workflow commits only an encrypted copy. The key comes from the environment
variable ``GETDEPLOYING_API_KEY`` and is never printed or logged.

robots.txt disallows ``/api/`` for crawlers. This client is not a crawler: it
calls the documented, authenticated API that GetDeploying granted us, so it
skips the robots check (D60).
"""

from __future__ import annotations

import json
import os
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

from compute_curve.http import PoliteClient

BASE = "https://getdeploying.com/api"
ENV_KEY = "GETDEPLOYING_API_KEY"
ACCESS_ENDS = "2026-12-14"
ATTRIBUTION = "GetDeploying API (getdeploying.com), research access"
GPUS = ("nvidia-h100", "nvidia-b200", "nvidia-h200")
EXCLUDED = frozenset({"vast-ai", "runpod", "together-ai"})
PAGE_SIZE = 100
MAX_REQUESTS = 2500  # the API allows 3000 a day
HISTORY_COLS = (
    "date",
    "gpu_model",
    "provider",
    "billing_type",
    "reservation_months",
    "median_price",
    "min_price",
    "max_price",
    "offering_count",
)

GetJson = Callable[[str, dict[str, Any]], dict[str, Any] | list[Any]]


class ApiError(RuntimeError):
    """A non-200 answer; the message carries the status and the API's error text only."""


class BudgetError(RuntimeError):
    """The request budget for one run would be exceeded."""


def api_key() -> str:
    key = os.environ.get(ENV_KEY, "").strip()
    if not key:
        raise ApiError(f"{ENV_KEY} is not set")
    return key


def make_get(client: PoliteClient, key: str) -> GetJson:
    """A JSON getter with the bearer header; errors never include the key."""
    headers = {"Authorization": f"Bearer {key}"}

    def get(path: str, params: dict[str, Any]) -> dict[str, Any] | list[Any]:
        resp = client.get(f"{BASE}{path}", params=params, check_robots=False, headers=headers)
        if resp.status_code != 200:
            try:
                msg = str(resp.json().get("error", ""))[:200]
            except ValueError:
                msg = ""
            raise ApiError(f"{path}: HTTP {resp.status_code} {msg}".strip())
        return resp.json()  # type: ignore[no-any-return]

    return get


@dataclass
class Counter:
    """Wraps a getter, counts requests and stops before the budget is exceeded."""

    get: GetJson
    limit: int = MAX_REQUESTS
    n: int = 0
    paths: list[str] = field(default_factory=list)

    def __call__(self, path: str, params: dict[str, Any]) -> dict[str, Any] | list[Any]:
        if self.n >= self.limit:
            raise BudgetError(f"request budget {self.limit} reached")
        self.n += 1
        self.paths.append(path)
        return self.get(path, params)


def fetch_pages(get: GetJson, path: str, params: dict[str, Any]) -> list[dict[str, Any]]:
    """All rows of a paginated endpoint."""
    rows: list[dict[str, Any]] = []
    page = 1
    while True:
        body = get(path, {**params, "page": page, "page_size": PAGE_SIZE})
        if not isinstance(body, dict):
            raise ApiError(f"{path}: unexpected payload")
        rows.extend(body.get("data") or [])
        if page >= int(body.get("page_count") or 0):
            return rows
        page += 1


def provider_ids(providers: Iterable[dict[str, Any]]) -> list[str]:
    """Provider slugs to request: everything except the excluded ones, sorted."""
    ids = {str(p.get("id", "")) for p in providers}
    return sorted(i for i in ids if i and i not in EXCLUDED)


def drop_excluded(rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Remove rows of excluded providers (offerings nest the slug under ``provider``)."""
    out = []
    for r in rows:
        prov = r.get("provider")
        slug = prov.get("id") if isinstance(prov, dict) else prov
        if slug not in EXCLUDED:
            out.append(r)
    return out


def _write(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, separators=(",", ":"), sort_keys=True))


def download(get: GetJson, root: Path, now: datetime, gpus: Iterable[str] = GPUS) -> dict[str, Any]:
    """Full per-provider history and today's offerings into ``root/<vintage>/``."""
    vintage = f"{now:%Y%m%dT%H%M%SZ}"
    out = root / vintage
    if out.exists():
        raise FileExistsError(out)
    counted = get if isinstance(get, Counter) else Counter(get)
    providers = counted("/providers", {})
    gpu_list = counted("/gpus", {})
    _write(out / "providers.json", providers)
    _write(out / "gpus.json", gpu_list)
    ids = provider_ids(providers if isinstance(providers, list) else [])
    n_rows: dict[str, int] = {}
    for gpu in gpus:
        offers = drop_excluded(fetch_pages(counted, "/gpu-offerings", {"gpu_model": gpu}))
        _write(out / "offerings" / f"{gpu}.json", offers)
        total = 0
        for prov in ids:
            rows = fetch_pages(
                counted,
                "/gpu-price-history",
                {"gpu_model": gpu, "provider": prov, "interval": "daily"},
            )
            if rows:
                _write(out / "history" / gpu / f"{prov}.json", drop_excluded(rows))
                total += len(rows)
        n_rows[gpu] = total
    manifest = {
        "vintage": vintage,
        "downloaded_utc": now.isoformat(),
        "n_requests": counted.n,
        "n_providers_requested": len(ids),
        "excluded": sorted(EXCLUDED),
        "history_rows": n_rows,
        "attribution": ATTRIBUTION,
    }
    _write(out / "manifest.json", manifest)
    return manifest


def _num(x: Any) -> float | None:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v


def history_frame(rows: Iterable[dict[str, Any]], vintage: str = "") -> pd.DataFrame:
    """Normalised history rows; ``ts_observed`` is 00:00 UTC the day after the snapshot."""
    recs = []
    for r in drop_excluded(rows):
        rec = {k: r.get(k) for k in HISTORY_COLS}
        for k in ("median_price", "min_price", "max_price"):
            rec[k] = _num(rec[k])
        recs.append(rec)
    df = pd.DataFrame(recs, columns=list(HISTORY_COLS))
    if df.empty:
        return df.assign(ts_observed=pd.Series(dtype="datetime64[ns, UTC]"), vintage=vintage)
    day = pd.to_datetime(df["date"], utc=True)
    return df.assign(ts_observed=day + timedelta(days=1), vintage=vintage)


def latest_vintage(root: Path) -> Path | None:
    done = sorted(p.parent for p in root.glob("*/manifest.json"))
    return done[-1] if done else None


def load_history(vintage_dir: Path) -> pd.DataFrame:  # pragma: no cover - reads local files
    frames = []
    for f in sorted((vintage_dir / "history").glob("*/*.json")):
        frames.append(history_frame(json.loads(f.read_text()), vintage_dir.name))
    frames = [f for f in frames if not f.empty]
    return pd.concat(frames, ignore_index=True) if frames else history_frame([])


def check(get: GetJson) -> dict[str, Any]:
    """One cheap call: how many GPU models and providers the key can see."""
    gpus = get("/gpus", {})
    provs = get("/providers", {})
    return {
        "ok": True,
        "n_gpu_models": len(gpus) if isinstance(gpus, list) else None,
        "n_providers": len(provs) if isinstance(provs, list) else None,
        "checked_utc": datetime.now(UTC).isoformat(timespec="seconds"),
    }
