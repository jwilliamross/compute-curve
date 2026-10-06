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
    n_tests: int = 1  # hypothesis tests or evaluations this entry stands for


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
    # Claim 4 (docs/claim4_plan.md), declared before any test-window return was seen.
    Variant(
        "claim4.leadlag",
        "claim4",
        "Family P: 6 signals x 3 horizons, basket minus XLK, HAC + permutation, Holm",
        "2026-10-06",
        True,
        18,
    ),
    Variant(
        "claim4.event",
        "claim4",
        "Family E: signed CAR after |level change| >= 2%, 2 GPUs x 3 horizons, Holm",
        "2026-10-06",
        False,
        6,
    ),
    Variant(
        "claim4.walkforward",
        "claim4",
        "Family W: expanding OLS vs zero and mean baselines, Clark-West, Holm",
        "2026-10-06",
        True,
        18,
    ),
    Variant(
        "claim4.buckets",
        "claim4",
        "Family S: lead-lag per bucket basket, 3 x 6 x 3, Benjamini-Hochberg",
        "2026-10-06",
        False,
        54,
    ),
    Variant(
        "claim4.strategy_pair",
        "claim4",
        "Gate G3: long-short basket vs XLK on each walk-forward forecast, net of costs",
        "2026-10-06",
        False,
        18,
    ),
    Variant(
        "claim4.crosscorr",
        "claim4",
        "Descriptive cross-correlogram, leads and lags -5..+5 (not a test)",
        "2026-10-06",
        False,
        0,
    ),
)


def count(claim: str | None = None) -> int:
    return sum(1 for v in REGISTERED if claim is None or v.claim == claim)


def count_tests(claim: str | None = None) -> int:
    """Total hypothesis tests and evaluations declared (``n_tests`` summed)."""
    return sum(v.n_tests for v in REGISTERED if claim is None or v.claim == claim)
