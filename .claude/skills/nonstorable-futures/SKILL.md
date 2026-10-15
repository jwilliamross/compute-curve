---
name: nonstorable-futures
description: "Price, analyse and test futures on non-storable commodities (electricity, GPU-hours) that settle on a monthly average of a daily index. Use when working on GPU1/GPU2, forward risk premia, balance-of-month fair value, average-price (Asian) settlement, inter-commodity spreads such as GPU2 vs GPU1 (spark-spread analogues), or basis risk between our index and the settlement index. Also trigger on 'power trading', 'megawatt-hour', 'forward premium', 'balance of month', 'delivery period', 'spark spread', 'non-storable'."
---

# Non-storable futures (power-market methods for GPU1/GPU2)

> **compute-curve note.** Written for this repository (D61). CLAUDE.md wins on
> any conflict. The citations below are the standard references. Any number
> that applies them to GPU data must come from this repo's own tested code,
> labelled as in CLAUDE.md.

## 1. Why storage changes everything

- **Storable commodities** (oil, gold, grain) are priced by cost of carry:
  `F = S·e^{(r+u−y)t}`. Arbitrage ties the futures price to today's spot:
  buy now, store, deliver later.
- **Non-storable commodities** have no such link. A megawatt-hour, or a
  GPU-hour, that is not used now is gone, so no "buy now, deliver later"
  trade exists.
- **Consequence.** The futures price is the market's risk-adjusted
  expectation of the delivery-period price, and nothing more:

  `F(t, T1, T2) = E_Q[ (1/N) Σ_{d∈[T1,T2]} S_d | F_t ]`

- **Forward (risk) premium:**

  `π = F − E_P[ (1/N) Σ S_d ]`

  It is the gap between the risk-neutral (Q) and real-world (P)
  expectations. It can be positive or negative, and it changes over time.
- **Electricity evidence:**
  - Bessembinder & Lemmon (2002, *Journal of Finance* 57(3)) derive a premium
    that falls with the variance of spot prices and rises with their
    skewness. Producers and retailers hedge opposite risks; when demand
    spikes are likely, buyers pay up for insurance.
  - Longstaff & Wang (2004, *Journal of Finance* 59(4)) find significant
    forward premia in PJM day-ahead versus real-time prices.

## 2. Price dynamics: mean reversion plus a slow level

- **Model.** Schwartz & Smith (2000, *Management Science* 46(7)): the log
  price is the sum of
  - a short-term deviation χ (Ornstein-Uhlenbeck, mean-reverting) and
  - a long-term level ξ (Brownian motion with drift).
- **Power application.** Lucia & Schwartz (2002, *Review of Derivatives
  Research* 5) fit one- and two-factor versions to Nord Pool and add a
  deterministic seasonal term.
- **In this repo:**
  - `compute_curve.models` (Schwartz-Smith Kalman);
  - `compute-curve fairvalue` (Monte Carlo, D55, docs/montecarlo_fair_value.md).
- **What the repo has found so far (rounds 5–7):**
  - GPU list prices behave close to a driftless random walk in level.
  - They are extremely sticky: few provider-weeks change at all.
  - So the short-term factor is mostly measurement noise, not
    weather-driven spikes as in power.

## 3. Average-price settlement and balance-of-month (BOM)

GPU1 and GPU2 settle on the **monthly average** of a daily index, like most
power swaps and futures.

- **BOM fair value.** On day k of an N-day month, with realised average
  A_k:

  `F_BOM = (k/N)·A_k + ((N−k)/N)·E[average of the remaining days]`

  The realised part is locked in. Only the remainder carries risk, so the
  contract's volatility falls towards zero as the month runs out.
- **Average-price (Asian) options.** Kemna & Vorst (1990) price the
  geometric average in closed form and use it as a control variate for the
  arithmetic one. `compute-curve fairvalue` uses this.
- **Delivery-period contracts.** Benth, Šaltytė Benth & Koekebakker (2008),
  *Stochastic Modelling of Electricity and Related Markets*, derive swap and
  forward dynamics for contracts that deliver over a period.
- **In this repo.**
  - docs/exploration_round7.md section 3.2 measures how far a monthly
    average strays from its first Monday:
    - H100: median 0.23%;
    - B200: up to 30%.
  - Risk sits in the M1 and M2 contracts, and in GPU2 more than GPU1.

## 4. Spreads between related contracts

- **Spark spread.** Power price minus heat rate × gas price: the margin of a
  gas plant. Deng, Johnson & Sogomonian (2001, *Decision Support Systems*
  30) value generation assets as spark-spread options.
- **Analogues here:**
  - **GPU2 vs GPU1 (B200 vs H100).** An inter-commodity spread. Round 7
    (R7-04) confirmed that the B200/H100 list-price ratio mean-reverts over
    8 weeks. That was measured on list prices, not on the settlement indices.
  - **M2 vs M1 (calendar spread).** Claim 7, FP-B
    (docs/futures_premium_plan.md).
  - **Our index vs Silicon Data's (location/basis spread).** Claim 1b
    (docs/index_gap_plan.md).

## 5. Basis risk

- **The problem.** A hedge or a model priced on one index while the
  contract settles on another carries basis risk. In power this is the
  difference between locations (nodes) or between day-ahead and real-time
  prices.
- **Here.**
  - Index method alone moves the latest B200 "market price" from USD 6.25 to
    8.30 (round 7, section 3.1).
  - Silicon Data's H100 (2.81 on 2026-10-05) sat below every list-price
    construction.
- **What follows.** A "better" fair value earns nothing unless it predicts
  the **settlement index**. Every GPU1/GPU2 trading claim must be tested
  against SD history (B7), not against our own index.

## 6. Testing premia honestly

- **One observation per contract month.** Overlapping horizons need
  Newey-West or block-bootstrap errors.
- **Short samples are the norm.** Power studies use years of hourly data;
  GPU1/GPU2 start with none.
  - Pre-register the rule (FP-A and FP-B are already pre-registered).
  - Set a minimum number of settled trades.
  - Say "too little history to conclude" until it is met.
- **Report the premium both ways:**
  - ex ante: the futures price against the model expectation;
  - ex post: the futures price against the realised settlement.
- **Costs.** Apply per leg with the contract specs in `config/default.toml`;
  stress at 2× costs.
- **Look-ahead.** A settlement price is usable only after its publication
  time (`ts_available`).

## 7. Quick map to code

| Concept | Where |
|---|---|
| Two-factor model, Monte Carlo fair value, Asian control variate | `compute_curve/fairvalue.py`, `compute_curve/models/schwartz_smith.py`, `compute_curve/models/montecarlo.py`, D55 |
| Forward premium rules (outright, calendar), shadow log | `compute_curve/futures_premium.py`, claim 7 |
| Basis: our index vs SD | `compute_curve/index/gap.py`, claim 1b |
| Index-construction basis and BOM settlement risk | `compute_curve/explore/round7_posthoc.py` |
| Contract months, settlement averaging | `compute_curve/contracts.py` |
