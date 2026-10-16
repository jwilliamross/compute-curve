# Status

_Last updated: 2026-10-14, GetDeploying API first download. Branch
`claude/compassionate-allen-uitctg`._

## Practice trading (2026-10-16)

- **What it is.** `compute-curve statarb signals` writes the exact SA2-M
  book for the next session to `reports/statarb/practice/latest.md`
  (weights and s-scores only). It runs nightly.
- **Check.** It matches the backtest engine's held weights exactly on three
  past dates.
- **Practice plan.** docs/learn_to_trade.md: daily routine, journal, a
  two-week concept plan, and a weekly Ornn H100 forecasting exercise.
- **Status.** Practice only. The paper-trading preconditions are unmet
  until the forward test passes.

## GPU1/GPU2 strategy book (2026-10-16): seven pre-registered rules, launch-ready

Full book: docs/strategy_book.md. Interview notes: docs/interview_guide.md.

- **New pre-registered rules.** All run nightly in shadow mode and log
  "waiting" until GPU1/GPU2 list:
  - **FP-C** balance of month (docs/bom_plan.md);
  - **FP-D** long the backwardation, a hedging-pressure carry
    (docs/carry_plan.md);
  - **SP-I, SP-F and SP-0**, the GPU2/GPU1 spread (docs/spread_plan.md).
  These join FP-A and FP-B (claim 7).
- **Fair-value sheet.** `reports/fair_value/sheet.md` values each contract
  month the way a power desk would. It uses a proxy (our own index) until
  Silicon Data history exists.
- **Drift (descriptive).** List prices did not fall over 2024–26: H100
  +3%/yr (CI −1% to +6%), B200 +13%/yr. Silicon Data's forward curve is
  reported in backwardation. This is FP-D's thesis.
- **Spread rule, in-sample.** On list-price proxies it loses: the ratio
  trended up all year. The rule is unchanged, and the result is recorded as
  a warning.
- **Claim 9: Kalshi GPU binaries.** These settle on Ornn indices.
  - KB-1R: too little history (37 trades over 9 dates).
  - Calibration slope 1.57, consistent with a favourite-longshot bias.
  - The forward test runs nightly.
  - Kalshi's implied H100 and B200 curves slope up for Oct–Dec 2026.
- **Power arithmetic.**
  - FP-C would confirm in about 9 trades if mispricing is about 4%.
  - FP-D needs about 17 trades at a 10% premium, or about 180 at 5%.
- **FP-K, cross-venue.** Ornn's H100 transaction index (2.79, from Kalshi
  settlements) sits at Silicon Data's level (2.81). So GPU1 will be compared
  with Kalshi's H100 monthly-average market (docs/crossvenue_plan.md).
  Kalshi's implied curve is logged nightly.
- **Basis (exploratory).** List-price indices do not track Ornn's index
  week to week. Our own H100 index is noisy at weekly horizons (SD 10%
  against Ornn's 3.4%).
- **Nightly checks.** A manual daily run (38830596835) passed every new step.
- **Variants:** 339. **Skills:** commodities, volatility-modeling and
  nonstorable-futures (D61).

## Round 7 on GetDeploying per-provider history (2026-10-14): two confirmed

Pre-registered one-shot test, Holm over 4 (docs/exploration_round7.md):

- **R7-01 confirmed: provider gaps close** (Holm p 0.003). It is the
  project's first confirmed GPU-price hypothesis, and it holds in all
  robustness variants. It is slow: about 6% of a gap closes per quarter.
- **R7-04 confirmed: the B200/H100 ratio mean-reverts** (slope −0.58 over
  8 weeks, CI [−1.04, −0.19], Holm p 0.002). This is a candidate
  GPU2-versus-GPU1 spread idea, untestable until the futures list and SD
  history exists.
- **R7-02 and R7-03 are degenerate.** The median weekly move is almost
  always zero, because prices are sticky. They will not be re-run on the
  same data.
- **Silicon Data is not in the data.** The comparison with Silicon Data
  still needs SD history: claim 1b, B7, possibly via Bloomberg at SMU.
- **Index method alone moves the price.** The latest B200 price ranges from
  USD 6.25 to 8.30 across constructions. The month-on-month change in the
  monthly average has an SD of 1.9% for H100 and 8.3% for B200.
- **Data handling.** The download was run from a cloud session, because
  GitHub Actions is blocked (B15). It is committed only encrypted (D60).
- Variants: 324.

## Claim 1b: our index vs Silicon Data's (2026-10-13, built; waiting for SD history, B7)

- **The idea (owner).** Use the gap between our index and Silicon Data's.
  The futures settle on Silicon Data's numbers, so being "more accurate"
  does not pay by itself. Only predicting Silicon Data's next move does.
- **GAP-1, lead-lag.** Do our last 5 business-day changes predict SD's next
  5?
- **GAP-2, error correction.** Does SD close an unusually wide gap?
- **Method.** Walk-forward, against a random walk, Clark-West, Holm over 2.
  Windows around SD's known restatement and membership changes are
  excluded.
- **Timing.** It runs once 60 out-of-sample predictions exist. Our panel
  starts 2026-08-04, so about January 2027, if SD history is obtained.
- **Data.** Needs licensed SDH100RT/SDB200RT daily history. The best route
  is a Bloomberg terminal: SMU's Sobey MFin workspace has Bloomberg
  Professional. docs/index_gap_plan.md, `compute-curve index-gap`.

## Claim 7: GPU1/GPU2 futures risk premium (2026-10-13, built; waiting for listing)

- **Idea.** GPU-hours cannot be stored, so futures can trade above or
  below the expected monthly average: a risk premium, as in power markets.
  Rounds 5 and 6 support a driftless random walk, so fair value is the
  current index level, the same for every future month.
- **FP-A, outright.** Sell next month's contract when it is more than 5%
  above the published index; buy when it is more than 5% below. Needs a
  licensed index history (B7).
- **FP-B, calendar.** Sell the month after next and buy next month when the
  curve slopes up by more than 3%; the reverse when it slopes down. Needs
  futures prices only.
- **Mechanics.**
  - Decisions on the first business day of each month, held to final
    settlement, existing cost assumptions.
  - It runs nightly (`futures-premium`). Until CME settlements are dropped
    in `data/manual/cme_settlements/` it only reports "no settlements yet".
- **Evaluation.** Once, after 12 settled trades of a strategy or on
  2028-01-01. Holm over 2, C2 at 2× costs. Shadow only, no orders.
  docs/futures_premium_plan.md.
- **Data handling.** Manual CSVs are git-ignored; logs keep derived numbers
  only (D59). Variants: 307.

## Round 6 on archived prices (2026-10-13): no tradable signal

Pre-registered, one-shot, Holm over 3 (docs/exploration_round6.md):

- **R6-01.** B200/H100 ratio mean reversion: p 0.30 (12 months).
- **R6-02.** H100 list-price change → next-month compute-stock excess:
  wrong sign, p 0.79 (24 months).
- **R6-03.** AR(1) vs random walk for monthly H100 changes: the random walk
  wins.
- **Implication.** Model GPU1's underlying as a driftless random walk.
  List prices change in only about 1 month in 6. Variants: 304.

## Round 5 on archived prices (2026-10-13): no new edge

- **Backfill finished.** USD 18.01 of the USD 20 cap. 3,358 verified H100,
  H200 and B200 list prices from 5 providers, 2023 to 2026. 99.6% of the
  proposed rows were verified, and the newest captures match the live
  collectors exactly.
- **R5-01 (provider gaps close?).** Slope −0.032, p 0.21: not confirmed.
  It is the same size as the two earlier estimates (−0.036, −0.037), all
  individually insignificant and economically tiny.
- **R5-02 (trend).** The median H100 list price was about flat from late
  2023 to 2026: −1.2% a year, CI [−15.6%, +11.8%]. This supports the
  zero-drift fair-value scenario. docs/exploration_round5.md.

## Wayback backfill with Claude (2026-10-12, D58)

- **What.** Archived copies of the provider pricing pages we already
  collect (Lambda, CoreWeave, Nebius, Hyperstack, Verda), back to 2023.
  Claude proposes H100/H200/B200 prices, and the code keeps a row only if
  its verbatim quote and price are on the page. Research-only:
  `data/raw/archive/`, not in the index.
- **Spending limit.** USD 20 total, approved by the owner, metered in
  `data/llm_spend.jsonl`.
- **To run.** The repository secret `ANTHROPIC_API_KEY`, then the manual
  `wayback-backfill` workflow. A dry run is free and needs no key.
  docs/wayback_backfill.md.

## Claim 6c forward test: power check (2026-10-12)

- **Finding.** The 60-session forward test is badly underpowered. Even if
  SA2-M's full confirmation edge persists, it passes only about 28% of the
  time; at half the edge, about 9%. With no edge it passes about 1.5%.
  Details: docs/statarb_forward_power.md.
- **Caveat.** The confirmation's significance leans on negative serial
  correlation in the daily P&L (iid t 1.42 against Newey-West 2.30).
  Block-mean t-statistics agree with Newey-West, but whether that
  dependence persists is unverified.
- **Decision (D57), before any forward statistic.** The 60-session test runs
  unchanged; a fail there is reported as "not confirmed", not as "no edge".
  SA2-M also runs a 250-session extension (to about 2027-10-01, power about
  0.85 at the full edge). Variants: 297.

## Operations (2026-10-12)

- **Scheduled run green.** The first scheduled run after the fix (run 8,
  2026-10-12) ended success.


- **What was wrong.** The nightly workflow had ended "failure" every night
  since launch. Data was still collected and committed. The cause was
  R2-04 reading the local-only AWS archive (PR 19).
- **Fix.** R2-04 now waits on CI and confirms locally after `claim5 fetch`.
  Round 4 reads committed data only.
- **Check.** Every exploration step was run with `var/` absent, then the
  workflow was triggered manually.

## Claim 6c: stock stat-arb passes its one-shot confirmation (2026-10-11)

- **The test.** Residual reversal (Avellaneda-Lee) on the compute-linked
  stocks.
  - Costs come from real quoted NBBO spreads.
  - It went straight to the pre-registered one-shot confirmation
    (2026-02-20 to 10-05). Plan: docs/statarb_plan3.md.
- **Both versions passed.**
  - All 20 stocks: 10.6 bps a day net, Sharpe 1.80, Holm p 0.023.
  - 10 liquid stocks: 4.9 bps a day, Sharpe 1.73, Holm p 0.049.
  - Both still positive at double costs.
- **But fragile (post-hoc).** Without the 5 best of 157 days, the return
  falls to about 1 bp a day. SMCI, CIFR and NBIS give most of the profit.
- **Independent code audit (D56).**
  - No look-ahead and no cost or statistics bug.
  - One upward bias: rebalancing was free in the engine.
  - Under fixed-share accounting SA2-M still passes (Holm p 0.020) and
    SA2-L fails (0.058), so SA2-L is now **borderline**.
  - The forward test must pass under both accountings.
- **Out-of-universe replication (claim 6d).** It **failed**: frozen SA2-M on
  20 large-cap tech names gives Sharpe −0.55, p 0.80. The edge, if real, is
  specific to volatile AI names. Confidence is lower; the forward test
  decides.
- **Paper-trading readiness (proposal; nothing executed).**
  - All names are shortable on Alpaca except WYFI. Without WYFI shorts the
    strategy makes 9.5 bps a day, p 0.018.
  - Within the claim-4 limits the size is about USD 8,600: 95% drawdown
    about USD 720, expected about USD 8 a day if the edge holds.
  - Needs: the forward test to pass, and the owner's approval. See
    docs/statarb_paper_readiness.md.
- **Next.** A 60-session forward shadow test from 2026-10-06 runs
  automatically (`statarb forward`, about the end of December). No orders.
  Details: docs/statarb_results.md.

## Round 4: provider-gap test (H01) forward replication (2026-10-11)

- **The Hugging Face history cannot test H01.** Under the index's filters,
  only Lambda qualifies on each day, and H01 needs at least 5 providers.
  Providers were counted only; no outcome was computed.
- **Pre-registered instead (R4-01).** H01's frozen specification runs once
  on our listings from 2026-10-07 to 12-31, days no test has used. Plan:
  docs/exploration_round4_plan.md.
- **Automatic.** The daily workflow runs it on or after 2027-01-01.
- **So far.** 4 listing days are in the window.
- **R4-02 (added): does AWS H100 spot scarcity lead neocloud prices?**
  - The exploration fits on 2026-07 to 09 are descriptive. Both slopes are
    negative, the wrong way for the hypothesis:
    - CGI: −0.20, one-sided p 0.90;
    - our panel: −2.2, from only 15 changing days.
  - The one-shot confirmation runs on 2026-10 to 12, once AWS publishes
    December.
- **Scarcity test.** Blocked: no usable availability measure (B14).

## Monte Carlo fair-value engine (2026-10-11)

- **What it does.** `compute-curve fairvalue` simulates the GPU1/GPU2
  monthly settlement average under the two-factor model. It reports:
  - fair value relative to spot;
  - quantiles;
  - the 95% value-at-risk per contract;
  - at-the-money Asian calls.
- **Checks.** Exact simulation and a geometric control variate cut the
  Monte Carlo error more than fivefold. Tested against closed forms. Method:
  docs/montecarlo_fair_value.md (D55).
- **Proxy calibration (illustrative).**
  - The CGI short-term half-life is about 1 day (H100) and 2.4 days (B200).
  - The long-term drift is not distinguishable from zero, so the slope of
    the curve is model risk.
  - The 12-month 95% value-at-risk is about a third to a half of the
    contract's value.

## Claim 6: stock statistical arbitrage (2026-10-10)

**Bottom line.** No significant edge after costs. Details are in
`docs/statarb_results.md`.

- **What was tested.** Pairs trading (cointegration) and Avellaneda-Lee
  residual reversal against XLK, on the 20 compute-linked stocks.
  - Pre-registered: docs/statarb_plan.md, c86c7ec.
  - A 21-cell grid, with a pooled region instead of the best cell.
  - Deflated Sharpe, Monte Carlo nulls, a drawdown bootstrap and a cost
    break-even.
- **Pairs: Sharpe −1.55.** It loses before costs. AI stocks trended apart on
  news.
- **Residual reversal: Sharpe +0.18**, CI −1.05 to 1.25, deflated Sharpe
  0.07.
  - Its entry timing beats random timing (99% of Monte Carlo draws), but the
    edge is below costs.
  - Break-even cost is 23 bps per side, against 15 assumed.
- **Confirmation set unspent.** Nothing survived, so the 2026-02-20 to 10-05
  set is untouched.
- **Skill.** `sharpe-ratio-non-iid-corrections` was added (D52). Its formulas
  are implemented in `compute_curve.statarb.evaluate` and tested against the
  paper's Exhibit 1.

## Exploration round 3, interim (2026-10-10)

**Bottom line.** Round 3 asks what drives the CGI reversal. It has no
finding yet. Details are in `docs/exploration_round3.md`.

- **Plan.** It was committed before any statistic was computed (80aaaa7).
  - Four tests, each run once on future CGI data (2026-10-11 to 12-31).
  - Holm across the four.
  - No exploration screen, because the window had been looked at (D49).
- **R2-02 was followed up.** Re-specified at 15-minute resolution (R3-01),
  it still shows nothing on the exploration window (p 0.50, contaminated).
- **Jump and band-edge channels.** Neither explains the reversal on the
  exploration window. The reversal looks broad-based.
- **Per-provider receipts would show which seats drive it.** Their licence
  is unclear, so they are blocked (B12).
- **Data.**
  - gpurentalprices.com was backfilled for 2026-07-05 to 07-18 from Zenodo
    (D48).
  - Collection runs on every turn.
  - Two new daily collectors from 2026-10-10: `azure_retail` (Azure H100
    and H200 VM prices by region, D50) and `fastgpu` (FastGPU open dataset,
    CC BY 4.0, Vast.ai and RunPod rows dropped, D51). First run: 480 and
    84 rows.
  - The remaining candidate sources are listed in docs/data_sources.md.
  - 2026-10-11: one-off backfill `gpuprices_hf` (GPU Price Tracker on
    Hugging Face, CC BY 4.0, D54). 148 days from 2026-05-07, 183,929
    H100/H200/B200 rows. Snapshots that reached the hub late are skipped,
    including all of January to March. Not in `history_sources`, so the
    rounds are unchanged.
- **Automatic confirmation.** The daily workflow runs `explore round3
  confirmation` once the window is complete (on or after 2027-01-01 05:55
  UTC).
- **Mechanism check (synthetic, section 6 of the report).**
  - CGI's vote rule alone produces no reversal.
  - Seat drop-outs or seat price deviations lasting hours can each produce
    one.
  - Real CGI's fingerprint (R3-01 null; ACF(1) flips sign after the EWMA)
    fits multi-hour seat deviations best. Unconfirmed: it needs receipts
    (B12).
- **New collectors (PR 9).**
  - `azure_retail` and `fastgpu` run daily from 2026-10-11.
  - The owner chose to keep FastGPU.

### Actions for you (round 3)

1. Optional: ask Computable whether research use of CGI's per-provider
   receipts is permitted (B12).
2. Optional: ask Overclock Labs about Akash availability data (B13).

## Final summary: exploration round 2 (2026-10-09)

**Bottom line.** Two new survivors wait for future data, and nothing is
confirmed. Details are in `docs/exploration_round2.md`.

- **H01 replication** (our own index; providers converge to the market
  price):
  - same effect size on unseen days;
  - not significant in 19 days (p 0.107);
  - not confirmed.
- **Survivors, exploratory:**
  - **R2-03:** CGI B200 6-hour reversal. Confirmation runs automatically on
    or after 2027-01-01.
  - **R2-04:** AWS H100 spot persistence with a daily re-estimated
    coefficient. Confirmation runs once Zenodo publishes the AWS 2026-10 to
    12 months.
- **H05:** provider churn does not explain its reversal (R2-02).
- **Term structure (R2-06):** nothing.
- **Fixed on the way:** H05's daily shadow step had failed since 2026-10-07,
  and its forward log was empty. It is fixed and merged (PR 6, D44), and the
  log was rebuilt point-in-time.
- **Merged.** The skills (PR 5), the shadow fix (PR 6) and round 2 (PR 7)
  are on main. The daily workflow runs the R2-03 confirmation itself.

### Actions for you (round 2)

1. **When Zenodo publishes the AWS 2026-12 month** (probably in January
   2027):
   - add `"2026-10"`, `"2026-11"`, `"2026-12"` to `[claim5].months` in
     `config/default.toml`;
   - run `uv run compute-curve claim5 fetch`;
   - then run `uv run compute-curve explore round2 confirmation`, or let the
     daily workflow run it.

## Final summary: exploration round 1 (find candidate signals, honestly)

**Bottom line.** One candidate, no findings. Nothing survived for our own
index. The gate was not loosened. Details are in
`docs/exploration_round1.md`.

- **Protocol.**
  - The plan was committed before any analysis (`6a21706`). It fixed:
    - per-dataset 70/30 time splits;
    - 12 hypotheses, one of them with an equity target;
    - Benjamini-Hochberg across the round;
    - survival filters;
    - a one-shot confirmation;
    - a 60-session forward test.
  - The code cuts each dataset to one set before computing anything, and
    synthetic tests check it.
- **Exploration** (exploratory).
  - **Two survivors:**
    - H05, the CGI H100 index giving back about a third of a 6-hour move;
    - H09, AWS H100 spot moves persisting over a week.
  - **Our own index:**
    - H01 (providers converge to the market price) passed the
      false-discovery screen but failed its sign-flip check (p 0.087);
    - H02 (price leadership) was not testable, because the five largest
      providers changed price on one day in 56.
  - **The rest:** the other eight show nothing.
- **Confirmation, one shot each.**
  - **H05 confirmed:** one-sided p 0.001 and out-of-sample R² +0.11
    against both baselines.
  - **H09 not confirmed:** the direction held, but the frozen forecast lost
    to "no change".
- **Forward test.** H05 is a **candidate**, not a finding.
  - `compute-curve explore round1 shadow` logs its frozen forecasts, with
    no orders, for every hourly decision point in the 60 US equity sessions
    from 2026-10-07 to 2026-12-31.
  - It is evaluated once, from 2027-01-01.
  - Even if it passes, it stays in shadow mode until a contract on such an
    index trades (D26).
- **Workflow.** A step was added after the tests in
  `.github/workflows/daily.yml` and `scripts/daily.sh`.
- **Tests.** 219 offline tests pass and ruff is clean. 23 are new, all on
  synthetic data:
  - outcome poisoning;
  - planted effects found and a null world clean;
  - the echo filter;
  - the one-shot guard;
  - forward-log immutability.
- **Variants.** 16 declared for this round; 217 project-wide.

### Actions for you (exploration round 1)

1. **Merge this branch into the default branch.** Scheduled workflows run
   only there, and H05's forward window starts on 2026-10-07.
   - If the merge comes later, nothing is lost: the shadow step re-imports
     CGI's last 90 days, and each logged forecast still uses only the
     values stamped before its decision time (D42).
   - But each day of delay makes the log less of a live record.
2. **Nothing else is required.** The most valuable new data for a round 2
   are listed in `docs/exploration_round1.md`. The first is licensed
   settlement-index history (B7).


## Final summary: claim 5 (do AWS GPU spot prices lead compute-linked equities?)

**Bottom line.** The gate does not pass, and claim 5 is not supported. The
gate was not loosened.

- **Nothing passed.** None of the 12 primary tests, 6 event tests, 12
  walk-forward forecasts or 36 secondary tests passes.
- **Correlations are near zero.** Every correlation between an AWS spot
  signal and the basket's later excess return over XLK is between −0.16 and
  0.11, and every 95% interval includes zero.
- **Forecasts lose to naive guesses.** Every walk-forward forecast does
  worse than both naive baselines.
- **This sample had power.** Unlike claim 4's, it had 402 sessions with
  dense signals, so correlations of about 0.18 or more after correction
  would most likely have been found. Smaller effects are not ruled out.

Details are in `docs/claim5_results.md`. The plan was committed before any
stock data was fetched (`docs/claim5_plan.md`, `35d5317`).

### What was done

- **Audit.** Zenodo "AWS Spot Price History" (Eric Pauley, UW-Madison):
  - licence CC BY 4.0;
  - current version 2026-09 (DOI 10.5281/zenodo.23082767);
  - 31 files, 5.16 GB;
  - 2026-03 to 2026-06 missing from the dataset;
  - robots.txt disallows `/api`, so the landing page was used instead.

  Recorded in `docs/data_sources.md`.
- **Data.** Only the 20 needed monthly files (3.5 GB):
  - MD5-verified and read-only, in git-ignored `var/aws_spot/raw/` (D36);
  - filtered to A100, H100, H200, B200 and B300 types in US zones on Linux
    (90,915 rows);
  - daily per-GPU-hour series in `reports/claim5/aws_spot_daily.csv`, with
    a checksum manifest.
- **Signals** (D37): A100 and H100 matched-pool level change and dispersion
  change, with claim 4's timing. No availability signal, and no signal
  across data gaps.
- **Stocks without full history** (D38): NBIS used from 2024-10-21; CRWV,
  WYFI and CBRS from their first bars. Claim 4's coverage rule kept the
  basket defined from 2024-10-21.
- **Battery.** Claim 4's battery and gate ran unchanged, through the same
  code. The only change to claim-4 code is an optional GPU list for the
  event study. 78 tests and evaluations were declared before the run, plus
  2 logged post-hoc descriptive checks.
- **Workflow.** Because the gate failed, **no claim-5 step was added to the
  daily workflow**.
- **Commands.** `uv run compute-curve claim5 fetch` and
  `uv run compute-curve claim5 evaluate`.

### Actions for you (claim 5)

- **None required.** The claim-4 actions below still stand.
- **Optional.** When Zenodo has published about 250 new sessions (about the
  2027-09 version), add those months to `[claim5].months` and re-run the
  two commands. That is the pre-registered confirmation test (K2).
- **Clean-up.** The 3.5 GB of raw spot files in `var/aws_spot/raw/` can be
  deleted to free disk. They can be re-downloaded and verified from the
  manifest.

## Final summary: claim 4 (does our GPU index lead compute-linked equities?)

**Bottom line.** The evidence neither supports nor rejects claim 4. That
was expected and stated in advance. There are 32 trading sessions of clean
index history (2026-08-20 to 2026-10-05), so only correlations of about 0.48
or more could be detected; realistic effects are 0.1 or less.

- None of the 18 primary tests, 6 event tests or 18 walk-forward forecasts
  passes.
- The validation gate failed for every signal, so paper trading is in
  **shadow mode**: the daily prediction is logged and no order is sent.
- One secondary test passes a 10% false-discovery screen (neocloud stocks
  after B200 price moves). It rests on two days, and without them the
  correlation drops from −0.42 to −0.12, so it is not a finding.

Details are in `docs/claim4_results.md`. A one-page plain-language version
is `docs/summary.md`.

### What was built in this run

- **Step 0** (`docs/env_check_claim4.md`):
  - all three Alpaca variables are set (names only);
  - the base URL is exactly the paper endpoint;
  - the paper account answers;
  - daily bars arrive from both feeds.

  Alpaca's terms allow personal, non-commercial use and forbid
  redistribution, so bars are cached in `var/` only and never committed
  (D29).
- **Paper-only adapter** (`compute_curve.claim4.alpaca`):
  - every client hard-fails unless `APCA_API_BASE_URL` is the paper
    endpoint;
  - every request is re-checked against the allowed host;
  - redirects are refused;
  - 42 tests try ways around the guard.

  CLAUDE.md records this as the single exception to "no brokerage
  connectivity" (D30). The local futures engine still has no broker code.
- **Pre-registration** (`docs/claim4_plan.md`), committed before any
  test-window return was seen:
  - the universe rule and a frozen list of 21 stocks in three buckets,
    against XLK;
  - six index signals with timing that matches the live cycle (D31);
  - horizons of 1, 5 and 20 sessions;
  - the test families, cost assumptions, gate, kill criteria and an honest
    power statement.

  114 tests and evaluations are declared in `docs/variants_log.md`.
- **Tests and gate** (`compute_curve.claim4.analysis`, `stats`):
  - lead-lag with Newey-West, Holm and permutation checks;
  - an event study;
  - walk-forward forecasts against zero and mean baselines;
  - net-of-cost strategy checks;
  - bucket baskets with Benjamini-Hochberg.

  After the first run, five guards against small-sample artifacts were
  added. All of them are stricter (D34).
- **Paper strategy and limits** (`claim4.strategy`, `claim4.risk`):
  - a long-short pair, the basket against XLK, with daily cohorts;
  - USD 10,000 per symbol, USD 20,000 gross;
  - a USD 1,000 daily loss halt;
  - a USD 3,000 drawdown latch;
  - a kill switch in config or the environment.

  Every check is recomputed from Alpaca's own history each run, so CI
  needs no stored state.
- **Daily cycle**:
  - `compute-curve claim4 evaluate` writes the report, the bar manifest and
    the gate file;
  - `compute-curve claim4 daily` decides only in the window before each
    session, appends to `reports/claim4/predictions.csv` and writes
    `reports/claim4/daily/<date>.md`.

  The first shadow prediction (session 2026-10-06) is logged.
- **Automation**: `.github/workflows/daily.yml`. The push was accepted.
  - It runs at 23:37 UTC and has a manual trigger.
  - It collects listings, updates the index, runs claims 1 to 3, then the
    claim-4 evaluation and daily step.
  - The claim-4 steps run only if the tests pass.
  - It commits and pushes, and turns red at the end if any step failed.
  - `scripts/daily.sh` runs the same claim-4 steps for a local cron.
- **Tests**: 186 offline tests pass and ruff is clean. The 94 new claim-4
  tests use synthetic data and a fake Alpaca. They cover:
  - no look-ahead in the walk-forward (outcome poisoning);
  - a planted effect is found and a null world passes nothing;
  - shadow mode sends no order;
  - every paper order respects the limits;
  - the kill switch closes only claim-4 symbols;
  - the CLI refuses the live endpoint;
  - a stale gate file sends nothing (D35).

### Actions you must take for claim 4, in order

1. **Merge this branch into the default branch.** GitHub runs scheduled
   workflows only from the default branch, so the daily cycle, including
   claim 4, starts only after the merge. No pull request was opened.
2. **Add two repository secrets**, under Settings → Secrets and variables →
   Actions: `APCA_API_KEY_ID` and `APCA_API_SECRET_KEY`, holding your
   **paper** keys. The workflow sets the base URL to the paper endpoint
   itself. Without the keys, listing collection and claims 1 to 3 still
   run, and the claim-4 steps fail and turn the run red.
3. **Allow the workflow to push.** If its push step fails with HTTP 403,
   set Settings → Actions → General → Workflow permissions to "Read and
   write", or let the Actions bot bypass branch protection on the default
   branch.
4. **Use a dedicated Alpaca paper account for claim 4.** The code only
   trades the 21 universe stocks and XLK. But the daily loss and drawdown
   limits read the whole account's equity, and a manual position in the
   same symbols would be netted against claim-4 targets.
5. **Pick one scheduler.** Use the GitHub workflow or `scripts/daily.sh`
   cron, not both. GitHub sometimes delays scheduled runs. A run that slips
   past midnight UTC can miss that day's listings, so cron on your own
   machine is the more reliable collector.
6. **Emergency stop.** Set the repository variable
   `COMPUTE_CURVE_KILL_SWITCH` to `1`, or `claim4.risk.kill_switch = true`
   in config. Either closes all claim-4 paper positions and blocks orders.
7. **Before making the repository public**, re-read D29. No Alpaca prices
   are committed, but daily reports state the paper account's daily
   percentage change and order quantities.
8. **Optional:** pin the workflow's actions (`actions/checkout@v4`,
   `astral-sh/setup-uv@v6`) to commit SHAs. This session could not look the
   SHAs up.

### Still open from the previous run (claims 1 to 3)

1. **Licensed settlement-index history** (B7). This is the most valuable
   input: it unblocks claim 1, and it would let claim 4 be asked over years
   instead of weeks.
2. **CME settlements once GPU1/GPU2 list.** The CFTC decision is due by
   2026-11-09. Save them in `data/manual/cme_settlements/`.
3. **Network policy.** No allowlist is active (docs/env_check.md). Claim 4
   adds `paper-api.alpaca.markets` and `data.alpaca.markets` to the needed
   hosts.
4. **Two conservative choices you may relax:** D13 (Vast.ai and RunPod rows
   dropped everywhere) and D16 (Together AI not collected directly).
5. **Optional:** licence requests to Vast.ai and FLOPS; the two SSRN PDFs.
   Backfilling 2026-07-05 to 07-18 from Zenodo would change the panel that
   claims 1 to 3 use. Claim 4's panels are frozen in config and would not
   change (D33).

## Done

- Previous run (2026-10-05): environment check, data layer, nine
  collectors, our index, the local paper engine, models, tearsheets and
  evaluations for claims 1 to 3 (merged as pull request 1).
- Claim-4 run: Step 0, pre-registration, implementation, the first
  real-data evaluation, the first shadow prediction, the daily workflow,
  the results and the plain-language summary.
- Claim-5 run (2026-10-06): the AWS spot archive audit and download,
  pre-registration, evaluation with claim 4's battery (gate not passed),
  and the results.
- Exploration round 1 (2026-10-06): plan, exploration, one-shot
  confirmation, and a shadow forward test for the one candidate (H05).

## In progress

- Daily collection and the claim-4 shadow log, once the workflow is merged
  and the secrets are added.
- H05's shadow forward test, 2026-10-07 to 2026-12-31, once the workflow is
  merged. It is evaluated once, from 2027-01-01.

## Blocked

- Claim 4: nothing blocks it; only time does. The gate needs at least 120
  out-of-sample forecasts. The earliest a frequently moving signal could
  pass is about March 2027.
- Claim 5: nothing blocks it. The test ran and the gate failed. A re-test
  waits for about 250 new sessions in the Zenodo archive.
- Claims 1 to 3: B7 (settlement-index licence) and B8 (contracts not
  listed). B2, B3, B5, B6, B9 and B10 as before. Details in
  docs/blockers.md.

## Needs you

- The merge (exploration action 1) and claim-4 actions 1 to 7 above, then
  the still-open items. Claim 5 needs nothing.
