"""UTC time helpers and contract-month calendars.

All timestamps in this project are timezone-aware UTC. Naive datetimes are
rejected so that look-ahead bugs from mixed timezones cannot slip in.
"""

from __future__ import annotations

import calendar
from datetime import UTC, date, datetime, timedelta


def utc_now() -> datetime:
    """Return the current time as an aware UTC datetime."""
    return datetime.now(tz=UTC)


def ensure_utc(ts: datetime) -> datetime:
    """Return ``ts`` converted to UTC. Raise if ``ts`` is naive."""
    if ts.tzinfo is None or ts.tzinfo.utcoffset(ts) is None:
        raise ValueError(f"naive datetime not allowed: {ts!r}")
    return ts.astimezone(UTC)


def snapshot_stamp(ts: datetime) -> str:
    """Compact, sortable, filesystem-safe UTC stamp, e.g. ``20261005T173914Z``."""
    return ensure_utc(ts).strftime("%Y%m%dT%H%M%SZ")


def month_start(d: date) -> date:
    """First calendar day of the month containing ``d``."""
    return d.replace(day=1)


def month_end(d: date) -> date:
    """Last calendar day of the month containing ``d``."""
    return d.replace(day=calendar.monthrange(d.year, d.month)[1])


def add_months(d: date, n: int) -> date:
    """First day of the month ``n`` months after the month containing ``d``."""
    idx = d.year * 12 + (d.month - 1) + n
    return date(idx // 12, idx % 12 + 1, 1)


def month_days(d: date, business_days_only: bool = False) -> list[date]:
    """All days in the month of ``d``; optionally Monday-Friday only.

    Exchange holidays are not modelled. Whether the GPU1/GPU2 final settlement
    averages calendar days or business days is a config parameter
    (``contract.settlement_days``) because it is not yet verified.
    """
    start, end = month_start(d), month_end(d)
    days = [start + timedelta(days=i) for i in range((end - start).days + 1)]
    if business_days_only:
        days = [x for x in days if x.weekday() < 5]
    return days


def month_code(d: date) -> str:
    """Contract month label ``YYYY-MM``."""
    return f"{d.year:04d}-{d.month:02d}"


def end_of_day_utc(d: date) -> datetime:
    """23:59:59.999999 UTC on ``d``; a conservative 'available by' time."""
    return datetime(d.year, d.month, d.day, 23, 59, 59, 999999, tzinfo=UTC)
