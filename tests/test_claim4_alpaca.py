"""The paper-only guard: every way of pointing an Alpaca client elsewhere must fail.

No network: every client here uses ``httpx.MockTransport``.
"""

from __future__ import annotations

import httpx
import pytest

from compute_curve.claim4.alpaca import (
    PAPER_ROOT,
    AlpacaConfigError,
    AlpacaCredentials,
    AlpacaDataClient,
    AlpacaPaperClient,
    AlpacaRequestError,
    LiveEndpointRefusedError,
    env_status,
    require_paper_base_url,
)

FAKE_KEY = "PKTESTKEYNOTREAL"
FAKE_SK = "not-a-real-secret-value"


def env(base: str | None = "https://paper-api.alpaca.markets") -> dict[str, str]:
    e = {"APCA_API_KEY_ID": FAKE_KEY, "APCA_API_SECRET_KEY": FAKE_SK}
    if base is not None:
        e["APCA_API_BASE_URL"] = base
    return e


@pytest.mark.parametrize(
    "url",
    [
        "https://paper-api.alpaca.markets",
        "https://paper-api.alpaca.markets/",
        "https://paper-api.alpaca.markets/v2",
        "https://paper-api.alpaca.markets/v2/",
        "  https://paper-api.alpaca.markets  ",
        "https://PAPER-API.alpaca.markets",
    ],
)
def test_paper_urls_accepted(url):
    assert require_paper_base_url(url) == PAPER_ROOT


@pytest.mark.parametrize(
    "url",
    [
        None,
        "",
        "   ",
        "https://api.alpaca.markets",
        "https://api.alpaca.markets/v2",
        "http://paper-api.alpaca.markets",
        "https://paper-api.alpaca.markets:443",
        "https://paper-api.alpaca.markets:8443",
        "https://paper-api.alpaca.markets.evil.example",
        "https://evil.example/paper-api.alpaca.markets",
        "https://user:pw@paper-api.alpaca.markets",
        "https://paper-api.alpaca.markets@api.alpaca.markets",
        "https://paper-api.alpaca.markets\\@api.alpaca.markets",
        "https://paper-api.alpaca.markets/v1",
        "https://paper-api.alpaca.markets/v2/orders",
        "https://paper-api.alpaca.markets?next=https://api.alpaca.markets",
        "https://paper-api.alpaca.markets#frag",
        "https://pаper-api.alpaca.markets",  # Cyrillic 'a' look-alike
        "paper-api.alpaca.markets",
        "https://data.alpaca.markets",
        "https://paper-api.alpaca.markets /v2",
    ],
)
def test_everything_else_refused(url):
    with pytest.raises(LiveEndpointRefusedError):
        require_paper_base_url(url)


def test_live_host_message_is_explicit():
    with pytest.raises(LiveEndpointRefusedError, match="LIVE"):
        require_paper_base_url("https://api.alpaca.markets")


def _counting_transport(calls: list[httpx.Request], status: int = 200, body: object = None):
    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(status, json=body if body is not None else {})

    return httpx.MockTransport(handler)


@pytest.mark.parametrize("cls", [AlpacaPaperClient, AlpacaDataClient])
@pytest.mark.parametrize(
    "base", [None, "https://api.alpaca.markets", "http://paper-api.alpaca.markets"]
)
def test_clients_refuse_to_start_off_paper(cls, base):
    calls: list[httpx.Request] = []
    with pytest.raises(LiveEndpointRefusedError):
        cls(env=env(base), transport=_counting_transport(calls))
    assert calls == []


def test_missing_credentials_fail_without_revealing_values():
    with pytest.raises(AlpacaConfigError) as ei:
        AlpacaPaperClient(env={"APCA_API_BASE_URL": "https://paper-api.alpaca.markets"})
    assert "APCA_API_KEY_ID" in str(ei.value)


def test_paper_client_only_talks_to_paper_host():
    calls: list[httpx.Request] = []
    c = AlpacaPaperClient(
        env=env(), transport=_counting_transport(calls, body={"status": "ACTIVE"}), min_interval_s=0
    )
    assert c.account()["status"] == "ACTIVE"
    assert calls[0].url.host == "paper-api.alpaca.markets"
    assert calls[0].url.scheme == "https"
    assert calls[0].headers["APCA-API-KEY-ID"] == FAKE_KEY
    # A direct request to any other host is blocked by the request hook.
    for url in ["https://api.alpaca.markets/v2/account", "https://evil.example/v2/account"]:
        with pytest.raises(LiveEndpointRefusedError):
            c._client.get(url)
    assert len(calls) == 1


def test_redirects_are_not_followed():
    calls: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        return httpx.Response(302, headers={"location": "https://api.alpaca.markets/v2/orders"})

    c = AlpacaPaperClient(env=env(), transport=httpx.MockTransport(handler), min_interval_s=0)
    with pytest.raises(AlpacaRequestError):
        c.submit_order(
            {"symbol": "XLK", "qty": "1", "side": "buy", "type": "market", "time_in_force": "day"}
        )
    assert len(calls) == 1 and calls[0].url.host == "paper-api.alpaca.markets"


def test_odd_paths_refused():
    calls: list[httpx.Request] = []
    c = AlpacaPaperClient(env=env(), transport=_counting_transport(calls), min_interval_s=0)
    for path in ["//api.alpaca.markets/v2/account", "v2/account", "/v2/@api.alpaca.markets"]:
        with pytest.raises(LiveEndpointRefusedError):
            c.request("GET", path)
    assert calls == []


def test_data_client_is_get_only_and_data_host_only():
    calls: list[httpx.Request] = []
    body = {"bars": {"SPY": [{"t": "2026-09-01T04:00:00Z", "c": 1.0}]}, "next_page_token": None}
    c = AlpacaDataClient(
        env=env(), transport=_counting_transport(calls, body=body), min_interval_s=0
    )
    out = c.daily_bars(["SPY"], "2026-09-01", "2026-09-02")
    assert len(out["SPY"]) == 1
    assert calls[0].url.host == "data.alpaca.markets"
    with pytest.raises(LiveEndpointRefusedError):
        c.request("POST", "/v2/stocks/bars")
    assert len(calls) == 1


def test_bars_follow_pagination():
    pages = [
        {"bars": {"A": [{"t": "1"}]}, "next_page_token": "tok"},
        {"bars": {"A": [{"t": "2"}], "B": [{"t": "2"}]}, "next_page_token": None},
    ]
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json=pages[len(seen) - 1])

    c = AlpacaDataClient(env=env(), transport=httpx.MockTransport(handler), min_interval_s=0)
    out = c.daily_bars(["A", "B"], "2026-09-01", "2026-09-30")
    assert [b["t"] for b in out["A"]] == ["1", "2"]
    assert seen[1].url.params["page_token"] == "tok"  # noqa: S105


def test_credentials_never_in_repr_or_env_status():
    creds = AlpacaCredentials.from_env(env())
    assert FAKE_SK not in repr(creds) and FAKE_KEY not in repr(creds)
    status = env_status(env())
    assert status == {
        "APCA_API_KEY_ID": True,
        "APCA_API_SECRET_KEY": True,
        "APCA_API_BASE_URL": True,
    }
    assert FAKE_SK not in str(status)


def test_error_message_does_not_echo_secret():
    calls: list[httpx.Request] = []
    c = AlpacaPaperClient(
        env=env(),
        transport=_counting_transport(calls, status=403, body={"message": "forbidden"}),
        min_interval_s=0,
        max_retries=0,
    )
    with pytest.raises(AlpacaRequestError) as ei:
        c.account()
    assert FAKE_SK not in str(ei.value) and FAKE_KEY not in str(ei.value)
