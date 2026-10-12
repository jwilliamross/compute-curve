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
| Azure Retail Prices API | Azure H100 and H200 VM prices by region: on-demand, spot, and 1- or 3-year reservations | Keyless JSON API (`prices.azure.com`), OData filter, paged | Microsoft documents unauthenticated use for "internal analysis and price comparison"; no robots.txt (404) | **Collector `azure_retail`** from 2026-10-10 (D50). Hyperscaler, so `index.exclude_providers` keeps it out of our index |
| FastGPU open dataset | Live offers from about 29 providers (neoclouds, marketplaces, hyperscalers): per-GPU price, GPUs per instance, `available_count` | Keyless CSV file `/api/v1/dataset/gpu-prices-current.csv` | Dataset files CC BY 4.0; robots.txt allows `/api/v1/dataset/`; site terms forbid automated collection from the rest of the site | **Collector `fastgpu`** from 2026-10-10 (D51). Vast.ai and RunPod rows dropped |
| GPU Price Tracker (Alex Hubbard), Hugging Face `afhubbard/gpu-prices` | Twice-daily listings scraped with `gpuhunt` from 13 providers (hyperscalers, Lambda, Verda, Nebius, Cudo, CloudRift, Daytona, TensorDock, Vast.ai, RunPod, Oracle, Vultr): SKU price, GPUs per SKU, spot flag, region | Hive-partitioned Parquet on huggingface.co (`prices/dt=YYYY-MM-DD/`); keyless | Data CC BY 4.0 (dataset card and upstream `DATA_LICENSE`); huggingface.co robots.txt allows `/` | **One-off backfill `gpuprices_hf`** (D54). Only snapshots the hub held by the end of the next UTC day: 2026-05-07 onward, with gaps. Vast.ai, RunPod, Oracle and Vultr rows dropped. Not in `history_sources` |
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
| Dataset | "AWS Spot Price History", Eric Pauley, University of Wisconsin-Madison. Zenodo concept record 14198917 (corrected 2026-10-10: 14254112 is version 3, "2024-11"); current version **2026-09**, record 23082767, DOI 10.5281/zenodo.23082767, published 2026-10-01. Updated on the 1st of each month with the previous month |
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
| FastGPU open dataset | CC BY 4.0 | "Data: FastGPU GPU cloud pricing dataset (https://fastgpu.co/dataset), CC BY 4.0." Credit FastGPU with a link, and say the data was filtered by compute-curve |
| GPU Price Tracker (Hugging Face) | CC BY 4.0 | "GPU Price Tracker by Alex Hubbard, CC BY 4.0" (https://huggingface.co/datasets/afhubbard/gpu-prices; code and methodology at https://github.com/alex-hubbard/gpu_price_tracker). Say the data was filtered and converted to per-GPU prices by compute-curve |
| Azure Retail Prices API | Microsoft public retail prices; no data licence stated | "Microsoft Azure Retail Prices API, https://prices.azure.com/api/retail/prices". These are Microsoft retail prices without discount |
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
- **Azure H200 spot meters equal on-demand.** On 2026-10-10 every
  `ND96isrH200v5 Spot` meter had the same price as the on-demand meter in
  the same region. They are stored as published. Do not treat Azure H200
  spot as a spot price until the two differ.
- **FastGPU rows enter the headline index**, not the fixed-panel history
  series, from 2026-10-10, at the lowest source priority (D51). Its region
  column was blank on every H100/H200/B200 row on 2026-10-10.
- **GPU Price Tracker spot rows look odd for some providers.** Nebius
  spot rows on 2026-10-10 include H200 at 0.79 and B200 at 0.99 USD per
  GPU-hour, far below every other source. Azure H200 spot equals on-demand,
  as in `azure_retail`. Stored as published (`gpuprices_hf`); check them
  before using spot rows from this source. Every kept row has
  `available = true`, so its availability carries no information.
- **List prices are sticky.** Our H100 history-panel index is unchanged on
  88% of days. Daily list-price changes are rare; the settlement index's
  methodology (basis adjustment, provider means, weekly recalibration) moves
  more often.

## Azure Retail Prices and FastGPU (reviewed 2026-10-10)

Both sources were reviewed first-hand on 2026-10-10 from the publishers' own
pages. Requests made for the review:

- Microsoft: the documentation page, four VM size pages,
  `prices.azure.com/robots.txt` and four small discovery queries (one got
  HTTP 429);
- FastGPU: robots.txt, `/dataset`, `/legal/terms` (`/terms` is a 404) and
  one download of the current snapshot file;
- Zenodo: robots.txt and the record page.

Nothing else was fetched.

### Azure Retail Prices API (`azure_retail`, D50)

| Item | Finding |
|---|---|
| Terms, verbatim | Microsoft, "Azure Retail Prices overview" (learn.microsoft.com, `rest/api/cost-management/retail-prices/azure-retail-prices`, last updated 2024-08-07): "This API gives you an unauthenticated experience to get retail rates for all Azure services. Use the API to explore prices for Azure services against different regions and different SKUs. The programmatic API can also help you create your own tools for internal analysis and price comparison across SKUs and regions." Also: "Prices shown in USD currency are Microsoft retail prices." |
| robots.txt | `https://prices.azure.com/robots.txt` returns 404, so nothing is disallowed |
| Rate limit | Bursts get HTTP 429 with the headers `x-ms-ratelimit-retailprices-retry-after: 60` and `x-ms-ratelimit-remaining-retailprices-requests`. A 4th request about 9 seconds after the 1st was refused. The collector spaces pages by 6 seconds and retries a 429 once, after the advertised wait (at most 90 seconds) |
| Query | One OData filter: `serviceName eq 'Virtual Machines'`, `priceType` Consumption or Reservation, and `armSkuName` equal to one of the five mapped SKUs. About 850 meters fit in one page. The API returns up to 1,000 items per page and links the next page with `NextPageLink`; at most 10 pages are followed. A run makes 1 or 2 requests plus robots.txt |
| Kept | Linux meters only (Windows meters include an OS licence; DevTest meters are not public prices). Primary meter regions only, no "Low Priority" meters, USD only |
| Terms mapping | `Consumption` is on-demand, or spot when the meter name ends in "Spot". `Reservation` is reserved; the term (1 or 3 years) goes in `listing_id` and `price_basis` |
| Price per GPU-hour | VM price per hour / GPUs per VM. Reservation prices are the total for the term. They are converted with 8,760 hours per year (**assumption**; Azure's calculator uses 730 hours per month) |
| Region | Coarse code from `location` ("US East" gives `US`). `armRegionName` is kept in `listing_id` and `raw_json` |

GPUs per VM, mapped only for SKUs whose count Microsoft's size pages state
(learn.microsoft.com, `azure/virtual-machines/sizes/gpu-accelerated/<page>`,
read 2026-10-10):

| armSkuName | GPUs | Page and wording |
|---|---|---|
| Standard_ND96isr_H100_v5 | 8 H100 (80 GB, NVLink 4.0) | `ndh100v5-series`: "starts with a single VM and eight NVIDIA H100 Tensor Core GPUs"; accelerator table: 8 |
| Standard_NC40ads_H100_v5 | 1 H100 NVL (94 GB) | `ncadsh100v5-series`: "up to 2 NVIDIA H100 NVL GPUs"; accelerator table: 1 |
| Standard_NC80adis_H100_v5 | 2 H100 NVL (94 GB) | same page; accelerator table: 2 |
| Standard_NCC40ads_H100_v5 | 1 H100 NVL (94 GB) | `nccadsh100v5-series`: "These VMs feature 1 NVIDIA H100 NVL GPUs"; accelerator table: 1 |
| Standard_ND96isr_H200_v5 | 8 H200 (141 GB) | `nd-h200-v5-series`: "starts with a single VM and eight NVIDIA H200 Tensor Core GPUs"; accelerator table: 8 |

Not mapped, so not requested:

- `Standard_ND96is_H100_v5`, `Standard_ND96is_flex_H100_v5`,
  `Standard_ND96is_noIB_H100_v5`, `Standard_ND96isf_H100_v5`,
  `Standard_ND96isrf_H100_v5` and `Standard_ND96isrf_H200_v5`: no public
  size page was found;
- the GB200 SKUs `Standard_ND128isr_NDR_GB200_v6` and
  `Standard_ND128isrf_NDR_GB200_v6`: Grace-Blackwell is a different product
  from B200.

The API listed no B200 or B300 SKU on 2026-10-10.

### FastGPU open dataset (`fastgpu`, D51)

| Item | Finding |
|---|---|
| Licence, verbatim | fastgpu.co/dataset: "The dataset is licensed under Creative Commons Attribution 4.0 International (CC BY 4.0). Use it in products, research, or reporting, even commercially. The only requirement is attribution: credit FastGPU with a link. This license covers the published dataset files only, not automated access to the live site (see the Terms)." Zenodo record 23132958 (version 2026-10-04 of concept DOI 10.5281/zenodo.22842387) carries the licence `cc-by-4.0` |
| Terms, verbatim | fastgpu.co/legal/terms. Section 5: users may not "use any automated means, such as bots, scrapers, or crawlers, to access or collect data from the Service, except as expressly permitted by us or by applicable law". Section 7, Open data: "That published dataset, and only that dataset, is made available under the Creative Commons Attribution 4.0 International (CC BY 4.0) license ... This open license applies solely to the published dataset files and does not grant any right to scrape, crawl, or otherwise bulk-extract data directly from the Service." Section 18: "Where it allows something that sections 5 or 7 restrict, this section applies to the data it covers." It defines "The open dataset" as "The files published at /dataset (the current snapshot and the rolling daily price history) and their archived copies", and says of web pages: "Collecting data from the pages by automated means is restricted by section 5. To work with the data, use the open dataset or the API instead." |
| Express permission to load the file | The dataset page says "Load it directly, no download needed:" followed by `pandas.read_csv("https://fastgpu.co/api/v1/dataset/gpu-prices-current.csv")` |
| robots.txt | `User-Agent: *` has `Allow: /`, `Allow: /api/v1/dataset/` and `Disallow: /api/`. A second group disallows everything for named AI crawlers (GPTBot, Google-Extended, CCBot, ClaudeBot, anthropic-ai and others). Our collector identifies as `compute-curve-research/0.1` and falls under `*` |
| What is fetched | Only `gpu-prices-current.csv`, which the terms call "the current snapshot". One request per run. The daily-history and fixings files are not used. The fixings file is not in the terms' list of open-dataset files. Its floors can also be set by Vast.ai or RunPod offers, which cannot be removed from an aggregate |
| Columns | provider, provider_label, gpu_model, gpu_slug, vram_gb, offer_type, region, price_usd_hr (per GPU), min_gpu_count, available_count, interconnect, source_url, fetched_at. No host-identifying fields |
| Kept | H100, H200 and B200 rows (GB200, GH200 and B300 are out of scope). Vast.ai and RunPod rows are dropped (D13), and so are serverless offers and rows without a price. `available_count` is kept in `raw_json`: 0 maps to `unavailable`, a positive count to `available`, and a blank to `unknown` |
| Price basis | The publisher's per-GPU rate. The dataset notes that Modal, Cudo Compute, TensorDock and Daytona price the GPU alone; their rows get `price_basis = gpu_only` |

## GPU Price Tracker on Hugging Face (`gpuprices_hf`, reviewed 2026-10-11, D54)

Reviewed first-hand on 2026-10-11. Requests made for the review, at least
4 seconds apart:

- huggingface.co: robots.txt, the dataset card (`README.md`), the dataset
  API record, the commit history (5 pages, 240 commits), the `prices/` tree
  at main and at each of the 240 commits, 8 current and 2 older sample
  files;
- raw.githubusercontent.com: `methodology.md`, `README.md`, `LICENSE`,
  `DATA_LICENSE`, `CITATION.cff` and `.github/workflows/daily_update.yml` of
  `alex-hubbard/gpu_price_tracker` (main).

github.com and api.github.com are blocked by this environment's proxy (403),
so the upstream repository's own commit history could not be read.

| Item | Finding |
|---|---|
| Licence, verbatim | Dataset card front matter: `license: cc-by-4.0`; its "License" section: "CC BY 4.0." Upstream `DATA_LICENSE`: "The pricing dataset published by this project (the contents of s3://hubbard-gpu-price-data/prices/ and any mirror, including the Hugging Face Datasets repository) is made available under the Creative Commons Attribution 4.0 International License (CC BY 4.0)." Suggested attribution: "Hubbard, A. (2026). GPU Price Tracker dataset. https://github.com/alex-hubbard/gpu_price_tracker (CC BY 4.0)." Code is MIT |
| robots.txt | `https://huggingface.co/robots.txt`: `User-agent: *` / `Allow: /`. raw.githubusercontent.com has no robots.txt (404). File downloads redirect to Hugging Face's CDN |
| How the publisher collects | "collected twice daily since January 2026 by scraping provider pricing surfaces via the [`gpuhunt`] library" (card). Methodology: a GitHub Actions cron at about 09:00 and 21:00 UTC; snapshots are "append-only Parquet files with names containing the snapshot timestamp". The README also describes a local twice-daily scheduler writing to SQLite. The data hold both: CI files (stamped about 09:00 and 21:00, with `git_sha` and `gpuhunt_version` in the file metadata) and local files (irregular stamps, more rows including CPU-only SKUs) |
| Columns | timestamp, provider, instance_type, gpu_type, gpu_count, gpu_memory_gb, vcpus, ram_gb, region, price_per_hour, is_spot, available, availability_zone, quality, region_canonical, country, region_lat, region_lon, region_group. No host-identifying fields, except that Vast.ai `instance_type` values are offer ids (Vast.ai rows are dropped) |
| Price basis | Card: "`price_per_hour` ... USD/hr for the full SKU"; "Compute `price_per_gpu_hour = price_per_hour / gpu_count`". Confirmed in the data: Lambda `gpu_8x_h100_sxm5` is 31.92 and `gpu_1x_h100_sxm5` 4.29 on 2026-10-10; Daytona 8x H100 is 48.0068 = 8 x 6.0008 |
| Schema v1.1 in-place upgrade | Methodology: "All previously published snapshot files were upgraded in place to v1.1 ... upgraded files carry `backfilled = true`". Every pre-2026-07-08 local file carries `backfilled = true` and `emitted_at_utc` 2026-07-08T22:0x. Two upgraded files (2026-05-08T10:20 and 2026-06-22T14:39) were compared with their versions at commit `7c784c66` (2026-07-08T11:05, before the upgrade): identical rows on provider, instance_type, gpu_type, gpu_count, region, price_per_hour, is_spot and available (49,999 and 50,956 rows). The upgrade added columns only, in these two files |
| Coverage on the hub | 371 snapshot files in 202 partitions, 2026-01-12 to 2026-10-10. Gaps: 2026-01-19, 2026-03-10 to 05-06 and isolated days. 85.7 MB in total for all GPUs |

### Provenance: when each file reached the hub

The repository was created on 2026-05-07T20:17:55Z (API `createdAt`). For each
of the 240 commits the `prices/` tree was listed, giving the first commit that
held each file:

| Files | Stamped | First on the hub | Lag |
|---|---|---|---|
| 51 local files | 2026-01-12T19:14 to 2026-03-09T09:43 | all in the first upload, 2026-05-07T20:26:07Z | 2 to 4 months |
| 85 CI files | 2026-05-08T09:00 to 2026-07-07T21:00 | all on 2026-07-08T22:31Z (the day the card was updated and `CITATION.cff` released v1.1) | 25 hours to 61 days |
| 235 others (local files from 2026-05-07T20:40, all files from 2026-07-08) | 2026-05-07 to 2026-10-10 | usually the sync commit of the same run | at most 13.5 hours (median 13 seconds) |

The CI files carry an `emitted_at_utc` a few hours after their stamp, which
points to contemporaneous collection with a late upload to Hugging Face (the
workflow also syncs to S3). That metadata is the publisher's own statement and
cannot be checked here.

**Rule applied.** A file is imported only if the hub held it at the last
commit before the end of the next UTC day (`publication_cutoff`: day + 2 at
00:00 UTC). It keeps 237 files: the 235 published within 13.5 hours, and the
two CI files of 2026-07-07 (lags 37.5 and 25.5 hours, uploaded before
2026-07-09 00:00). It skips 134. The 2026-01-12 to 03-09 history is therefore
**not imported**, and neither are the CI files of 2026-05-08 to 07-06. Local
files from those days are imported, so most of them still have one snapshot.
The check runs on every backfill (one tree request per day at the chosen
commit).

### Imported (2026-10-11)

Command: `compute-curve backfill gpuprices-hf --start 2026-01-12 --end 2026-10-10`.

| Item | Count |
|---|---|
| Days written | 148, 2026-05-07 to 2026-10-10 (one Parquet per day, 4.9 MB in total) |
| Days skipped | 54 partition days with no verifiable file (51 in January to March, 3 in May and June); 70 calendar days with no partition |
| Snapshot files | 237 downloaded, 134 skipped as unverified |
| Rows kept | 183,929: H100 127,927, H200 26,218, B200 29,784 |
| By provider | gcp 68,725; azure 39,199; lambda 35,238; verda 18,460; aws 15,889; nebius 5,688; daytona 672; cudo 58 |
| Rows dropped | Oracle 28,908; RunPod 8,540; Vast.ai 4,026; Vultr 0 (no H100/H200/B200 rows); quality not `ok` 0 |

**Effect on our index (checked 2026-10-11).** With the defaults the
fixed-panel history series is unchanged (it reads `history_sources` only).
The headline series is unchanged on every day that meets coverage: Lambda,
the main neocloud in this source, is already reported on those days by a
higher-priority source, and the source's other neoclouds list mostly outside
the US. It gains 112 rows on 2026-05-07 to 07-04, none of which meets
coverage, and one uncovered value changes (B200 on 2026-07-05).

### What is kept

- H100, H200 and B200 rows (`gpu_type` H100, H100NVL, H200, H200NVL, B200)
  with `quality = 'ok'`. GB200, GH200, B300 and other families are out of
  scope. A100 is not kept: the schema has no A100 model.
- Dropped providers: Vast.ai and RunPod (D13); Oracle (`oci`) and Vultr,
  because their direct collection was rejected on terms (above).
  Hyperscaler rows (aws, azure, gcp) are kept; `index.exclude_providers`
  keeps them out of our index.
- `term`: spot if `is_spot`, else on-demand. The methodology warns that spot
  semantics differ by provider.
- `availability` from `available` (true, false, null). It was true on every
  kept row checked; the methodology calls it best-effort.
- `region`: the publisher's ISO `country` where given, else the coarse code
  from the raw region (`normalize_region`). The raw region, canonical region
  and region group stay in `raw_json`, with the source file path (`hf_path`).
- `gpu_variant`: NVL for the NVL types, else from the SKU name (Lambda
  `sxm5`, `pcie`; Nebius `sxm`), else UNKNOWN.
- `price_usd_per_gpu_hour = price_per_hour / gpu_count`;
  `price_basis = instance_hour_list_div_gpus`.
- `ts_source` is the row's `timestamp`; `ts_observed` is when we downloaded
  the file (2026-10-11). Each upstream snapshot keeps its own `snapshot_id`,
  so the index takes the latest snapshot of a day.

## Candidates (2026-10-10, not collected yet)

A data-source agent searched for more H100/B200 price history on 2026-10-10.
Its notes are unverified until each source is reviewed again here.

**No free history older than 2026-07-05 was found.** The candidates below
add data from today forward.

FastGPU and the Azure Retail Prices API were reviewed first-hand on
2026-10-10 and are now collected (previous section; D50, D51).

| Source | What it adds | Licence and terms (agent's reading) | Status |
|---|---|---|---|
| Lium `pricing.json` (hourly) | Hourly prices | robots.txt describes the file as hourly. No history: Grafana needs a login and `/api/` is disallowed | Already collected daily; hourly polling would need a scheduler |
| AWS Price List Bulk API | p5/p6 on-demand list prices back to 2015 | AWS Site Terms ban "data mining, robots" on the AWS Site. About 254 MB per month | Owner decision needed |
| Akash Console API | Daily H100 total, leased and utilization since about 2024-10 | Its terms ban "any robot, spider, or other automatic device". About 6 test requests were made before the terms were read; nothing was stored | **Rejected**; ask Overclock Labs for written permission (B13) |

**Rejected by terms or robots.txt:**

- Voltage Park, Prime Intellect, Thunder Compute, Denvr, Hyperbolic, Oracle
  and DigitalOcean;
- the Vultr, Scaleway and gpuperhour.com API hosts;
- Zenodo 22053861 (built from Vast.ai data);
- the AWS Spot Advisor JSON;
- the SkyPilot catalog (no licence file).

The Wayback Machine could not be reached from this environment.

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

## Wayback Machine archived pricing pages (`wayback_<provider>`, D58, 2026-10-12)

- **What.** Dated captures of the live pricing pages approved above: Lambda,
  CoreWeave, Nebius, Hyperstack and Verda. Only captures with distinct
  content (CDX `collapse=digest`) are fetched, at least 4 s apart, with a
  robots.txt check.
- **Extraction.** Claude proposes prices. Only rows whose verbatim quote and
  price are found on the page are kept. Details: docs/wayback_backfill.md.
- **Storage.** `data/raw/archive/`, research-only, never in the own index
  without pre-registration. No host-identifying fields.
- **Terms.** The Internet Archive's use condition (non-infringing or fair
  use; docs/data_costs.md §7) plus each provider's own terms, which were
  already accepted for the live pages. Never Vast.ai, RunPod or Together.
- **Reachability.** Not reachable from the agent sandbox; runs from GitHub
  Actions only.
