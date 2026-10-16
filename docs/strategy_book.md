# Strategy book: GPU1/GPU2 compute futures (and what trades today)

_As of 2026-10-16. Research and simulation only: no real money, no orders._

## The honest headline

- **No strategy on GPU1 or GPU2 can be proven profitable yet.** The
  contracts are not listed (the CFTC review runs to about 2026-11-09), so no
  futures price exists to test against.
- **What exists is a launch-ready book.** Seven pre-registered rules, each
  written down with its costs and pass/fail test before any futures data
  exists, are coded and run every night in shadow mode. On listing day they
  start logging decisions with no room for hindsight tuning.
- **One strategy has passed a held-out test, but it is on stocks.** SA2-M,
  stock statistical arbitrage on compute-linked names, is in a live forward
  test.

## 1. What we know about the underlying

These results come from 2 years of per-provider data (54 providers), round 7
and the archives.

| Fact | Evidence | Why it matters for trading |
|---|---|---|
| Rental prices are a sticky random walk | Only 8% of provider-weeks move; AR(1) loses to a random walk (R6-03) | Fair value of a future month ≈ today's index; no momentum to ride |
| Expensive providers slowly cut toward the market | R7-01 confirmed (Holm p 0.003); about 6% of a gap closes per quarter | Helps predict an average-type index; too slow to trade alone |
| B200/H100 ratio mean-reverts | R7-04 confirmed (p 0.002); about 58% of a deviation undone in 8 weeks | Basis for the GPU2/GPU1 spread (SP) |
| ...but the ratio trended up all year (1.4× to 2.1×) | Proxy backtest of the spread rule: loses in-sample | The spread trade can lose to the trend; costs are large |
| List prices did not fall over 2 years | H100 +3%/yr (CI −1% to +6%), B200 +13%/yr, H200 +25%/yr | If futures price declines, longs earn a premium (FP-D) |
| The market prices declines | Silicon Data's forward curve is reported in backwardation | The opportunity behind FP-D |
| Index method moves the price by up to a third | Same data: B200 USD 6.25 to 8.30 depending on construction | Basis risk: only Silicon Data's number pays |
| List prices don't track a transaction index week to week | Ornn's weekly values (from Kalshi settlements) against list-price indices: correlations of about 0 | Nowcasting the settlement index from list prices won't work; use futures-only rules or licensed SD data |
| Once a month has started, H100's monthly average is nearly known | Average within 0.23% of its first Monday (median) | Balance-of-month mispricing is cheap to exploit and to test (FP-C) |

## 2. The GPU1/GPU2 book (all pre-registered, all shadow, all nightly)

| Rule | Bet | Power analogue | Needs | Trades to confirm, if the edge is real |
|---|---|---|---|---|
| **FP-C** balance of month | Mid-month, trade the current month when the futures price is far from the locked-in average plus today's level | Balance-of-month trade | SD daily index (licensed) + CME prices | About 9 if mispricing is about 4% (fastest to confirm) |
| **FP-D** long the backwardation | Buy the contract 3 months out when it is more than 5% below spot | Normal backwardation / hedging pressure | CME prices (FP-D-F); SD index for FP-D-I | About 17 trades at a 10% premium; about 180 at 5% |
| **FP-A** outright premium | Sell or buy next month when it is more than 5% away from the index | Forward premium | SD index + CME prices | About 80 at a 5% gap |
| **FP-B** calendar | Month after next vs next month when the curve slopes more than 3% | Calendar spread | CME prices only | Depends on curve noise |
| **SP-I / SP-F** GPU2 vs GPU1 | Bet the B200/H100 ratio reverts | Spark spread / inter-commodity spread | CME prices (SP-F); SD index (SP-I) | Unknown; the proxy warns it can lose |
| **FP-K** cross-venue | Sell or buy GPU1 next month when it is more than 8% away from Kalshi's implied H100 monthly average (Ornn index, about equal to SD's level) | The same product on two exchanges | CME prices + nightly Kalshi curve log | Depends on basis; a forecast gate comes first |
| **SP-0** forward check | Our own index's B200/H100 ratio must revert as R7-04 says | – | Nothing (running) | Evaluates 2027-07 |

- **Costs everywhere:**
  - 5-tick half-spread plus 2 ticks of slippage on a USD 0.01 tick;
  - plus exchange, broker and cash-settlement fees: about USD 60 per
    contract per leg, about 2.8% of an H100 contract's value;
  - stress-tested at 2×.
- **How each is judged:** one-shot evaluation, Newey-West standard errors,
  Holm where variants compete.

### Day-one checklist (owner actions)

1. **Download CME settlements** for GPU1 and GPU2 each day into
   `data/manual/cme_settlements/`. Format:
   `data/manual/cme_settlements/README.md`.
2. **Get Silicon Data history,** SDH100RT and SDB200RT, through SMU's
   Bloomberg or LSEG access. Drop it into
   `data/manual/published_index/`. This unlocks FP-A, FP-C, FP-D-I, SP-I
   and claim 1b.
3. **Read the nightly reports:**
   - `reports/fair_value/sheet.md` (fair value per contract month);
   - `reports/futures_premium/`;
   - `reports/carry/`;
   - `reports/spread/`.

## 3. What trades today

| Strategy | Instrument | Status | Evidence |
|---|---|---|---|
| **SA2-M** residual reversal | 20 compute-linked US stocks against XLK | Live forward test (7/60 sessions; 250-session extension) | Held-out: 10.6 bps a day net, Sharpe 1.80, Holm p 0.023; fragile (5 days carry it); failed on large-cap tech |
| **MX1–MX4** modern overlays and models | Same 20 stocks against XLK | Tested 2026-10-16: none confirmed; nightly descriptive shadow (`reports/statarb/lab/`) | Vol management, volume conditioning, PCA factors and a ridge forecast all failed to beat plain SA2-M (docs/modern_results.md) |
| **KB-1** favourite-longshot | Kalshi GPU price binaries (Ornn indices) | Forward test (needs 30 close dates, about Q1 2027) | Retrospective: too little history; market looks under-confident (logit slope 1.57, SE 0.30). Kalshi serves US persons only |

## 4. Why this is a GPU1/GPU2 strategy and not a stock strategy

**GPU-hours, like megawatt-hours, cannot be stored.** Nothing ties the
futures price to today's price, so futures can sit away from the expected
average: a risk premium paid by hedgers.

- **The candidate edges are:**
  1. the premium itself (FP-A, FP-D);
  2. mispricing of the part of the month already averaged (FP-C);
  3. relative value between the two contracts (SP).
- **The constraint is basis.** Only Silicon Data's index pays. Getting its
  history is the most valuable next step.

## 5. Risks that could sink every rule

- **Liquidity.** A new contract may be too thin. The 5-tick assumption may
  be optimistic or pessimistic.
- **Basis.** List prices are not Silicon Data's transaction-based index.
  Silicon Data's H100 was 2.81 against list medians of about 3.5.
- **Regime.** H100 prices fell hard in 2023–24. The flat 2024–26 drift may
  not last.
- **Small samples.** Monthly decisions give about 24 trades a year across
  both products.
