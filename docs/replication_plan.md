# Claim 12: two out-of-sample replications that decide the final candidate (plan)

_Written 2026-10-18, before any of the data below was fetched or joined. Research and
simulation only: no orders. Owner request: "keep gathering data and testing
hypothesis. Get back to me when u have a final candidate."_

## 1. Why these two

The two live leads both carry the same doubt: is the effect real, or a regime?

| Lead | Evidence so far | The doubt |
|---|---|---|
| **SA2-M** stock residual reversal (paper trading, D63) | Held-out 2026 pass: 10.6 bps/day, Holm p 0.023 | The edge is concentrated in 2026. It failed on large-cap tech (claim 6d). |
| **MD-4** rates lead GPU rents (claim 11) | Holm p 0.035 on GetDeploying list prices | Almost all of it is in the last year. One dataset only. |

Each test below uses data this project has never fetched or joined for that
question, so its outcome is unknown today.

## 2. R12-A: frozen SA2-M out of time, 2019–2024

**Data.**

- Alpaca daily SIP bars (adjustment "all", D29; cached under `var/`), from
  2018-06-01 so the first window has history.
- Universe: the claim-4 members plus XLK.
- **Test window: 2019-01-02 to 2024-08-30.** That is every session before the
  existing data began (2024-09-03). None of these sessions has been used.

**Eligibility.** A name enters only after `[statarb] min_history` sessions of its
own bars, and only from the dates below. These are its listing under the current
business, per public listing records. They are ASSUMPTIONS, not verified here;
where a date is wrong, the cost is fewer sessions, never look-ahead.

| Name | Used from |
|---|---|
| VRT | 2020-02-07 |
| IREN | 2021-11-17 |
| CIFR | 2021-08-30 |
| WULF | 2021-12-14 |
| CEG | 2022-02-02 |
| APLD | 2022-04-13 |
| CORZ | 2024-01-24 (after its Chapter 11 exit) |
| TLN | 2024-07-10 |
| NBIS | not used (2024-10-21; Yandex before) |
| CRWV, WYFI | not listed in the window |

All other names are used whenever bars exist.

**Strategy.** Exactly the frozen SA2-M: the 12 pooled cells, the `[statarb]`
parameters, and `pipeline.confirm_strategy`, run under both accountings
(weights and shares, D56).

**Costs** (ASSUMPTIONS):

- The claim-6c quoted-spread costs per symbol (2024–26 medians).
- Spreads were probably wider in 2019–22, so the **stress case (costs ×2,
  borrow at 10% a year) must also be positive**.

**Pass (fixed now).** Under both accountings, all three of:

- C1: one-sided Newey–West p ≤ 0.05 for a mean > 0 (lag 10);
- C2: stress-case mean > 0;
- the 95% block-bootstrap CI of the mean must not be entirely below 0.

**Known biases, stated now.**

- **Survivorship and selection.** The universe was chosen in 2026 because these
  are AI-infrastructure names today. For a market-neutral reversal strategy this
  bias is smaller than for momentum, but it is not zero.
- **Composition.** The 2019–2021 universe is mostly semiconductors and power
  utilities: few names, and a different industry mix.

**Reporting.**

- the full-window result;
- each calendar year, descriptive only;
- the number of names eligible each year.

## 3. R12-B: the rates effect on AWS spot GPU prices

**Data.**

- **GPU prices:** the claim-5 AWS spot archive, `var/aws_spot/pool_daily.parquet`
  (Zenodo, CC BY 4.0).
  - H100 is the primary class, from 2024-10-01 to 2026-09-30.
  - A100 is the secondary class.
- **Rates:** FRED DGS2 (`var/fred/DGS2.csv`), as in claim 11.

These prices come from a different market (AWS spot auctions), not providers'
list prices. They have never been joined to rates.

**Panel.**

- Each pool (availability zone × instance type) is valued on each Monday at its
  last observation in the 7 days up to and including that Monday.
- `y(t)` is the pool-equal mean of the 4-week log change, over pools valued at
  both t and t+4, with at least 5 pools.

**Predictor.** `x(t)` is exactly MD-4: the 20-session change in DGS2 at the last
session on or before the Friday before Monday t.

**Test.**

- OLS slope of y on x, with a one-sided (+) Newey–West test at lag 6.
- Holm over the two classes, α = 0.05.
- Slopes reported with block-bootstrap 95% CIs (block 8).

**Pass.** H100's Holm p ≤ 0.05 with a positive slope. A100 is secondary: it is
reported, and enters Holm.

## 4. How the final candidate is chosen (fixed now)

**If R12-A passes:**

- SA2-M is the final candidate.
- It is confirmed in two eras and keeps paper trading.
- The 60- and 250-session forward tests still run.

**If R12-A fails:**

- SA2-M is downgraded to "regime bet".
- The paper account keeps its kill switches, and no size increase is ever
  considered.
- The final candidate is then the best remaining pre-registered rule.
  - For GPU1/GPU2, FP-C (balance of month) is the default candidate. It is
    low-risk by construction, but it can't be tested before listing.
  - If R12-B also passes, FP-M joins it as a filter.

**R12-B passing or failing** decides only whether FP-M is kept as a filter
(MD-4F still runs forward).

## 5. Variants

- R12-A: 1 (two accountings, as in D56).
- R12-B: 2 (H100 and A100).
- Per-year descriptives: 1.
- **Total added: 4.**
