"""SA2-M paper-trading rules on hand-made inputs (no network, no orders)."""

from datetime import UTC, date, datetime

from compute_curve.claim4.strategy import Order
from compute_curve.config import StatArbPaperConfig
from compute_curve.statarb import paper as pp

PC = StatArbPaperConfig(paper_start=date(2026, 10, 16))


def _hist(equity: list[float], pl: list[float]) -> dict:
    ts = [int(datetime(2026, 10, 16 + i, tzinfo=UTC).timestamp()) for i in range(len(equity))]
    return {"timestamp": ts, "equity": equity, "profit_loss": pl}


def test_assess_passes_a_quiet_account() -> None:
    r = pp.assess(
        _hist([100_000, 100_050, 99_900], [0, 50, -150]), {"equity": "99950"}, PC, [5, -3], {}
    )
    assert not r.kill and r.sessions == 3 and abs(r.drawdown_usd - 150) < 1e-9
    assert r.bad_fill_share == 0.0


def test_assess_kills_on_drawdown_breaches_switch_and_fills() -> None:
    r = pp.assess(_hist([100_000, 98_400], [0, -1_600]), {}, PC, [], {})
    assert any("drawdown" in k for k in r.kill)
    r2 = pp.assess(
        _hist([100_000, 99_000, 99_100, 98_100], [0, -1_000, 100, -1_000]), {}, PC, [], {}
    )
    assert any("daily loss" in k for k in r2.kill)
    r3 = pp.assess(
        _hist([100_000], [0]), {}, PC, [100.0] * 5 + [0.0] * 15, {"COMPUTE_CURVE_KILL_SWITCH": "1"}
    )
    assert any("fills" in k for k in r3.kill) and any("kill switch" in k for k in r3.kill)


def test_scale_targets_respects_limits() -> None:
    t = pp.scale_targets({"A": 0.1, "XLK": -0.75}, PC)
    assert abs(t["A"] - 860) < 1e-9 and abs(t["XLK"] + 6450) < 1e-9
    small = StatArbPaperConfig(paper_start=date(2026, 10, 16), max_position_usd=3225.0)
    t2 = pp.scale_targets({"A": 0.1, "XLK": -0.75}, small)
    assert abs(t2["XLK"] + 3225) < 1e-9 and abs(t2["A"] - 430) < 1e-9


def test_payload_slippage_and_no_short() -> None:
    p = pp.payload(Order("SMCI", "buy", 12.5, "rebalance"), "2026-10-16", "s")
    assert p["client_order_id"].startswith("sa2-2026-10-16-SMCI") and p["qty"] == "12.5"
    assert p["time_in_force"] == "day" and p["type"] == "market"
    assert (
        pp.slippage_bps("buy", 101.0, 100.0) == 100.0
        and pp.slippage_bps("sell", 101.0, 100.0) == -100.0
    )
    ns = pp.no_short_set(
        {"A": {"shortable": True, "easy_to_borrow": True}, "W": {"shortable": False}}
    )
    assert ns == frozenset({"W"})
