# Status

_Last updated: 2026-10-06, end of the claim-4 autonomous run. Branch
`claude/eager-archimedes-fjo2e4`._

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
- This run: claim 4 Step 0, pre-registration, implementation, the first
  real-data evaluation, the first shadow prediction, the daily workflow,
  the results and the plain-language summary.

## In progress

- Daily collection and the claim-4 shadow log, once the workflow is merged
  and the secrets are added.

## Blocked

- Claim 4: nothing blocks it; only time does. The gate needs at least 120
  out-of-sample forecasts. The earliest a frequently moving signal could
  pass is about March 2027.
- Claims 1 to 3: B7 (settlement-index licence) and B8 (contracts not
  listed). B2, B3, B5, B6, B9 and B10 as before. Details in
  docs/blockers.md.

## Needs you

- Claim-4 actions 1 to 7 above, then the still-open items.
