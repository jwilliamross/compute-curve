# Summary for a finance reader

_As of 6 October 2026. Simulation only: no real money is involved._

## What this project is

CME has filed futures on GPU rental prices: GPU1 for NVIDIA's H100 chip and
GPU2 for the newer B200. They are not trading yet, because the US regulator
extended its review to 9 November 2026. Until they list, this project builds
its own measure of GPU rental prices and tests trading ideas with simulated
money only.

## The dataset

- **Rental prices.** Every day we record the advertised hourly price of
  renting an H100 or B200 from about 20 to 40 cloud providers. These come
  from public price lists and open datasets whose terms allow it.
- **Our own index.** Each day we take the typical (median) price, counting
  each provider once. On 5 October 2026 it stood at USD 3.21 per GPU-hour
  for H100 and USD 7.04 for B200. Alongside it we track how far apart
  providers' prices are and how many listings are offered.
- **History.** A consistent series exists only from 18 August 2026. That is
  32 trading days so far.
- **Stocks.** Daily prices for 21 US-listed companies whose business depends
  on GPU computing:
  - GPU cloud providers: CoreWeave, Nebius, IREN, WhiteFiber;
  - chip makers: NVIDIA, AMD, Broadcom, TSMC, Micron, Marvell, Super Micro,
    Cerebras;
  - data-center power and capacity: Vistra, Constellation, Talen, Vertiv,
    Bloom Energy, Applied Digital, Core Scientific, Cipher, TeraWulf.

  Each is compared with XLK, a broad technology fund. The prices come from
  Alpaca, a broker's data service. Its terms bar redistribution, so they
  are not stored with the project.

## The question

When GPU rental prices change, do these stocks then do better or worse
than the technology sector over the next 1, 5 or 20 trading days? If they
do, our index could become a trading signal.

## How it was tested

- **Rules written first.** The companies, signals, tests, cost assumptions
  and pass-or-fail rules were committed before we looked at any stock
  returns. That stops the test from being tuned until it "works".
- **No hindsight.** A price change counts only from the time our system
  would actually have seen it. Trades are assumed at the next day's opening
  price.
- **Three checks.**
  1. Do index changes line up with the stocks' later performance against
     the technology fund?
  2. What happened after large index moves?
  3. Would a simple forecast, refitted each day using only past data, have
     beaten two naive guesses: "no difference" and "the average difference
     so far"?
- **A higher bar for many tests.** Because many tests are run, each one
  must clear a stricter threshold.
- **Costs included.** Trading costs are set conservatively, at about 0.4%
  for a round trip.

## The result so far

- **No test passed.** The evidence neither supports nor rejects the idea.
- **The cause is too little data.** With 32 trading days only a very strong
  relationship could show up, much stronger than the ones usually found in
  stock returns. And our index rarely changes: the H100 price moved on only
  5 of the 32 days, so most days add no information.
- **One pattern to watch, not a finding.** Cloud-provider stocks did worse
  than the technology fund after B200 prices rose. The whole pattern comes
  from two days, and one of them reflects a change in which listings were
  recorded rather than in prices.
- **Costs set a high bar.** At about 0.4% a round trip, a useful signal
  would have to predict daily moves of at least that size.

## What happens now

- **Daily, automatically.** After each US market close the system collects
  prices, updates the index, re-runs the tests and records what the model
  would have predicted. This is called "shadow mode".
- **No orders yet.** Orders are placed only if the pre-agreed rules pass,
  which needs at least six more months of data. Even then they go only to
  Alpaca's simulated paper account, within strict limits:
  - USD 10,000 per stock and USD 20,000 in total;
  - a USD 1,000 daily loss limit;
  - a USD 3,000 maximum drawdown, after which everything is closed and an
    emergency stop stays on.
- **When an answer is possible.** A modest relationship would take roughly
  one to six years of daily data to detect reliably. If nothing has passed
  by August 2027, the idea is reported as not supported. If nothing has
  passed by August 2028, it is rejected.

All cost and size figures are assumptions, not measurements. The details
are in `docs/claim4_plan.md` (the rules) and `docs/claim4_results.md` (the
results).
