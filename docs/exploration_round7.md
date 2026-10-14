# Round 7 results: GetDeploying per-provider price history

Run once on 2026-10-14. The plan, docs/exploration_round7_plan.md, was
committed before the download.

- **Data.** GetDeploying API, research access, vintage 20261014T172009Z
  (D60). Source credit: GetDeploying, getdeploying.com.
- **Rows used.** On-demand prices on Mondays from 2024-08-05 to 2026-10-12:
  - H100: 54 providers, median 31 a week;
  - B200: 28 providers, median 10 a week.
- **Excluded.** Vast.ai, RunPod and Together.
- **Publishing.** Aggregates only.
- **Costs.** No trade is simulated, so no cost assumption applies.
- **Variants.** 6 pre-registered and 9 post-hoc: project total 324.

## 1. Pre-registered tests (Holm over 4)

| Test | n | Estimate | 95% CI | Holm p | Verdict |
|---|---|---|---|---|---|
| R7-01 Provider gaps close (4-week slope < 0) | 111 | −0.023 | [−0.039, −0.011] | 0.003 | **confirmed** |
| R7-02 Breadth of cuts predicts the next 4-week market move | 107 | 0.000 | degenerate | 1.000 | not confirmed |
| R7-03 AR(1) beats a random walk, weekly market move | 87 | n/a | n/a | n/a | too little history to conclude |
| R7-04 B200/H100 ratio mean-reverts (8-week slope < 0) | 50 | −0.577 | [−1.04, −0.19]¹ | 0.002 | **confirmed** |

¹ Paired circular block bootstrap (block 8, 2000 draws, project seed). The
plan did not ask for this interval; it is added because CLAUDE.md requires
an interval for every reported result. It does not change the verdict.

### R7-01: provider gaps close

This is the project's first confirmed hypothesis about GPU prices.

- **History.** Round 1 found it as H01. Round 2 replicated its size on
  unseen days but missed significance (p 0.107). Round 5 did not confirm it
  on the archived list prices (p 0.21). Here it is confirmed on a larger,
  independent dataset: 111 weekly cross-sections across 54 providers.
- **Economic size: slow.** A slope of −0.023 per 4 weeks means about 2% of a
  provider's gap to the market median closes in a month, and about 6% in a
  quarter (13-week slope −0.059). Gaps are large: the median absolute
  premium is 22%, and the 90th percentile is 84%. They are persistent,
  closing over years, not weeks.
- **Robustness (post-hoc, exploratory). Every variant keeps the sign:**

  | Variant | n | Mean slope | NW t |
  |---|---|---|---|
  | As registered | 111 | −0.023 | −3.15 |
  | Premium lagged one week (removes shared measurement noise) | 110 | −0.020 | −2.85 |
  | Without AWS, Google, Azure, Oracle | 111 | −0.040 | −3.12 |
  | Before 2025-10-06 (possibly back-filled weeks) | 61 | −0.014 | −1.70 |
  | From 2025-10-06 | 50 | −0.034 | −2.95 |
  | 13-week horizon | 102 | −0.059 | −3.35 |
  | B200 instead of H100 | 55 | −0.029 | −2.01 |

- **Not ruled out.** A provider's median can shift when its mix of listed
  instance types changes, and mix changes that later reverse look like gap
  closing. Lagging the premium by one week removes noise that shows up in
  both the premium and the outcome, but not a mix change that persists for
  weeks.

### R7-04: the B200/H100 ratio mean-reverts

- **The ratio.** The median of ln(B200/H100) rose from 0.34 to 0.73 over the
  sample: B200 went from about 1.4× to about 2.1× the H100 price.
- **The trend works against a false positive.** In a rising series, a
  reading above the past average tends to be followed by further rises,
  which would give a positive slope. A negative slope is therefore not an
  artefact of the trend.
- **Size.** About 58% of a deviation from the running average is undone
  within 8 weeks.
- **Robustness (post-hoc).** Using only the 6 providers that price both GPUs
  on at least 60% of weeks gives slope −0.547 (t −3.29, p 0.001).
- **Caveat.** The cross-section is small: a median of 8 providers price
  both GPUs in a given week.

### R7-02 and R7-03: the plan's definitions were degenerate

- **The cause.** GetDeploying's per-provider prices are very sticky: only
  8% of provider-weeks move by more than 0.5%. So the median move across
  providers (the outcome in R7-02 and the series in R7-03) is exactly zero
  in almost every week.
- **What it does not mean.** Neither test speaks to the hypothesis. This is
  a design flaw in the plan, found only by running it.
- **What happens next.** They are not redefined and re-run on the same
  data; that would be a new variant chosen after seeing the data. A
  redefinition (for example the provider-equal mean of moves) would need
  its own plan and data not yet used.

## 2. Silicon Data is not in GetDeploying's data

- **Checked.** The download has 116 providers and no Silicon Data series:
  no SDH100RT or SDB200RT values, and no provider named Silicon Data.
- **Consequence.** The data cannot be used to compare our index with Silicon
  Data's, or to test whether the gap between them predicts Silicon Data's
  next move.
- **That test is still claim 1b** (docs/index_gap_plan.md), which needs
  licensed SD history (B7). The most practical route is a Bloomberg
  terminal, which SMU's Sobey MFin workspace has.

## 3. Post-hoc descriptives (exploratory)

### 3.1 Index construction changes the price: basis risk

Four ways of turning the same daily provider rows (2026-07-30 to 10-14)
into one price:

| GPU | Provider median | Offering-weighted median | Provider median without hyperscalers | 20% trimmed mean |
|---|---|---|---|---|
| H100, latest (10-14) | 3.54 | 3.54 | 3.40 | 3.83 |
| H100, 77-day mean | 3.44 | 3.41 | 3.31 | 3.55 |
| B200, latest | 7.95 | 8.30 | 6.25 | 7.13 |
| B200, 77-day mean | 6.52 | 6.33 | 6.10 | 6.68 |

- **The point.** Method alone moves the latest B200 "market price" by a
  third, from USD 6.25 to 8.30. For H100 the spread is about 12%.
- **Silicon Data.** Its published H100 value on 2026-10-05 was 2.81 (public
  page, docs/data_sources.md). That is below every construction above, so
  its method or inputs differ materially from a median of list prices.
- **Implication for GPU1/GPU2.** A list-price model is not "a better
  estimate" of the settlement. It measures something else. What matters for
  trading is how well it predicts the settlement index, which is untestable
  without SD history.

### 3.2 Monthly-average settlement risk (the power-market view)

- **Measure.** The Monday provider median, averaged over each calendar
  month, compared with:
  - the month's first Monday;
  - the previous month's average.
- **Results:**

  | GPU | Months | Average vs first Monday, median | Average vs first Monday, max | Month-on-month SD | Largest month-on-month move | Months with no change |
  |---|---|---|---|---|---|---|
  | H100 | 27 | 0.23% | 3.3% | 1.9% | 6.4% | 19% |
  | B200 | 18 | 0.19% | 30% | 8.3% | 24% | 24% |

- **Reading.**
  - Once an H100 month starts, the monthly average is nearly known. This is
    like a balance-of-month power contract in a calm season.
  - The forward months carry the risk: about 2% a month for H100 and about
    8% for B200, whose distribution has fat tails.
  - Any risk premium (claim 7) should therefore sit mainly in the M1 and M2
    contracts, and in GPU2 more than GPU1.
- **Caveat.** All of this is on list-price medians, not on Silicon Data's
  index.

## 4. What this means for trading (no position implied)

- **R7-04 maps onto an inter-commodity spread.** If Silicon Data's B200/H100
  ratio behaves like the list-price ratio, a GPU2-versus-GPU1 spread that
  strays from its running average would tend to come back. That is like a
  spark spread or a peak/off-peak spread in power.
  - Testing it needs both futures listed and SD history.
  - It would need its own pre-registered plan with costs before any use.
- **R7-01 is real but slow.** It helps forecast an individual provider's
  price. Its effect on a median index is weaker, because cuts by expensive
  providers above the median do not move the median.
