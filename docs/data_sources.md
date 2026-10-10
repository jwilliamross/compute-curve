# Data sources

Audit date: 2026-10-05. Every source below was checked for access method,
robots.txt, terms of use, fields, history depth and cost. The raw research
notes, with verbatim terms quotations and a request log, are in
`docs/audit/2026-10-05_data_sources_audit.md`. Nothing was bought, no account
was created, and no key was sent to any source.

## Summary

| Source | What it gives | Access | Terms verdict | Status in this repo |
|---|---|---|---|---|
| Silicon Data (SDH100RT, SDB200RT) | The settlement index | Latest value public; history paid (Pro USD 998/month) or free Basic account (30 days, needs sign-up) | Terms forbid storing site content in a database; redistribution needs an index licence | **Not collected.** Owner action needed (B7) |
| CME GPU1/GPU2 settlements | Futures prices | cmegroup.com blocks automation; DataMine free after midnight CT with a CME login (snippet) | Automated access to cmegroup.com prohibited | **Manual CSV drop** (`data/manual/cme_settlements/`). None yet: not listed (B8) |
| Computable GPU Index (CGI) | Independent H100/B200 index, 15-minute values, per-provider receipts | Keyless JSON API | Data CC BY-NC 4.0; not for settlement or products | **Collector `cgi`**; history backfilled from 2026-08-30 |
| GetDeploying | Weekly medians by billing type, 53 weeks | Keyless CSV | CC BY 4.0 | **Collector `getdeploying`** (index rows) |
| gpurentalprices.com | Daily per-provider offers with source URLs | Keyless JSON; archive on raw.githubusercontent.com | CC BY 4.0 | **Collector `gpurentalprices`**; archive backfilled 2026-07-19 to 2026-10-04; Zenodo archive 2026-07-05 to 07-18 (D48) |
| Lium | Marketplace reference price plus listed/rented/idle GPUs | Keyless JSON advertised in robots.txt | No restriction found | **Collector `lium`** |
| Nebius | List prices by platform and region | Markdown docs page | No scraping clause | **Collector `nebius`** |
| Lambda | On-demand list prices by instance size | HTML | No scraping clause in website terms; AUP requires rate-limited crawling | **Collector `lambda`** |
| CoreWeave | On-demand and spot prices by region | HTML | Non-commercial use permitted; no anti-bot clause | **Collector `coreweave`** |
| Hyperstack | On-demand and reserved list prices | HTML | No scraping clause | **Collector `hyperstack`** |
| Verda (DataCrunch) | On-demand and spot list prices | HTML | Bans only "malicious automated use" | **Collector `verda`** |
| Vast.ai | Marketplace offers; public 90-day feed | Keyless API and feed | **Terms prohibit automated collection and any index or benchmark use**; feed licence requires a data licence | **Not collected** (B5). Collector code kept behind a licence flag |
| RunPod | List prices | Public page; API needs a key | **Terms prohibit automated access and building a database** | **Not collected** (B6) |
| Together AI | On-demand, spot and reserved prices | HTML | Terms on its Services ban "competitive analysis or benchmarking" | **Not collected directly** (conservative; D16). Its prices still arrive through CGI and gpurentalprices.com |
| FLOPS Index | Independent index on a 6-hour grid | Keyless public catalog | No public terms found (`/terms` returns 401); README says proprietary | **Not collected** until terms are confirmed (B9) |
| Ornn OCPI | Transaction-based index | Blocked by this environment's egress policy | Unknown | **Not reviewed** (B10) |
| SemiAnalysis | Hourly composite | JavaScript page | Proprietary | View only |
| Crusoe, Jarvislabs | List prices | HTML | Crusoe terms forbid reproduction without permission; Jarvislabs terms unreadable | Manual reading only |
| Shadeform | Aggregated offers | API needs a key | Terms ban scrapers | Not collected |
| GitHub price trackers (cherielilili, Zeno00-00, xcidjazz) | Archived prices | raw files | No licence, or scraped against source terms | Not used |

## Equity market data for claim 4 (Alpaca)

Added 2026-10-05 for claim 4 (docs/claim4_plan.md). Checked in
docs/env_check_claim4.md.

| Source | What it gives | Access | Terms verdict | Status in this repo |
|---|---|---|---|---|
| Alpaca market data API (`data.alpaca.markets`) | Daily OHLCV bars for US stocks and ETFs; consolidated (SIP) history except the latest 15 minutes on the free plan | API key from the owner's paper account, read from the environment | Personal, non-commercial use; no copying or uploading for publication or distribution; no redistribution | **Fetched at run time into git-ignored `var/market_data/`; never committed** (D29). Only a manifest with counts and a hash is committed |
| Alpaca paper trading API (`paper-api.alpaca.markets`) | Simulated account, orders, positions, trading calendar | Same key; paper endpoint only | Same terms | **Paper adapter** `compute_curve.claim4.alpaca`, hard-fails off the paper endpoint (D30) |

## AWS GPU spot price history for claim 5 (Zenodo)

Audited 2026-10-06 for claim 5 (docs/claim5_plan.md).

| Item | Finding |
|---|---|
| Dataset | "AWS Spot Price History", Eric Pauley, University of Wisconsin-Madison. Zenodo concept record 14254112; current version **2026-09**, record 23082767, DOI 10.5281/zenodo.23082767, published 2026-10-01. Updated on the 1st of each month with the previous month |
| Licence | **Creative Commons Attribution 4.0** (`cc-by-4.0` on the record). Reuse, adaptation and redistribution are allowed with attribution and an indication of changes. Research use is permitted |
| Attribution to show | "Eric Pauley (University of Wisconsin-Madison), "AWS Spot Price History", Zenodo, version 2026-09, https://doi.org/10.5281/zenodo.23082767, CC BY 4.0", plus "filtered and aggregated by compute-curve" |
| Format | One zstd-compressed TSV per month in the format of AWS `describe-spot-price-history`: availability zone ID, instance type, product description, USD per instance-hour, timestamp. Each month starts with the price in effect at 00:00 UTC on the 1st |
| Coverage | `2022.tsv.zst` (110 MB) and `2023.tsv.zst` (511 MB) cover default regions only; monthly files 2024-01 to 2026-02 and 2026-07 to 2026-09. **2026-03 to 2026-06 are missing** from the current version. 31 files, 5.16 GB in total; monthly files are 81 to 267 MB |
| Access | Zenodo robots.txt disallows `/api` except `/api/records/*/files` and sets `Crawl-delay: 10`. Metadata was read from the record's landing page; files come from `/records/<id>/files/<name>`. Both are allowed |
| Used here | 20 monthly files, 2024-10 to 2026-09 (3.7 GB), the months the pre-registered sample needs. MD5-verified, read-only, kept in git-ignored `var/aws_spot/raw/` (D36). Filtered to A100/H100/H200/B200/B300 instance types in US availability zones (`use1`, `use2`, `usw1`, `usw2`) on Linux/UNIX |
| Committed | `reports/claim5/aws_spot_daily.csv` (per day and GPU class: pools, median USD per GPU-hour, IQR of log price) and `reports/claim5/aws_spot_manifest.json` (files, checksums, rows kept, coverage) |
| Caveat | The timestamps are when AWS changed the price; the archive was collected monthly. Backtests assume AWS published each price in real time, through its API, and never revised it. This is plausible but not verified |

## Rules applied to every collector

- robots.txt is fetched and obeyed before any request; a host whose robots.txt
  cannot be read is treated as disallowed.
- At least 2 seconds between requests to the same host. One fetch per source
  per day by default.
- A descriptive User-Agent: `compute-curve-research/0.1 (non-commercial research)`.
- No credentials are sent to any source.
- Providers whose own terms prohibit automated collection or index use
  (Vast.ai, RunPod) are dropped even when their prices arrive through an
  aggregator (D13). This is stricter than the audit's suggestion, which was
  to rely on the aggregators' licences.
- Host-identifying fields (IP addresses, hostnames) are never stored.

## Licence obligations for stored data

| Source | Licence | Attribution to show in any output |
|---|---|---|
| Computable GPU Index | CC BY-NC 4.0 | "Computable GPU Index (CGI), (c) 2026 Computable, https://github.com/getcomputable/gpu-index, licensed CC BY-NC 4.0". Non-commercial use only; not for settlement or in a product |
| GetDeploying | CC BY 4.0 | "GetDeploying, GPU rental price history, https://getdeploying.com/gpus, CC BY 4.0" |
| gpurentalprices.com | CC BY 4.0 | "GPU rental price data by gpurentalprices.com, CC BY 4.0" |
| Provider list prices (Lium, Nebius, Lambda, CoreWeave, Hyperstack, Verda) | Public list prices | Cite the provider page |

If this repository is ever made public or used commercially, re-check these
terms first. The CGI data in particular is non-commercial only.

## Data held after the first run (2026-10-05)

| Dataset | Rows | Span |
|---|---|---|
| Live listings from 9 sources | 192 | 2026-10-05 snapshot |
| gpurentalprices.com archive | 78 daily snapshots | 2026-07-19 to 2026-10-04 |
| CGI 15-minute index values | about 3,530 per GPU | 2026-08-30 to 2026-10-05 |
| GetDeploying weekly medians | 53 weeks per GPU and billing type | 2025-10-06 to 2026-10-05 |

All of it is under `data/raw/` as immutable Parquet. The collection log is
`data/collection_log.jsonl`.

## Data quality notes

- **Index levels disagree.** On 2026-10-05 the H100 readings were: Silicon
  Data 2.81, FLOPS 2.99, GetDeploying weekly median 3.41, CGI 3.62, our
  headline index 3.20 (USD per GPU-hour). B200: Silicon Data 5.87, FLOPS
  5.10, GetDeploying 6.79, CGI 6.94, our headline 6.25. Any proxy for the
  settlement index needs its basis calibrated against licensed history.
- **The settlement reference is not the public number.** The contracts use
  SD-H100/SD-B200 with "Geography: United States", averaged over Business
  Days. The public SDH100RT is described as a global neocloud reading.
- **Silicon Data level breaks.** History was restated on 2025-12-04, and
  provider membership changed on 2026-04-06, 2026-07-15 and 2026-09-25
  (impacts up to 7%). Any model fitted across these dates must treat them
  as breaks.
- **GetDeploying back-fill.** The first weeks from 2025-10-06 repeat identical
  medians and counts, which suggests filled rather than observed values. Treat
  the early part of that series with caution.
- **gpurentalprices.com coverage expanded** on 2026-10-03 and 2026-10-04
  (from about 22 to 37 providers). The fixed-panel history series removes
  this composition change (docs/index_methodology.md).
- **List prices are sticky.** Our H100 history-panel index is unchanged on
  88% of days. Daily list-price changes are rare; the settlement index's
  methodology (basis adjustment, provider means, weekly recalibration) moves
  more often.

## Follow-ups for the owner

1. Silicon Data: ask for research access to the US-geography, business-day
   SD-H100/SD-B200 settlement series, or export history from a Bloomberg
   terminal (`SDH100RT Index`, `SDB200RT Index`) if one is available. Save it
   as CSV under `data/manual/published_index/` (format in README).
2. Vast.ai: email data@vast.ai about a non-commercial research licence. Only
   then add `vast` to `collectors.licensed`.
3. FLOPS Index: ask team@flopsindex.com whether research collection of the
   public catalog is permitted.
4. CME: once GPU1/GPU2 list, download daily settlements under your own CME
   account and drop them in `data/manual/cme_settlements/`.
5. Done 2026-10-10 (D48): the Zenodo record 21435394 (gpurentalprices.com,
   2026-07-05 to 2026-07-18, CC BY 4.0) was imported in one request.
