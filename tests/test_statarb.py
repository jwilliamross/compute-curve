"""Claim-6 engine tests on SYNTHETIC bars (compute_curve.synthetic, is_synthetic=True)."""

from datetime import date

import numpy as np
import pandas as pd
import pytest

from compute_curve.config import load_config
from compute_curve.statarb import evaluate as ev
from compute_curve.statarb.engine import Costs, Trade, book_returns, run_book, run_book_shares
from compute_curve.statarb.pipeline import (
    FORWARD_START,
    Prices,
    cell_trades,
    costs_of,
    forward_window,
    wide_prices,
)
from compute_curve.statarb.spreads import corwin_schultz, first_valid_spread, sample_points
from compute_curve.synthetic import synthetic_statarb_bars

SA = load_config().statarb
GROUPS = {"pair": ["PA", "PB"], "other": ["RC", "N1", "N2", "N3"]}
SYMS = ["PA", "PB", "RC", "N1", "N2", "N3", "XLK"]
ZERO = Costs(0.0, 0.0, 0.0, 0.0)


def prices(seed=1, n=600, planted=True) -> Prices:
    bars = synthetic_statarb_bars(n, seed, planted=planted)
    assert bars["is_synthetic"].all()
    return wide_prices(bars, SYMS, {}, SA.min_history)


def test_book_returns_by_hand():
    opens = np.array([[10.0, 100.0], [11.0, 100.0], [12.0, 100.0]])
    closes = np.array([[10.0, 100.0], [11.5, 100.0], [12.0, 100.0]])
    w = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 0.0]])
    costs = Costs(0.001, 0.0, 0.0, 0.0)
    r = book_returns(w, opens, closes, costs, ["A", "XLK"])
    # day 1: buy at the open (10 bps), earn 11.5/11 - 1
    # day 2: earn the overnight 12/11.5 - 1, sell at the open (10 bps)
    assert r[1] == pytest.approx(11.5 / 11 - 1 - 0.001)
    assert r[2] == pytest.approx(12 / 11.5 - 1 - 0.001)


def test_borrow_is_charged_on_shorts_only():
    opens = closes = np.full((3, 1), 10.0)
    w = np.array([[-1.0], [-1.0], [0.0]])
    r = book_returns(w, opens, closes, Costs(0.0, 0.0, 0.0, 0.252), ["A"])
    assert r[0] == pytest.approx(-0.001) and r[2] == 0.0


@pytest.mark.parametrize(("strategy", "p1", "p2"), [("SA1", 60, 2.0), ("SA2", 60, 1.25)])
def test_no_look_ahead(strategy, p1, p2):
    p = prices()
    cut = 400
    short = Prices(p.opens.iloc[: cut + 1], p.closes.iloc[: cut + 1], p.signal_logp.iloc[: cut + 1])
    full = cell_trades(p, SA, GROUPS, strategy, p1, p2, 0, len(p.closes) - 1)
    trunc = cell_trades(short, SA, GROUPS, strategy, p1, p2, 0, cut)
    key = {(t.start, tuple(sorted(t.weights.items()))) for t in full if t.start <= cut}
    key_t = {(t.start, tuple(sorted(t.weights.items()))) for t in trunc if t.start <= cut}
    assert key == key_t and key


@pytest.mark.parametrize(("strategy", "p1", "p2"), [("SA1", 250, 2.0), ("SA2", 60, 1.25)])
def test_planted_mispricing_pays_and_null_does_not(strategy, p1, p2):
    def mean_sharpe(planted: bool) -> float:
        out = []
        for seed in (1, 2, 3):
            q = prices(seed=seed, n=800, planted=planted)
            tr = cell_trades(q, SA, GROUPS, strategy, p1, p2, 0, len(q.closes) - 1)
            out.append(ev.moments(run_book(tr, q.opens, q.closes, costs_of(SA)).to_numpy()).sr)
        return float(np.nanmean(out)) * np.sqrt(252)

    planted, null = mean_sharpe(True), mean_sharpe(False)
    assert planted > 0.5 and planted - null > 0.5, (planted, null)


def test_eligibility_mask_and_member_start():
    bars = synthetic_statarb_bars(200, 3)
    p = wide_prices(bars, SYMS, {"PA": date(2030, 3, 1)}, 60)
    assert p.closes.loc[p.closes.index < pd.Timestamp("2030-03-01"), "PA"].isna().all()
    assert (
        p.signal_logp["PB"].iloc[:60].isna().all() and p.signal_logp["PB"].iloc[60:].notna().all()
    )


def test_sharpe_formulas_reproduce_exhibit_1():
    sr, t, g3, g4, rho = 0.036 / 0.079, 24, -2.448, 10.164, 0.2
    assert np.sqrt(ev.sr_variance(sr, t, g3, g4, rho)) == pytest.approx(0.379, abs=1e-3)
    assert ev.psr(sr, 0.0, t, g3, g4, rho) == pytest.approx(0.966, abs=1e-3)
    assert ev.psr(sr, 0.1, t, g3, g4, rho) == pytest.approx(0.900, abs=1e-3)


def test_deflated_sharpe_falls_with_more_trials():
    rng = np.random.default_rng(0)
    trials = list(rng.normal(0.0, 0.05, 20))
    few = ev.deflated_sharpe(0.1, trials[:3], 400, 0.0, 3.0, 0.0)
    many = ev.deflated_sharpe(0.1, trials, 400, 0.0, 3.0, 0.0)
    assert many < few


def test_region_and_pool():
    grid = np.array([[0.1, 0.2, 0.1], [0.2, 2.0, 0.3], [0.1, 0.2, 0.1]])
    cells = ev.region(grid, years=1.0)
    assert (1, 1) in cells and len(cells) >= 2
    a = pd.Series([1.0, 2.0])
    b = pd.Series([3.0, 4.0])
    assert ev.pool([a, b]).tolist() == [2.0, 3.0]


def test_cost_breakeven_is_linear():
    free, base = np.full(10, 0.002), np.full(10, 0.0005)
    assert ev.cost_breakeven(free, base, 15.0) == pytest.approx(20.0)


def test_drawdown_tail_exceeds_realized_on_noise():
    r = np.random.default_rng(1).normal(0.0005, 0.01, 300)
    assert ev.drawdown_tail(r, 500, 20, 1) >= ev.max_drawdown(r) * 0.5


def _bars_with_spread(spread: float, n_days: int = 400, seed: int = 0) -> tuple[np.ndarray, ...]:
    rng = np.random.default_rng(seed)
    highs, lows, closes = [], [], []
    mid = 100.0
    for _ in range(n_days):
        path = mid * np.exp(np.cumsum(rng.normal(0, 0.02 / np.sqrt(78), 78)))
        highs.append(path.max() * (1 + spread / 2))
        lows.append(path.min() * (1 - spread / 2))
        closes.append(path[-1] * (1 + rng.choice([-1, 1]) * spread / 2))
        mid = path[-1]
    return np.array(highs), np.array(lows), np.array(closes)


def test_corwin_schultz_recovers_a_known_spread():
    for true in (0.0, 0.01):
        h, lo, c = _bars_with_spread(true)
        est = float(np.median(corwin_schultz(h, lo, c)))
        assert abs(est - true) < 0.004, (true, est)


def test_measured_costs_override_the_flat_cost():
    opens = closes = np.full((2, 2), 10.0)
    w = np.array([[1.0, 1.0], [1.0, 1.0]])
    flat = Costs(0.001, 0.0, 0.0, 0.0)
    measured = Costs(0.001, 0.0, 0.0, 0.0, per_symbol=(("A", 0.005),))
    r_flat = book_returns(w, opens, closes, flat, ["A", "B"])
    r_meas = book_returns(w, opens, closes, measured, ["A", "B"])
    assert r_flat[0] == pytest.approx(-0.002) and r_meas[0] == pytest.approx(-0.006)
    assert measured.scaled(2.0, 0.1).side(["A", "B"]).tolist() == [0.01, 0.002]


def test_quoted_spread_uses_the_first_valid_quote():
    quotes = [{"bp": 0, "ap": 10.0}, {"bp": 10.0, "ap": 9.9}, {"bp": 99.99, "ap": 100.01}]
    assert first_valid_spread(quotes) == pytest.approx(0.02 / 100.0)
    assert first_valid_spread([{"bp": 0, "ap": 0}]) is None


def test_sample_points_are_new_york_times_on_every_18th_session():
    sessions = [(pd.Timestamp("2025-01-02") + pd.Timedelta(days=i)).date() for i in range(40)]
    pts = sample_points(sessions)
    assert len(pts) == 3 * 4  # sessions 0, 18, 36
    assert pts[0] == ("2025-01-02T15:00:00Z", "2025-01-02T15:00:02Z")  # 10:00 EST = 15:00 UTC


def test_forward_window_needs_60_sessions_from_the_start_date():
    few = pd.bdate_range(FORWARD_START, periods=59)
    assert forward_window(few) is None
    enough = pd.bdate_range("2026-09-01", periods=100)
    win = forward_window(enough)
    assert win is not None and win[0] == FORWARD_START
    assert len(pd.bdate_range(win[0], win[1])) == 60


def test_fixed_share_book_by_hand():
    idx = pd.bdate_range("2030-01-02", periods=3)
    opens = pd.DataFrame({"A": [10.0, 11.0, 12.0]}, index=idx)
    closes = pd.DataFrame({"A": [10.0, 11.5, 12.5]}, index=idx)
    # buy 1/11 shares (capital 1) at the open of day 1, sell at the open of day 2
    r = run_book_shares([Trade(1, 2, {"A": 1.0})], opens, closes, Costs(0.001, 0, 0, 0))
    shares = 1 / 11
    assert r.iloc[1] == pytest.approx(shares * (11.5 - 11.0) - 0.001)
    assert r.iloc[2] == pytest.approx(shares * (12.0 - 11.5) - shares * 12.0 * 0.001)
