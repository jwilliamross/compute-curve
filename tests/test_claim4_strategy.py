"""Claim-4 paper strategy and hard limits (pure functions; no network)."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from compute_curve.claim4.risk import evaluate_risk
from compute_curve.claim4.strategy import (
    apply_limits,
    cohort_target,
    flatten_orders,
    orders_for_targets,
    pair_weights,
)


def test_pair_weights_balance_buckets_and_legs(cfg):
    c4 = cfg.claim4
    w = pair_weights(1, c4)
    assert w[c4.benchmark] == -1.0
    for members in c4.universe.buckets().values():
        assert sum(w[s] for s in members) == pytest.approx(1 / 3)
    assert sum(v for k, v in w.items() if k != c4.benchmark) == pytest.approx(1.0)


def test_short_basket_drops_names_that_cannot_be_shorted(cfg):
    c4 = cfg.claim4
    shortable = {s: s != "WYFI" for s in c4.universe.members()}
    w = pair_weights(-1, c4, shortable)
    assert "WYFI" not in w
    assert w["CRWV"] == pytest.approx(-1 / 9)
    assert sum(v for k, v in w.items() if k != c4.benchmark) == pytest.approx(-1.0)
    assert w[c4.benchmark] == 1.0


def test_cohorts_net_out(cfg):
    c4 = cfg.claim4
    t = cohort_target([1, 1, 1, 0, -1], 5, c4)
    per = c4.risk.pair_notional_usd / 5
    assert t[c4.benchmark] == pytest.approx(-2 * per)
    assert sum(v for k, v in t.items() if k != c4.benchmark) == pytest.approx(2 * per)
    assert cohort_target([1, -1], 2, c4) == {}


def test_limits_scale_both_legs_proportionally(cfg):
    c4 = cfg.claim4
    big = {"XLK": -15000.0, "NVDA": 15000.0}
    s = apply_limits(big, c4)
    assert s.factor == pytest.approx(10000 / 15000)
    assert abs(s.target["XLK"]) <= c4.risk.max_position_usd + 1e-6
    assert s.target["NVDA"] == pytest.approx(-s.target["XLK"])
    gross = {f"S{i}": 3000.0 for i in range(10)}
    s2 = apply_limits(gross, c4)
    assert sum(abs(v) for v in s2.target.values()) == pytest.approx(c4.risk.max_gross_exposure_usd)


def test_orders_follow_share_rules_and_never_touch_other_symbols():
    managed = ["NVDA", "WYFI", "XLK", "AMD", "TLN"]
    target = {"NVDA": 1000.0, "WYFI": 1000.0, "XLK": -1000.0, "AMD": -900.0, "TLN": 10.0}
    current = {"AMD": 5.0, "AAPL": 10.0}
    price = {"NVDA": 300.0, "WYFI": 300.0, "XLK": 300.0, "AMD": 150.0, "TLN": 5.0}
    frac = {"NVDA": True, "WYFI": False, "XLK": True, "AMD": True, "TLN": True}
    orders, notes = orders_for_targets(target, current, price, frac, managed)
    by = {o.symbol: o for o in orders}
    assert by["NVDA"].side == "buy" and by["NVDA"].qty == pytest.approx(3.333333)
    assert by["WYFI"].qty == 3  # not fractionable: whole shares
    assert by["XLK"].side == "sell" and by["XLK"].qty == 3  # short: whole shares
    assert by["AMD"].side == "sell" and by["AMD"].qty == 5  # flip: close only
    assert any("flips" in n for n in notes)
    assert "TLN" not in by  # below the minimum order size
    assert "AAPL" not in by
    assert by["NVDA"].payload("2026-10-12", "x")["client_order_id"].startswith("c4-2026-10-12-NVDA")


def test_flatten_closes_only_managed_positions():
    out = flatten_orders({"NVDA": 3.0, "XLK": -5.0, "AAPL": 10.0}, ["NVDA", "XLK"])
    assert {(o.symbol, o.side, o.qty) for o in out} == {("NVDA", "sell", 3.0), ("XLK", "buy", 5.0)}


def _hist(equities, pls, start=datetime(2026, 10, 7, tzinfo=UTC)):
    ts = [int(start.timestamp()) + 86400 * i for i in range(len(equities))]
    return {"timestamp": ts, "equity": equities, "profit_loss": pls}


def test_risk_kill_switch_from_config_or_environment(cfg):
    c4 = cfg.claim4
    acct = {"equity": "100000", "last_equity": "100000"}
    assert not evaluate_risk(acct, _hist([], []), c4, env={}).kill_switch
    assert evaluate_risk(
        acct, _hist([], []), c4, env={"COMPUTE_CURVE_KILL_SWITCH": "1"}
    ).kill_switch
    on = c4.model_copy(update={"risk": c4.risk.model_copy(update={"kill_switch": True})})
    st = evaluate_risk(acct, _hist([], []), on, env={})
    assert st.kill_switch and st.requires_flatten and st.blocks_new_positions


def test_daily_loss_breach_and_halt(cfg):
    c4 = cfg.claim4
    st = evaluate_risk({"equity": "98900", "last_equity": "100000"}, _hist([], []), c4, env={})
    assert st.daily_breach_today and st.requires_flatten
    assert st.daily_pnl_pct == pytest.approx(-1.1)
    st2 = evaluate_risk(
        {"equity": "98900", "last_equity": "98900"}, _hist([100000, 98900], [0, -1100]), c4, env={}
    )
    assert st2.halted_after_breach and st2.blocks_new_positions and not st2.requires_flatten


def test_drawdown_latch_persists_after_recovery(cfg):
    c4 = cfg.claim4
    hist = _hist([100000, 102000, 98900, 100500], [0, 2000, -3100, 1600])
    st = evaluate_risk({"equity": "101000", "last_equity": "100500"}, hist, c4, env={})
    assert st.drawdown_latched and st.requires_flatten


def test_history_before_paper_start_is_ignored(cfg):
    c4 = cfg.claim4
    hist = _hist([150000, 100000], [0, -50000], start=datetime(2026, 9, 1, tzinfo=UTC))
    st = evaluate_risk({"equity": "100000", "last_equity": "100000"}, hist, c4, env={})
    assert not st.drawdown_latched and not st.halted_after_breach
