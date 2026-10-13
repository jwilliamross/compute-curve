"""Round 5 panel construction and statistics on small hand-made frames (no real data)."""

from datetime import UTC, date, datetime

import numpy as np
import pandas as pd

from compute_curve.explore.round5 import (
    capture_prices,
    cross_sections,
    month_end_panel,
    r501,
    r502,
)


def _rows(records: list[tuple[str, datetime, float, str]]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "provider": [r[0] for r in records],
            "ts_observed": [r[1] for r in records],
            "price_usd_per_gpu_hour": [r[2] for r in records],
            "gpu_model": [r[3] for r in records],
            "term": "on_demand",
            "is_synthetic": True,
        }
    )


def test_capture_price_is_the_median_of_h100_rows_and_drops_other_gpus() -> None:
    t = datetime(2024, 1, 10, tzinfo=UTC)
    rows = _rows(
        [("lambda", t, 2.0, "H100"), ("lambda", t, 3.0, "H100"), ("lambda", t, 9.0, "B200")]
    ).assign(is_synthetic=False)
    caps = capture_prices(rows)
    assert len(caps) == 1 and caps["price"].iloc[0] == 2.5


def test_synthetic_rows_never_enter() -> None:
    rows = _rows([("lambda", datetime(2024, 1, 10, tzinfo=UTC), 2.0, "H100")])
    assert capture_prices(rows).empty


def test_month_end_carries_forward_at_most_92_days() -> None:
    caps = pd.DataFrame(
        {"provider": ["lambda"], "ts": [pd.Timestamp("2024-01-15", tz="UTC")], "price": [2.0]}
    )
    panel = month_end_panel(caps, date(2024, 1, 1), date(2024, 6, 30))
    col = panel["lambda"]
    assert col.iloc[0] == 2.0 and col.iloc[2] == 2.0  # Jan, Mar (76 days)
    assert np.isnan(col.iloc[4])  # May 31: 137 days old


def _panel(n_months: int, revert: float, seed: int) -> pd.DataFrame:
    """Prices whose log premium moves back towards the median by ``revert`` per 3 months."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2023-01-31", periods=n_months, freq="ME", tz="UTC")
    prem = rng.normal(0, 0.2, 5)
    rows = []
    for _ in idx:
        rows.append(np.exp(1.0 + prem))
        prem = prem * (1 - revert / 3) + rng.normal(0, 0.05, 5)
    return pd.DataFrame(
        rows, index=idx, columns=["lambda", "coreweave", "nebius", "hyperstack", "verda"]
    )


def test_r501_detects_planted_reversion_and_needs_enough_sections() -> None:
    assert r501(_panel(30, 0.9, 1))["verdict"] == "pass"
    assert r501(_panel(10, 0.9, 1))["verdict"] == "too little history to conclude"


def test_cross_sections_need_four_providers() -> None:
    p = _panel(8, 0.5, 2)
    p.iloc[:, :2] = np.nan
    assert cross_sections(p) == []


def test_r502_recovers_a_planted_trend() -> None:
    idx = pd.date_range("2023-01-31", periods=36, freq="ME", tz="UTC")
    years = (idx - idx[0]).days / 365.25
    base = np.exp(1.0 - 0.3 * np.asarray(years))
    panel = pd.DataFrame({p: base for p in ["lambda", "coreweave", "nebius"]}, index=idx)
    r = r502(panel, seed=3, n_boot=200)
    assert abs(r["slope_per_year"] + 0.3) < 1e-6
    assert r["ci95"][0] <= -0.3 <= r["ci95"][1] + 1e-9
