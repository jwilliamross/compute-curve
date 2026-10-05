"""Normalized schema for price observations and published series.

Every collector emits :class:`PriceObservation` rows. The required fields
(``ts_observed``, ``provider``, ``gpu_model``, ``config``,
``price_usd_per_gpu_hour``, ``term``, ``region``, ``availability``) match the
project specification. The extra fields carry provenance so raw data can be
re-normalized later without re-collecting it.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from compute_curve.timeutil import ensure_utc


class GpuModel(StrEnum):
    """Canonical GPU families tracked by the project."""

    H100 = "H100"
    H200 = "H200"
    B200 = "B200"
    OTHER = "OTHER"


class Term(StrEnum):
    """Commercial term of a listing."""

    ON_DEMAND = "on_demand"
    SPOT = "spot"
    RESERVED = "reserved"
    UNKNOWN = "unknown"


class Availability(StrEnum):
    """Coarse availability state reported or implied by the source."""

    AVAILABLE = "available"
    LIMITED = "limited"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


_H100_RE = re.compile(r"\bh\s*100\b", re.IGNORECASE)
_H200_RE = re.compile(r"\bh\s*200\b", re.IGNORECASE)
_B200_RE = re.compile(r"\bb\s*200\b", re.IGNORECASE)
_EXCLUDE_RE = re.compile(r"\b(gb\s*200|gh\s*200|b\s*300|gb\s*300)\b", re.IGNORECASE)


def canonical_gpu_model(name: str) -> GpuModel:
    """Map a provider's GPU name to a canonical family.

    Grace-Blackwell (GB200) and Grace-Hopper (GH200) superchips and B300 are
    deliberately *not* mapped to B200/H200: they are different products.
    """
    if _EXCLUDE_RE.search(name):
        return GpuModel.OTHER
    if _B200_RE.search(name):
        return GpuModel.B200
    if _H200_RE.search(name):
        return GpuModel.H200
    if _H100_RE.search(name):
        return GpuModel.H100
    return GpuModel.OTHER


def gpu_variant(name: str) -> str:
    """Form factor hint from a GPU name.

    Returns ``SXM``, ``PCIE``, ``NVL`` (the H100/H200 NVL product),
    ``NVLINK`` (a provider label for NVLink-connected boards whose form factor
    the name does not state) or ``UNKNOWN``.
    """
    upper = name.upper().replace("-", " ")
    if "NVLINK" in upper:
        return "NVLINK"
    for token in ("SXM", "PCIE", "NVL"):
        if re.search(rf"\b{token}", upper):
            return token
    return "UNKNOWN"


def normalize_region(text: str | None) -> str | None:
    """Coarse region code from free text: US, NA, EU, ... or None if unknown."""
    if not text:
        return None
    t = text.strip().upper()
    if t.startswith("US") or "UNITED STATES" in t:
        return "US"
    if "NORTH AMERICA" in t or t == "NA":
        return "NA"
    if t.startswith("EU") or "EUROPE" in t or "NORDIC" in t:
        return "EU"
    if t.startswith("CA") or "CANADA" in t:
        return "CA"
    return t.split()[0][:12]


class PriceObservation(BaseModel):
    """One observed rental price for one listing at one point in time."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    # --- required normalized fields -------------------------------------
    ts_observed: datetime = Field(description="UTC time the response was received")
    provider: str = Field(min_length=1, description="Cloud provider selling the capacity")
    gpu_model: GpuModel
    config: str = Field(description="Instance shape, e.g. '8x H100 SXM 80GB'")
    price_usd_per_gpu_hour: float = Field(gt=0, lt=1000)
    term: Term
    region: str | None = None
    availability: Availability

    # --- provenance -------------------------------------------------------
    source: str = Field(min_length=1, description="Collector id that produced the row")
    snapshot_id: str = Field(min_length=1, description="<source>_<UTC stamp>")
    ts_source: datetime | None = Field(
        default=None,
        description="Time the upstream source says it observed the price (aggregators); "
        "None when we observed the provider directly",
    )
    gpu_variant: str = "UNKNOWN"
    gpus_per_instance: int | None = Field(default=None, ge=1)
    listing_id: str | None = None
    source_url: str | None = None
    price_basis: str = Field(
        default="list",
        description="What the price includes, e.g. 'gpu_only' or 'total_incl_storage'",
    )
    raw_json: str | None = Field(
        default=None, description="Source record with host-identifying fields removed"
    )
    is_synthetic: bool = False

    @field_validator("ts_observed")
    @classmethod
    def _utc(cls, v: datetime) -> datetime:
        return ensure_utc(v)

    @field_validator("ts_source")
    @classmethod
    def _utc_opt(cls, v: datetime | None) -> datetime | None:
        return None if v is None else ensure_utc(v)


class IndexObservation(BaseModel):
    """A value of a third-party reference index or aggregate, as we observed it.

    Examples: Computable GPU Index values, GetDeploying weekly medians. These
    are *not* the CME settlement index. ``as_of`` is the time the publisher
    assigns to the value; ``ts_observed`` is when we fetched it. History that
    a publisher serves today is stored with today's ``ts_observed`` so later
    revisions remain visible (each fetch is a vintage).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    ts_observed: datetime
    source: str = Field(min_length=1)
    snapshot_id: str = Field(min_length=1)
    index_name: str = Field(min_length=1)
    gpu_model: GpuModel
    term: Term
    as_of: datetime
    value: float = Field(gt=0, lt=1000)
    band_low: float | None = None
    band_high: float | None = None
    n_providers: int | None = Field(default=None, ge=0)
    n_listings: int | None = Field(default=None, ge=0)
    methodology_id: str | None = None
    license: str | None = None
    raw_json: str | None = None
    is_synthetic: bool = False

    @field_validator("ts_observed", "as_of")
    @classmethod
    def _utc(cls, v: datetime) -> datetime:
        return ensure_utc(v)


class PublishedIndexValue(BaseModel):
    """A published index value (e.g. Silicon Data H100 rental index).

    ``as_of_date`` is the date the value refers to. ``ts_available`` is the
    earliest time a model may use it. For values collected live this is the
    observation time. For history loaded from a manual file it is the
    ``as_of_date`` plus the configured publication lag, which is an
    *assumption* recorded in ``docs/decisions.md``.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    index_name: str
    as_of_date: date
    value: float = Field(gt=0)
    ts_available: datetime
    ts_observed: datetime
    source: str
    is_synthetic: bool = False

    @field_validator("ts_available", "ts_observed")
    @classmethod
    def _utc(cls, v: datetime) -> datetime:
        return ensure_utc(v)


class Settlement(BaseModel):
    """A CME daily settlement price for one futures contract month."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    product: str = Field(description="'GPU1' or 'GPU2'")
    contract_month: str = Field(pattern=r"^\d{4}-\d{2}$")
    trade_date: date
    settle_price: float = Field(gt=0, description="USD per GPU-hour")
    volume: int | None = None
    open_interest: int | None = None
    ts_available: datetime
    ts_observed: datetime
    source: str
    is_synthetic: bool = False

    @field_validator("ts_available", "ts_observed")
    @classmethod
    def _utc(cls, v: datetime) -> datetime:
        return ensure_utc(v)


SENSITIVE_KEYS: frozenset[str] = frozenset(
    {
        "public_ipaddr",
        "ip",
        "ipaddr",
        "ip_address",
        "hostname",
        "host_name",
        "ssh_host",
        "ssh_port",
        "webpage",
        "email",
        "owner_email",
        "user",
        "username",
    }
)


def strip_sensitive(record: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of ``record`` without host- or person-identifying keys."""
    return {k: v for k, v in record.items() if k.lower() not in SENSITIVE_KEYS}
