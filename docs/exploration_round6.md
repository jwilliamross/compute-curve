# Round 6 results: trading-relevant tests on archived list prices (one-shot, 2026-10-13)

Plan: docs/exploration_round6_plan.md, committed at 17:20 UTC before any
statistic was computed. The code was committed before it was run. It ran
once. Holm over 3 tests at 5%.

## Plain-language summary

- **No tradable signal.** None of the three ideas passed.
- **R6-01. Does the B200/H100 price ratio snap back?** The estimate leans
  that way. But with only 12 usable months it is indistinguishable from
  chance. This is the spread the GPU1/GPU2 futures trade.
- **R6-02. Do rising GPU rental prices predict compute stocks beating
  tech?** No. The estimate even has the wrong sign: correlation −0.16 over
  24 months.
- **R6-03. Can last month's price change forecast next month's?** No. The
  "no change" forecast (random walk) was more accurate than the AR(1) model.

That last result is useful in its own right. For GPU1's underlying, the
best simple forecast of next month's list price is this month's. It agrees
with round 5's flat trend: model the index as a random walk with no drift.

## Results

| Test | n | Estimate | One-sided p | Holm p | Verdict |
|---|---|---|---|---|---|
| R6-01 B200/H100 ratio mean reversion | 12 | slope −0.246 (SE 0.448), corr −0.18 | 0.298 | 0.893 | not confirmed |
| R6-02 H100 price change → next-month stock excess over XLK | 24 | slope −0.487 (SE 0.589), corr −0.16 | 0.792 | 0.893 | not confirmed |
| R6-03 AR(1) vs random walk, monthly H100 change | 27 | Clark-West 0.38. MSE: AR(1) 0.00136, random walk 0.00128 | 0.351 | 0.893 | not confirmed |

**Stock months.** 2024-10 to 2026-09. Equal-weight claim-4 universe minus
XLK, from cached Alpaca closes; no costs, since no strategy was formed.

## Descriptive (for futures risk, not findings)

| Series | Annualised vol of monthly log changes | Share of provider-months with a price change | Months |
|---|---|---|---|
| Median H100 on-demand list price | 0.290 | 0.17 | 40 |
| Median B200 on-demand list price | 0.288 | 0.20 | 17 |

**List prices are sticky.** A provider changes its list price in about 1
month in 6. Much of the median's movement therefore comes from which
providers and captures are present: a composition effect. The index that
settles GPU1 is built from transaction-level data and may move
differently (unverified; B7).

## Caveats

- **Tiny samples.** Only a correlation above about 0.45 to 0.55 could have
  passed.
- **List prices only.** No discounts or contracts.
- **Capture dates.** Captures are irregular, and month-end prices carry the
  latest capture forward for up to 92 days.
