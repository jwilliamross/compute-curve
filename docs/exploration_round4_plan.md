# Exploration round 4: forward replication of H01, the provider gap (plan)

_Written 2026-10-11, before any outcome in the test window exists. Owner request:
"keep going with the provider gap test". Simulation only._

## 1. Why a forward test

H01 is round 1's lead for our own index:

- Hypothesis: a provider priced above the cross-provider median for H100
  on-demand tends to cut, and one priced below tends to raise. The predictor
  is the premium; the outcome is the provider's own matched 5-day change.
- Round 1, exploration window: slope −0.036.
- Round 2's one-shot replication on 2026-09-13 to 10-06 (R2-01): slope
  −0.037, one-sided p 0.107, 19 cross-sections. Not confirmed.

**The newly imported Hugging Face history (`gpuprices_hf`, D54) cannot test
H01.**

- Under the index's filters (US or unknown region, no hyperscalers), only one
  provider qualifies on every one of its 148 days: Lambda.
- H01 needs at least 5 providers per cross-section (`min_cs_providers`).
- That was checked by counting providers per day only. No outcome was
  computed.
- Relaxing the filters to make it fit would be a different hypothesis, chosen
  after seeing the data, so it is not done.

**So H01 is replicated forward, once, with its frozen round-1 specification,**
on listing days no test has used.

## 2. Test (fixed now)

| Item | Value |
|---|---|
| ID | R4-01 |
| Data | our listings, the same sources and filters as H01 (`index.history_sources`, `listing_prices`) |
| Window | as_of 2026-10-07 to 2026-12-31. The 5-day outcomes must lie inside the window (truncate before compute) |
| Specification | H01 as frozen in round 1: Fama-MacBeth daily cross-sectional slopes, HAC lag 5, at least 5 providers per cross-section |
| C1 | one-sided p ≤ 0.05 in the expected direction (negative slope). A single test, so no adjustment |
| C2 | frozen round-1 coefficients give out-of-sample R² > 0 against zero and against the exploration mean (as R2-01) |
| Runs | once, on or after 2027-01-01, automatically in the daily workflow (`explore round4 confirmation`). Until then the stage only counts days |

**Outcomes.**

- **Confirmed.** H01 becomes a candidate signal for our index's nowcast. It
  still cannot trade: D26 holds until GPU1 lists.
- **Not confirmed.** Report it, and stop testing H01 on these sources.

**Variants.** One new variant: the project total rises from 257 to 258.

## 3. Addendum (2026-10-11, before running): R4-02, does AWS scarcity lead neocloud prices?

### Question

When the AWS H100 spot price rises, do neocloud H100 rental prices rise
over the following week?

- **Mechanism.** AWS spot prices reflect AWS's spare capacity. Tight
  hyperscaler capacity pushes demand to neoclouds.
- **Expected sign.** Positive.
- **New idea, not a re-test.** It was not tested in rounds 1 to 3. H09 and
  H10 used AWS against AWS itself; H11 and H12 used AWS against equities.

### Data

| Role | Series |
|---|---|
| Signal x(t) | 7-day log change of the AWS H100 daily median spot price per GPU-hour (`reports/claim5/aws_spot_daily.csv`) |
| Target R4-02a | next 7-day log change of the CGI H100 daily close |
| Target R4-02b | next 7-day log change of our H100 history-panel index (`reports/own_index.csv`, `series = history_panel`) |

Pairs need exact dates on both sides; nothing is filled in.

### Sets

- **Exploration (descriptive, freezes the coefficients for C2).** AWS months
  2026-07 to 09, the only months that overlap the targets.
  - Contamination: the AWS rows were used in round 1's H09 confirmation, but
    only against AWS itself, never against a neocloud target.
  - CGI overlap starts 2026-08-30.
- **Confirmation (one shot).** Pairs with t from 2026-10-01 to 12-24, so
  every outcome ends by 12-31. It runs when the AWS 2026-12 month is
  published.

### Test

- Fit y = a + b·x.
- Use Newey-West errors with lag 7, and a one-sided test of b > 0.
- **C1.** Holm-adjusted p ≤ 0.05 across the two targets.
- **C2.** The frozen exploration coefficients give out-of-sample R² > 0
  against zero.
- Confirmed means C1 and C2.

### Power, stated now

About 85 overlapping daily pairs make about 12 independent weeks. Only a
strong link can confirm, so a null result means "no evidence".

### Variants

2 confirmation tests, plus 2 descriptive exploration fits. The project total
rises from 258 to 262.
