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
    # Claim 5 (docs/claim5_plan.md): claim 4's battery on AWS GPU spot signals.
    Variant(
        "claim5.leadlag",
        "claim5",
        "Family P: 4 spot signals x 3 horizons, basket minus XLK, HAC + permutation, Holm",
        "2026-10-06",
        True,
        12,
    ),
    Variant(
        "claim5.event",
        "claim5",
        "Family E: signed CAR after |spot level change| >= 2%, A100 and H100 x 3 horizons",
        "2026-10-06",
        False,
        6,
    ),
    Variant(
        "claim5.walkforward",
        "claim5",
        "Family W: expanding OLS vs zero and mean baselines, Clark-West, Holm",
        "2026-10-06",
        True,
        12,
    ),
    Variant(
        "claim5.buckets",
        "claim5",
        "Family S: lead-lag per bucket basket, 3 x 4 x 3, Benjamini-Hochberg",
        "2026-10-06",
        False,
        36,
    ),
    Variant(
        "claim5.strategy_pair",
        "claim5",
        "Gate G3: long-short basket vs XLK on each walk-forward forecast, claim 4 costs",
        "2026-10-06",
        False,
        12,
    ),
    Variant(
        "claim5.crosscorr",
        "claim5",
        "Descriptive cross-correlogram for the two level signals (not a test)",
        "2026-10-06",
        False,
        0,
    ),
    Variant(
        "explore1.H01",
        "explore1",
        "Provider premium vs cross-provider median -> own 5-day matched change (Fama-MacBeth)",
        "2026-10-06",
        True,
    ),
    Variant(
        "explore1.H02",
        "explore1",
        "Leaders' 5-day mean change -> followers' next 5-day mean change (our H100)",
        "2026-10-06",
        True,
    ),
    Variant(
        "explore1.H03",
        "explore1",
        "Neocloud H100 spot 5-day change -> H100 on-demand next 5-day change",
        "2026-10-06",
        True,
    ),
    Variant(
        "explore1.H04",
        "explore1",
        "B200 on-demand 5-day change -> H100 on-demand next 5-day change",
        "2026-10-06",
        True,
    ),
    Variant(
        "explore1.H05",
        "explore1",
        "CGI H100 past 6-hour change -> next 6-hour change",
        "2026-10-06",
        True,
    ),
    Variant(
        "explore1.H06",
        "explore1",
        "GetDeploying H100 spot weekly change -> H100 on-demand next week",
        "2026-10-06",
        True,
    ),
    Variant(
        "explore1.H07",
        "explore1",
        "GetDeploying H100 on-demand offer-count change -> H100 on-demand next week",
        "2026-10-06",
        True,
    ),
    Variant(
        "explore1.H08",
        "explore1",
        "GetDeploying B200 on-demand offer-count change -> H100 on-demand next week",
        "2026-10-06",
        True,
    ),
    Variant(
        "explore1.H09",
        "explore1",
        "AWS H100 spot 7-day change -> next 7-day change",
        "2026-10-06",
        True,
    ),
    Variant(
        "explore1.H10",
        "explore1",
        "AWS H200 minus H100 7-day change -> H100 next 7-day change",
        "2026-10-06",
        True,
    ),
    Variant(
        "explore1.H11",
        "explore1",
        "Neocloud 5-session excess over XLK -> AWS H100 spot next 7 days",
        "2026-10-06",
        True,
    ),
    Variant(
        "explore1.H12",
        "explore1",
        "AWS H100 20-day spot trend -> neocloud minus semis excess, next 5 sessions",
        "2026-10-06",
        True,
    ),
    Variant(
        "explore1.echo",
        "explore1",
        "Echo filter: partial slope without the target's own past change (not a test)",
        "2026-10-06",
        False,
        0,
    ),
    Variant(
        "explore1.posthoc_stability",
        "explore1",
        "Survivors' correlation by half and without the 1% largest signals (descriptive)",
        "2026-10-06",
        False,
        0,
    ),
    Variant(
        "explore1.confirm",
        "explore1",
        "One-shot confirmation of <= 3 survivors: one-sided HAC (Holm), OOS R2 vs 2 baselines",
        "2026-10-06",
        True,
        3,
    ),
    Variant(
        "explore1.forward.H05",
        "explore1",
        "Forward test of candidate H05 in shadow mode: 60 sessions, C1 and C2 on forward data",
        "2026-10-06",
        True,
        1,
    ),
)


def count(claim: str | None = None) -> int:
    return sum(1 for v in REGISTERED if claim is None or v.claim == claim)


def count_tests(claim: str | None = None) -> int:
    """Total hypothesis tests and evaluations declared (``n_tests`` summed)."""
    return sum(v.n_tests for v in REGISTERED if claim is None or v.claim == claim)
