"""Polite HTTP client: robots.txt aware, per-host rate limited, no secrets logged.

Every collector goes through :class:`PoliteClient`. It

* fetches and caches ``/robots.txt`` per host and refuses disallowed paths,
* enforces a minimum interval between requests to the same host,
* retries transient failures with exponential backoff,
* never logs request headers (which could carry credentials).
"""

from __future__ import annotations

import logging
import time
import urllib.robotparser
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlsplit

import httpx

log = logging.getLogger(__name__)


class RobotsDisallowedError(RuntimeError):
    """The target path is disallowed by the host's robots.txt."""


@dataclass
class PoliteClient:
    """Rate-limited, robots-aware wrapper around :class:`httpx.Client`."""

    user_agent: str
    min_interval_s: float = 2.0
    timeout_s: float = 30.0
    max_retries: int = 2
    sleep: Callable[[float], None] = time.sleep
    clock: Callable[[], float] = time.monotonic
    transport: httpx.BaseTransport | None = None
    _last_request: dict[str, float] = field(default_factory=dict)
    _robots: dict[str, urllib.robotparser.RobotFileParser | None] = field(default_factory=dict)
    _client: httpx.Client | None = None

    def _http(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(
                headers={"User-Agent": self.user_agent, "Accept": "application/json, */*"},
                timeout=self.timeout_s,
                follow_redirects=True,
                transport=self.transport,
            )
        return self._client

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self) -> PoliteClient:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    # ------------------------------------------------------------------
    def _throttle(self, host: str) -> None:
        last = self._last_request.get(host)
        if last is not None:
            wait = self.min_interval_s - (self.clock() - last)
            if wait > 0:
                self.sleep(wait)
        self._last_request[host] = self.clock()

    def robots_allows(self, url: str) -> bool:
        """True if ``url`` may be fetched by our user agent.

        A missing robots.txt (404) means everything is allowed. A robots.txt
        that cannot be fetched for other reasons (5xx, network) is treated as
        *disallow* to stay conservative.
        """
        parts = urlsplit(url)
        origin = f"{parts.scheme}://{parts.netloc}"
        if origin not in self._robots:
            self._throttle(parts.netloc)
            robots_url = f"{origin}/robots.txt"
            try:
                resp = self._http().get(robots_url)
            except httpx.HTTPError as exc:
                log.warning("robots.txt fetch failed for %s: %s", origin, type(exc).__name__)
                self._robots[origin] = None
                return False
            if resp.status_code in (404, 410):
                parser = urllib.robotparser.RobotFileParser()
                parser.parse([])
                self._robots[origin] = parser
            elif resp.status_code == 200:
                parser = urllib.robotparser.RobotFileParser()
                parser.parse(resp.text.splitlines())
                self._robots[origin] = parser
            else:
                log.warning("robots.txt for %s returned %s", origin, resp.status_code)
                self._robots[origin] = None
        parser = self._robots[origin]
        if parser is None:
            return False
        return parser.can_fetch(self.user_agent, url)

    def request(
        self,
        method: str,
        url: str,
        *,
        json: Any = None,
        params: dict[str, Any] | None = None,
        check_robots: bool = True,
    ) -> httpx.Response:
        """Send a request after robots and rate-limit checks; retry transient errors."""
        if check_robots and not self.robots_allows(url):
            raise RobotsDisallowedError(url)
        host = urlsplit(url).netloc
        attempt = 0
        while True:
            self._throttle(host)
            try:
                resp = self._http().request(method, url, json=json, params=params)
            except httpx.TransportError as exc:
                if attempt >= self.max_retries:
                    raise
                log.info("transport error %s on %s; retrying", type(exc).__name__, host)
            else:
                if resp.status_code < 500 and resp.status_code != 429:
                    return resp
                if attempt >= self.max_retries:
                    return resp
                log.info("status %s from %s; retrying", resp.status_code, host)
            attempt += 1
            self.sleep(self.min_interval_s * (2**attempt))

    def get(self, url: str, **kw: Any) -> httpx.Response:
        return self.request("GET", url, **kw)

    def post(self, url: str, **kw: Any) -> httpx.Response:
        return self.request("POST", url, **kw)
