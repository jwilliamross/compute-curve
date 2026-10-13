# Round 5 results: archived list prices (one-shot, 2026-10-13)

Plan: docs/exploration_round5_plan.md, committed at 03:39:54 UTC before any
archived row existed on main. It ran exactly once, after the backfill
finished. Data: verified Wayback rows (D58), research-only.

## Plain-language summary

- **Do expensive providers cut and cheap ones raise? Not shown.** The
  estimate points that way. It is about the same size as the two earlier,
  independent estimates on our own listings. But it is too weak to be
  distinguishable from chance (p 0.21).
- **Are H100 list prices falling? Not on average.** From late 2023 to
  September 2026 the median provider's H100 on-demand list price was about
  flat: −1.2% a year, 95% CI −15.6% to +11.8%.
- **Providers moved in different directions.** Hyperstack and Verda fell
  sharply into 2025. Lambda and Nebius rose.

## Data

| Item | Value |
|---|---|
| Verified rows | 3,358 (H100, H200 and B200; every term) |
| Provider captures with an H100 on-demand price | 382 |
| Months | 2023-01 to 2026-09 (last complete month) |
| Claude API spend for the backfill | USD 18.01 of the owner's USD 20 cap |

## R5-01: monthly provider-gap test

| Statistic | Value |
|---|---|
| Cross-sections (≥ 4 providers) | 20 |
| Mean Fama-MacBeth slope | −0.032 |
| Newey-West SE (lag 3) | 0.038 |
| One-sided p (slope < 0) | 0.209 |
| Verdict | **not confirmed** |

**Context (an observation, not a new test).** Our listings give two
earlier, independent estimates of the same idea:

- round 1: −0.036;
- R2-01: −0.037, p 0.107.

That is three estimates of about −0.03 on different data, none
significant alone. Pooling them was not pre-registered, so no pooled
p-value is reported.

**What −0.03 means.** A provider 10% above the median closes about 0.3% of
the gap over 3 months: economically tiny even if real. The forward test
R4-01 stays as declared.

## R5-02: list-price trend (descriptive)

| Statistic | Value |
|---|---|
| Months with ≥ 3 providers | 33 (2023-11 to 2026-09) |
| Slope of the median log price | −0.012 per year |
| 95% block-bootstrap CI (block 6) | [−0.156, +0.118] |
| GetDeploying drift used in D55, for comparison | +0.135, CI [−0.33, 0.60] |

**Implication for the Monte Carlo fair value (D55).** Both sources agree
the drift is not distinguishable from zero. The archive's interval is
about three times narrower. The zero-drift scenario is the better-supported
default; this is a calibration note, not a finding.

## Descriptive only (post hoc, not a test)

Median verified H100 on-demand list price by provider and year, in USD per
GPU-hour. It is the median over rows, so it is weighted by how often each
page was archived.

| Provider | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|
| CoreWeave | n/a | n/a | 6.16 | 6.16 |
| Hyperstack | 4.30 | 3.00 | 1.95 | 2.50 |
| Lambda | 2.59 | 2.99 | 3.09 | 3.99 |
| Nebius | n/a | 2.95 | 2.95 | 3.85 |
| Verda | 3.50 | 3.17 | 2.19 | 3.58 |

## Caveats

- **List prices only.** Discounts, contracts and committed-use prices are
  not seen.
- **Irregular dates.** Captures are irregular, and a month-end price
  carries the latest capture forward for up to 92 days.
- **Small panel.** There are only 5 providers. CoreWeave has no extractable
  H100 on-demand price before 2025.
- **Verda pages list two price sets** about 10% apart (docs/wayback_backfill.md
  §7). The capture price is their median, as pre-registered.
- **Unread pages.** About 30 captures could not be fetched; the archive
  reset the connections.
