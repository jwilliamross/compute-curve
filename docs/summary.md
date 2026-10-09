# Summary for a finance reader

_As of 6 October 2026. Simulation only: no real money is involved._

## What this project is

CME has filed futures on GPU rental prices: GPU1 for NVIDIA's H100 chip and
GPU2 for the newer B200. The US regulator extended its review to 9 November
2026, so they are not trading yet. Until they list, this project measures
GPU rental prices itself and tests trading ideas with simulated money.

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
  on GPU computing: GPU cloud providers such as CoreWeave and Nebius, chip
  makers such as NVIDIA, AMD and TSMC, and data-center power and capacity
  firms such as Vistra and Vertiv (full list in `docs/claim4_plan.md`). They
  are compared with XLK, a broad technology fund. The prices come from
  Alpaca, a broker's data service, whose terms bar storing them with the
  project.

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
- **Three checks.** Do index changes line up with the stocks' later
  performance against the technology fund? What happened after large
  moves? Would a forecast refitted each day on past data alone have beaten
  the naive guesses "no difference" and "the average difference so far"?
- **A higher bar for many tests.** Because many tests are run, each one
  must clear a stricter threshold.
- **Costs included.** Trading costs are set conservatively, at about 0.4%
  for a round trip.

## The result of the first test

- **No test passed.** The evidence neither supports nor rejects the idea.
- **The cause is too little data.** With 32 trading days only a very strong
  relationship could show up, much stronger than the ones usually found in
  stock returns. And our index rarely changes: the H100 price moved on only
  5 of the 32 days, so most days add no information.
- **One pattern to watch, not a finding.** Cloud-provider stocks lagged the
  technology fund after B200 prices rose, but the pattern comes from two
  days, one of them a change in which listings were recorded.

## A second test: Amazon's GPU spot prices

- **The data.** A public research archive from the University of
  Wisconsin-Madison records every change in the price of renting spare
  ("spot") GPU capacity on Amazon Web Services. We used its US prices for
  NVIDIA's A100 and H100 chips from October 2024 to September 2026: 402
  trading days, with prices that change almost daily.
- **The test.** The same stocks, the same three checks and the same
  pass-or-fail rules, all written down before any stock return was looked
  at.
- **The result.** No test passed. Amazon's spot price moves did not
  foretell how these stocks did against the technology fund. Here, unlike
  the first test, there was enough data to spot a moderately strong
  relationship, and none appeared. A weak one cannot be ruled out. Nothing
  was added to the daily routine.

## A third piece of work: searching for signals

- **The question.** Can anything in our data forecast GPU rental prices
  themselves? Those prices are what the futures and prediction markets pay
  out on.
- **How the search was kept honest.**
  - Each dataset was split by date. Ideas were tried only on the earlier
    70%, and anything promising had one chance on the later 30%.
  - Twelve ideas were written down, with their tests, before any data was
    looked at.
  - The bar was raised for running twelve at once.
- **Our own index.** Nothing usable yet. It has only 80 days of history,
  and list prices rarely change. The five biggest cloud providers changed
  their H100 price on one day in 56. One idea is worth re-testing in about
  six months: providers priced above the market tend to cut.
- **Amazon's spot prices.** Price moves tended to continue for a week in
  2024–25. They continued in the later period too, but more weakly, so a
  forecast built on the earlier strength did worse than guessing "no
  change". It was not adopted.
- **One candidate.** An independent index that is updated every 15 minutes
  (the Computable GPU Index) tends to give back about a third of any
  6-hour move. This held in the test period.
  - It is probably a quirk of how that index is measured, not a market
    effect.
  - No contract trades on that index.
  - It is now being watched for 60 trading days, to 31 December 2026,
    without any trades. Only if it holds up then is it judged against
    the project's usual rules.
- **Stocks.** The one new stock idea, and a check of whether stock moves
  foretell Amazon's prices, found nothing.

The details are in `docs/exploration_plan.md` (the rules) and
`docs/exploration_round1.md` (the results).

## A second search round (9 October 2026)

- **Our own index.** The one promising pattern was re-checked on days it had
  never been tested on: providers priced above the market tend to cut, and
  those below to raise.
  - It came out the same size as before.
  - With only 19 days it is not yet strong enough to count.
  - It is worth re-checking in a few months.
- **Two new leads, not findings.**
  - The B200 version of the independent 15-minute index also gives back
    about a third of each 6-hour move.
  - Amazon's spot price moves tend to continue for a week. The forecast is
    re-estimated every day, which fixes the reason the first attempt failed.
  - Each gets one test on data that does not exist yet: the index through
    31 December, and Amazon's October to December prices once published.
- **No trades.** Nothing trades. No contract settles on these prices yet.

## What happens now

- **Daily, automatically.** After each US market close the system collects
  prices, updates the index, re-runs the tests and records what the model
  would have predicted. This is called "shadow mode".
- **No orders yet.** Orders are placed only if the pre-agreed rules pass,
  which needs at least six more months of data. Even then they go only to
  Alpaca's simulated paper account, within strict limits: USD 10,000 per
  stock, USD 20,000 in total, a USD 1,000 daily loss limit, and a USD 3,000
  maximum drawdown that closes everything and leaves an emergency stop on.
- **When an answer is possible.** For our own index, a modest relationship
  would take roughly one to six years of daily data to detect. If nothing
  has passed by August 2027 the idea is reported as not supported, and by
  August 2028 it is rejected. The Amazon test is repeated once about a year
  of new data exists.

All cost and size figures are assumptions, not measurements. The details
are in `docs/claim4_plan.md` (the rules) and `docs/claim4_results.md` (the
results); for the Amazon test, `docs/claim5_plan.md` and
`docs/claim5_results.md`.
