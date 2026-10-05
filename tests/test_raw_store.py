from datetime import UTC, datetime

import pytest

from compute_curve.collectors.vast import VastCollector
from compute_curve.storage.raw_store import (
    ImmutableWriteError,
    observations_to_frame,
    read_snapshot,
    snapshot_path,
    snapshots_for_day,
    write_snapshot,
)


def test_write_is_immutable(tmp_path, vast_payload, t0):
    rows, _ = VastCollector().normalize(vast_payload, t0, "vast_x")
    df = observations_to_frame(rows)
    p = write_snapshot(tmp_path, "vast", t0, df)
    assert p == snapshot_path(tmp_path, "vast", t0)
    before = p.read_bytes()
    with pytest.raises(ImmutableWriteError):
        write_snapshot(tmp_path, "vast", t0, df)
    assert p.read_bytes() == before
    back = read_snapshot(p)
    assert len(back) == 3
    assert str(back["ts_observed"].dt.tz) == "UTC"
    assert not list(tmp_path.rglob("*.tmp"))


def test_snapshots_for_day(tmp_path, vast_payload, t0):
    rows, _ = VastCollector().normalize(vast_payload, t0, "vast_x")
    df = observations_to_frame(rows)
    write_snapshot(tmp_path, "vast", t0, df)
    write_snapshot(tmp_path, "vast", datetime(2026, 10, 5, 18, tzinfo=UTC), df)
    write_snapshot(tmp_path, "vast", datetime(2026, 10, 6, 1, tzinfo=UTC), df)
    assert len(snapshots_for_day(tmp_path, "vast", t0.date())) == 2
