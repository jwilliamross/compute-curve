"""Claim 10 (docs/modern_plan.md) on SYNTHETIC frames only (compute_curve.synthetic)."""

from datetime import date

import numpy as np
import pandas as pd

from compute_curve.config import load_config
from compute_curve.statarb import modern as mx
from compute_curve.statarb import modern_run as mr
from compute_curve.statarb.engine import Costs
from compute_curve.statarb.pipeline import wide_prices
from compute_curve.statarb.strategies import residual_trades
from compute_curve.synthetic import synthetic_modern_bars

SA = load_config().statarb
COSTS = Costs(0.0015, 0.0003, 0.0001, 0.03, "XLK")
STRESS = COSTS.scaled(2.0, 0.10)


def _prices(n_days: int = 260, n_names: int = 10, seed: int = 4):
    bars = synthetic_modern_bars(n_days, n_names, seed)
    assert bars["is_synthetic"].all()
    symbols = [*(f"S{k}" for k in range(n_names)), "XLK"]
    prices = wide_prices(bars, symbols, {}, 20)
    return prices, mr.volume_wide(bars, prices.closes)


def test_gated_trades_reproduce_residual_trades() -> None:
    p, _ = _prices()
    lp = p.signal_logp
    for window, entry in ((40, 1.0), (60, 1.5)):
        a = residual_trades(lp, "XLK", window, entry, SA.residual, 10, 20, window, len(lp) - 1)
        b = mx.gated_trades(
            lp, window, entry, SA.residual, 10, 20, window, len(lp) - 1, mx.etf_scorer()
        )
        assert a == b


def test_abnormal_volume_formula() -> None:
    v = pd.DataFrame({"A": [1.0] * 64 + [2.0] * 5})
    av = mx.abnormal_volume(v)
    assert np.isnan(av["A"].iloc[63])
    assert av["A"].iloc[-1] == 2.0  # last 5 at 2, the 60 before at 1


def test_volume_gate_splits_at_the_daily_median() -> None:
    av = pd.DataFrame({"A": [0.5], "B": [1.0], "C": [2.0]})
    el = pd.DataFrame({"A": [True], "B": [True], "C": [True]})
    quiet, loud = mx.volume_gate(av, el, False), mx.volume_gate(av, el, True)
    assert [quiet(s, 0) for s in "ABC"] == [1, 1, 0]
    assert [loud(s, 0) for s in "ABC"] == [0, 0, -1]


def test_momentum_gate_flips_sign_and_holds_fixed() -> None:
    p, _ = _prices()
    lp = p.signal_logp
    rev = mx.gated_trades(lp, 40, 1.0, SA.residual, 10, 20, 40, len(lp) - 1, mx.etf_scorer())
    mom = mx.gated_trades(
        lp, 40, 1.0, SA.residual, 10, 20, 40, len(lp) - 1, mx.etf_scorer(), lambda s, t: -1
    )
    assert mom and all(t.end - t.start == 20 or t.end == len(lp) for t in mom)
    first_rev = min(rev, key=lambda t: (t.start, sorted(t.weights)))
    match = [
        t
        for t in mom
        if t.start == first_rev.start and t.weights.keys() == first_rev.weights.keys()
    ]
    sym = next(k for k in first_rev.weights if k != "XLK")
    assert match and np.sign(match[0].weights[sym]) == -np.sign(first_rev.weights[sym])


def test_pca_scores_use_only_the_window() -> None:
    p, _ = _prices()
    rets = p.signal_logp.diff()
    t = 150
    a = mx.pca_s_scores(rets, "XLK", t, 60, 2)
    later = rets.copy()
    later.iloc[t + 1 :] = later.iloc[t + 1 :] * 5 + 0.1
    b = mx.pca_s_scores(later, "XLK", t, 60, 2)
    assert a and a.keys() == b.keys()
    np.testing.assert_allclose([a[k] for k in a], [b[k] for k in a], rtol=1e-9)
    assert all(np.isfinite(s) and np.isfinite(b) for s, b in a.values())


def test_vol_scale_is_lagged_and_capped() -> None:
    rng = np.random.default_rng(0)
    r = rng.normal(0, 0.01, 200)
    w = np.ones((200, 2))
    c = mx.vol_scale(r, w)
    assert (c[:60] == 1).all() and (c >= 0).all() and (c <= mx.SCALE_CAP).all()
    r2 = r.copy()
    r2[120] = 0.5
    assert mx.vol_scale(r2, w)[120] == c[120]  # today's return never sets today's scale
    assert mx.vol_scale(r2, w)[121] < c[121]


def test_mm_alpha() -> None:
    rng = np.random.default_rng(1)
    u = rng.normal(0, 0.01, 400)
    a0, p0 = mx.mm_alpha_p(2 * u, u, 10)
    a1, p1 = mx.mm_alpha_p(u + 0.002, u, 10)
    assert abs(a0) < 1e-12 and p1 < 0.01 and a1 > 0


def test_ridge_book_has_no_look_ahead() -> None:
    p, v = _prices(n_days=300, n_names=10)
    full = mx.ridge_book(p.signal_logp, p.opens, v, len(p.closes) - 1, 10)
    assert full.n_trades > 0 and full.forecast_dates
    cut = 260
    q = p.until(p.closes.index[cut].date())
    part = mx.ridge_book(q.signal_logp, q.opens, v.iloc[: cut + 1], cut, 10)
    np.testing.assert_allclose(part.weights[: cut + 1], full.weights[: cut + 1])


def test_build_and_evaluate_books_on_synthetic_data() -> None:
    p, v = _prices(n_days=320, n_names=10)
    books = mr.build_books(p, v, SA, COSTS)
    assert set(books) == {"SA2-M", *mx.STRATEGIES}
    window = (p.closes.index[200].date(), p.closes.index[-1].date())
    rows = mr.evaluate_books(books, p, (COSTS, COSTS, STRESS), window, SA, 1)
    assert [r.strategy for r in rows] == ["SA2-M", *mx.STRATEGIES]
    mx1 = rows[1]
    assert mx1.test.startswith("Moreira-Muir") and "alpha_daily" in mx1.extra
    assert "ic_p" in rows[-1].extra
    md = mr.render("t", rows, "note", {})
    assert "| MX3-k2 |" in md
    lines = mr.lab_lines(books, p, COSTS, window[0])
    assert len(lines) == 8


def test_screen_and_confirm_rules() -> None:
    def row(name: str, mean: float, p: float, stress: float, ic_p: float = 0.01) -> mx.MxResult:
        return mx.MxResult(
            name, ("a", "b"), 100, 10, {"mean": mean, "effective_n": 80.0}, "t", p,
            (0.0, 0.0), (0.0, 0.0), stress, 0.5, {"ic_p": ic_p},
        )  # fmt: skip

    assert mx.screen(row("MX1", 1e-4, 0.15, 1e-5))
    assert not mx.screen(row("MX1", -1e-4, 0.15, 1e-5))
    assert not mx.screen(row("MX4", 1e-4, 0.1, 1e-5, ic_p=0.5))
    out = mx.confirm([row("MX1", 1e-4, 0.01, 1e-5), row("MX3-k1", 1e-4, 0.04, -1e-5)], 0.05)
    assert out[0]["confirmed"] and not out[1]["confirmed"] and out[1]["p_holm"] == 0.04


def test_forward_start_is_after_the_plan() -> None:
    assert date(2026, 10, 19) == mx.FORWARD_START
