"""Round-4 tests on SYNTHETIC listings (compute_curve.synthetic, is_synthetic=True)."""

from datetime import date

import numpy as np
import pandas as pd

from compute_curve.config import Round4Config, load_config
from compute_curve.explore import round4 as r4
from compute_curve.explore.data import Round1Data
from compute_curve.synthetic import synthetic_round1

CFG = load_config()
ECFG = CFG.exploration
WIN = Round4Config(h01_forward=(date(2026, 8, 20), date(2026, 10, 6)))
FROZEN = {
    "hid": "H01",
    "direction": -1,
    "intercept": 0.0,
    "slope": -0.04,
    "slope_se_explore": 0.01,
    "n_explore": 50,
    "rho_explore": -0.12,
    "y_mean_explore": 0.0,
}


def data(seed: int, plant: frozenset[str]) -> Round1Data:
    f = synthetic_round1(seed, plant, CFG.claim4.universe.buckets(), CFG.claim4.benchmark)
    assert all(bool(df["is_synthetic"].all()) for df in f.values())
    return Round1Data(**f)


def test_window_truncates_before_compute():
    d = data(1, frozenset({"H01"}))
    win = r4.in_window(d.listings, WIN.h01_forward)
    days = pd.to_datetime(win["as_of_date"]).dt.date
    assert days.min() >= WIN.h01_forward[0] and days.max() <= WIN.h01_forward[1]


def test_planted_convergence_confirms_and_null_does_not():
    planted = r4.confirm_forward(data(2, frozenset({"H01"})), FROZEN, ECFG, WIN)
    assert planted["hid"] == "R4-01" and planted["slope"] < 0
    assert planted["c1"]
    lo, hi = (date.fromisoformat(x) for x in planted["window"])
    assert lo >= WIN.h01_forward[0] and hi <= WIN.h01_forward[1]
    nulls = [r4.confirm_forward(data(s, frozenset()), FROZEN, ECFG, WIN) for s in range(4, 12)]
    assert sum(r["confirmed"] for r in nulls) <= 2  # chance false positives stay rare


def test_waits_until_the_window_has_closed():
    assert not r4.window_complete(WIN, date(2026, 10, 6))
    assert r4.window_complete(WIN, date(2026, 10, 7))


def _series(values, start=date(2026, 7, 1)):
    idx = [start + pd.Timedelta(days=i) for i in range(len(values))]
    return pd.Series(values, index=[d.date() if hasattr(d, "date") else d for d in idx])


def test_lead_lag_pairs_use_past_signal_and_future_target_only():
    x = _series(list(range(30)))
    y = _series([float(i) ** 2 for i in range(30)])
    f = r4.lead_lag_pairs(x, y, (date(2026, 7, 10), date(2026, 7, 15)))
    first = f.iloc[0]
    assert first["t"] == date(2026, 7, 10)
    assert first["x"] == 9 - 2  # x(t) - x(t-7)
    assert first["y"] == 16**2 - 9**2  # y(t+7) - y(t)
    late = r4.lead_lag_pairs(x, y, (date(2026, 7, 20), date(2026, 7, 28)))
    assert late["t"].max() <= date(2026, 7, 23)  # outcome must exist (t + 7 <= last day)


def test_planted_lead_is_recovered_and_holm_applied():
    rng = np.random.default_rng(0)
    n = 200
    shocks = rng.normal(0, 0.02, n)
    aws = np.cumsum(shocks)
    lagged = np.concatenate([np.zeros(7), aws[:-7]])  # target follows AWS one week later
    tgt = lagged + np.cumsum(rng.normal(0, 0.003, n))
    xs, ys = _series(aws), _series(tgt)
    win = (date(2026, 7, 10), date(2026, 12, 1))
    fit = r4.fit_r402(r4.lead_lag_pairs(xs, ys, win))
    assert fit["b"] > 0.5 and fit["p_one_sided"] < 0.01
    noise = _series(np.cumsum(rng.normal(0, 0.01, n)))
    frames = {"cgi": r4.lead_lag_pairs(xs, ys, win), "own_panel": r4.lead_lag_pairs(xs, noise, win)}
    rows = r4.confirm_r402(frames, {"cgi": fit, "own_panel": fit}, 0.05)
    assert rows[0]["confirmed"] and all(r["p_holm"] >= r["p_one_sided"] for r in rows)
