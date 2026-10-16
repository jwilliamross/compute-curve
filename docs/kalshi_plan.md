# Claim 9 plan: GPU price binaries on Kalshi (favourite-longshot test)

Pre-registered 2026-10-16, before any Kalshi price, candle or outcome was read.

What had been looked at by then:

- series metadata;
- the field names of the market list and candle responses;
- the structural fields (ticker, strike, open, close, rules) of three
  markets.

Research and simulation only; no account, no orders. Kalshi serves US
persons, and the owner is in Canada.

## 1. Data

- **Source.** Kalshi's public market-data API (no key),
  `https://api.elections.kalshi.com/trade-api/v2`. Requests are at least
  2.5 s apart, with backoff on HTTP 429.
- **Series.**
  - Weekly "price at 4 PM ET on date": KXH100WS, KXB200WS, KXH200WS,
    KXA100WS.
  - Monthly average: KXH100MS, KXB200MS, KXH200MS, KXA100MS.
  - All settle on Ornn's compute price indices, not Silicon Data's. The
    monthly-average series are the closest traded analogue of GPU1/GPU2,
    which settle on a monthly average.
  - Test series (names containing TEST) are excluded.
- **Storage.** Raw responses go to git-ignored `var/kalshi/`. Kalshi's terms
  on redistributing data have not been reviewed, so the conservative choice
  is D62. Reports carry derived numbers only.

## 2. Decision point and prices

- **Universe.** Every market with `status = finalized` and `result` in
  {yes, no}.
- **Decision candle.** The last daily candle with
  `end_period_ts ≤ close_time − 48 h`.
- **Prices.** `yes_bid.close` and `yes_ask.close` of that candle. Skip the
  market if either is missing or if not `0 < bid ≤ ask < 1`.
- **Fee per contract.** Kalshi's taker formula, rounded up to the cent:
  `ceil_cent(0.07 · P · (1 − P))`, where P is the price paid.
  - Stress: 2× fee plus 1 cent of slippage.

## 3. KB-1: favourite-longshot rule (fixed)

- **Longshot.** If 0.03 ≤ yes_bid ≤ 0.20, buy NO at `1 − yes_bid`. It pays
  1 if the result is no.
- **Favourite.** If 0.80 ≤ yes_ask ≤ 0.97, buy YES at `yes_ask`. It pays 1
  if the result is yes.
- **Size.** One contract per qualifying market. Profit per trade is
  `payoff − price − fee`.
- **Unit of inference: close date.**
  - Every strike of an event settles on the same index value, and different
    GPUs on the same date are related.
  - So P&L is summed per close date, and the test runs on the date series in
    time order.
- **Test.**
  - Mean date-level P&L > 0: one-sided, Newey-West lag 1, α = 0.05.
  - The mean must also stay > 0 under the stress costs.
  - 95% circular block bootstrap CI over dates (block 2, 2000 draws, project
    seed).

### KB-1R: retrospective (runs once now)

- **Sample.** All qualifying markets with close_time ≤ 2026-10-16 23:59 UTC.
- **Minimum.** Fewer than 10 close dates with trades reads "too little
  history to conclude".
- **Status.** A first look, reported whatever it shows. It does not confirm
  the strategy.

### KB-1F: forward confirmation

- **Sample.** Markets whose decision candle ends after 2026-10-17 00:00 UTC.
  Collected by a step that runs after each daily cycle.
- **Trigger.** Runs once when 30 close dates with trades have settled, or on
  2027-04-01, whichever comes first.
- **Verdict.** The strategy counts as **confirmed** only if KB-1F passes.

## 4. KB-2: calibration (descriptive)

- **Reliability table.** Market mid `(bid + ask)/2` at the decision candle,
  in buckets of 0.1, against the realised YES frequency.
- **Scores.**
  - Brier score of the mid, against a 0.5 baseline.
  - The slope of a logistic regression of the outcome on logit(mid). A slope
    above 1 means the market is under-confident, which is what a
    favourite-longshot bias shows.
- **Monthly-average series.** For each settled month, the implied median
  (the strike where the YES price crosses 0.5) at the decision candle,
  against the settled value.

## 5. Why it might work

- **The bias is well documented.** Long shots tend to be overpriced and
  favourites underpriced in betting and prediction markets (Snowberg &
  Wolfers 2010, *Journal of Political Economy*; Thaler & Ziemba 1988).
- **Fees are small at the extremes.** The quadratic fee is about 0.6 cents
  per contract at P = 0.1.
- **Index stickiness.** GPU rental indices are sticky (rounds 5–7). A strike
  far from the current level two days before close rarely gets crossed.
  Retail traders may overpay for that.

## 6. Variants

KB-1R, KB-1F and KB-2: 3. Project total 333.
