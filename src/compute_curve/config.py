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
    exchange_fee_per_contract: float = Field(ge=0)
    initial_margin_per_contract: float = Field(ge=0)
    verified: bool = False
    notes: str = ""

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
    exclude_providers: list[str] = []
    variants: dict[str, list[str]] = {
        "H100": ["SXM", "PCIE", "NVL", "UNKNOWN"],
        "B200": ["SXM", "UNKNOWN"],
    }


class CostConfig(_Strict):
    half_spread_ticks: float = Field(ge=0)
    slippage_ticks: float = Field(ge=0)
    fee_per_contract: float = Field(ge=0, description="All-in exchange + clearing + broker, USD")
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


class Config(_Strict):
    project: ProjectConfig = ProjectConfig()
    http: HttpConfig = HttpConfig()
    contracts: dict[str, ContractSpec]
    index: IndexConfig = IndexConfig()
    costs: CostConfig
    risk: RiskConfig
    nowcast: NowcastConfig = NowcastConfig()
    schwartz_smith: SchwartzSmithConfig = SchwartzSmithConfig()
    launches: list[HardwareLaunch] = []
    relative_value: RelativeValueConfig
    bootstrap: BootstrapConfig = BootstrapConfig()

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
