# Wayback backfill: archived pricing pages read by Claude (D58)

_2026-10-12. Data collection, not a hypothesis test._

## 1. Why

Our own provider-level price history starts in 2026. The provider-gap test
(H01, R4-01) needs at least 5 providers per day, and the term-structure work
needs years, not months. Paid histories are pending (GetDeploying,
docs/data_costs.md). The Wayback Machine holds dated copies of the public
pricing pages we already collect today, back to 2023 or earlier.

## 2. What it does

1. **List captures.** For each approved page, the CDX API lists captures
   with HTTP 200 and **distinct content** (`collapse=digest`). An unchanged
   page is fetched once, not once per crawl.
2. **Fetch the original HTML** (`<timestamp>id_/<url>`), at least 4 s apart.
   robots.txt is checked as for every other source.
3. **Reduce to visible text.** If a page is longer than 60,000 characters,
   only price-like lines and their neighbours are kept, and the ledger
   records the truncation.
4. **Claude proposes rows** (structured output: GPU name, GPUs per unit,
   price, per GPU or per instance, term, verbatim quote). Model
   `claude-opus-5-5`, effort `low`. Only H100, H200 and B200.
5. **The code verifies every row** (`collectors.wayback.verify_row`). A row
   is kept only if:
   - its quote appears verbatim on the page (whitespace-normalized);
   - its price appears as a number in that quote;
   - the GPU is named in the quote or in the 400 characters before it;
   - the per-GPU price is between USD 0.05 and 100.

   A model mistake can therefore drop a real price, but it cannot add a
   price that is not on the page.
6. **Store.** One immutable Parquet per capture under
   `data/raw/archive/wayback_<provider>/`. `ts_observed` is the capture
   time; the quote, digest, model and extraction time are kept in
   `raw_json`.

## 3. Status of the data: research-only

- **Not in the own index.** The rows sit outside `data/raw/listings`, so the
  own index and every existing test ignore them.
- **Use needs pre-registration.** Any use in a test must be declared first.
- **Sparse dates.** Captures are irregular, so the data dates list-price
  changes. It is not a daily series.

## 4. Sources

Only pages whose live versions we already collect under their terms
(docs/data_sources.md): Lambda, CoreWeave, Nebius, Hyperstack and Verda
(formerly DataCrunch). Never Vast.ai, RunPod or Together.

**Unverified:**
- The older URLs: `lambdalabs.com/service/gpu-cloud` and
  `datacrunch.io/products`. A wrong URL simply returns no captures.
- Wayback's own rate limit.
- Whether "noncommercial" is still in the Internet Archive's terms. Use here
  is non-commercial research either way (docs/data_costs.md §7).

## 5. Cost and spending limit

- **Price.** USD 4 per million input tokens and USD 20 per million output
  tokens (Anthropic list price for `claude-opus-5-5`, 2026-10-12).
- **Owner-approved cap.** USD 20 in total and USD 20 per run, from the
  owner's USD 100 credit (2026-10-12).
- **How the cap is enforced:**
  - Every call is metered into `data/llm_spend.jsonl` (committed;
    append-only; no secrets).
  - A call is made only if the worst case (about USD 0.24: 20,000 input
    and 8,000 output tokens) still fits under both caps.
  - Cache tokens are metered at the full input price, which is
    conservative.
- **Repeat runs.** A capture already processed is never sent again.
- **Order: coverage first.** Pages are processed in this order:
  - the earliest capture of every calendar month for every page, months
    oldest first and pages interleaved;
  - then each month's second capture;
  - and so on.

  A run stopped by the cap has covered as many provider-months as it could.
  It has not spent everything on one provider.
- **Dry run, 2026-10-12** ([run 38316386448](https://github.com/jwilliamross/compute-curve/actions/runs/38316386448)).
  It found 454 distinct captures, from 2023 to now:

  | Page | Captures |
  |---|---|
  | lambda.ai/pricing | 90 |
  | lambdalabs.com/service/gpu-cloud | 102 |
  | coreweave.com/pricing | 114 |
  | nebius.com/prices | 55 |
  | hyperstack.cloud/gpu-pricing | 49 |
  | verda.com/pricing | 21 |
  | datacrunch.io/products | 23 |

  All 454 at the worst case would cost about USD 109. So USD 20 covers at
  least about 82 pages, and likely more at typical cost (unverified).
- **Typical page.** Probably USD 0.03 to 0.10 (unverified until the first
  run).

## 6. How to run

1. **Dry run (free).** Actions → `wayback-backfill` → Run workflow, with
   `dry_run` ticked. This counts captures per page and calls no API.
2. **Real run.** Needs the repository secret `ANTHROPIC_API_KEY`. Untick
   `dry_run`. It stops at the cap.
3. **Where it runs.** The agent sandbox cannot reach `web.archive.org`
   (docs/data_costs.md §7), so it runs only from GitHub Actions.

## 7. Pilot (2026-10-13, Verda only)

- **Volume and cost.** 44 captures, 34 sent to Claude, 5 with no GPU text.
  545 rows were proposed, and all 545 were verified. Cost USD 1.65, about
  USD 0.05 per page (6,100 input and 1,200 output tokens on average).
- **Cross-check against the live collector.** The archived 2026-10-05
  capture gives H100 on-demand USD 3.77 and spot USD 1.89. That is exactly
  what our live `verda` collector recorded that day.
- **Two prices per page.** Recent Verda pages list two H100 price sets about
  10% apart (for example USD 3.89 and 4.28 on 2026-10-09). Both are on the
  page, so the extraction is faithful. The live collector takes the first.
- **Fix for later pages.** The pilot rows carry no label telling the two
  apart. From now on Claude also returns `qualifier`, the page's own label
  for such a price (location, section or plan). It is stored in `config`,
  `listing_id` and `raw_json`.
- **Round 5 unchanged.** The plan, frozen beforehand, uses the median over
  a capture's rows. That stays as written.

## 8. Full backfill (2026-10-13): finished

- **Runs.** Three: the Verda pilot, the full run, and one retry of failed
  pages.
- **Spend.** USD 18.01 in total, under the USD 20 cap. About USD 2 is left
  unspent.
- **Pages.** 427 settled captures (sent to Claude, or with no GPU text) out
  of 454. About 30 still fail on archive connection resets. They were not
  retried further: diminishing value, since every reachable provider-month
  is already covered first.
- **Verification.** 3,374 of 3,389 proposed rows verified (99.6%), 3,358
  rows after de-duplication.
- **Cross-check.** For every provider, the newest archived H100 prices
  exactly match the live collectors on nearby days:
  - Lambda 3.99 to 4.29 (SXM) and 3.29 (PCIe);
  - CoreWeave 6.155;
  - Nebius 4.50;
  - Hyperstack 3.20, 2.60 and 2.50;
  - Verda 3.77 and 1.89.
- **Results.** Round 5 used this data once (docs/exploration_round5.md).
