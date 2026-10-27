"""Insider tracker (D69) on hand-made Form 4 documents and index text (no real filings)."""

# ruff: noqa: E501  (fixture XML and fixed-width index lines)

from datetime import UTC, date, datetime
from pathlib import Path

import pandas as pd
import pytest

from compute_curve import insiders as ins
from compute_curve.storage.raw_store import write_snapshot

TS = datetime(2030, 1, 9, 12, tzinfo=UTC)


def form4(
    cik: str,
    ticker: str,
    owner: str,
    title: str,
    code: str = "P",
    shares: float = 1000,
    price: float = 50.0,
    after: float = 5000,
    plan: str = "0",
    tdate: str = "2030-01-08",
    director: str = "0",
) -> str:
    return f"""<?xml version="1.0"?>
<ownershipDocument>
  <documentType>4</documentType>
  <aff10b5One>{plan}</aff10b5One>
  <issuer><issuerCik>{cik}</issuerCik><issuerName>Test Co {ticker}</issuerName>
    <issuerTradingSymbol>{ticker.lower()}</issuerTradingSymbol></issuer>
  <reportingOwner>
    <reportingOwnerId><rptOwnerCik>{owner}</rptOwnerCik><rptOwnerName>Owner {owner}</rptOwnerName></reportingOwnerId>
    <reportingOwnerAddress><rptOwnerStreet1>1 Main St</rptOwnerStreet1></reportingOwnerAddress>
    <reportingOwnerRelationship><isDirector>{director}</isDirector><isOfficer>{1 if title else 0}</isOfficer>
      <officerTitle>{title}</officerTitle></reportingOwnerRelationship>
  </reportingOwner>
  <nonDerivativeTable>
    <nonDerivativeTransaction>
      <transactionDate><value>{tdate}</value></transactionDate>
      <transactionCoding><transactionCode>{code}</transactionCode></transactionCoding>
      <transactionAmounts>
        <transactionShares><value>{shares}</value></transactionShares>
        <transactionPricePerShare><value>{price}</value></transactionPricePerShare>
        <transactionAcquiredDisposedCode><value>{"A" if code == "P" else "D"}</value></transactionAcquiredDisposedCode>
      </transactionAmounts>
      <postTransactionAmounts><sharesOwnedFollowingTransaction><value>{after}</value></sharesOwnedFollowingTransaction></postTransactionAmounts>
      <ownershipNature><directOrIndirectOwnership><value>D</value></directOrIndirectOwnership></ownershipNature>
    </nonDerivativeTransaction>
  </nonDerivativeTable>
</ownershipDocument>"""


def rows(xml: str, acc: str = "0000000000-30-000001", filed: str = "20300109") -> list[dict]:
    return ins.parse_form4(xml, acc, filed, f"https://www.sec.gov/Archives/{acc}.txt", TS)


def test_parse_index_dedupes_accessions() -> None:
    text = (
        "Form Type   Company Name   CIK   Date Filed   File Name\n"
        "-----\n"
        "4           TEST CO            1111111     20300109    edgar/data/1111111/0001-30-000001.txt\n"
        "4           SMITH JOHN         2222222     20300109    edgar/data/2222222/0001-30-000001.txt\n"
        "4/A         TEST CO            1111111     20300109    edgar/data/1111111/0001-30-000002.txt\n"
        "8-K         OTHER CO           3333333     20300109    edgar/data/3333333/0001-30-000003.txt\n"
    )
    out = ins.parse_index(text)
    assert [r["accession"] for r in out] == ["0001-30-000001"]


def test_extract_xml_from_submission() -> None:
    sub = (
        "<SEC-DOCUMENT><DOCUMENT><TEXT><XML>\n" + form4("1", "ABC", "9", "CEO") + "\n</XML></TEXT>"
    )
    xml = ins.extract_xml(sub)
    assert xml and xml.startswith("<ownershipDocument") and xml.endswith("</ownershipDocument>")
    assert ins.extract_xml("no xml here") is None


def test_parse_keeps_purchases_only_and_never_addresses() -> None:
    r = rows(form4("1", "ABC", "9", "Chief Executive Officer"))
    assert len(r) == 1 and r[0]["ticker"] == "ABC" and r[0]["value_usd"] == 50_000
    assert r[0]["shares_after"] == 5000 and r[0]["direct"] and not r[0]["plan_10b5_1"]
    assert "Main St" not in str(r)
    assert rows(form4("1", "ABC", "9", "CEO", code="S")) == []


def test_entity_declarations_are_refused() -> None:
    evil = '<!DOCTYPE x [<!ENTITY a "aaaa">]>' + form4("1", "ABC", "9", "CEO")
    assert rows(evil) == []


def _hist(*xmls: str) -> pd.DataFrame:
    out = []
    for i, x in enumerate(xmls):
        out += rows(x, acc=f"acc-{i}")
    return ins.frame(out)


def test_alert_tiers() -> None:
    rules = ins.Rules()
    cluster = _hist(*(form4("1", "CLU", str(k), "") for k in range(3)))
    al = ins.alerts(cluster, {"2030-01-09"}, rules)
    assert al.iloc[0]["tier"].startswith("cluster") and al.iloc[0]["insiders"] == 3
    ceo = _hist(form4("2", "CEO", "7", "President and CEO", shares=3000))
    assert ins.alerts(ceo, {"2030-01-09"}, rules).iloc[0]["tier"] == "C-suite buy"
    small = _hist(form4("3", "SML", "8", "", shares=100))  # USD 5,000: below the minimum
    assert ins.alerts(small, {"2030-01-09"}, rules).empty
    planned = _hist(*(form4("4", "PLN", str(k), "", plan="1") for k in range(3)))
    assert ins.alerts(planned, {"2030-01-09"}, rules).empty


def test_alerts_need_a_new_filing() -> None:
    cluster = _hist(*(form4("1", "CLU", str(k), "") for k in range(3)))
    assert ins.alerts(cluster, {"2030-01-10"}, ins.Rules()).empty


def test_holding_increase_and_render() -> None:
    h = _hist(form4("2", "CEO", "7", "CEO", shares=4000, after=5000))  # 4,000 on 1,000 before
    al = ins.alerts(h, {"2030-01-09"}, ins.Rules())
    assert round(al.iloc[0]["holding_increase_pct"]) == 400
    md = ins.render(al, h, ["2030-01-09"], ins.Rules())
    assert "| CEO |" in md and "C-suite buy" in md and "400%" in md


def test_user_agent_requires_contact_email() -> None:
    with pytest.raises(RuntimeError):
        ins.user_agent({})
    assert ins.user_agent({"SEC_USER_AGENT": "Name a@b.c"}) == "Name a@b.c"


def test_pending_days_skip_weekends_and_done() -> None:
    days = ins.pending_days(date(2030, 1, 14), {"20300110"})  # a Monday
    assert days == [date(2030, 1, 9), date(2030, 1, 11)]
    assert ins.index_url(date(2030, 11, 3)).endswith("2030/QTR4/form.20301103.idx")


def test_raw_roundtrip_and_done_days(tmp_path: Path) -> None:
    h = _hist(form4("2", "CEO", "7", "CEO", shares=4000))
    write_snapshot(tmp_path, ins.SOURCE, datetime(2030, 1, 9, tzinfo=UTC), h)
    write_snapshot(tmp_path, ins.SOURCE, datetime(2030, 1, 10, tzinfo=UTC), ins.frame([]))
    assert ins.done_days(tmp_path) == {"20300109", "20300110"}
    back = ins.load_history(tmp_path, date(2030, 1, 1))
    assert len(back) == 1 and back.iloc[0]["ticker"] == "CEO" and bool(back.iloc[0]["is_officer"])
    assert not ins.alerts(back, {"2030-01-09"}, ins.Rules()).empty
