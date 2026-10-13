"""Wayback capture parsing, quote verification and the spend ledger (D58). No network."""

from datetime import UTC, datetime
from pathlib import Path

from compute_curve import llm_extract as lx
from compute_curve.collectors.wayback import (
    Capture,
    cdx_query,
    coverage_order,
    has_gpu_text,
    page_text,
    parse_cdx,
    to_observation,
    verify_row,
)
from compute_curve.schema import GpuModel, Term

PAGE = """
<html><body><h1>GPU Cloud pricing</h1>
<table><tr><th>GPU</th><th>Price</th></tr>
<tr><td>8x NVIDIA H100 SXM</td><td>$23.92 / hr</td></tr>
<tr><td>1x NVIDIA H100 PCIe</td><td>$2.49 per GPU-hour</td></tr>
<tr><td>1x A100 40GB</td><td>$1.29 / hr</td></tr>
</table></body></html>
"""
CAP = Capture(datetime(2024, 3, 1, 12, 0, 5, tzinfo=UTC), "https://example.com/pricing", "ABC")


def _row(**kw: object) -> lx.PriceRow:
    base: dict[str, object] = {
        "gpu_name": "NVIDIA H100 PCIe",
        "gpus_per_unit": 1,
        "price_usd": 2.49,
        "unit": "per_gpu_hour",
        "term": "on_demand",
        "quote": "$2.49 per GPU-hour",
        "qualifier": "",
    }
    base.update(kw)
    return lx.PriceRow.model_validate(base)


def _text() -> str:
    return page_text(PAGE, 60000)[0]


def test_parse_cdx_keeps_200s_oldest_first() -> None:
    payload = [
        ["timestamp", "original", "statuscode", "digest"],
        ["20240301120005", "https://example.com/pricing", "200", "B"],
        ["20230101000000", "https://example.com/pricing", "200", "A"],
        ["20230601000000", "https://example.com/pricing", "301", "C"],
        ["bad", "https://example.com/pricing", "200", "D"],
    ]
    caps = parse_cdx(payload)
    assert [c.digest for c in caps] == ["A", "B"]
    assert (
        caps[1].archive_url
        == "https://web.archive.org/web/20240301120005id_/https://example.com/pricing"
    )
    assert parse_cdx([]) == []


def test_cdx_query_collapses_by_digest() -> None:
    q = cdx_query("lambda.ai/pricing", "2023", "20261012")
    assert "collapse=digest" in q and "filter=statuscode%3A200" in q


def test_verify_accepts_a_quoted_price() -> None:
    assert verify_row(_row(), _text()) == (GpuModel.H100, 2.49)


def test_verify_divides_instance_prices_by_gpu_count() -> None:
    row = _row(
        gpu_name="NVIDIA H100 SXM",
        gpus_per_unit=8,
        price_usd=23.92,
        unit="per_instance_hour",
        quote="$23.92 / hr",
    )
    ok = verify_row(row, _text())
    assert ok is not None and ok[0] == GpuModel.H100 and abs(ok[1] - 2.99) < 1e-9


def test_verify_rejects_a_quote_not_on_the_page() -> None:
    assert verify_row(_row(quote="$1.99 per GPU-hour", price_usd=1.99), _text()) is None


def test_verify_rejects_a_price_not_in_the_quote() -> None:
    assert verify_row(_row(price_usd=1.99), _text()) is None


def test_verify_rejects_out_of_scope_and_unnamed_gpus() -> None:
    assert (
        verify_row(_row(gpu_name="A100 40GB", quote="$1.29 / hr", price_usd=1.29), _text()) is None
    )
    far = "H100 " + "x " * 400 + "$9.99 / hr"
    assert verify_row(_row(quote="$9.99 / hr", price_usd=9.99), far) is None


def test_page_text_truncates_to_price_lines() -> None:
    filler = "<p>lorem ipsum</p>" * 5000
    text, truncated = page_text(f"<html>{filler}{PAGE}</html>", 5000)
    assert truncated and len(text) <= 5000 and "$2.49 per GPU-hour" in text
    assert has_gpu_text(text) and not has_gpu_text("A100 only")


def test_qualifier_separates_two_prices_for_the_same_gpu() -> None:
    a = _row(qualifier="Location A")
    b = _row(qualifier="")
    oa = to_observation(a, GpuModel.H100, 2.49, "verda", CAP, "m", CAP.ts)
    ob = to_observation(b, GpuModel.H100, 2.49, "verda", CAP, "m", CAP.ts)
    assert oa.listing_id != ob.listing_id and "[Location A]" in oa.config
    assert "[" not in ob.config


def test_observation_carries_capture_time_and_quote() -> None:
    row = _row()
    obs = to_observation(row, GpuModel.H100, 2.49, "lambda", CAP, "claude-opus-5-5", CAP.ts)
    assert obs.ts_observed == CAP.ts and obs.term == Term.ON_DEMAND
    assert obs.source == "wayback_lambda" and "$2.49 per GPU-hour" in (obs.raw_json or "")
    assert obs.source_url == CAP.archive_url


def test_ledger_caps_and_done_digests(tmp_path: Path) -> None:
    path = tmp_path / "llm_spend.jsonl"
    price = lx.Pricing(4.0, 20.0)
    assert abs(price.cost(1_000_000, 100_000) - 6.0) < 1e-9
    for i, status in enumerate(["ok", "no_gpu_text", "max_tokens"]):
        lx.append_ledger(
            path,
            lx.SpendEntry(
                ts="t", run_id="r1", provider="lambda", capture=str(i), digest=f"d{i}",
                model="m", input_tokens=0, output_tokens=0, cost_usd=6.0, n_proposed=0,
                n_kept=0, truncated=False, status=status,
            ),
        )  # fmt: skip
    entries = lx.read_ledger(path)
    assert lx.spent(entries) == 18.0 and lx.spent(entries, "r2") == 0.0
    assert lx.done_digests(entries) == {("lambda", "d0"), ("lambda", "d1")}
    assert lx.within_budget(entries, "r2", 2.0, total=20.0, per_run=20.0)
    assert not lx.within_budget(entries, "r2", 2.5, total=20.0, per_run=20.0)
    assert not lx.within_budget(entries, "r1", 1.0, total=100.0, per_run=18.5)


def test_coverage_order_spreads_months_and_targets_first() -> None:
    def cap(y: int, m: int, d: int, tag: str) -> Capture:
        return Capture(datetime(y, m, d, tzinfo=UTC), "u", tag)

    a = [cap(2024, 1, 5, "a1"), cap(2024, 1, 20, "a2"), cap(2024, 2, 3, "a3")]
    b = [cap(2024, 1, 9, "b1"), cap(2024, 3, 1, "b2")]
    order = [c.digest for _, c in coverage_order([a, b])]
    assert order == ["a1", "b1", "a3", "b2", "a2"]
    assert [i for i, _ in coverage_order([a, b])][:2] == [0, 1]
