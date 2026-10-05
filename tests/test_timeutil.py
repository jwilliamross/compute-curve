from datetime import UTC, date, datetime, timedelta, timezone

import pytest

from compute_curve.timeutil import (
    add_months,
    ensure_utc,
    month_code,
    month_days,
    month_end,
    snapshot_stamp,
)


def test_ensure_utc_rejects_naive():
    with pytest.raises(ValueError):
        ensure_utc(datetime(2026, 1, 1))  # noqa: DTZ001


def test_ensure_utc_converts():
    ts = datetime(2026, 1, 1, 12, tzinfo=timezone(timedelta(hours=-5)))
    assert ensure_utc(ts).hour == 17


def test_snapshot_stamp_sortable():
    a = snapshot_stamp(datetime(2026, 10, 5, 9, 0, tzinfo=UTC))
    b = snapshot_stamp(datetime(2026, 10, 5, 10, 0, tzinfo=UTC))
    assert a < b and a == "20261005T090000Z"


def test_month_helpers():
    assert month_end(date(2028, 2, 10)) == date(2028, 2, 29)
    assert add_months(date(2026, 11, 15), 3) == date(2027, 2, 1)
    assert add_months(date(2026, 1, 31), -1) == date(2025, 12, 1)
    assert month_code(date(2026, 10, 5)) == "2026-10"
    assert len(month_days(date(2026, 10, 1))) == 31
    assert len(month_days(date(2026, 10, 1), business_days_only=True)) == 22
