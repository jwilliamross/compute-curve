"""Registry of every model and strategy variant the project has declared.

Reports print ``len(REGISTERED)`` as "variants tried" so the multiple-testing
burden is visible. Add a line here *before* running a new variant; never
delete one. Mirrors ``docs/variants_log.md``.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Variant:
    key: str
    claim: str
    description: str
    declared: str  # ISO date
    primary: bool


REGISTERED: tuple[Variant, ...] = (
    Variant(
        "index.provider_weighted_median", "index", "Primary own-index aggregate", "2026-10-05", True
    ),
    Variant(
        "index.pooled_median", "index", "Robustness: listing-level median", "2026-10-05", False
    ),
    Variant("index.trimmed_mean_10", "index", "Robustness: 10% trimmed mean", "2026-10-05", False),
    Variant(
        "nowcast.own_bridge", "claim1", "Own-index bridge, no fitted parameters", "2026-10-05", True
    ),
    Variant("ss.spot_only", "claim2", "Schwartz-Smith real-world fit on index", "2026-10-05", True),
    Variant("ss.panel", "claim2", "Schwartz-Smith panel fit with launch jumps", "2026-10-05", True),
    Variant("rv.ar1_spread", "claim3", "AR(1) on perf-normalized log spread", "2026-10-05", True),
    Variant(
        "strategy.nowcast_front",
        "claim3",
        "Trade front month on nowcast edge > 2x cost",
        "2026-10-05",
        True,
    ),
    Variant("strategy.rv_fade", "claim3", "Fade |z|>2 on second-month spread", "2026-10-05", True),
)


def count(claim: str | None = None) -> int:
    return sum(1 for v in REGISTERED if claim is None or v.claim == claim)
