"""GetDeploying API client: pagination, exclusions, budget, key hygiene. Fake API, no network."""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx
import pytest

from compute_curve.collectors import getdeploying_api as gd
from compute_curve.http import PoliteClient

NOW = datetime(2026, 10, 20, 6, 0, tzinfo=UTC)


def _hist(provider: str, n: int) -> list[dict[str, Any]]:
    return [
        {
            "date": f"2026-01-{i + 1:02d}",
            "gpu_model": "nvidia-h100",
            "provider": provider,
            "billing_type": "ON_DEMAND",
            "reservation_months": None,
            "median_price": "2.50",
            "min_price": "2.00",
            "max_price": "3.00",
            "offering_count": 2,
        }
        for i in range(n)
    ]


class FakeApi:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self.hist = {"lambda-labs": _hist("lambda-labs", 150), "nebius": _hist("nebius", 3)}

    def __call__(self, path: str, params: dict[str, Any]) -> dict[str, Any] | list[Any]:
        self.calls.append((path, params))
        rows: list[dict[str, Any]]
        if path == "/providers":  # paginated, like every list endpoint of the real API
            rows = [{"id": p} for p in ("lambda-labs", "nebius", "vast-ai", "runpod", "heroku")]
        elif path == "/gpus":
            rows = [{"id": "nvidia-h100"}]
        elif path == "/gpu-offerings":
            rows = [{"provider": {"id": "vast-ai"}}, {"provider": {"id": "nebius"}}]
        else:
            rows = (
                self.hist.get(params["provider"], [])
                if params["gpu_model"] == "nvidia-h100"
                else []
            )
        size, page = params["page_size"], params["page"]
        pc = (len(rows) + size - 1) // size
        return {
            "page": page,
            "page_count": pc,
            "total": len(rows),
            "data": rows[(page - 1) * size : page * size],
        }


def test_download_paginates_skips_excluded_and_writes_manifest(tmp_path: Path) -> None:
    api = FakeApi()
    man = gd.download(api, tmp_path, NOW, gpus=("nvidia-h100",))
    requested = {p["provider"] for path, p in api.calls if path == "/gpu-price-history"}
    assert requested == {"lambda-labs", "nebius", "heroku"}
    assert man["history_rows"] == {"nvidia-h100": 153}
    vint = tmp_path / man["vintage"]
    rows = json.loads((vint / "history/nvidia-h100/lambda-labs.json").read_text())
    assert len(rows) == 150
    assert not (vint / "history/nvidia-h100/heroku.json").exists()
    offers = json.loads((vint / "offerings/nvidia-h100.json").read_text())
    assert offers == [{"provider": {"id": "nebius"}}]
    assert gd.latest_vintage(tmp_path) == vint
    with pytest.raises(FileExistsError):
        gd.download(api, tmp_path, NOW, gpus=("nvidia-h100",))


def test_check_reports_paginated_totals() -> None:
    out = gd.check(FakeApi())
    assert out["ok"] and out["n_gpu_models"] == 1 and out["n_providers"] == 5


def test_budget_stops_before_the_daily_limit(tmp_path: Path) -> None:
    with pytest.raises(gd.BudgetError):
        gd.download(gd.Counter(FakeApi(), limit=4), tmp_path, NOW, gpus=("nvidia-h100",))
    assert gd.latest_vintage(tmp_path) is None  # no manifest for a partial run


def test_history_frame_parses_prices_and_dates_observation_next_day() -> None:
    rows = _hist("nebius", 2) + _hist("runpod", 1)
    rows[0]["median_price"] = "n/a"
    df = gd.history_frame(rows, "v1")
    assert len(df) == 2 and set(df["provider"]) == {"nebius"}
    assert df["median_price"].isna().iloc[0] and df["median_price"].iloc[1] == 2.5
    assert df["ts_observed"].iloc[0] == datetime(2026, 1, 2, tzinfo=UTC)


def test_key_goes_in_the_header_and_never_in_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[httpx.Request] = []

    def handler(req: httpx.Request) -> httpx.Response:
        seen.append(req)
        if req.url.path.endswith("/gpus"):
            return httpx.Response(200, json=[{"id": "nvidia-h100"}])
        return httpx.Response(401, json={"error": "Invalid token"})

    client = PoliteClient(
        user_agent="t",
        min_interval_s=0,
        transport=httpx.MockTransport(handler),
        sleep=lambda s: None,
    )
    secret = "sk-test-not-a-real-key"  # noqa: S105
    get = gd.make_get(client, secret)
    assert get("/gpus", {}) == [{"id": "nvidia-h100"}]
    assert seen[0].headers["Authorization"] == f"Bearer {secret}"
    assert all(not r.url.path.endswith("robots.txt") for r in seen)
    with pytest.raises(gd.ApiError) as err:
        get("/providers", {})
    assert "401" in str(err.value) and "Invalid token" in str(err.value)
    assert secret not in str(err.value)
    monkeypatch.delenv(gd.ENV_KEY, raising=False)
    with pytest.raises(gd.ApiError):
        gd.api_key()


def test_error_description_names_a_bot_challenge() -> None:
    html = httpx.Response(
        403,
        headers={"content-type": "text/html; charset=UTF-8", "cf-mitigated": "challenge"},
        text="<html><title>Just a moment...</title></html>",
    )
    assert "Cloudflare challenge" in gd.describe_error(html)
    plain = httpx.Response(403, headers={"content-type": "text/html"}, text="<title>Denied</title>")
    assert "Denied" in gd.describe_error(plain)
    js = httpx.Response(403, json={"detail": "Key inactive"})
    assert "Key inactive" in gd.describe_error(js)
