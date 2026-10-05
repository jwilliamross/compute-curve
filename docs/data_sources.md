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
| gpurentalprices.com | Daily per-provider offers with source URLs | Keyless JSON; archive on raw.githubusercontent.com | CC BY 4.0 | **Collector `gpurentalprices`**; archive backfilled 2026-07-19 to 2026-10-04 |
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
5. Optional backfill: the Zenodo record 21435394 covers gpurentalprices.com
   for 2026-07-05 to 2026-07-18 (CC BY 4.0). It was not fetched because
   Zenodo sets a 10-second crawl delay and serves a zip archive.
