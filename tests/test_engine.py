"""Paper trading engine tests on hand-built SYNTHETIC markets."""

from datetime import date

import pandas as pd
import pytest

from compute_curve.paper import ledger
from compute_curve.paper.engine import CostModel, flat_strategy
from compute_curve.paper.market import MarketData
from compute_curve.paper.runner import run_backtest, run_forward
from compute_curve.synthetic import synthetic_config
from compute_curve.timeutil import month_days
from tests.helpers import INDEX, flat_curve_market, index_frame, settlements, weekdays


@pytest.fixture
def scfg(cfg):
    return synthetic_config(cfg)


def const_target(key, qty):
    def strat(view, state):
        return {key: qty}

    return strat


def test_accounting_identity_and_fill_timing(scfg):
    days = weekdays(date(2026, 11, 2), date(2026, 11, 20))
    prices = {d: 2.0 + 0.01 * i for i, d in enumerate(days)}
    md = MarketData.build(settlements=settlements([(d, "2026-12", p) for d, p in prices.items()]))
    r = run_backtest(md, const_target(("GPU1", "2026-12"), 3), days[0], days[-1], scfg, "t")
    cf = r.cash_flows["amount"].sum()
    assert cf == pytest.approx(r.account["equity"].iloc[-1] - scfg.risk.starting_cash)
    fill = r.fills.iloc[0]
    # Decided at end of day 0, filled at day 1 settlement plus 7 ticks.
    assert fill["day"] == days[1]
    tick = scfg.contracts["GPU1"].tick_size
    assert fill["fill_price"] == pytest.approx(prices[days[1]] + 7 * tick)
    per_side = (
        scfg.contracts["GPU1"].exchange_fee_per_contract
        + scfg.costs.broker_clearing_fee_per_contract
    )
    assert fill["fees"] == pytest.approx(3 * per_side)


def test_strategy_never_sees_future(scfg):
    days = weekdays(date(2026, 11, 2), date(2026, 11, 13))
    md = MarketData.build(
        settlements=settlements([(d, "2026-12", 2.0 + i) for i, d in enumerate(days)]),
        published_index=index_frame({d: 2.0 for d in days}),
    )
    seen: list[tuple[pd.Timestamp, pd.Timestamp]] = []

    def spy(view, state):
        s = view.settlements()
        seen.append((pd.Timestamp(view.as_of), s["ts_available"].max()))
        assert s["trade_date"].max() <= view.as_of.date()
        idx = view.published_index(INDEX)
        assert all(d < view.as_of.date() for d in idx.index)  # one-day publication lag
        return {}

    run_backtest(md, spy, days[0], days[-1], scfg, "t")
    assert seen and all(ts <= asof for asof, ts in seen)


def test_costs_reduce_pnl_monotonically(scfg):
    md = flat_curve_market(date(2026, 11, 2), date(2026, 11, 27), ["2026-12", "2027-01"])

    def flip(view, state):
        n = len(view.settlements())
        return {("GPU1", "2027-01"): 2 if (n // 2) % 2 == 0 else -2}

    finals = []
    for m in (0.0, 1.0, 2.0):
        r = run_backtest(md, flip, date(2026, 11, 2), date(2026, 11, 27), scfg, f"c{m}", m)
        finals.append(r.account["equity"].iloc[-1])
    assert finals[0] == pytest.approx(scfg.risk.starting_cash)  # flat prices, zero cost
    assert finals[0] > finals[1] > finals[2]


def test_position_limits(scfg):
    md = flat_curve_market(date(2026, 11, 2), date(2026, 11, 6), ["2026-12", "2027-01", "2027-02"])

    def greedy(view, state):
        return {("GPU1", "2026-12"): 100, ("GPU1", "2027-01"): -100, ("GPU1", "2027-02"): 100}

    r = run_backtest(md, greedy, date(2026, 11, 2), date(2026, 11, 6), scfg, "t")
    assert r.account["gross_contracts"].max() <= scfg.risk.max_gross_contracts
    per_month = r.fills.groupby("contract_month")["qty"].sum().abs()
    assert (per_month <= scfg.risk.max_contracts_per_month).all()
    assert {"limit_clip_month", "limit_clip_gross"} <= set(r.events["kind"])


def test_daily_loss_limit_flattens_and_halts(scfg):
    days = weekdays(date(2026, 11, 2), date(2026, 11, 13))
    px = {d: 2.0 for d in days}
    px[days[3]] = 1.0  # one-day crash: 5 contracts x 730 x 1.0 = 3650 > 2000 limit
    md = MarketData.build(settlements=settlements([(d, "2026-12", p) for d, p in px.items()]))
    r = run_backtest(md, const_target(("GPU1", "2026-12"), 5), days[0], days[-1], scfg, "t")
    assert "daily_loss_breach" in set(r.events["kind"])
    acct = r.account.set_index("day")
    assert acct.loc[days[4], "gross_contracts"] == 0  # flattened at next settlement
    assert bool(acct.loc[days[4], "halted"])


def test_max_drawdown_kill_switch(scfg):
    days = weekdays(date(2026, 11, 2), date(2026, 11, 27))
    # 5 contracts x 730 GPU-h x 0.5 = 1825 per day: below the daily limit,
    # but the cumulative loss crosses the 7500 drawdown limit.
    px = {d: 5.0 - 0.5 * i for i, d in enumerate(days[:7])}
    px.update({d: 2.0 for d in days[7:]})
    md = MarketData.build(settlements=settlements([(d, "2026-12", p) for d, p in px.items()]))
    r = run_backtest(md, const_target(("GPU1", "2026-12"), 5), days[0], days[-1], scfg, "t")
    assert "max_drawdown_breach" in set(r.events["kind"])
    after = r.account.loc[r.account["killed"]]
    assert after["gross_contracts"].iloc[-1] == 0
    assert r.events["kind"].iloc[0] == "max_drawdown_breach"
    assert r.fills["day"].max() <= after["day"].iloc[0] + pd.Timedelta(days=4)


def test_expiry_cash_settles_at_month_average(scfg):
    nov = weekdays(date(2026, 11, 2), date(2026, 11, 30))
    idx = {date(2026, 11, d): 2.0 + 0.01 * d for d in range(1, 31)}
    st = [(d, "2026-11", 2.1) for d in nov]
    md = MarketData.build(settlements=settlements(st), published_index=index_frame(idx))
    r = run_backtest(
        md, const_target(("GPU1", "2026-11"), 1), date(2026, 11, 2), date(2026, 12, 3), scfg, "t"
    )
    assert "expired" in set(r.events["kind"])
    bdays = month_days(date(2026, 11, 1), business_days_only=True)  # verified: Business Days
    final = sum(idx[d] for d in bdays) / len(bdays)
    fs = r.cash_flows.loc[r.cash_flows["kind"] == "final_settlement", "amount"].iloc[0]
    assert fs == pytest.approx(1 * (final - 2.1) * 730)
    assert r.account["gross_contracts"].iloc[-1] == 0


def test_forward_is_idempotent_and_matches_backtest(scfg, tmp_path):
    days = weekdays(date(2026, 11, 2), date(2026, 11, 20))
    md = MarketData.build(
        settlements=settlements([(d, "2026-12", 2.0 + 0.02 * (i % 4)) for i, d in enumerate(days)])
    )
    strat = const_target(("GPU1", "2026-12"), 2)
    bt = run_backtest(md, strat, days[0], days[-1], scfg, "bt")

    con = ledger.open_ledger(tmp_path / "paper.duckdb")
    for i, d in enumerate(days):
        start = days[0] if i == 0 else None
        processed = run_forward(md, strat, d, scfg, con, start, allow_synthetic_for_tests=True)
        assert processed
        assert run_forward(md, strat, d, scfg, con, allow_synthetic_for_tests=True) == []
    con.close()
    con = ledger.open_ledger(tmp_path / "paper.duckdb")  # reload from disk
    fwd = ledger.table(con, "account_daily", "forward")
    merged = bt.account.merge(fwd, on="day", suffixes=("_bt", "_fw"))
    assert len(merged) == len(fwd)
    assert merged["equity_bt"].to_numpy() == pytest.approx(merged["equity_fw"].to_numpy())


def test_forward_refuses_synthetic(scfg):
    md = flat_curve_market(date(2026, 11, 2), date(2026, 11, 6), ["2026-12"])
    with pytest.raises(ValueError, match="synthetic"):
        run_forward(md, flat_strategy, date(2026, 11, 6), scfg, ledger.open_ledger(None))


def test_fill_price_direction():
    c = CostModel(half_spread_ticks=2, slippage_ticks=1, fee_per_contract=1.0)
    assert c.fill_price(2.0, 3, 0.01) == pytest.approx(2.03)
    assert c.fill_price(2.0, -3, 0.01) == pytest.approx(1.97)
    assert c.fees(-3) == 3.0
