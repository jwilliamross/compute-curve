"""End-to-end daily cycle on temporary directories (no network)."""

from datetime import date

from compute_curve.config import load_config
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


def test_daily_cycle_end_to_end_and_idempotent(tmp_path):
    cfg = tmp_cfg(tmp_path)
    assert "No forward paper account" in status(cfg)
    run_snapshot(cfg, ["gpurentalprices"], client=client())
    inp = load_inputs(cfg)
    assert len(inp.observations) == 1
    assert write_own_index_outputs(cfg, inp).exists()
    report = daily(cfg, date(2026, 10, 5), do_snapshot=False)
    text = report.read_text()
    assert "Daily report 2026-10-05" in text
    assert "shadow mode" in text
    assert "last_date: 2026-10-05" in status(cfg)
    again = daily(cfg, date(2026, 10, 5), do_snapshot=False).read_text()
    assert "none (already up to date)" in again
