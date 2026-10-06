"""Alpaca clients for claim 4: paper trading API and market data API.

Hard limits, enforced in code and in ``tests/test_claim4_alpaca.py``:

* Every client calls :func:`require_paper_base_url` when it is built. Unless
  ``APCA_API_BASE_URL`` is exactly ``https://paper-api.alpaca.markets``
  (optionally followed by ``/v2``), it raises :class:`LiveEndpointRefusedError`
  and no request is ever built.
* Request URLs are built from the constants below, never from the
  environment string, and an httpx request hook re-checks the scheme and
  host of every request before it is sent. Redirects are not followed.
* The data client sends ``GET`` requests only.
* Credentials come from the environment. They are sent only as Alpaca's
  authentication headers and never appear in a ``repr``, log line or
  exception message.

There is no code path to Alpaca's live trading host.
"""

from __future__ import annotations

import logging
import os
import time
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlsplit

import httpx

log = logging.getLogger(__name__)

PAPER_HOST = "paper-api.alpaca.markets"
PAPER_ROOT = f"https://{PAPER_HOST}"
DATA_HOST = "data.alpaca.markets"
DATA_ROOT = f"https://{DATA_HOST}"
LIVE_HOST = "api.alpaca.markets"

ENV_NAMES = ("APCA_API_KEY_ID", "APCA_API_SECRET_KEY", "APCA_API_BASE_URL")
USER_AGENT = "compute-curve-research/0.1 (personal non-commercial paper-trading research)"


class LiveEndpointRefusedError(RuntimeError):
    """Raised when any Alpaca client is asked to use anything but the paper endpoint."""


class AlpacaConfigError(RuntimeError):
    """Raised when Alpaca credentials are missing."""


class AlpacaRequestError(RuntimeError):
    """An Alpaca API call returned an error status."""


def require_paper_base_url(value: str | None) -> str:
    """Return the canonical paper root URL, or raise :class:`LiveEndpointRefusedError`.

    Accepted: ``https://paper-api.alpaca.markets`` with an optional trailing
    ``/`` or ``/v2``. Rejected: anything else, including the live host, other
    schemes, explicit ports, credentials in the URL, query strings,
    fragments, look-alike hosts and backslashes. The returned value is the
    module constant, never the input string.
    """
    if value is None or not value.strip():
        raise LiveEndpointRefusedError("APCA_API_BASE_URL is not set; refusing to start")
    raw = value.strip()
    if "\\" in raw or any(ch.isspace() for ch in raw):
        raise LiveEndpointRefusedError("APCA_API_BASE_URL is malformed; refusing to start")
    try:
        parts = urlsplit(raw)
        port = parts.port
    except ValueError as exc:
        raise LiveEndpointRefusedError("APCA_API_BASE_URL is malformed; refusing to start") from exc
    if parts.hostname == LIVE_HOST:
        raise LiveEndpointRefusedError(
            "APCA_API_BASE_URL points at Alpaca's LIVE trading host; this project is "
            "paper-only and will not start"
        )
    ok = (
        parts.scheme == "https"
        and parts.hostname == PAPER_HOST
        and parts.netloc.lower() == PAPER_HOST
        and port is None
        and parts.username is None
        and parts.password is None
        and parts.path.rstrip("/") in ("", "/v2")
        and not parts.query
        and not parts.fragment
    )
    if not ok:
        raise LiveEndpointRefusedError(
            f"APCA_API_BASE_URL is not the Alpaca paper endpoint {PAPER_ROOT}; refusing to start"
        )
    return PAPER_ROOT


@dataclass(frozen=True)
class AlpacaCredentials:
    """API key pair read from the environment. ``repr`` never shows values."""

    key_id: str = field(repr=False)
    secret_key: str = field(repr=False)

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> AlpacaCredentials:
        e = os.environ if env is None else env
        key, secret = e.get(ENV_NAMES[0], ""), e.get(ENV_NAMES[1], "")
        missing = [n for n, v in zip(ENV_NAMES[:2], (key, secret), strict=True) if not v]
        if missing:
            raise AlpacaConfigError(f"missing environment variables: {', '.join(missing)}")
        return cls(key_id=key, secret_key=secret)

    def headers(self) -> dict[str, str]:
        return {"APCA-API-KEY-ID": self.key_id, "APCA-API-SECRET-KEY": self.secret_key}


def env_status(env: Mapping[str, str] | None = None) -> dict[str, bool]:
    """Which Alpaca variables are set (names only; values are never returned)."""
    e = os.environ if env is None else env
    return {n: bool(e.get(n)) for n in ENV_NAMES}


def _host_guard(allowed_host: str, allowed_methods: frozenset[str] | None) -> Any:
    def hook(request: httpx.Request) -> None:
        if request.url.scheme != "https" or request.url.host != allowed_host:
            raise LiveEndpointRefusedError(f"request to a host other than {allowed_host} blocked")
        if request.url.port not in (None, 443):
            raise LiveEndpointRefusedError("request with a non-standard port blocked")
        if allowed_methods is not None and request.method not in allowed_methods:
            raise LiveEndpointRefusedError(f"{request.method} not allowed on {allowed_host}")

    return hook


class _BaseClient:
    """Shared plumbing: guard, pacing, retries on 429 and 5xx, safe errors."""

    root: str
    host: str
    methods: frozenset[str] | None = None

    def __init__(
        self,
        env: Mapping[str, str] | None = None,
        transport: httpx.BaseTransport | None = None,
        min_interval_s: float = 0.35,
        timeout_s: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        e = os.environ if env is None else env
        require_paper_base_url(e.get("APCA_API_BASE_URL"))
        creds = AlpacaCredentials.from_env(e)
        self._min_interval = min_interval_s
        self._max_retries = max_retries
        self._last = 0.0
        self._client = httpx.Client(
            base_url=self.root,
            headers={**creds.headers(), "User-Agent": USER_AGENT},
            timeout=timeout_s,
            follow_redirects=False,
            transport=transport,
            event_hooks={"request": [_host_guard(self.host, self.methods)]},
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> _BaseClient:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def _pace(self) -> None:
        wait = self._min_interval - (time.monotonic() - self._last)
        if wait > 0:
            time.sleep(wait)
        self._last = time.monotonic()

    def request(
        self,
        method: str,
        path: str,
        params: Mapping[str, Any] | None = None,
        json_body: Mapping[str, Any] | None = None,
    ) -> Any:
        if not path.startswith("/") or "//" in path or "@" in path:
            raise LiveEndpointRefusedError("request paths must be absolute API paths")
        for attempt in range(self._max_retries + 1):
            self._pace()
            r = self._client.request(method, path, params=params, json=json_body)
            retryable = r.status_code == 429 or r.status_code >= 500
            if retryable and attempt < self._max_retries:
                time.sleep(min(30.0, 2.0 ** (attempt + 1)))
                continue
            if r.status_code >= 300:
                # Alpaca error bodies are short JSON messages; headers are never echoed.
                raise AlpacaRequestError(f"{method} {path} -> HTTP {r.status_code}: {r.text[:300]}")
            if r.status_code == 204 or not r.content:
                return None
            return r.json()
        raise AlpacaRequestError(f"{method} {path}: retries exhausted")  # pragma: no cover


class AlpacaPaperClient(_BaseClient):
    """Alpaca *paper* trading API. Cannot be pointed anywhere else."""

    root = PAPER_ROOT
    host = PAPER_HOST

    def account(self) -> dict[str, Any]:
        return self.request("GET", "/v2/account")

    def clock(self) -> dict[str, Any]:
        return self.request("GET", "/v2/clock")

    def calendar(self, start: str, end: str) -> list[dict[str, Any]]:
        return self.request("GET", "/v2/calendar", params={"start": start, "end": end})

    def asset(self, symbol: str) -> dict[str, Any]:
        return self.request("GET", f"/v2/assets/{symbol}")

    def positions(self) -> list[dict[str, Any]]:
        return self.request("GET", "/v2/positions")

    def orders(self, status: str = "open", limit: int = 500) -> list[dict[str, Any]]:
        return self.request("GET", "/v2/orders", params={"status": status, "limit": limit})

    def portfolio_history(self, period: str = "3M", timeframe: str = "1D") -> dict[str, Any]:
        return self.request(
            "GET",
            "/v2/account/portfolio/history",
            params={"period": period, "timeframe": timeframe},
        )

    def submit_order(self, order: Mapping[str, Any]) -> dict[str, Any]:
        """Submit one paper order. Callers must pass the claim-4 gate and risk checks first."""
        return self.request("POST", "/v2/orders", json_body=order)

    def cancel_order(self, order_id: str) -> Any:
        if not order_id.replace("-", "").isalnum():
            raise ValueError("unexpected order id format")
        return self.request("DELETE", f"/v2/orders/{order_id}")


class AlpacaDataClient(_BaseClient):
    """Alpaca market data API, read-only. Still refuses to start off the paper endpoint."""

    root = DATA_ROOT
    host = DATA_HOST
    methods = frozenset({"GET"})

    def daily_bars(
        self,
        symbols: list[str],
        start: str,
        end: str,
        feed: str = "sip",
        adjustment: str = "all",
    ) -> dict[str, list[dict[str, Any]]]:
        """Daily bars for ``symbols`` between ISO dates ``start`` and ``end``, all pages."""
        out: dict[str, list[dict[str, Any]]] = {s: [] for s in symbols}
        token: str | None = None
        while True:
            params: dict[str, Any] = {
                "symbols": ",".join(symbols),
                "timeframe": "1Day",
                "start": start,
                "end": end,
                "feed": feed,
                "adjustment": adjustment,
                "limit": 10000,
                "sort": "asc",
            }
            if token:
                params["page_token"] = token
            page = self.request("GET", "/v2/stocks/bars", params=params)
            for sym, bars in (page.get("bars") or {}).items():
                out.setdefault(sym, []).extend(bars)
            token = page.get("next_page_token")
            if not token:
                return out
