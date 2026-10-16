"""SA2-M practice sheet helpers on hand-made frames (no real data)."""

import numpy as np
import pandas as pd

from compute_curve.config import load_config
from compute_curve.statarb import signals as sg


def test_next_session_row_is_a_business_day_copy() -> None:
    idx = pd.to_datetime(["2026-10-15", "2026-10-16"])  # Thu, Fri
    lp = pd.DataFrame({"A": [1.0, 2.0], "XLK": [0.5, 0.6]}, index=idx)
    out = sg.with_next_session(lp)
    assert len(out) == 3 and out.index[-1] == pd.Timestamp("2026-10-19")
    assert out.iloc[-1].tolist() == [2.0, 0.6]


def test_book_lines_sort_and_render() -> None:
    lines = sg.book_lines(
        {"A": 0.05, "B": -0.1, "XLK": 0.02, "C": 0.0}, {"A": [6, 0], "B": [0, 12]}
    )
    assert [x.symbol for x in lines] == ["B", "A", "XLK"]
    md = sg.render(lines, {"A": -1.3, "B": 2.0}, "2026-10-15", 10_000)
    assert "| B | SHORT | -0.100 | -1,000 | 0 / 12 |" in md and "| XLK | LONG" in md
    assert "Practice only" in md


def test_target_book_drops_unborrowable_shorts() -> None:
    rng = np.random.default_rng(3)
    n = 120
    m = rng.normal(0, 0.01, n).cumsum()
    df = {"XLK": m}
    for i in range(6):
        df[f"S{i}"] = (
            m + rng.normal(0, 0.02, n).cumsum() * 0.3 + np.sin(np.arange(n) / (3 + i)) * 0.05
        )
    lp = pd.DataFrame(df, index=pd.bdate_range("2026-01-01", periods=n))
    sa = load_config().statarb
    full, _ = sg.target_book(lp, sa, region=[[40.0, 1.0]])
    shorts = {k for k, v in full.items() if v < 0 and k != "XLK"}
    if shorts:
        cut, _ = sg.target_book(lp, sa, region=[[40.0, 1.0]], no_short=frozenset(shorts))
        assert all(cut.get(s, 0.0) >= 0 for s in shorts)
