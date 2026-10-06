"""Typed, validated configuration loaded from TOML.

Every tunable number lives in ``config/*.toml``. Values that come from
assumptions rather than verified sources are flagged with ``verified=false``
in the TOML and surfaced in every report.
"""

from __future__ import annotations

import tomllib
from datetime import date
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = REPO_ROOT / "config" / "default.toml"


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ProjectConfig(_Strict):
    seed: int = 20261005
    data_dir: Path = Path("data")
    var_dir: Path = Path("var")
    reports_dir: Path = Path("reports")

    def resolve(self, p: Path) -> Path:
        return p if p.is_absolute() else REPO_ROOT / p


class HttpConfig(_Strict):
    user_agent: str = "compute-curve-research/0.1 (non-commercial research)"
    min_interval_s: float = Field(default=2.0, ge=1.0)
    timeout_s: float = Field(default=30.0, gt=0)
    max_retries: int = Field(default=2, ge=0, le=5)


class ContractSpec(_Strict):
    product: str
    gpu_model: str
    underlying_index: str
    gpu_hours_per_contract: float = Field(gt=0)
    listed_months: int = Field(ge=1)
    tick_size: float = Field(gt=0, description="USD per GPU-hour")
    settlement_days: Literal["calendar", "business"]
    exchange_fee_per_contract: float = Field(ge=0, description="Per side, USD")
    cash_settlement_fee_per_contract: float = Field(default=0.0, ge=0, description="At expiry")
    initial_margin_per_contract: float = Field(ge=0)
    listing_status: str = "unknown"
    verified_fields: list[str] = []
    sources: list[str] = []
    notes: str = ""

    @property
    def verified(self) -> bool:
        """True only if every economic term used by the engine is verified."""
        needed = {
            "gpu_hours_per_contract",
            "tick_size",
            "settlement_days",
            "exchange_fee_per_contract",
            "initial_margin_per_contract",
        }
        return needed <= set(self.verified_fields)

    def is_verified(self, field_name: str) -> bool:
        return field_name in self.verified_fields

    @property
    def tick_value(self) -> float:
        return self.tick_size * self.gpu_hours_per_contract


class IndexConfig(_Strict):
    method: Literal["provider_weighted_median", "pooled_median", "trimmed_mean"] = (
        "provider_weighted_median"
    )
    trim_fraction: float = Field(default=0.1, ge=0.0, lt=0.5)
    min_providers: int = Field(default=2, ge=1)
    min_listings: int = Field(default=3, ge=1)
    terms: list[str] = ["on_demand"]
    # Hyperscalers are excluded: the settlement index tracks neoclouds.
    exclude_providers: list[str] = ["aws", "azure", "gcp", "oci"]
    variants: dict[str, list[str]] = {
        "H100": ["SXM", "PCIE", "NVL", "NVLINK", "UNKNOWN"],
        "B200": ["SXM", "UNKNOWN"],
    }
    # GPU1/GPU2 reference "Geography: United States". Listings with an explicit
    # region outside this list are excluded; unknown regions are kept when
    # include_unknown_region is true (most sources do not state a region).
    allowed_regions: list[str] = ["US", "NA"]
    include_unknown_region: bool = True
    # When several sources report the same provider on the same day, keep the
    # highest-priority source only (direct pages first, aggregators last).
    # Consistent single-publisher panel used for the historical series (the
    # live multi-source panel only starts on 2026-10-05).
    history_sources: list[str] = ["gpurentalprices_hist", "gpurentalprices"]
    history_min_presence: float = Field(default=0.9, gt=0, le=1)
    source_priority: list[str] = [
        "lambda",
        "coreweave",
        "nebius",
        "hyperstack",
        "verda",
        "lium",
        "gpurentalprices",
        "gpurentalprices_hist",
        "cgi",
    ]


class CollectorsConfig(_Strict):
    enabled: list[str] = [
        "cgi",
        "getdeploying",
        "gpurentalprices",
        "lium",
        "nebius",
        "lambda",
        "coreweave",
        "hyperstack",
        "verda",
    ]
    # Providers whose own terms prohibit automated collection or index use;
    # dropped even when they arrive via a third-party aggregator.
    excluded_providers: list[str] = ["vast", "runpod"]
    # Sources that need a licence; listed here only once a licence is held.
    licensed: list[str] = []


class SignalsConfig(_Strict):
    """Trading signals. A signal trades only if listed here AND validated.

    Validation status is written by ``compute-curve evaluate`` to
    ``var/validation.json``; a model that has not beaten its baseline out of
    sample runs in shadow mode (predictions logged, no orders).
    """

    trade: list[str] = ["nowcast", "relative_value"]
    nowcast_size: int = Field(default=1, ge=0)
    nowcast_edge_multiple: float = Field(
        default=2.0, gt=0, description="Required edge as a multiple of round-trip cost"
    )
    rv_size_gpu2: int = Field(default=1, ge=0)
    rv_contract_offset: int = Field(default=1, ge=0, description="0=front, 1=second month")


class CostConfig(_Strict):
    half_spread_ticks: float = Field(ge=0)
    slippage_ticks: float = Field(ge=0)
    broker_clearing_fee_per_contract: float = Field(
        ge=0, description="Assumed broker + clearing charge per contract per side, USD"
    )
    sensitivity_multipliers: list[float] = [0.0, 0.5, 1.0, 2.0, 4.0]


class RiskConfig(_Strict):
    starting_cash: float = Field(gt=0)
    max_contracts_per_month: int = Field(ge=0)
    max_gross_contracts: int = Field(ge=0)
    daily_loss_limit: float = Field(gt=0, description="USD; breach flattens and halts for the day")
    max_drawdown: float = Field(gt=0, description="USD from peak equity; breach flattens and halts")
    halt_days_after_daily_breach: int = Field(default=1, ge=0)


class NowcastConfig(_Strict):
    min_training_months: int = Field(default=6, ge=1)
    min_days_observed: int = Field(default=1, ge=0)
    publication_lag_days: int = Field(
        default=1, ge=0, description="Assumed lag between index as-of date and availability"
    )


class SchwartzSmithConfig(_Strict):
    dt_years: float = Field(default=1.0 / 365.0, gt=0)
    min_observations: int = Field(default=180, ge=10)
    jump_mean_prior: float = 0.0
    jump_std_prior: float = Field(default=0.15, gt=0)
    depreciation_rate_prior: float = Field(
        default=0.20, description="Annual log-price decline prior; assumption, not a finding"
    )


class HardwareLaunch(_Strict):
    name: str
    window_start: date
    affects: list[str]
    kind: Literal["announced", "volume_shipments", "cloud_ga"]
    source: str


class RelativeValueConfig(_Strict):
    perf_ratio_b200_over_h100: float = Field(gt=0)
    perf_ratio_low: float = Field(gt=0)
    perf_ratio_high: float = Field(gt=0)
    perf_ratio_source: str
    zscore_window_days: int = Field(default=60, ge=10)
    entry_z: float = Field(default=2.0, gt=0)
    exit_z: float = Field(default=0.5, ge=0)

    @model_validator(mode="after")
    def _ordered(self) -> RelativeValueConfig:
        if not self.perf_ratio_low <= self.perf_ratio_b200_over_h100 <= self.perf_ratio_high:
            raise ValueError("perf ratio must lie within [low, high]")
        return self


class BootstrapConfig(_Strict):
    n_boot: int = Field(default=2000, ge=100)
    block_length: int = Field(default=5, ge=1)
    confidence: float = Field(default=0.95, gt=0.5, lt=1.0)


class Claim4Universe(_Strict):
    neocloud: list[str]
    gpu_semis: list[str]
    power_capacity: list[str]

    def buckets(self) -> dict[str, list[str]]:
        return {
            "neocloud": self.neocloud,
            "gpu_semis": self.gpu_semis,
            "power_capacity": self.power_capacity,
        }

    def members(self) -> list[str]:
        return [s for b in self.buckets().values() for s in b]


class Claim4Costs(_Strict):
    """All values are assumptions (docs/claim4_plan.md section 7)."""

    stock_side_bps: float = Field(ge=0)
    benchmark_side_bps: float = Field(ge=0)
    sell_fee_bps: float = Field(ge=0)
    commission_per_order: float = Field(ge=0)
    stock_borrow_annual: float = Field(ge=0)
    benchmark_borrow_annual: float = Field(ge=0)
    sensitivity_multipliers: list[float] = [0.0, 0.5, 1.0, 2.0, 4.0]


class Claim4Risk(_Strict):
    pair_notional_usd: float = Field(gt=0)
    max_position_usd: float = Field(gt=0)
    max_gross_exposure_usd: float = Field(gt=0)
    daily_loss_limit_usd: float = Field(gt=0)
    max_drawdown_usd: float = Field(gt=0)
    halt_sessions_after_daily_breach: int = Field(default=1, ge=0)
    kill_switch: bool = False


class Claim4Config(_Strict):
    """Pre-registered claim-4 settings (docs/claim4_plan.md)."""

    benchmark: str
    first_session: date
    bars_start: date
    horizons: list[int]
    signals: list[str]
    feed: Literal["sip", "iex"] = "sip"
    adjustment: Literal["raw", "split", "dividend", "all"] = "all"
    availability_margin_minutes: int = Field(default=60, ge=0)
    daily_cutoff_utc: str = Field(default="23:30", pattern=r"^\d{2}:\d{2}$")
    open_buffer_minutes: int = Field(default=5, ge=0)
    min_bucket_coverage: float = Field(default=0.5, gt=0, le=1)
    event_threshold: float = Field(default=0.02, gt=0)
    min_events: int = Field(default=10, ge=1)
    min_nonzero_signal: int = Field(default=10, ge=1)
    min_train: int = Field(default=20, ge=3)
    alpha: float = Field(default=0.05, gt=0, lt=0.5)
    fdr_q: float = Field(default=0.10, gt=0, lt=0.5)
    min_oos_forecasts: int = Field(default=120, ge=1)
    min_oos_nonzero: int = Field(default=30, ge=1)
    max_index_age_days: int = Field(default=3, ge=0)
    paper_start: date
    universe: Claim4Universe
    panels: dict[str, list[str]]
    costs: Claim4Costs
    risk: Claim4Risk

    @model_validator(mode="after")
    def _consistent(self) -> Claim4Config:
        if self.benchmark in self.universe.members():
            raise ValueError("benchmark must not be a universe member")
        if len(set(self.universe.members())) != len(self.universe.members()):
            raise ValueError("a symbol appears in two buckets")
        if self.risk.pair_notional_usd > self.risk.max_position_usd:
            raise ValueError("pair notional per leg exceeds the per-symbol limit")
        if 2 * self.risk.pair_notional_usd > self.risk.max_gross_exposure_usd:
            raise ValueError("a full pair exceeds the gross exposure limit")
        return self


class Config(_Strict):
    project: ProjectConfig = ProjectConfig()
    http: HttpConfig = HttpConfig()
    collectors: CollectorsConfig = CollectorsConfig()
    signals: SignalsConfig = SignalsConfig()
    contracts: dict[str, ContractSpec]
    index: IndexConfig = IndexConfig()
    costs: CostConfig
    risk: RiskConfig
    nowcast: NowcastConfig = NowcastConfig()
    schwartz_smith: SchwartzSmithConfig = SchwartzSmithConfig()
    launches: list[HardwareLaunch] = []
    relative_value: RelativeValueConfig
    bootstrap: BootstrapConfig = BootstrapConfig()
    claim4: Claim4Config | None = None

    def path(self, kind: Literal["data", "var", "reports"]) -> Path:
        raw = {
            "data": self.project.data_dir,
            "var": self.project.var_dir,
            "reports": self.project.reports_dir,
        }[kind]
        return self.project.resolve(raw)


def load_config(path: Path | None = None) -> Config:
    """Load and validate a TOML config file (default: ``config/default.toml``)."""
    p = path or DEFAULT_CONFIG_PATH
    with p.open("rb") as fh:
        raw = tomllib.load(fh)
    return Config.model_validate(raw)
