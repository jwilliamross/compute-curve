# Claim 11: do AI-economy signals lead GPU rental prices? (plan)

_Written 2026-10-18, before any predictor below was joined to a GPU price. Research only:
no trade, no order. Owner request: "the macro AI and tech landscape … maybe there's an
indicator there that indicates when GPU prices are going to go up."_

## 1. The economics: what a GPU-hour is a complement or substitute for

**Derived demand.** Nobody wants GPU-hours for their own sake. Demand for them
derives from demand for AI training and inference, which in turn derives from
demand for AI products. So GPU-hours are:

- **Complements in production** with what else is needed to turn a GPU into
  useful compute:
  - electricity and data-centre space (power, cooling);
  - networking and HBM memory;
  - models, software and engineers.

  A shortage of any complement caps how many GPUs can run. It raises the rent on
  the GPUs that can run, and lowers demand for the ones that can't.
- **Complements in consumption** with AI applications. More AI usage (tokens
  served) means more inference GPU-hours.
- **Substitutes** for four things:
  1. **Buying a GPU instead of renting.** Rent is tied to the purchase price
     through the user cost of capital (below).
  2. **Newer generations.** B200 substitutes for H100: a launch lowers the older
     chip's rent (docs/hardware_launches.md).
  3. **Other accelerators,** such as TPU, Trainium and AMD MI-series.
  4. **Buying tokens from an API provider instead of running a model.**

**The user cost of capital** (Jorgenson 1963, *AER* 53(2)). In competitive
rental markets:

    rent per hour ≈ [ P_gpu · (r + δ − g) + power + opex ] / (8,760 · u)

- `P_gpu`: the purchase price.
- `r`: the financing rate.
- `δ`: economic depreciation, which is high when a new generation is coming.
- `g`: the expected change in the GPU's price.
- `u`: utilization.

**What would move rent:**

- **Up:** higher GPU prices, higher rates, faster expected obsolescence,
  power-price shocks, demand shocks that raise u.
- **Down:** the opposite of each, and new supply.

**Power is a small cost share.** All inputs here are ASSUMPTIONS, not findings.

- An H100 SXM draws about 700 W; with a PUE of 1.3 that is about 0.9 kWh per
  GPU-hour.
- At USD 0.08/kWh this is about USD 0.07 per GPU-hour, about 3% of a USD 2.80
  rent.
- **So power matters through availability,** whether new capacity can be
  switched on, much more than through its price.

**Why asset prices might lead rents.**

- Stock prices of chipmakers, neoclouds and hyperscalers are forward-looking.
  They move on news (earnings, capex guidance, model launches) the day it
  arrives.
- Rental list prices are sticky: only 8% of provider-weeks move (round 7).
- **If both respond to the same demand news,** equities move first and list
  prices follow. That is the testable claim.

**Why they might not.**

- Equities price long-run profits, mostly from chip sales and multi-year
  contracts. Spot on-demand rents are a small, noisy corner of the market.
- Earlier work found the reverse link (GPU prices → stocks) absent (claims 4
  and 5).

## 2. Data (fixed now)

**Target: GetDeploying API per-provider H100 on-demand history** (D60), exactly
the round-7 panel (`explore.round7.weekly_panel`).

- Mondays from the first with at least 8 providers to **2026-10-12**.
- `y(t)` is the provider-equal **mean** of `p(i, t+4) − p(i, t)` over providers
  priced at both t and t+4, with at least 8 of them. This is the 4-week log
  change.
- Round 7 found the cross-provider *median* of moves degenerate (almost always
  0) and named the provider-equal mean as the fix. That fix needs its own plan,
  and this is it.
- **Known before this plan:** the H100 level path, which was flat to slightly
  up over two years (+3%/yr). No predictor has been joined to it.

**Predictors.**

- Alpaca daily SIP closes (D29; cached under `var/`), from 2024-06-03. The
  baskets are equal-weighted; each name enters on its first trading day.
  - **AI hardware:** `[claim4.universe] gpu_semis`.
  - **Neoclouds:** `[claim4.universe] neocloud`.
  - **Hyperscalers:** MSFT, GOOGL, AMZN, META, ORCL.
  - **Power and capacity:** `[claim4.universe] power_capacity`.
  - **Market:** SPY.
- The 2-year Treasury yield, DGS2 (FRED; US government data, public domain).

**Timing (no look-ahead).** `x(t)` uses closes up to and including the last
session on or before the Friday before Monday t. GPU snapshots dated t count as
observed at 00:00 UTC on t+1 (round 7), so every predictor is at least three days
older than the price it predicts.

## 3. Tests (one shot, Holm over five, α = 0.05, one-sided)

For each test: OLS of `y(t)` on `x(t)`, with a Newey–West HAC slope test at lag 6
(the overlap is 4 weeks). The signs are fixed now, from the economics in §1.

| ID | x(t) | Sign | Story |
|---|---|---|---|
| MD-1 | AI-hardware basket's 20-session log return minus SPY's | + | Chip-demand news reaches rents later |
| MD-2 | Neocloud basket's 20-session log return minus SPY's | + | The market prices GPU-rental economics first |
| MD-3 | Hyperscaler basket's 20-session log return minus SPY's | + | Demand-side news (capex, AI usage) |
| MD-4 | 20-session change in DGS2 (percentage points) | + | User cost of capital: higher r means higher rent |
| MD-5 | Power and capacity basket's 20-session log return minus SPY's | + | Power-complement scarcity raises the rent on running GPUs |

**Reported for each:**

- the slope;
- a circular block bootstrap 95% CI (block 8, 2,000 draws, project seed);
- the HAC p and the Holm p;
- n.

**Power, stated now.**

- About 105 overlapping weeks, about 26 independent 4-week blocks.
- After Holm (α/5 one-sided), only correlations of about 0.45 or more are
  reliably detectable.
- A null result therefore means "no large effect", not "no effect".

## 4. Descriptive (exploratory, not tests)

1. **Lead–lag correlogram.** The correlation of the weekly provider-mean H100
   change with each basket's weekly excess return, at leads and lags of −8 to
   +8 weeks. This shows which way any link runs.
2. **Granger causality,** both directions, MD-1's basket against the weekly
   H100 change, at lag 4 (statsmodels). This is predictive "cause" only, not
   structural causation.
3. **Event windows.** The H100 4-week change after each NVIDIA earnings date in
   the window, against all other weeks. There are about 9 events, too few for a
   test. Dates are verified against NVIDIA's investor-relations releases before
   use; unverified dates are dropped.
4. **B200** (fewer weeks): MD-1 to MD-5 repeated, descriptive only.

## 5. What a result would mean, fixed now

- **A confirmed test (Holm p ≤ 0.05)** becomes a pre-registered **shadow** input
  for GPU1, rule FP-M:
  - written in its own plan before GPU1 lists;
  - judged forward only.
- **It is not a trading result.** List prices are not Silicon Data's
  transaction index, so basis risk applies (strategy book §5).
- **No confirmed test:** the conclusion is "at a 4-week horizon, AI-economy asset
  prices do not detectably lead list rents". No variant is re-run on this data.

## 6. Variants

- **Declared tests: 5** (MD-1 to MD-5).
- **Descriptive measures: 4** (§4).
- **Total added: 9.**
