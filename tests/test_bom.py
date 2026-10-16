"""Balance-of-month fair value and FP-C on hand-made series (no real data)."""

from datetime import date

import numpy as np
import pandas as pd

from compute_curve import bom
from compute_curve.config import load_config


def test_rw_average_sd_matches_closed_form() -> None:
    # Mean of a random walk at steps 1..m: var = sigma^2 (m+1)(2m+1) / (6m)
    m, sigma = 10, 0.02
    got = bom.rw_average_sd(np.arange(1, m + 1), sigma)
    want = sigma * np.sqrt((m + 1) * (2 * m + 1) / (6 * m))
    assert abs(got - want) < 1e-12
    assert bom.rw_average_sd(np.array([]), sigma) == 0.0


def test_month_fair_value_blends_realised_and_level() -> None:
    cfg = load_config()
    spec = cfg.contracts["GPU1"]
    days = pd.bdate_range("2026-10-01", "2026-10-15").date
    idx = pd.Series([2.0] * (len(days) - 1) + [3.0], index=days)
    r = bom.month_fair_value(idx, spec, date(2026, 10, 1), date(2026, 10, 15), 0.01)
    assert r["days_total"] == 22 and r["days_realized"] == 11
    want = (10 * 2.0 + 1 * 3.0 + 11 * 3.0) / 22
    assert abs(r["fair_value"] - want) < 1e-12
    assert r["low90"] < r["fair_value"] < r["high90"]
    nxt = bom.month_fair_value(idx, spec, date(2026, 11, 1), date(2026, 10, 15), 0.01)
    assert nxt["days_realized"] == 0 and nxt["fair_value"] == 3.0 and nxt["sd_log"] > r["sd_log"]


def test_sigma_floor_and_fpc_rule() -> None:
    flat = pd.Series([2.0] * 30, index=pd.bdate_range("2026-01-01", periods=30).date)
    assert bom.sigma_daily(flat)[0] == bom.SIGMA_FLOOR
    assert bom.fpc_decide(3.5, 3.0, 0.2) == -1 and bom.fpc_decide(2.5, 3.0, 0.2) == 1
    assert bom.fpc_decide(3.1, 3.0, 0.2) == 0


def test_decision_day_is_mid_month() -> None:
    spec = load_config().contracts["GPU1"]
    d = bom.decision_day(spec, date(2026, 10, 1))
    assert d == date(2026, 10, 16)  # 22 business days: the 12th one


def test_fpc_evaluate_waits() -> None:
    rows = [{"pnl": 10.0, "pnl_stress": 5.0}] * 3
    assert bom.fpc_evaluate(rows, date(2027, 1, 1))["due"] is False
    assert bom.fpc_evaluate(rows, date(2028, 1, 1))["verdict"] == "too little history to conclude"
