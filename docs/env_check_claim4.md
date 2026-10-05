# Environment check for claim 4 (Alpaca)

Run at 2026-10-05 19:25 UTC in the Claude Code cloud container, before any
claim-4 code existed and before any equity return was looked at.

## Summary

**All checks passed.** The three Alpaca variables are set. The base URL is
exactly Alpaca's paper endpoint. The paper account endpoint answers. The
market data API returns daily bars from both its IEX and its consolidated
(SIP) feed. Nothing was logged in `docs/blockers.md` from this step.

**Rule taken from Alpaca's terms.** Alpaca content is for personal,
non-commercial use. It may not be copied, uploaded or posted to another
server "for publication or distribution", and Alpaca says its API data may
not be redistributed. Therefore Alpaca bars are cached only in the
git-ignored `var/` folder and are never committed. Reports carry only
aggregate statistics and our own signals and predictions. They contain no
prices, no per-stock return series and no dollar balances (decision D29).

## Results

| # | Check | Result | Detail |
|---|---|---|---|
| 1 | `APCA_API_KEY_ID` set | PASS | Non-empty. Value not read into any log, file or output |
| 1 | `APCA_API_SECRET_KEY` set | PASS | Non-empty. Value not read into any log, file or output |
| 1 | `APCA_API_BASE_URL` set | PASS | Non-empty. Compared in code; the value was not printed |
| 2 | Base URL is the paper endpoint | PASS | Scheme `https`, host `paper-api.alpaca.markets`, no port, no credentials in the URL, path empty or `/v2`. The host is not the live host `api.alpaca.markets` |
| 2 | Account endpoint responds | PASS | `GET /v2/account` returned HTTP 200. Status `ACTIVE`, currency USD, trading and account not blocked. The account number carries Alpaca's paper prefix `PA` (the number itself was not recorded). Equity about USD 100,000, Alpaca's default paper balance |
| 2 | Other read-only endpoints | PASS | `/v2/clock` 200 (market open at check time), `/v2/positions` 200 (0 positions), `/v2/orders` 200 (0 orders), `/v2/assets/SPY` 200 |
| 3 | Daily bars, IEX feed | PASS | `GET data.alpaca.markets/v2/stocks/bars`, `timeframe=1Day`, SPY, 2026-09-01 to 2026-10-02: HTTP 200, 23 bars with fields `t o h l c v n vw` |
| 3 | Daily bars, SIP feed | PASS | Same request with `feed=sip`: HTTP 200, 23 bars |
| 3 | Rate limit | INFO | Response headers state 200 requests per minute, which matches the free Basic plan |
| 4 | Terms on storing market data | READ | See below |

No orders were placed during this check. Only `GET` requests were sent.

### How the checks avoided looking at returns

The bar check used SPY. SPY is outside the claim-4 universe and is not the
benchmark (docs/claim4_plan.md). Only bar counts, field names and timestamps
were printed, not prices. The pre-registration was written before any
return of a universe stock or the benchmark was fetched.

### Bar timestamps

Daily bars are stamped `04:00:00Z`, which is midnight in New York. The
timestamp labels the trading session. It does not say when the bar became
final. The claim-4 code dates each bar by its session's official close plus
the 15-minute delay that applies to historical SIP data on the free plan
(the "latest 15 minutes" restriction). A bar is used only after that time.

## Alpaca terms on market data

Sources read on 2026-10-05:

1. **Alpaca Terms and Conditions**
   (<https://files.alpaca.markets/disclosures/library/TermsAndConditions.pdf>,
   linked from <https://alpaca.markets/disclosures>). Its definition of
   "Content" includes market data (quotations and last-sale information) and
   account positions, balances and order history. Two clauses matter:
   - *Personal and Non-Commercial Usage*: "you agree to use the Services and
     Content solely for your own personal and non-commercial purposes."
     Making Content available to others through your own application needs
     30 days' written notice to Alpaca.
   - *Content*: "No part of the Service or Content may be copied, reproduced,
     republished, uploaded, posted, publicly displayed, encoded, translated,
     transmitted or distributed in any way (including "mirroring") to any
     other computer, server, web site or other medium for publication or
     distribution or for any commercial enterprise, without Alpaca's express
     prior written consent."
2. **Alpaca support article** "Can I redistribute Alpaca API data via my
   platform?" (<https://alpaca.markets/support/redistribute-alpaca-api>):
   "Unfortunately, you cannot redistribute Alpaca API data."
3. **Market data documentation**
   (<https://docs.alpaca.markets/docs/about-market-data-api>, updated
   2026-07-16). The free Basic plan gives historical data from the
   consolidated tape since 2016, except the latest 15 minutes, and allows 200
   historical calls per minute. The page says nothing about storage.
4. The NASDAQ and NYSE subscriber agreements on the disclosures page apply
   to the paid plan. They were not needed, because the rule below already
   bars redistribution.

### How this project follows them

- **Use.** Personal, non-commercial research by the account holder. No
  third party is given access to the data.
- **Storage.** Bars are fetched at run time into `var/market_data/`. That
  folder is git-ignored, local to the machine or CI runner, and rebuilt on
  demand. Bars are never written under `data/raw/` and never committed. The
  GitHub Actions workflow does not upload them as an artifact or a cache.
- **What is committed.** A fetch manifest is committed: symbols, date range,
  feed, row counts and a content hash. It allows audit without the prices.
  Our own index signals and model predictions are committed, along with
  aggregate test statistics: correlations, mean excess returns with
  confidence intervals, and hit rates. None of these reproduces the Content.
- **Account data.** Daily reports state risk-check outcomes and percentage
  changes. They give no dollar balances, quotes or fill prices. The account
  itself is visible in the Alpaca dashboard.
- **Exception to CLAUDE.md's raw-data rule.** CLAUDE.md asks for immutable
  raw Parquet under `data/raw/`. Alpaca data is exempt, for the same reason
  Silicon Data content is not stored (D14). Reproducibility rests on
  re-fetching. The manifest's hash shows whether a re-fetch returned the
  same data.

## Paper-only guard

All Alpaca trading code goes through one guard,
`compute_curve.claim4.alpaca.require_paper_base_url`. Before any request is
built, it raises `LiveEndpointRefusedError` unless `APCA_API_BASE_URL` is exactly
`https://paper-api.alpaca.markets`, optionally followed by `/v2`. Every
request URL is checked again against the paper host, and redirects are not
followed. Tests cover the live host, look-alike hosts, `http`, ports,
credentials embedded in the URL, query strings and a missing variable
(`tests/test_claim4_alpaca.py`).

## Other notes

- No MCP connector tool was called (CLAUDE.md). Alpaca's documents were read
  with the built-in web tools, as in D28.
- The market was open during the check, at 15:25 New York time.
