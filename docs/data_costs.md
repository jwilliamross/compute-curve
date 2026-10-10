_Research notes by a data-source agent, 2026-10-10, kept as written. [V] = read first-hand, [S]/[U] = unverified. Nothing here was bought, signed up for or bulk-downloaded._

# R4: more GPU price history, what each route costs

Date: 2026-10-10. Researcher: data-source subagent. The repository was not modified.

Scope: every realistic route to more H100/B200 rental-price history (and A100/H200 as
proxies), GPU availability data and related index data, with costs and licence terms.

Rules followed: no sign-ups, purchases, form submissions or log-ins. robots.txt was read
before fetching from each host, and requests to the same host were at least 3 s apart.
No bulk data was downloaded: only pages, READMEs, licence files and small metadata or
index files (the largest was the 28 kB AWS version index). HEAD requests were used for
file sizes.

Labels:
- **[V]** read first-hand today from the publisher's own page or file.
- **[S]** search-engine snippet or third-party page only. Unverified.
- **[U]** an unverified number or estimate.

---

## 0. Bottom line

1. **No free route to the settlement index's history exists.** Silicon Data's terms forbid
   storing its content. The $998/month Pro plan has full history in the dashboard but no
   CSV/API export. Downloads and API are Enterprise-only, priced by quote. The realistic
   routes are:
   - an Enterprise or research licence from Silicon Data;
   - a university Bloomberg or LSEG export, under that library's licence.
2. **There is one new free source that extends history back to January 2026:** the Hugging
   Face dataset `afhubbard/gpu-prices` (CC BY 4.0). It holds twice-daily listings from 13
   providers, starting 2026-01-12. That is about 6 months older than our current history
   start of 2026-07-05.
3. **There is one new free source for hyperscaler list prices since 2015:** the AWS Price
   List Bulk API keeps 123 historical EC2 price-list versions, from 2015-12 to 2026-10.
   AWS documents that these versions can be downloaded.
4. **Ornn (OCPI) is now reachable.** This partly resolves B10. Ornn is the best-value
   transaction-based alternative:
   - Premium costs $500/month and includes all-time daily history and an API.
   - A free 72-hour "Research Grant" trial exists.
   - Ornn offers "one-off historical extracts" for backtesting on request.
   - Its terms require deleting the data when access ends, so ask for written retention
     rights.
5. **GetDeploying sells per-provider weekly history from mid-2024** through its API, at
   $299/month or $2,499/year. This is the cheapest paid route to two years of multi-provider
   H100/B200 history. Because the rows are per provider, Vast.ai and RunPod can be dropped
   (D13), which is not possible with its free aggregated CSV.
6. **CME:** the CFTC extended its review of GPU1/GPU2 to the end of **2026-11-09** [V]. No
   futures history exists yet.

---

## 1. Settlement index and competing indices

### 1.1 Silicon Data (SD-H100 `SDH100RT`, SD-B200 `SDB200RT`, SD-A100 `SDA100RT`, H200 portal-only)

| Item | Finding |
|---|---|
| History | Full history "back to each index's launch date" [V, index-datasets page]. Starts per the repo audit: H100 2024-09-01, B200 2025-08, H200 2026-05-04 |
| Plans [V, silicondata.com/pricing, 2026-10-10] | **Basic: free** with sign-up, "SiliconIndex™ 30 days history". **Pro: "$998 / Month", "7-day trial", "No credit card required"**: "GPU, RAM & Token indices — full history" in the dashboard. Pro's download row reads "Download image / chart: Dashboard visuals" only. **Enterprise: "Custom"**: "Full History", "API & CSV download", "Data Product Add-Ons: Downloadable data, raw exports, full history" |
| Note | A search-engine snippet claimed "Pro $499/month … 90-day historical pricing" [S]. That is stale or garbled; the live page says $998 |
| Licence [V, index-datasets FAQ] | "Settlement reference and redistribution are licensed separately from data access — the subscription covers internal use." |
| Site terms [V, /terms-of-use] | "You may download the Site Contents for personal and non-commercial use … No Site Content or any part thereof may be modified, reverse-engineered, reproduced or distributed in any form by any means, or stored in a database or retrieval system, without the prior written consent of Silicon Derivatives." |
| robots.txt | `Allow: /` |
| Distribution | Bloomberg (`SDH100RT`, `SDA100RT`, `SDB200RT`, `SDLLMTK` [V]). Refinitiv/LSEG via dxFeed: H100 and A100 "accessible to Refinitiv users" by end of July 2025 [V, press release 2025-10-08]. Kaiko (named as partner [S]) |
| Academic programme | None found [S]. The contact page lists **support@silicondata.com** [V] and a sales form (not submitted) |
| Free? | Only the 30-day Basic dashboard (sign-up) and the latest public values, which may not be stored |
| **Recommendation** | **ASK OWNER TO REQUEST** a research licence (template in §8). **PAID: Pro is NOT worth it**: it has no export, and the terms forbid storing values copied from the dashboard. Enterprise (quote) is the only paid route that yields stored data |

### 1.2 Ornn Compute Price Index (OCPI): reachable from here today (update B10)

data.ornn.com, index.ornn.com and ornn.com resolve now (they were egress-blocked on
2026-10-05). The data.ornn.com robots.txt allows `/` and disallows `/api/`, `/auth/` and
other paths.

| Item | Finding [V unless noted] |
|---|---|
| What | A transaction-based index: "volume-weighted winsorized mean of executed transaction prices … over a rolling one-hour window". About 150 providers and about 1,000 transactions a day, mostly in the US. Daily reference print over the 24 hours ending 4:00 PM ET. GPUs: H100 SXM, H200, A100 SXM4, B200, RTX PRO 6000 |
| History | "H100 history runs from January 2025 at hourly granularity, with sparser data back to mid-2024 … B200 from November 2025. Earlier, sparser history can be shared on request for diligence and backtesting." Also: "we also fulfill one-off historical extracts while platform backfill catches up." "history is never silently restated" |
| Bloomberg | "The H100 index is available to Bloomberg Terminal subscribers under the ORNNH100 ticker family" |
| Plans (/pricing) | **Index: Free**: "OCPI: 5 public GPUs, daily (three months)", view only. **Premium: "$500 per month"**: "All-time daily index history", "Daily API keys". **Full: Custom**: hourly data and "CSV Dataset exports". **"Research Grants Program — Evaluate Ornn Premium on a research desk for free. A grant is the Premium tier for 72 hours, covering daily grain, every index family, and all-time history."** FAQ: "External distribution of the data is prohibited during a trial. Request one from data.ornn.com/pricing or data@ornn.com." |
| Exports | "CSV and Excel export from charts and tables is Full only". Premium API keys (`sk_prem_`) are "daily-grain only, with complete daily history" |
| Terms (/terms) | Bans: "scrape, crawl, harvest, mine, index, copy, cache, download in bulk, extract, record, monitor, or systematically collect data … except as expressly authorized by the Company in writing". Bans using Company Data to "create … any index, benchmark … dataset, derived data product … without the Company's prior express written consent" |
| Premium Data Use Addendum (effective 2026-08-19) | Permits: "use Company Data for internal research, monitoring, reporting, and decision-making within the named organization" and "for your own trading, hedging". **On ending:** "Upon request, or upon termination of Premium, you must promptly stop using Company Data, delete or return all Company Data in your possession". Also: "Derived data is still Company Data" |
| Contact | **data@ornn.com** |
| Futures | ICE and Ornn announced cash-settled GPU futures on 2026-05-19, "subject to regulatory approval" [S]. Architect's offshore AX exchange lists an `OCPI-H100-PERP` perpetual [S, Nautilus Trader docs]. Live perpetual prices could be a futures-like series, but no public history endpoint was found [S] |
| Free? | Viewing only. Stored history needs Premium, a grant or written permission |
| **Recommendation** | **ASK OWNER TO REQUEST** (1) the free 72-hour Research Grant and (2) written permission to retain the daily OCPI history for non-commercial research, plus the "earlier, sparser history". **PAID: worth it ($500/month) only with retention rights**, because data must be deleted when Premium ends |

### 1.3 SemiAnalysis GPU Spot-Contract Composite Index

- **What [V, gpu-index.semianalysis.com]:** hourly composites for H100, A100 and B200. The
  page also shows term-structure columns from on-demand to 5 years. H100 is on Bloomberg as
  `SAH100SC`. Hyperscalers are "weighted more strongly than marketplaces and neoclouds". The
  H100 index blends in analyst contract surveys.
- **What the public page shows:** latest-month values only (April 2026; for example H100
  $2.82, B200 $3.68).
- **History:** a monthly H100 1-year contract index from 2023. Newsletter quote: "from
  $1.70/hr/GPU in October 2025 to $2.35/hr/GPU by March 2026" [S].
- **Cost:** quote on request. The "AI Cloud TCO Model" is a separately sold Excel workbook
  plus dashboard with one year of quarterly updates, not part of the newsletter [S]. No
  price published.
- **Terms:** none published. robots.txt returns 404, and `api.semianalysis.com` returns 403.
- **Recommendation:** **ASK** sales@semianalysis.com for academic pricing. View only until
  then. **PAID: probably not worth it** for us (quote unknown, likely institutional [U]).

### 1.4 CF Benchmarks: CF H100 Neo-Cloud GPU Compute Index (new, not in the repo docs)

- **What [V]:** methodology guide V1.0, dated 2026-07-28, at
  docs.cfbenchmarks.com/CF GPU Rental Series Methodology Guide.pdf. On-demand single H100
  SXM, USD per GPU-hour. Quotes come from provider and marketplace APIs, aggregated as a
  capped weighted mean with outlier gates. The guide says it is meant as a reference rate
  and, "subject to further development", an input to perpetual contracts.
- **History:** from about late July 2026 only [U].
- **Access, cost and licence:** not reviewed (licensed CF Benchmarks data).
- **Recommendation:** low priority. **ASK** only if it becomes a futures underlier.

### 1.5 Other indices

- **NativX COIL:** an energy-normalised compute index. ICE plans futures on it [S]. No
  public data access found.
- **The Compute Index / Compute Desk:** behind Architect's planned US exchange (H100, H200,
  B200 and B300 rental indexes, "pending regulatory review") [S]. No data access found.
- **AIMultiple GPU index [V, aimultiple.com/gpu-index]:** "weekly price history … spans July
  2024 through September 2026"; monthly medians for 17 GPUs across 75 providers. A "Download
  as CSV" button builds the file client-side. The source data is not named; it probably
  comes from an aggregator [U]. No licence statement found. **ASK** for licence terms.
- **FLOPS Index:** unchanged (B4/B9). **ASK** team@flopsindex.com.

---

## 2. Terminals and data vendors

| Vendor | Carries GPU indices? | Cost | Terms for research and storage | Recommendation |
|---|---|---|---|---|
| **Bloomberg Terminal** | Yes: `SDH100RT`, `SDA100RT`, `SDB200RT` (Silicon Data) [V]; `ORNNH100` (Ornn) [V]; `SAH100SC` (SemiAnalysis) [V] | Not published. About **$31,980 per seat per year on a 2-year contract** [U, CostBench]; another estimate is about $27,660 [U]. API (Data License) priced separately [S] | University terminals: exports count against per-terminal daily and monthly limits (HBS, NYU, Tufts guides [S]). NYU: "data downloaded using the API should not, under any circumstances, be removed from the Bloomberg terminal" [S]. Tufts: "non-commercial, academic research only" [S] | **Best single route if the owner has university access.** One session can export all three providers' histories. **ASK OWNER** to check his library's Bloomberg export policy first. **PAID: not worth it** at about $32k/year [U] for this project |
| **NYPL (public library, NYC)** | Same Bloomberg data | Free with a library card [S] | "Access is for viewing only. Printing, downloading or electronic reproduction of any Bloomberg content or screens is prohibited." [S, libguides.nypl.org] | **NOT ALLOWED** for data capture. Viewing only |
| **LSEG Workspace (Refinitiv)** | H100 and A100 by RIC via dxFeed [V, press release]. RIC `.SDH100RT` per the repo audit. B200 on LSEG not confirmed | Not published. CostBench lists "Eikon Web $300/user/year … Desktop Premium $1,830" and elsewhere "$21,960/user/year": conflicting [U]. Median customer about $15,000/year [U] | University licences: non-commercial academic use. Datastream cap of 10 million data points per user per month at several universities [S] | **ASK OWNER** (university route). **PAID: not worth it** |
| **FactSet, S&P Capital IQ** | No evidence that either carries any GPU rental index (searched; nothing found) [S] | Quote only | n/a | **Skip** |
| **WRDS** | No GPU rental data found [S] | Through the institution | n/a | **Skip** for prices. Useful only for equities through an institution |
| **Kaiko** | Named by Silicon Data as a distribution partner [S] | Quote | Unknown | **Skip**. Same data as Silicon Data, and Silicon Data's licence still applies |
| **dxFeed** | Silicon Data's index-management partner for Refinitiv [V] | Quote | No academic programme found [S] | **Skip** |

---

## 3. CME, other exchanges and futures data

| Item | Finding |
|---|---|
| **GPU1/GPU2 status** | [V, cftc.gov/filings/documents/2026/orgdcmnymexcompcontr260921.pdf, letter dated 2026-09-21]: "the initial review period for the Submission is hereby extended for an additional 45 days, until the end of November 9, 2026." The stated reason is "novel or complex issues" and the pending Request for Comment, 91 FR 54259, whose "comment period clos[es] October 20, 2026". Not listed. No new CME launch date found [S] |
| **CME DataMine** | Daily settlement files "available top day only", overwritten daily [S, CME client wiki]. "Historical end-of-day data … can be purchased from the CME DataMine". Prices are shown only after sign-in. A dated report of about $10,000/year for historical EOD (later withdrawn) [U, Waters] |
| **Recommendation, CME** | When listed: the owner downloads daily settlements manually (B2/B8). **PAID later:** DataMine historical EOD (quote) |
| **Databento** (vendor of CME Globex MDP 3.0) | $125 of free credit on sign-up; historical data "from $0.50/GB", "no monthly license fees" for historical [S]. Its "statistics" schema includes settlement prices and open interest [S] |
| **Recommendation, Databento** | **PAID, cheap and worth it once GPU1/GPU2 list.** Owner sign-up required. Re-check its licence before storing |
| **ICE / Ornn and ICE / NativX** | Announced, "subject to regulatory approval" [S]. No data yet |
| **Architect AX** (Bermuda) | Lists `OCPI-H100-PERP` [S]. Its market data needs an AX account. Not reviewed. **ASK** only if a futures proxy is needed before CME lists |

---

## 4. Marketplaces whose terms prohibit collection

| Source | Data | Licence / terms (quoted) | Route and cost | Recommendation |
|---|---|---|---|---|
| **Vast.ai** | Public feed [V, vast.ai/pricing.md] `storage.googleapis.com/vast-public-gpu-pricing/gpu-pricing-public.json`: per GPU model, min, p10 and median hourly price, offer counts, "up to 90 days of daily median history", updated hourly | "Free for display and citation with attribution. Bulk collection, redistribution, or use in any index, benchmark, or derivative product requires a data license: data@vast.ai." | Licence by quote | **ASK OWNER** data@vast.ai for a non-commercial research licence. With one, a single fetch gives 90 days of daily medians. **NOT ALLOWED** without it |
| **RunPod** | List prices | ToS §6 and §9 ban automated access and building a database (B6) | No data programme found [S] | **ASK** for written permission (contact unverified; use runpod.io contact). Otherwise **NOT ALLOWED** |
| **Akash (Overclock Labs)** | Console API: daily H100 total, leased and utilization since about 2024-10 (B13) | Console terms ban "any robot, spider, or other automatic device" | Free if permitted. **Alternative:** Akash is a public blockchain, and its node and console code are Apache-2.0 [S]. Leases and bids are on-chain, so running our own indexer against a public node could reconstruct GPU leases and prices. This is plausible but unverified [U]; it is heavy work and the node operator's terms need review | **ASK OWNER** Overclock Labs (B13). The on-chain indexer is a later option |
| `thsysmfh/gpu-spot-rental-prices` (HF, CC0, created 2026-08-06) | Weekly medians of Vast.ai asks | Built from Vast.ai data | n/a | **NOT ALLOWED** (D13) |

---

## 5. Open datasets and trackers

### 5.1 NEW: `afhubbard/gpu-prices` (Hugging Face): **GET NOW** (subject to the owner's D13 check)

- **URL:** https://huggingface.co/datasets/afhubbard/gpu-prices. Code and methodology:
  github.com/alex-hubbard/gpu_price_tracker.
- **Licence [V, README and card metadata]:** `license: cc-by-4.0`. The README says
  "## License — CC BY 4.0", with a suggested citation
  `@misc{hubbard2026gpuprices, author = {Alex Hubbard}, title = {GPU Price Tracker}, year = {2026}}`.
- **What [V]:** "cross-cloud GPU rental pricing covering 13 public cloud providers (AWS, GCP,
  Azure, Lambda Labs, RunPod, Vast.ai, DataCrunch, Cudo Compute, TensorDock, Vultr, Oracle,
  Nebius, CloudRift): 3M+ listing observations, 70+ GPU types, collected twice daily since
  January 2026 … via the `gpuhunt` library". Hive-partitioned Parquet files
  `prices/dt=YYYY-MM-DD/*.parquet`.
- **Columns:** timestamp (UTC), provider, instance_type, gpu_type, gpu_count, region,
  price_per_hour, is_spot, **available**, quality, and region_canonical / country.
- **Span [V, HF tree API]:** 202 daily partitions from `dt=2026-01-12` to `dt=2026-10-10`.
  About 70 days are missing [U: count of partitions versus calendar days]. "Files are
  append-only".
- **Size:** 373 files, size category 1M to 10M rows. Not downloaded.
- **Caveats:**
  - The HF repo was created on 2026-05-07, so January to May was uploaded later. Check the
    GitHub commit history to confirm contemporaneous collection (no look-ahead and
    provenance).
  - Files were "upgraded in place" to schema v1.1 in July 2026 and carry
    `backfilled = true`.
  - Vast.ai and RunPod rows must be dropped (D13).
  - Oracle and Vultr were rejected for direct collection in docs/data_sources.md. Decide
    whether to drop them here too; the conservative choice is to drop them.
  - Rows are collected by scraping provider surfaces, but AWS, Azure and GCP come from
    their official price APIs (gpuhunt).
  - Hyperscaler rows should stay out of the index (`index.exclude_providers`).
- **Value:** extends multi-provider listing history about 6 months earlier, and adds an
  availability flag.

### 5.2 NEW: `gpueconomy/cloud-gpu-price-index` (Hugging Face, CC BY 4.0, version 2026-10-02)

- **Own series [V]:** weekly median listed on-demand H100 SXM price from the week of
  2026-09-07, with receipts. Also hourly and monthly files. Short.
- **`price-index-history.csv` [V]:** 90 weeks of a "reconstructed series, second-hand":
  "the weekly median of the cheapest per-GPU on-demand H100 SXM instance per provider **as
  published in skypilot-org/skypilot-catalog** … at most 7 providers". Azure is excluded. It
  starts around January 2025 [U].
- **Caveat:** the README calls skypilot-catalog "(Apache 2.0)". But
  `raw.githubusercontent.com/skypilot-org/skypilot-catalog/master/LICENSE` returns **404**
  [V], as do `LICENSE.md` and `LICENSE.txt`, which matches the repo's earlier finding (no
  licence file). The CC BY 4.0 re-licence of numbers taken from an unlicensed catalog is
  therefore uncertain.
- **Recommendation:**
  - **GET NOW as an exploratory reference only** (CC BY 4.0 on its face; tiny file). Label
    it second-hand. Do not use it in results until the licence question is settled.
  - **ASK** the SkyPilot maintainers (GitHub issue on skypilot-org/skypilot-catalog) to add
    a LICENSE. That would unlock the catalog's whole git history (AWS, GCP, Lambda and
    others, refreshed every 7 hours [V, README]), which is probably the longest free
    multi-provider H100 list-price history (back to 2023 [U]). Cloning github.com is blocked
    here (B11); the owner can clone it locally.

### 5.3 GetDeploying: free CSV (in use) and **paid API**

- **Free [V]:** "Weekly price history for 103 GPU models across 88 cloud providers. Free
  with attribution · CC BY 4.0 · updated daily". 53 trailing weeks. Already collected. It
  aggregates over Vast.ai and RunPod, which cannot be removed.
- **API [V, getdeploying.com/api]:**
  - "weekly snapshots since mid-2024, and a daily series since July 2026"; "[2] Weekly
    snapshots since mid-2024, daily since July 2026, with coverage widening over time."
  - Per-provider rows ("Per-provider rows, daily data and longer history are in the API").
  - **"Monthly plan $299 /mo, Billed monthly · cancel any time"; "Annual plan … $2,499
    /yr"**; 3,000 requests a day.
  - Use: "We do not permit the resale of raw data feeds. However, you may use the API to
    power features within your own applications (eg. internal dashboards, aggregated data).
    If you are building a direct competitor to this API or website, usage is not permitted."
  - "We provide limited trial keys for technical evaluation upon request."
  - Contact: **support@getdeploying.com** [V].
  - Its `/terms` page is disallowed by robots.txt, so it was not read; the owner should read
    it manually, especially on retaining data after cancelling.
- **Recommendation:** **PAID: the best value.** One month at $299 should pull per-provider
  weekly history from mid-2024 for H100, H200, B200 and A100, with Vast.ai and RunPod
  removable. First **ASK** for a trial key and written confirmation that stored history may
  be kept for internal non-commercial research after cancelling.

### 5.4 Other datasets and trackers checked

| Source | History | Licence / terms | Verdict |
|---|---|---|---|
| FastGPU daily history file (`/api/v1/dataset/gpu-prices-daily.csv`, also on HF `fastgpu/cloud-gpu-prices`) | "Days of history 61 · daily history since 2026-08-11" [V] | CC BY 4.0 (open dataset per its terms) | Allowed, but later than our start and aggregated over Vast.ai and RunPod (floors cannot be cleaned). **Skip** (as D51) |
| `tokenwatt/gpu-cloud-prices` (HF) | from 2026-10-07 | CC BY 4.0 | Too short. Skip |
| `Viswa-k/cloud-gpu-pricing` (HF) | one monthly snapshot (2026-10) | CC BY 4.0 | Skip |
| `exalsius/gpu-prices` (HF, 2025-05) | README only, no data files | MIT | Nothing to use |
| gpurentalprices.com full history | from 2026-07-05 (already held) | "full history licensed (data@gpurentalprices.com)" (repo audit) | Nothing older. Skip |
| Epoch AI ML Hardware dataset | Accelerator specs and launch prices (not rental) | CC BY 4.0 [S, epoch.ai/llms.txt] | **GET NOW** only if hardware launch prices are needed (hardware_launches.md). Not a rental series |
| Full Stack Deep Learning cloud-GPU table (raw.githubusercontent.com/full-stack-deep-learning/website/main/docs/cloud-gpus/cloud-gpus.csv) | "These tables were last updated in October 2023" [V] | No LICENSE file (404) [V] | **Skip**: stale, unlicensed, few snapshots |
| dstack `gpuhunt` catalog on S3 (`dstack-gpu-pricing.s3.eu-west-1.amazonaws.com/v2/version` = `20261010-20155`) | Versioned, but listing is AccessDenied [V], so old versions cannot be enumerated | No data licence found | **Skip** |
| gpus.llm-utils.org | Live page; no history or licence found | robots `Allow: /` | Skip |
| cloud-gpus.com (Jolt ML) | Snapshot only ("Last updated: 10 October 2026") | Terms: "permission to download one copy of the materials for personal, non-commercial transitory use" [V] | **NOT ALLOWED** for storage |
| Kaggle | Nothing relevant found [S]. The Kaggle API needs a login | n/a | Skip |
| The Information | No GPU rental tracker found [S] | n/a | Skip |
| Shadeform | API needs a key; terms ban scrapers (repo docs) | n/a | **NOT ALLOWED** |
| Lambda, Together, CoreWeave | No published price histories found | n/a | Wayback only (§7) |
| YipitData | "$20 billion in observed Cloud spend … by provider, GPU model, and realized invoice price" [S] | Commercial alternative data | Quote. Probably institutional and expensive [U]. Skip |

---

## 6. Hyperscaler price archives

### 6.1 AWS Price List Bulk API: version history (NEW): **GET NOW** (owner confirms)

- **Version index [V]:**
  `https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/index.json` (28 kB)
  lists **123 versions, from `20151209144527` to `20261009203134`**, about monthly. 2023
  has 12 versions and 2024 has 13.
- **Format:** each version has `region_index.json` (106 regions).
  `…/20260925174521/us-east-1/index.csv` is **302,856,576 bytes** [V, HEAD], so about
  0.3 GB per version for us-east-1 alone [U for other versions].
- **AWS documentation [V]:** "Each service version includes the URL that you can use to
  download the prices for that service for the specified time period." Also: "The Price
  List Query API and Price List Bulk API provide pricing details for informational
  purposes only."
- **robots.txt:** 404 on the pricing host.
- **Open issue:** docs/data_sources.md flagged the AWS Site Terms ("data mining, robots").
  The Bulk API is a documented programmatic interface, which in my reading is distinct from
  "the AWS Site"; the owner should confirm.
- **Value:** monthly on-demand and reserved list prices for p4d, p5, p5e, p5en and
  p6-b200 since each launch. It dates hyperscaler price cuts, such as the mid-2025 P5 cut
  [U]. Stream each version and keep only GPU instance rows; do not store the full files.
  Hyperscaler, so keep it out of the index.

### 6.2 Others

- **Azure Retail Prices API:** current prices only. Each meter carries an
  `effectiveStartDate`, which dates the current price but gives no older prices [U].
  Already collected (D50).
- **GCP:** Cloud Billing Catalog API, current prices only, and it needs an API key. Spot
  prices "can change up to once every 30 days" [S]. No official archive.
- **AWS spot (Pauley, Zenodo):** already used (claim 5).

---

## 7. Wayback Machine

- **Reachability [V, 2026-10-10]:**
  - `web.archive.org`: "Connection reset by peer" on robots.txt and on a single CDX query,
    twice. The proxy logs `ws_closed_mid_exchange` for web.archive.org:443. WebFetch is
    refused ("unable to fetch from web.archive.org").
  - `archive.org` itself returns 200.
  - So Wayback is **unreachable from this environment**.
- **Terms [V, blog.archive.org 2014-12-30, "Update to Terms of Use"]:** "you certify that
  your use of any part of the Archive's Collections will be limited to noninfringing or fair
  use under copyright law."
  - The 2014 post shows an earlier wording with "will be noncommercial and"; whether
    "noncommercial" remains is unverified because the live terms page needs JavaScript.
  - The provider's own terms still apply to the content captured.
- **Recommendation: ASK OWNER** to run CDX queries from his own machine, limited to
  providers whose terms we already accept (Lambda, CoreWeave, Nebius, Hyperstack, Verda).
  Never Vast.ai, RunPod or Together. Use about 1 request every 3 to 5 s; Wayback's own rate
  limit is unverified [U]. Example query:
  `https://web.archive.org/cdx/search/cdx?url=lambda.ai/pricing&from=2023&output=json&fl=timestamp,statuscode,digest&collapse=digest`.
  Expect sparse, irregular snapshots: good for dating list-price changes, poor as a daily
  series.

---

## 8. Requests the owner should send

Do not send a request from this agent. Suggested wording is below each item.

1. **Silicon Data**: support@silicondata.com [V], or the "Talk to sales" form [V]. Ask:
   - non-commercial academic or research access to the daily SD-H100 and SD-B200 history
     (plus SD-A100 and H200), **in the US-geography, Business-Day configuration that settles
     NYMEX GPU1/GPU2**, from launch;
   - written consent to store it in a private research database (their terms forbid storage
     otherwise);
   - the Enterprise price for "Index & Curve Datasets" limited to H100 and B200;
   - the restatement and membership-change log.
2. **Ornn**: data@ornn.com [V]. Ask for:
   - the 72-hour Research Grant;
   - written permission to retain the daily OCPI H100/H200/B200/A100 history for
     non-commercial research after the grant or Premium ends;
   - the "earlier, sparser history … on request for diligence and backtesting".
3. **GetDeploying**: support@getdeploying.com [V]. Ask for:
   - a trial key;
   - an academic price;
   - written confirmation that per-provider weekly history from mid-2024 may be stored and
     kept for internal research after cancelling.
4. **Vast.ai**: data@vast.ai [V]: a non-commercial research data licence for the public
   pricing feed (90-day daily medians, hourly current). This would unblock B5.
5. **University library (if the owner has an affiliation)**: export from Bloomberg
   `SDH100RT Index`, `SDB200RT Index`, `SDA100RT Index`, `ORNNH100` and `SAH100SC` (daily,
   full history), or LSEG `.SDH100RT` / `.SDA100RT`. Confirm with the librarian that keeping
   the exported series in a private, non-commercial research repository is allowed.
6. **SkyPilot maintainers** (GitHub issue on skypilot-org/skypilot-catalog): ask them to add
   a LICENSE to the catalog repo.
7. **Overclock Labs (Akash)**: written permission for the Console API's GPU availability
   history (B13). Contact address unverified.
8. **SemiAnalysis**: sales@semianalysis.com [V]: academic price for the GPU Pricing Product
   (H100, B200 hourly composite and term curves).
9. **AIMultiple**: licence for its monthly GPU index CSV (Jul 2024 to Sep 2026). Contact
   unverified.
10. **RunPod**: written permission (B6). Contact unverified.

---

## 9. Paid options ranked by value

| Rank | Option | Cost | What it buys | Verdict |
|---|---|---|---|---|
| 1 | GetDeploying API | **$299/month or $2,499/year** [V] | Per-provider weekly history from mid-2024; daily from 2026-07 | **Worth it** (one month), after the retention question is answered |
| 2 | Ornn Premium | **$500/month** [V] (72-hour grant free) | All-time daily OCPI history: transaction-based H100 from 2025-01, B200 from 2025-11 | Worth it **only with retention rights** (the addendum requires deletion on termination) |
| 3 | Databento (CME) | $125 free credit; from $0.50/GB [S] | GPU1/GPU2 settlements once listed | Worth it after listing |
| 4 | Silicon Data Enterprise | Quote only [V] | The settlement index itself, CSV/API, full history | Essential if no research licence is granted; ask for a quote |
| 5 | Silicon Data Pro | **$998/month** [V] | Dashboard only; no export; storage forbidden | **Not worth it** |
| 6 | CME DataMine historical EOD | Quote after sign-in; about $10k/year dated [U] | Official settlement history | Later, only if Databento is insufficient |
| 7 | SemiAnalysis | Quote [V: "contact sales"] | Hourly composite and term curves | Low priority |
| 8 | Bloomberg Terminal | About $32k per seat per year [U] | All three GPU index families | Not worth it; use a university terminal |
| 9 | LSEG Workspace | $300 to $22k per year, conflicting [U] | SD H100 and A100 | Not worth it; use a university licence |

---

## 10. Changes to suggest for the repo docs (not made)

- **B10:** data.ornn.com is reachable as of 2026-10-10. Record Ornn's terms, the $500
  Premium tier, the free 72-hour grant, and that downloads are Full-only.
- **docs/data_sources.md:** Silicon Data's pricing page is confirmed at $998/month for Pro
  (2026-10-10). Correct "API needs Plus and Professional tiers": CSV/API is Enterprise-only.
- **Candidates to add:**
  - `afhubbard/gpu-prices` (CC BY 4.0, from 2026-01-12): needs a D13 decision on Vast.ai,
    RunPod, Oracle and Vultr rows.
  - The AWS Price List version history.
  - The gpueconomy reconstructed H100 series (exploratory only).
- **New index to watch:** CF Benchmarks' CF H100 Neo-Cloud GPU Compute Index (V1.0,
  2026-07-28).

---

## 11. Request log (hosts contacted today)

All requests used the UA `compute-curve-research/0.1 (non-commercial research)`, with at
least 3 s between requests to the same host.

| Host | Requests |
|---|---|
| www.silicondata.com | robots.txt, /pricing, /sitemap.xml, /terms-of-use, /products/index-datasets, /data-partnerships, /contact-us, /mcp (404), one press-release page |
| data.ornn.com | robots.txt, sitemap.xml, /pricing, /terms, /premium-data-use, /faq, /methodology |
| ornn.com, www.ornn.com | robots.txt |
| index.ornn.com | robots.txt (404), / |
| www.cftc.gov | robots.txt, one PDF (extension letter) |
| vast.ai | robots.txt, /pricing.md (terms text only; the feed was not fetched) |
| getdeploying.com | robots.txt, /dataset/gpu-prices, /gpu-price-api (404), /api |
| gpu-index.semianalysis.com | robots.txt (404), / |
| api.semianalysis.com | robots.txt (403) |
| web.archive.org | 2 attempts, both reset |
| archive.org | robots.txt, /about/terms (JavaScript shell) |
| blog.archive.org | robots.txt, one 2014 post |
| help.archive.org | robots.txt |
| huggingface.co | robots.txt; 4 dataset-search API calls; 7 dataset metadata calls; 2 README files; 1 commits list; 1 tree list |
| raw.githubusercontent.com | skypilot-catalog LICENSE / LICENSE.md / LICENSE.txt (404) and README; FSDL LICENSE (404), README (404), cloud-gpus.csv (17 kB), index.md |
| dstack-gpu-pricing.s3.eu-west-1.amazonaws.com | one list attempt (AccessDenied), /v2/version |
| pricing.us-east-1.amazonaws.com | robots.txt (404), EC2 version index (28 kB), one region_index.json (19 kB), 2 HEAD requests |
| docs.aws.amazon.com | robots.txt, 2 documentation pages |
| docs.cfbenchmarks.com | robots.txt (404), one methodology PDF |
| gpus.llm-utils.org, cloud-gpus.com, aimultiple.com | robots.txt plus 1 to 3 pages each |
| fastgpu.co | /dataset |
| Agent proxy status endpoint | 1 request |

Web searches were made through the search tool and the Firecrawl paper index. The only
directly relevant paper found is Bandi & Su, arXiv 2607.12156, which is already in the
repo. Its data is licensed Silicon Data and Ornn data, so it cannot be shared.
