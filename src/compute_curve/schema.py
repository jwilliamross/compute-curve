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
    """Form factor hint (``SXM``, ``PCIE``, ``NVL`` or ``UNKNOWN``) from a GPU name."""
    upper = name.upper().replace("-", " ")
    for token in ("NVL", "PCIE", "SXM"):
        if token in upper:
            return token
    return "UNKNOWN"


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
