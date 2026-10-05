"""End-to-end daily cycle on temporary directories (no network)."""

from datetime import UTC, date, datetime

from compute_curve.config import load_config
from compute_curve.evaluation import run_evaluation
from compute_curve.pipeline import daily, load_inputs, status, write_own_index_outputs
from compute_curve.snapshot import run_snapshot
from tests.test_snapshot import client


def tmp_cfg(tmp_path):
    cfg = load_config()
    project = cfg.project.model_copy(
        update={
            "data_dir": tmp_path / "data",
            "var_dir": tmp_path / "var",
            "reports_dir": tmp_path / "reports",
        }
    )
    return cfg.model_copy(update={"project": project})


def test_daily_cycle_end_to_end(tmp_path):
    cfg = tmp_cfg(tmp_path)
    assert "No forward paper account" in status(cfg)
    run_snapshot(cfg, ["gpurentalprices"], client=client())
    inp = load_inputs(cfg)
    assert len(inp.observations) == 1
    assert write_own_index_outputs(cfg, inp).exists()
    text = daily(cfg, date(2026, 10, 5), do_snapshot=False).read_text()
    assert "Daily report 2026-10-05" in text
    assert "shadow mode" in text
    assert "last_date: 2026-10-05" in status(cfg)


def test_same_day_rerun_changes_nothing(tmp_path):
    """A second run on the same UTC day must leave every committed output identical."""
    cfg = tmp_cfg(tmp_path)
    today = datetime.now(tz=UTC).date()  # the snapshot log is keyed by the real UTC date
    run_snapshot(cfg, ["gpurentalprices"], client=client())
    log = tmp_path / "data" / "collection_log.jsonl"
    report = daily(cfg, today, do_snapshot=False)
    evaluation = run_evaluation(cfg)
    before = (log.read_bytes(), report.read_bytes(), evaluation.read_bytes())
    assert b"gpurentalprices" in before[1]  # ingestion comes from the collection log

    run_snapshot(cfg, ["gpurentalprices"], client=client())  # skipped: already collected
    report2 = daily(cfg, today, do_snapshot=False)
    evaluation2 = run_evaluation(cfg)
    assert (log.read_bytes(), report2.read_bytes(), evaluation2.read_bytes()) == before
    raw = list((tmp_path / "data" / "raw").rglob("*.parquet"))
    assert len(raw) == 1
