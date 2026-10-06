"""Claim-4 orchestration end to end against a fake Alpaca. SYNTHETIC data; no network."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import httpx
import pandas as pd
import pytest

from compute_curve.claim4 import pipeline as c4p
from compute_curve.claim4.alpaca import (
    AlpacaDataClient,
    AlpacaPaperClient,
    LiveEndpointRefusedError,
)
from compute_curve.claim4.market_data import sessions_from_calendar
from compute_curve.cli import main
from compute_curve.synthetic import (
    synthetic_bars_json,
    synthetic_equity_bars,
    synthetic_signals,
    synthetic_weekday_calendar,
)

ENV = {
    "APCA_API_KEY_ID": "PKTESTONLY",
    "APCA_API_BASE_URL": "https://paper-api.alpaca.markets",
    "APCA_API_SECRET_KEY": "test-only",
}
SUNDAY_EVENING = pd.Timestamp("2026-10-11 23:40", tz="UTC")  # decides for Monday 10-12
FRIDAY_EVENING = pd.Timestamp("2026-10-09 23:40", tz="UTC")  # Monday is two days away


class FakeAlpaca:
    """Answers the endpoints the claim-4 code uses; records every write."""

    def __init__(self, calendar, bars_json, positions=None, account=None):
        self.calendar = calendar
        self.bars_json = bars_json
        self.positions = positions or []
        self.account = account or {"equity": "100000", "last_equity": "100000", "status": "ACTIVE"}
        self.posted: list[dict] = []
        self.deleted: list[str] = []

    def paper(self, request: httpx.Request) -> httpx.Response:  # noqa: PLR0911
        path, method = request.url.path, request.method
        if method == "GET" and path == "/v2/calendar":
            lo, hi = request.url.params["start"], request.url.params["end"]
            return httpx.Response(200, json=[c for c in self.calendar if lo <= c["date"] <= hi])
        if method == "GET" and path == "/v2/account":
            return httpx.Response(200, json=self.account)
        if method == "GET" and path == "/v2/account/portfolio/history":
            return httpx.Response(200, json={"timestamp": [], "equity": [], "profit_loss": []})
        if method == "GET" and path == "/v2/positions":
            return httpx.Response(200, json=self.positions)
        if method == "GET" and path == "/v2/orders":
            return httpx.Response(200, json=[])
        if method == "POST" and path == "/v2/orders":
            body = json.loads(request.content)
            self.posted.append(body)
            return httpx.Response(200, json={"id": f"id{len(self.posted)}", "status": "accepted"})
        if method == "DELETE" and path.startswith("/v2/orders/"):
            self.deleted.append(path)
            return httpx.Response(204)
        if method == "GET" and path.startswith("/v2/assets/"):
            sym = path.rsplit("/", 1)[-1]
            return httpx.Response(
                200, json={"symbol": sym, "shortable": True, "fractionable": True}
            )
        return httpx.Response(404, json={"message": "not found"})

    def data(self, request: httpx.Request) -> httpx.Response:
        if request.method == "GET" and request.url.path == "/v2/stocks/bars":
            syms = request.url.params["symbols"].split(",")
            lo, hi = request.url.params["start"], request.url.params["end"]
            out = {
                s: [b for b in self.bars_json.get(s, []) if lo <= b["t"][:10] <= hi] for s in syms
            }
            return httpx.Response(200, json={"bars": out, "next_page_token": None})
        return httpx.Response(404)

    def clients(self):
        p = AlpacaPaperClient(env=ENV, transport=httpx.MockTransport(self.paper), min_interval_s=0)
        d = AlpacaDataClient(env=ENV, transport=httpx.MockTransport(self.data), min_interval_s=0)
        return p, d


def make_world(cfg, tmp_path: Path, monkeypatch, effect: float = 0.0, positions=None):
    project = cfg.project.model_copy(
        update={"var_dir": tmp_path / "var", "reports_dir": tmp_path / "reports"}
    )
    boot = cfg.bootstrap.model_copy(update={"n_boot": 100})
    cfg = cfg.model_copy(update={"project": project, "bootstrap": boot})
    c4 = cfg.claim4
    calendar = synthetic_weekday_calendar(date(2026, 6, 1), date(2026, 12, 31))
    sessions = sessions_from_calendar(calendar)
    signals = synthetic_signals(sessions, seed=5)
    # A large signal for the decided session makes the forecast clear the trading cost.
    signals.loc[signals["session"] == date(2026, 10, 12), "level_h100"] = 0.05
    past = sessions.loc[sessions["session"] <= date(2026, 10, 9)].reset_index(drop=True)
    bars = synthetic_equity_bars(
        past,
        c4.universe.members(),
        c4.benchmark,
        seed=5,
        effect=effect,
        driver=signals.loc[: len(past) - 1, "level_h100"].to_numpy(),
    )
    monkeypatch.setattr(c4p, "build_signals", lambda *a, **k: (signals, {}))
    fake = FakeAlpaca(calendar, synthetic_bars_json(bars), positions=positions)
    return cfg, fake


def run(cfg, fake, now, env=None):
    paper, data = fake.clients()
    c4p.run_evaluation(cfg, now=now, paper=paper, data=data, observations=pd.DataFrame())
    return c4p.run_daily(
        cfg, now=now, paper=paper, data=data, observations=pd.DataFrame(), env=env or {}
    )


def test_shadow_mode_sends_no_order_and_logs_once(cfg, tmp_path, monkeypatch):
    cfg, fake = make_world(cfg, tmp_path, monkeypatch)
    report = run(cfg, fake, SUNDAY_EVENING)
    assert fake.posted == [] and fake.deleted == []
    text = report.read_text()
    assert "SHADOW" in text and "2026-10-12" in text
    preds = pd.read_csv(c4p.paths(cfg)["predictions"], dtype=str)
    assert len(preds) == 1 and preds["action"].iloc[0] == "shadow"
    assert preds["target_session"].iloc[0] == "2026-10-12"
    run(cfg, fake, SUNDAY_EVENING + pd.Timedelta(minutes=20))
    assert len(pd.read_csv(c4p.paths(cfg)["predictions"], dtype=str)) == 1  # first decision stands
    validation = json.loads(c4p.paths(cfg)["validation"].read_text())
    assert validation["selected"] is None


def test_friday_evening_defers_to_sunday(cfg, tmp_path, monkeypatch):
    cfg, fake = make_world(cfg, tmp_path, monkeypatch)
    report = run(cfg, fake, FRIDAY_EVENING)
    assert "DEFERRED" in report.read_text()
    assert not c4p.paths(cfg)["predictions"].exists()
    assert fake.posted == []


def test_decision_window_rules(cfg):
    c4 = cfg.claim4
    s = sessions_from_calendar(synthetic_weekday_calendar(date(2026, 10, 5), date(2026, 10, 20)))
    tgt, _, start, end = c4p.decision_window(s, pd.Timestamp("2026-10-06 15:00", tz="UTC"), c4)
    assert tgt == date(2026, 10, 7)
    assert not start <= pd.Timestamp("2026-10-06 15:00", tz="UTC") <= end
    assert start == pd.Timestamp("2026-10-06 23:30", tz="UTC")


def _force_gate(cfg, pair: str) -> None:
    p = c4p.paths(cfg)["validation"]
    data = json.loads(p.read_text())
    data["selected"] = pair
    p.write_text(json.dumps(data))


def test_gated_paper_orders_respect_hard_limits(cfg, tmp_path, monkeypatch):
    cfg, fake = make_world(cfg, tmp_path, monkeypatch, effect=1.0)
    paper, data = fake.clients()
    c4p.run_evaluation(cfg, now=SUNDAY_EVENING, paper=paper, data=data, observations=pd.DataFrame())
    _force_gate(cfg, "level_h100|h1")  # stands in for a gate that passed
    report = c4p.run_daily(
        cfg, now=SUNDAY_EVENING, paper=paper, data=data, observations=pd.DataFrame(), env={}
    )
    c4 = cfg.claim4
    managed = {*c4.universe.members(), c4.benchmark}
    assert fake.posted, report.read_text()
    assert {o["symbol"] for o in fake.posted} <= managed
    assert all(o["client_order_id"].startswith("c4-2026-10-12-") for o in fake.posted)
    assert all(o["type"] == "market" and o["time_in_force"] == "day" for o in fake.posted)
    bars = pd.DataFrame(
        [(s, b["c"]) for s, bs in fake.bars_json.items() for b in bs[-1:]], columns=["s", "c"]
    )
    last = dict(zip(bars["s"], bars["c"], strict=True))
    notional = {o["symbol"]: float(o["qty"]) * last[o["symbol"]] for o in fake.posted}
    assert max(notional.values()) <= c4.risk.max_position_usd + 1e-6
    assert sum(notional.values()) <= c4.risk.max_gross_exposure_usd + 1e-6
    assert "PAPER" in report.read_text()
    assert c4p.paths(cfg)["orders"].exists()


def test_kill_switch_flattens_only_claim4_positions(cfg, tmp_path, monkeypatch):
    positions = [
        {"symbol": "NVDA", "qty": "3", "side": "long"},
        {"symbol": "XLK", "qty": "-5", "side": "short"},
        {"symbol": "AAPL", "qty": "10", "side": "long"},
    ]
    cfg, fake = make_world(cfg, tmp_path, monkeypatch, positions=positions)
    paper, data = fake.clients()
    c4p.run_evaluation(cfg, now=SUNDAY_EVENING, paper=paper, data=data, observations=pd.DataFrame())
    _force_gate(cfg, "level_h100|h1")
    c4p.append_rows(
        c4p.paths(cfg)["predictions"],
        c4p.PRED_FIELDS,
        [{"target_session": "2026-10-09", "action": "paper"}],
    )
    report = c4p.run_daily(
        cfg,
        now=SUNDAY_EVENING,
        paper=paper,
        data=data,
        observations=pd.DataFrame(),
        env={"COMPUTE_CURVE_KILL_SWITCH": "1"},
    )
    got = {(o["symbol"], o["side"], o["qty"]) for o in fake.posted}
    assert got == {("NVDA", "sell", "3"), ("XLK", "buy", "5")}
    assert "FLATTEN" in report.read_text()


def test_cli_refuses_the_live_endpoint(monkeypatch):
    monkeypatch.setenv("APCA_API_BASE_URL", "https://api.alpaca.markets")
    monkeypatch.setenv("APCA_API_KEY_ID", "x")
    monkeypatch.setenv("APCA_API_SECRET_KEY", "y")
    with pytest.raises(LiveEndpointRefusedError):
        main(["claim4", "check"])
    with pytest.raises(LiveEndpointRefusedError):
        main(["claim4", "daily"])


def test_evaluation_report_is_aggregate_only(cfg, tmp_path, monkeypatch):
    cfg, fake = make_world(cfg, tmp_path, monkeypatch)
    paper, data = fake.clients()
    out = c4p.run_evaluation(
        cfg, now=SUNDAY_EVENING, paper=paper, data=data, observations=pd.DataFrame()
    )
    text = out.read_text()
    assert "Family P" in text and "No signal passed" in text
    man = json.loads(c4p.paths(cfg)["manifest"].read_text())
    assert set(man["symbols"]["NVDA"]) == {"bars", "first", "last"}
    sig = pd.read_csv(c4p.paths(cfg)["signals"])
    assert not {"open", "close", "price"} & set(sig.columns)
    assert not list((tmp_path / "reports").rglob("*.parquet"))  # bars stay under var/
    assert list((tmp_path / "var" / "market_data").glob("*.parquet"))
