> Research notes produced by a research agent on 2026-10-05 for this project.
> Appendix to docs/contract_specs.md and docs/term_structure_model.md.

# CME compute futures (GPU1 / GPU2): contract terms, Silicon Data indices, literature, hardware calendar

Prepared 2026-10-05, for research only. Every fact has a source URL and one of these status tags:

- **[V-P]**: I fetched the primary document and checked the fact against it.
- **[V-S]**: I fetched a secondary document (news, blog, or an academic paper quoting a primary source) and checked the fact against it.
- **[SNIP]**: I saw the fact only in a search-engine snippet and did not fetch the page. All cmegroup.com and ssrn.com content falls here.
- **[INF]**: my own arithmetic or inference from verified data, labelled as such.

**How sources were accessed.** I did not access cmegroup.com (including investor.cmegroup.com) or ssrn.com. I checked robots.txt for every host I fetched. I left at least 2 s between requests to the same host, and at least 15 s on arxiv.org, which sets `Crawl-delay: 15`.

- `export.arxiv.org/robots.txt` is `User-agent: * / Disallow: /`, so I did **not** call `export.arxiv.org/api`. The arXiv metadata comes from the `arxiv.org/abs/...` meta tags, which robots.txt allows.
- The SSRN metadata comes from the open Crossref REST API (`api.crossref.org/works/10.2139/ssrn.*`). That host has no robots.txt (it returns 404).
- `cftc.gov/robots.txt` forbids `/search`, so I did not use the CFTC site search. I found the filings through a web search, and `/filings/` and `/IndustryOversight/` are allowed.
- Raw copies of fetched documents were kept only in the session scratchpad and were not retained.
- Silicon Data's Terms of Use forbid storing site content "in a database or retrieval system" without written consent. Its methodology PDF says it "may not be shared or distributed". I therefore summarise those sources and do not reproduce them.

---

## 0. Key findings

1. **The contracts did NOT start trading on 2026-10-05.**
   - NYMEX filed the contracts on 2026-08-11 under **CFTC Reg. 40.3(a)**. This is a *voluntary submission for Commission approval*, not a 40.2 self-certification.
   - On 2026-09-21 the CFTC Division of Market Oversight extended the review by 45 days, "until the end of November 9, 2026". The letter cites "novel or complex issues" and the pending CFTC Request for Comment on compute derivatives.
   - The CFTC product records for both contracts read **"Approval Pending (90)"**, dated 2026-09-21 (fetched 2026-10-05).
   - I found no new listing date from CME. November 9 is the end of the review period, not a listing date. [V-P]
2. **Checking the working assumptions.**
   - Confirmed: 730 GPU-hours, financially settled, 36 consecutive monthly contracts.
   - Final settlement is an arithmetic average, with two qualifications. It averages the index's **"on-demand settlement prices" on each *Business Day*** of the contract month. The "Index Technical Configuration" is **"Geography: United States"**.
   - Neocloud rather than hyperscaler: confirmed by Silicon Data's own documentation, which calls the index the "Silicon Data H100 Neocloud Index (SDH100RT)". CME's own wording ("neocloud indices (non-hyperscaler)") appeared only in a snippet.
3. **What happens on a missing index day is not specified** in the filed rule chapters, so it is not confirmed.
4. **Index methodology.** Each record is converted to USD per GPU-hour and filtered. A proprietary model then adjusts it to a "benchmark-equivalent contract", covering rental type, country, CPU platform and GPU variant (SXM/PCIe). Records are averaged per provider, and the index is a **weighted average of the provider means**, with weights reflecting "market relevance". It is not a median and not explicitly volume-weighted.
   - Publication time and time zone are not disclosed.
   - History starts on 2024-09-01 for H100 and in August 2025 for B200.
   - The series has several documented level breaks (see §2.6).
5. **arXiv 2607.12156 is Bandi & Su, "(Early) AI Compute Asset Pricing" (Johns Hopkins).** It builds a no-arbitrage and risk-premium framework and computes synthetic futures returns from Silicon Data term-rental curves.
   - It contains **no SDE state-variable model, no depreciation term and no launch jumps**.
   - The "Schwartz–Smith plus scheduled hardware-launch jumps" model belongs to **SSRN 6926798 (Amine Assody)**. Only its abstract was reachable, via Crossref. It reports a jump size of about −0.22 in log terms per generational transition and incumbent depreciation of 15–20% per year.
6. **Schwartz & Smith (2000).** Citation and DOI verified. The equations below were transcribed from the author-hosted PDF at Dartmouth.

---

## 1. CME GPU1 / GPU2 contract specifications

### 1.1 Primary documents (all fetched)

| Document | URL |
|---|---|
| NYMEX Submission No. 26-370 (cover sheet, letter, Exhibits A, C, D; E redacted), dated 2026-08-11 | https://www.cftc.gov/filings/ptc/ptc08112615405.pdf |
| Exhibit B: position limit / accountability / reportable level table (xlsx) | https://www.cftc.gov/filings/ptc/ptc08112615406.xlsx |
| Submission 26-370S: FOIA confidential-treatment letter for the supplement | https://www.cftc.gov/filings/ptc/ptc08112615408.pdf |
| CFTC letter of 2026-09-21 extending the review | https://www.cftc.gov/filings/documents/2026/orgdcmnymexcompcontr260921.pdf |
| CFTC product record, H100 | https://www.cftc.gov/IndustryOversight/IndustryFilings/TradingOrganizationProducts/62544 |
| CFTC product record, B200 | https://www.cftc.gov/IndustryOversight/IndustryFilings/TradingOrganizationProducts/62545 |
| CME / Silicon Data press release, 2026-08-11 (PR Newswire) | https://www.prnewswire.com/news-releases/cme-group-and-silicon-data-to-launch-compute-futures-on-october-5-to-unlock-new-way-to-hedge-ai-risks-302848593.html |
| CME / Silicon Data partnership release, 2026-05-12 (copy in Silicon Data newsroom) | https://www.silicondata.com/news-room/cme-group-and-silicon-data-partner-to-launch-first-compute-futures |
| CFTC press release 9286-26 (2026-08-19), Request for Comment | https://www.cftc.gov/PressRoom/PressReleases/9286-26 |
| Federal Register, 91 FR 54259 (2026-08-21), FR Doc. 2026-17163, RIN 3038-AF77 | https://www.govinfo.gov/content/pkg/FR-2026-08-21/pdf/2026-17163.pdf |

### 1.2 Contract terms (all [V-P] from Submission 26-370 and Exhibit B unless noted)

| Item | GPU1 (H100) | GPU2 (B200) |
|---|---|---|
| Official title | Silicon Data H100 Rental Index Futures | Silicon Data B200 Rental Index Futures |
| Exchange; rulebook chapter | NYMEX; Chapter **1045** | NYMEX; Chapter **1047** |
| CME Globex and ClearPort code | **GPU1** | **GPU2** |
| Underlying ("Floating Price", rule 1045101 / 1047101) | "the **arithmetic average** of the Silicon Data H100 Rental Index (SD-H100) **on-demand settlement prices** as published by Silicon Derivatives Inc. (Silicon Data) for **each Business Day during the contract month**" | Same wording for SD-B200 |
| Index technical configuration (1045102.C / 1047102.C) | "Geography: United States" | "Geography: United States" |
| Contract unit | **730 GPU-hours**; "Each futures contract shall be valued at the contract quantity multiplied by the settlement price" | Same |
| Price quotation | U.S. dollars and cents per GPU-hour | Same |
| Minimum tick and tick value | **$0.01 per GPU-hour = $7.30 per contract**. Inter-commodity spreads executed simultaneously on Globex (Rule 542.F) may trade in multiples of **$0.005** | Same |
| Settlement type | Financial (cash) | Same |
| Final settlement (1045103; the B200 rule is printed as "104703", apparently a typo for 1047103) | "by cash settlement … following termination of trading … based on the Floating Price. The final settlement price will be the Floating Price calculated for each contract month." | Same |
| Termination of trading | "on the **last Business Day** of the contract month" | Same |
| Listing schedule | "Monthly contracts listed for **36 consecutive months**"; initial listing **October 2026**. The rule text adds: "number of months open … determined by the Exchange" | Same |
| Intended start | "Subject to Commission approval … effective Sunday, October 4, 2026, for trade date Monday, October 5, 2026" | Same |
| Globex matching algorithm | F (FIFO) | Same |
| Trading and clearing hours | Globex: Sun 5:00 pm to Fri 4:00 pm CT, daily maintenance 4:00–5:00 pm CT. Pre-open: Sun 4:00–5:00 pm CT and Mon–Thu 4:45–5:00 pm CT. ClearPort: Sun 5:00 pm to Fri 4:00 pm CT, no reporting Mon–Thu 4:00–5:00 pm CT | Same |
| Block trades | Minimum **5 contracts**; **15-minute** reporting window | Same |
| Globex non-reviewable range (Rule 588.H, Exhibit D) | $0.20 per GPU-hour (20 ticks); for spreads, each leg is evaluated as an outright | Same |
| Reportable level (Exhibit B) | 25 contracts | 25 contracts |
| Spot-month position **limit** | **7,500** contracts (5,475,000 GPU-hours), effective from "Close of trading 3 business days prior to last trading day of the contract" | **5,500** contracts (4,015,000 GPU-hours), same effective time |
| Single-month **accountability** level | 15,000 | 11,000 |
| All-month **accountability** level | 22,500 | 16,500 |
| Other Exhibit B fields | Group "Power"; "Diminishing Balance Contract: **Y**" (the filing does not define this) | Same |
| Exchange fees per contract (Exhibit C; one table for both) | CME Globex: member $3.65 / non-member $5.50. Block, EFP, EFR, EOO: $6.00 / $7.30. Cash settlement: $0.90 / $1.35. Facilitation fee $0.70; give-up surcharge $0.05; position adjustment/transfer $0.10 | Same |
| Margins / performance bonds | **Not in the filing and not found elsewhere. Not confirmed.** | Same |
| Exhibit E | "Supplemental Market Information": confidential, redacted | Same |

The filing describes Silicon Data's index publisher as **Silicon Derivatives Inc.** [V-P]. The press releases describe Silicon Data as backed by the trading firm **DRW** [V-P].

### 1.3 Regulatory timeline

| Date | Event | Source | Status |
|---|---|---|---|
| 2026-05-12 | CME and Silicon Data announce a compute futures market "later this year, pending regulatory review", based on Silicon Data's "daily GPU benchmarks for on-demand rental rates" | silicondata.com newsroom (PR Newswire text) | [V-P] |
| 2026-08-11 | NYMEX Submission 26-370, a "CFTC Regulation 40.3(a) Voluntary Submission for Product Approval", plus confidential supplement 26-370S. Press release names a 2026-10-05 launch "pending regulatory review" | CFTC filings; PR Newswire | [V-P] |
| 2026-08-19 | CFTC issues its Request for Comment on the Listing of Compute Derivatives Contracts. Topics: cash-market size and liquidity, manipulation, customer protection, perpetual compute futures | CFTC PR 9286-26 | [V-P] |
| 2026-08-21 | RFC published at 91 FR 54259 (17 CFR Parts 1 and 38, RIN 3038-AF77). Comments due **2026-10-20**. Chairman Selig voted in favour; no Commissioner voted against. The RFC cites Bandi (2026), "(Early) AI Compute Asset Pricing" | govinfo PDF | [V-P] |
| 2026-09-21 | Division of Market Oversight (Acting Director DJ Hennes) acts under Reg. 40.3(c)(2) "to extend the review period … for additional 45 days … until the end of November 9, 2026", citing "novel or complex issues" and the pending RFC | CFTC letter | [V-P] |
| 2026-09-25 | *The Information* reports the hold; FinanceFeeds summarises it on 2026-09-29 | https://financefeeds.com/nvidia-gpu-futures-730-hours-45-day-hold/ | [V-S] |
| 2026-10-05 | CFTC records for both products still read "Approval Pending (90)", dated 2026-09-21 | CFTC product records 62544 and 62545 | [V-P] |

[INF] The arithmetic is consistent: 2026-08-11 + 45 days = 2026-09-25 (end of the initial review), and + 45 more days = 2026-11-09.

**Did trading begin on 2026-10-05? No.** A 40.3 product cannot be listed before approval, and the CFTC records show approval still pending as of 2026-10-05. Whether the CFTC acts before 2026-11-09, and when CME will list, is **not confirmed**.

### 1.4 Final settlement and missing index days

- **Floating price:** the arithmetic mean of the SD-H100 (or SD-B200) "on-demand settlement prices" over the **Business Days** of the contract month. [V-P]
- **Missing days:** chapters 1045 and 1047 as filed contain **no fallback clause** for a day on which the index is missing or late. They do say "any other matters not specifically covered herein shall be governed by the general rules of the Exchange". I could not check those general rules or the NYMEX definition of "Business Day", because cmegroup.com is off-limits. **Not confirmed.**
- **On the index side,** since 2025-12-04 Silicon Data has applied "a look-back mechanism in the daily index calculation" to "address short-term data gaps caused by unforeseeable provider-side disruptions" (https://docs.silicondata.com/products/gpu-index-announcements). [V-P] This affects how the index is computed, not the contract.

### 1.5 Working assumptions against findings

| Assumption | Finding | Status |
|---|---|---|
| 730 GPU-hours per contract | Confirmed | [V-P] |
| Cash settled | Confirmed ("Financial") | [V-P] |
| 36 consecutive monthly expiries | Confirmed; initial listing October 2026 | [V-P] |
| Final settlement = arithmetic average of the daily index over the contract month | Confirmed, with qualifications: **Business Days only**, of the index's "on-demand settlement prices", configuration "Geography: United States" | [V-P] |
| Index tracks on-demand neocloud prices, not hyperscalers | Silicon Data docs call the products "Silicon Data H100 Neocloud Index (SDH100RT Index, .SDH100RT)" and "… B200 Neocloud Index". Silicon Data's hedging guide (2026-09-14): "GPU1 settles exclusively against an index of independent neocloud providers". CME page: "neocloud indices (non-hyperscaler) measuring hourly on-demand rental GPU costs" | Silicon Data [V-P]; CME wording [SNIP] |
| Listing 2026-10-05, pending regulatory review | It was the target, but the CFTC extended its review to 2026-11-09; no listing on 10-05 | [V-P] |

Other context [V-S]:
- ICE and Ornn announced cash-settled GPU futures on Ornn's transaction-based Compute Price Index on 2026-05-19, subject to approval (Bandi & Su, footnote 4).
- FinanceFeeds reports that Kalshi launched GPU forward curves in July 2026.

---

## 2. Silicon Data indices (SDH100RT, SDB200RT)

### 2.1 Names and tickers [V-P]

| Index | Name in the CME filing | Bloomberg / Reuters | Silicon Data name |
|---|---|---|---|
| H100 | Silicon Data H100 Rental Index (SD-H100) | `SDH100RT Index` / `.SDH100RT` | "Silicon Data H100 Neocloud Index". A separate **H100 Hyperscaler** index is portal-only |
| B200 | SD-B200 | `SDB200RT Index` / `.SDB200RT` | "Silicon Data B200 Neocloud Index" |

Sources:
- https://docs.silicondata.com/products/gpu-index-announcements
- https://www.silicondata.com/products/silicon-index/h100
- https://www.silicondata.com/products/silicon-index/b200
- https://www.silicondata.com/news-room/silicon-data-announces-major-revision-to-a100-h100-rental-indices-launches-first-ever-b200-index-and-introduces-new-hyperscaler-rental-benchmarks (2025-12-05)

Other indices in the family: A100 (SDA100RT), H200 neocloud, B300 neocloud, MI300X neocloud, plus A100 and H100 hyperscaler. [V-P]

### 2.2 Methodology ("Silicon Data GPU Rental Index™ Methodology Overview", updated 2026-08-27) [V-P]

Source: https://www.silicondata.com/documents/silicon-data-index-methodology.pdf (linked as "Download methodology" from https://www.silicondata.com/products/silicon-index)

**Scale.** "Each day the index processes over 10,000 GPU rental records collected across 40+ independent, market-relevant cloud providers." A separate blog post describes the underlying dataset: "150k daily verified pricing records | 40–50 countries and regions | 50–100 platforms across hyperscalers, neoclouds, and marketplaces | Sep 1, 2024 onward" (https://www.silicondata.com/blog/building-a-robust-gpu-index, 2026-03-12).

The index is built in four steps:

1. **Preprocessing** converts each record to a per-GPU-hour price:
$$\text{unit\_price}=\frac{\text{total\_rental\_price}}{\text{num\_gpu}\times\text{duration}}\qquad[\text{USD per GPU-hour}]$$
   Here total_rental_price is the price for the whole server, num_gpu is the number of GPUs on the server, and duration is in hours.
2. **Filtering**:
   - completeness checks;
   - anomaly checks, which flag large day-over-day shifts for manual review;
   - outlier screening against *dynamic historical price bands*.
3. **Standardization (basis adjustment).** A proprietary pricing model maps each record to a "benchmark-equivalent contract". Factors include:
   - rental type (On-Demand, Reserved, Spot/Interruptible);
   - country (US, AU, FR, …);
   - CPU platform (Intel, AMD, Other);
   - GPU variant (SXM, PCIe, other form factors).
4. **Aggregation.** Prices are averaged by provider first, "preventing any single provider with massive individual records from skewing the market average". The index is then
$$\text{Index}(t)=\sum_{j=1}^{N} w_j(t)\,\bar P_j(t)$$
   where $\bar P_j(t)$ is the average adjusted price for provider $j$ and $w_j(t)$ is a weight "reflecting the market relevance of the j-th cloud provider". The weights are **not disclosed**.

**Maintenance.** The pricing model is recalibrated weekly. Validation uses dynamic reference ranges by provider and GPU variant, and flagged records are held for manual review. Material changes are announced in advance, and the index is reviewed quarterly.

### 2.3 Answers to the specific questions

- **On-demand neocloud only?** Partly confirmed.
  - Supporting evidence:
    - The index is labelled "Neocloud" (the API parameter is `neo` versus `hs` for hyperscaler).
    - The CME rule references "on-demand settlement prices".
    - The B200 launch release says it captures "Early pricing across on-demand from neo clouds and marketplaces".
    - The 2026-09-24 B200 blog says it measures "B200 rental rates quoted by neocloud providers".
  - Conflicting evidence:
    - The methodology basis-adjusts *rental type* (On-Demand, Reserved, Spot), which implies non-on-demand records can be converted to the benchmark.
    - The **B200 product page says the index "blends neo-cloud, hyperscaler, colocation, and private-market observations into a single standardized reading"**.
  - The exact inclusion rules are **not confirmed**.
- **Aggregation:** a weighted mean of provider means, with "market relevance" weights. Not a median, and not stated to be volume-weighted. Outliers are removed by dynamic price bands; no explicit trimming percentage is given. The "divisor adjustment" was removed on 2025-12-04.
- **Normalization:** USD per GPU-hour. SXM versus PCIe (and interconnect, cluster scale, geography, performance variance; see the 2025-12 release) is handled by basis adjustment to a baseline configuration.
  - The **H100 baseline GPU variant changed on 2026-09-25** "to reflect the more widely offered type among neoclouds" (estimated impact up to +4%, no restatement).
  - The variant itself is not named, so whether the baseline is SXM or PCIe is **not confirmed**.
- **Publication time and time zone:** **not disclosed (not confirmed).**
  - "Every index is processed and published once per business day" (silicon-index FAQ); "The indices update every business day" (pricing FAQ). [V-P]
  - The API returns two-decimal strings, and "-1 or any negative number indicates that the data has not yet been generated" (https://docs.silicondata.com/api-reference/gpu_index_api). [V-P]
  - Possible calendar-day values:
    - The API example shows a value for **2025-04-05, a Saturday**.
    - Bandi & Su's Table 1 has 595 observations from 2024-09-01 to 2026-04-18, which is exactly the inclusive calendar-day count [INF].
    - Both suggest the series has calendar-day values, while the futures average uses Business Days only. Not confirmed.
- **Free availability:**
  - The public product pages show the latest value and a 7-day chart without login. [V-P] Readings as of 2026-10-05:

    | Index | Latest (USD/GPU-hour) | 7-day change |
    |---|---|---|
    | SDH100RT | 2.81 | +2.9% |
    | SDB200RT | 5.87 | −0.2% |
    | H100 hyperscaler | 7.16 | not recorded |
    | H200 | 3.25 | not recorded |
    | B300 | 6.82 | not recorded |

    The H100 page's FAQ text still says "$2.53", which is stale.
  - Full history requires an account or subscription. The free Basic account (requires sign-up, not done) gives 30 days of history; Pro is $998/month with full history; the API needs the "Plus and Professional" tiers. The indices are also distributed via Bloomberg, Refinitiv/LSEG and Kaiko (https://www.silicondata.com/pricing). [V-P]
- **History start dates:**

  | Index | History start | Source / status |
  |---|---|---|
  | H100, A100 | 2024-09-01 (history restated in Dec 2025) | [V-P] |
  | B200 | August 2025 | Silicon Data blog "began in August 2025" [V-P]; Bandi & Su Table 1 gives 2025-08-01 [V-S] |
  | H200 neocloud | 2026-05-04 | [V-P] |
  | B300 neocloud | 2026-04-23 | [V-P] |
  | MI300X neocloud | 2026-01-01 | Bandi & Su [V-S] |

  SDH100RT launched on Bloomberg in May 2025: the newsroom page's JSON-LD datePublished is 2025-05-20 [V-P], and Bandi & Su say "May 2025" [V-S]. SDB200RT went live on 2025-12-04 [V-P].

### 2.4 Statistics published by Silicon Data (for calibration) [V-P]

**Realized statistics** of the NeoCloud indices through 2026-08-14 (https://www.silicondata.com/blog/cash-settled-compute-futures, 2026-08-24). Volatility is annualized from daily log returns.

| Index | Sample | Max drawdown | Max run-up | Annualized realized vol |
|---|---|---|---|---|
| B200 | Aug 2025 – Aug 2026 | −19.7% | +42.4% | 30.2% |
| H100 | Sep 2024 – Aug 2026 | −45.3% | +50.5% | 26.2% |
| A100 | Sep 2024 – Aug 2026 | −26.8% | +23.9% | 14.7% |

**B200 index, recent behaviour** (blog of 2026-09-24):
- In August 2026 daily values stayed between 5.58 and 5.69.
- Annualized August volatility was 7.1%, computed on a calendar-day basis.

**Neocloud forward curve, 2026-07-19** (https://www.silicondata.com/blog/gpu-futures):

| GPU | Spot | 36-month term rate | Backwardation |
|---|---|---|---|
| B200 | ~5.62 | ~5.17 | about −8% |
| H100 | ~2.72 | ~2.38 | about −13% |
| A100 | ~1.65 | ~1.40 | about −15% |

**B200 term structure, 2026-09-07** (spot 5.69):

| Tenor | Term rate | Forward rate |
|---|---|---|
| 3 months | 5.73 | 5.68 |
| 6 months | 5.64 | 5.41 |
| 12 months | 5.39 | 5.03 |

**H100 term-implied forwards, 2026-09-07** (index 2.63): $2.50 at 3 months, falling to $2.14 at 12 months (practitioner guide).

### 2.5 Licensing caution

- Terms of Use (https://www.silicondata.com/terms-of-use): content may be downloaded "for personal and non-commercial use"; no "stored in a database or retrieval system" without consent.
- The methodology PDF footer: "may not be shared or distributed without Silicon Data's express written consent."

### 2.6 Index change log: level breaks to model (https://docs.silicondata.com/products/gpu-index-announcements) [V-P]

| Effective date | Index | Change | Stated impact |
|---|---|---|---|
| 2025-03-01 | H100, A100 | "rapid expansion of provider coverage … index may experience a large jump on that day" | Not quantified |
| 2025-12-04 | SDH100RT, SDA100RT | Methodology change: divisor removed, pricing model improved, coverage expanded, provider weights updated, look-back added. **History restated from 2024-09-01** | SDH100RT −6% to −4%; SDA100RT +35% to +40% |
| 2025-12-04 | SDB200RT | Index launched (API, Bloomberg, Reuters) | n/a |
| 2026-04-06 | SDH100RT | Provider membership expansion | −7% to −3% |
| 2026-07-15 | SDB200RT | Provider membership expansion | Up to −6% |
| 2026-07-15 | H200 neocloud | Index launched; history from 2026-05-04 | n/a |
| 2026-09-14 | B300 neocloud | Index launched; start 2026-04-23 | n/a |
| 2026-09-25 | SDH100RT | Hardware baseline (GPU variant) update | Up to +4% |
| 2026-09-25 | SDB200RT | Removal of stale providers | Up to +4% |

---

## 3. Literature

### 3a. arXiv 2607.12156: Bandi, F.M. & Su, Y., "(Early) AI Compute Asset Pricing" [V-P]

**Metadata** (arxiv.org/abs/2607.12156 meta tags and the PDF):
- Authors: Federico M. Bandi and Yinan Su, Johns Hopkins University.
- Category q-fin.PR; JEL G12, G13; DOI 10.48550/arXiv.2607.12156.
- Versions: v1 2026-07-13, v2 2026-08-03, v3 2026-09-10. The PDF says "This draft: August 22, 2026; First draft: June 30, 2026". 49 pages.
- Data provided by Silicon Data and ORNN.
- I read the full v3 PDF from https://arxiv.org/pdf/2607.12156v3.

**What the paper is, and is not.** It is a pricing *framework* plus a first empirical panel of *synthetic* futures returns.
- **There is no stochastic-differential-equation state-variable model, no depreciation process, no hardware-launch jump component, no Kalman filter and no structural estimation.**
- Estimation is simple time-series averaging of realized hold-to-maturity and constant-maturity returns.
- (The launch-jump model the project assumed is in SSRN 6926798; see §3b.)

**Main arguments:**
1. Compute is not storable, so the cost-of-carry link from spot to futures fails.
2. Term-rental (reserved) contracts give a no-arbitrage reference. The resulting synthetic futures are likely an **upper bound** on true futures prices, because physical term rentals bundle a capacity-locking option. The authors call the difference a "physical access wedge".
3. After financialization, $F_t(T)=E_t[S_T]-\lambda_t(T)$. If compute providers are the marginal hedgers, $\lambda>0$.

**Key equations, as written in the paper.**

Monthly-average settlement and payoff:
$$S^{m}_{M}=\frac{1}{N_M}\sum_{d\in M}S_d ,\qquad \text{payoff}=S^{m}_{M}-F^{m}_{t}(M)$$
Marked-to-market P&L (1) and daily return:
$$F^{m}_{t'}(M)-F^{m}_{t}(M),\qquad r_{t+1}=\frac{F^{m}_{t+1}(M)-F^{m}_{t}(M)}{F^{m}_{t}(M)}$$
Cost-of-carry relation (2), which the authors argue does **not** apply to compute:
$$F_t(T)=S_t\exp[(r_t+c_t-y_t)(T-t)]$$
Synthetic futures from term-rental rates $\Pi_t(t\to T)$, ignoring discounting, (3)–(4):
$$F^{syn,m}_t(M)=(M-t)\,\Pi_t(t\to M)-(M-t-1)\,\Pi_t(t\to M-1),\qquad F^{syn}_t(T)=\frac{\partial}{\partial T}\big[(T-t)\,\Pi_t(t\to T)\big]$$
Futures strip as a financial term rate (5)–(6):
$$\Pi^{fin}_t(t\to T)=\frac{1}{T-t}\int_t^T F_t(s)\,ds,\qquad \Pi^{fin,m}_t(t\to M)=\frac{1}{M-t}\sum_{J=t+1}^{M}F^m_t(J)$$
Frictionless no-arbitrage (7):
$$F_t(T)=F^{syn}_t(T),\qquad \Pi^{fin}_t(t\to T)=\Pi_t(t\to T)$$
Physical access wedge (8)–(11):
$$\Delta^{\Pi}_t(t\to T)=\Pi_t(t\to T)-\Pi^{fin}_t(t\to T),\quad F_t(T)=F^{syn}_t(T)-\Delta^{F}_t(T),\quad \Delta^{F}_t(T)=\frac{\partial}{\partial T}\big[(T-t)\Delta^{\Pi}_t(t\to T)\big],\quad F_t(T)<F^{syn}_t(T)$$
The wedge is expected to be $\ge 0$ and to increase with horizon.

Risk premium (§6 and App. A.2):
$$F_t(T)=E_t[S_T]-\lambda_t(T),\qquad \lambda_t(T)=E_t[S_T-F_t(T)],\qquad \lambda_t(T)=-\frac{\mathrm{Cov}_t(M_{t,T},S_T)}{E_t[M_{t,T}]},\qquad F_t(T)=E^{Q}_t[S_T]$$
The main text prints the denominator as $M_{t,T}$; the derivation in App. A.2 gives $E_t[M_{t,T}]$. Equation (12): $F_t(T)<E_t[S_T]$ when $\lambda>0$.

Empirical proxy: $\bar F^{syn}_t(T)=F_t(T)+\bar\Delta^F_t(T)$ with $\bar\Delta^F_t(T)>0$.

Hold-to-maturity return:
$$r_{t\to M}=\frac{S_M-\bar F^{syn}_t(M)}{\bar F^{syn}_t(M)}=\frac{\lambda^{syn}_t(M)}{\bar F^{syn}_t(M)}+\varepsilon_{t\to M},\qquad \varepsilon_{t\to M}:=\frac{S_M-E_t[S_M]}{\bar F^{syn}_t(M)}$$
Here $S_M$ is taken from end-of-month spot values.

Constant-maturity returns, with rolls at month-end:
$$r^{[M]}_t:=\frac{\bar F^{syn}_t(M)}{\bar F^{syn}_{t-1}(M)}-1,\qquad r^{(h_m)}_t:=r^{[\mathrm{month}(t)+h_m]}_t$$
Log decomposition (13):
$$\tilde r_m(M)=\tilde r^{(M-m-1)}_{m+1}+\dots+\tilde r^{(0)}_{M},\qquad \tilde\lambda^{syn}_m(M)=\tilde\mu^{(M-m-1)}+\tilde\mu^{(M-m-2)}+\dots+\tilde\mu^{(0)},\qquad \hat{\tilde\mu}^{(h)}=\frac{1}{|\text{sample}|}\sum_t \tilde r^{(h)}_t$$
Wedge "run-off" (App. A.6), with $h=T-t$:
$$r^{syn}_t(T)\approx r_t(T)-\frac{1}{\bar F^{syn}_t(T)}\frac{d\Delta^F(h)}{dh}dt,\qquad \Delta^{\Pi}(h)=\tilde\Delta^{\Pi}\frac{h}{h+a},\qquad \Delta^{F}(h)=\tilde\Delta^{\Pi}\frac{h(h+2a)}{(h+a)^2},\qquad \frac{d\Delta^F}{dh}=\tilde\Delta^{\Pi}\frac{2a^2}{(h+a)^3}$$
The last derivative is printed indistinctly in the PDF text; I re-derived $2a^2/(h+a)^3$ from the line before it.

Silicon Data's forward-curve construction, replicated by the authors (App. A.3), with $\delta=0.25$ month:
$$\text{forward}_{SD}(t,x)\approx\frac{(x+\delta)\,\text{term}_{SD}(t,x+\delta)-(x-\delta)\,\text{term}_{SD}(t,x-\delta)}{2\delta}\approx\frac{\partial}{\partial x}\big[x\,\text{term}_{SD}(t,x)\big]$$
With discounting (A.1):
$$F^{syn,m}_t(M)=\frac{APV_t(t\to M)\Pi_t(t\to M)-APV_t(t\to M-1)\Pi_t(t\to M-1)}{PV_t(M)}$$

**Data:**
- Six Silicon Data daily indices: A100 and H100 for both neocloud (NEO) and hyperscaler (HS), plus B200 NEO and MI300X NEO, ending 2026-04-18.

  | Series | Start | Latest value |
  |---|---|---|
  | A100 NEO | 2024-09-01 | 1.430 |
  | H100 NEO | 2024-09-01 | 2.500 |
  | B200 NEO | 2025-08-01 | 5.100 |
  | MI300X NEO | 2026-01-01 | 2.380 |
  | A100 HS | 2024-09-01 | 3.690 |
  | H100 HS | 2024-09-01 | 7.430 |

- Six Ornn series, ending 2026-04-14.
- Silicon Data term and forward curves: tenors 0–36 months on a 0.25-month grid, daily.
- Hold-to-maturity sample starts in 2025-03. Constant-maturity sample starts 2025-08-01 (the B200 36-month series starts 2025-12-11).
- Market betas are estimated against the Fama–French daily market factor (data to 2026-03-31). Trading days follow the `CME_TradeDate` calendar.

**Findings and reported numbers.**

Table 3, average hold-to-maturity returns (%), with annualized values in brackets:

| Maturity | A100 | H100 | B200 |
|---|---|---|---|
| 3 months | 0.83 [3.32] | 6.54 [26.16] | −3.83 [−15.31] |
| 6 months | 2.97 [5.94] | 11.40 [22.80] | 10.21 [20.41] |
| 9 months | 2.18 [2.91] | 17.17 [22.89] | 4.58 [6.11] |
| 12 months | 16.34 [16.34] | 28.72 [28.72] | 12.61 [12.61] |
| All-in (equal-weighted, 1–12 months) | 4.18 [7.46] | 13.43 [26.22] | 4.28 [11.16] |

Table 4, constant-maturity strategies (annualized mean / annualized standard deviation / market beta):

| Maturity | A100 | H100 | B200 |
|---|---|---|---|
| 1 month | −41.7 / 30.2 / 0.21 | 44.4 / 36.5 / −0.11 | −15.3 / 38.5 / 0.18 |
| 6 months | 82.3 / 42.0 / 0.34 | 111.6 / 33.9 / 0.05 | −1.7 / 41.3 / 0.43 |
| 12 months | 9.3 / 31.1 / 0.48 | 30.7 / 29.0 / 0.25 | 88.2 / 43.5 / 0.29 |
| 24 months | 40.0 / 37.6 / 0.29 | 97.2 / 50.5 / 0.12 | −2.3 / 54.2 / 0.11 |
| 36 months | 34.9 / 57.7 / 0.43 | 131.7 / 89.2 / 0.12 | 39.4 / 48.4 / 0.33 |

- 11 of the 15 strategies have positive means.
- The authors attribute weak short-maturity returns to the run-off of the access wedge.

Other reported numbers:
- **Rule of thumb:** if the expected B200 spot price one year ahead is $7, a futures price of about $6.25 implies a premium of about 12% of notional.
- **H100-equivalent prices (Table 2, end of sample):**

  | | A100 | H100 | B200 |
  |---|---|---|---|
  | Rental price per GPU-hour | $1.433 | $2.514 | $5.111 |
  | Peak dense 8-bit throughput (POPS) | 0.624 | 1.979 | 5.000 |
  | Price per H100-equivalent hour | $4.543 | $2.514 | $2.023 |

- **Correlation network:** built on 30-day trailing EMA trends. The Silicon Data and Ornn indices are partly disconnected, with some negative links.
- **Data quality:** early forward-curve records are not harmonized with the spot index, so the authors use the later sample.
- **Scale:** installed stock of 19.70 million H100-equivalents. At $2.50/h (neocloud) that is $431B a year, 1.35% of GDP; at $7.43/h (hyperscaler) it is $1,282B, 4.03% of GDP.

### 3b. SSRN papers (ssrn.com not accessed)

Route used: the Crossref REST API, which carries metadata deposited by SSRN/Elsevier ([V-P] for metadata and abstract only). I searched author pages, RePEc, ResearchGate snippets and arXiv for open full texts and found none. Seung Jung Lee's homepage (https://sites.google.com/site/seunglee98/research) does not list the paper.

**SSRN 6926798.** "Pricing Compute Futures: Forward Curve and Volatility for a Non-Storable, Depreciating Commodity", by **Amine Assody**.
- DOI 10.2139/ssrn.6926798 (https://api.crossref.org/works/10.2139/ssrn.6926798). Crossref record created 2026-07-29.
- Snippets say the paper is dated June 12, 2026, was posted June 19, 2026, is 14 pages, and the author works independently [SNIP].
- Abstract (Crossref, condensed):
  - Compute cannot be stored, so there is no cash-and-carry anchor.
  - Hardware depreciates with each silicon generation, so the forward curve embeds semi-predictable downward jumps.
  - Spot rates mean-revert toward an equilibrium bounded below by an energy-linked marginal cost.
  - **Model:** "a Schwartz-Smith two-factor model extended with a scheduled jump component in which each announced hardware launch window carries a repricing event that is certain to occur but uncertain in size and timing". Options are priced with **Black-76** on the forward.
  - **Predictions:** structural backwardation as the resting curve shape; a steeply declining volatility term structure; localized implied-volatility bumps at launch windows.
  - **Calibration:** the jump size is calibrated to the A100 across the H100 ramp and the H100 across the Blackwell ramp. "Three measurements cluster at **−0.22 in log terms** (roughly −20% in price) per event". "Realized incumbent depreciation runs **15 to 20 percent per year**."
  - It also examines basis risk between blended settlement indices and a specific buyer's exposure.
- **Full text, SDEs and parameter tables: not accessed, so not confirmed.**

**SSRN 7342241.** "Pricing, Hedging, and Securitizing AI Compute: A Non-Storable Commodity Framework for Infrastructure Risk", by **Seung Jung Lee and Sriram Nagaraj**.
- DOI 10.2139/ssrn.7342241 (https://api.crossref.org/works/10.2139/ssrn.7342241). Crossref record created 2026-08-26.
- Snippets say the paper is dated Aug 23, 2026, with Lee at the Federal Reserve Board and Nagaraj at the Federal Reserve Bank of Cleveland [SNIP].
- Abstract (Crossref, condensed):
  - The GPU-hour is treated as a non-storable commodity: the spot price is a rental rate and cannot be inventoried.
  - "We model the log spot rental rate as a **seasonal Schwartz–Smith two-factor process, augmented by upward, fast-reverting price spikes**". A secondary **token-price layer** is driven by **downward algorithmic-efficiency jumps**.
  - The market is incomplete (perishable spot), and a single risk-neutral specification is used.
  - Results include:
    - closed-form forward curves (contango, backwardation, Samuelson and seasonal structure);
    - swap rates and the term structure of the forward risk premium;
    - tail risk, where expected shortfall can be infinite while VaR stays finite;
    - no-arbitrage price intervals and utility-indifference prices;
    - an irreducible basis between token and GPU-hour exposure.
  - It builds a large-pool securitization model. Collateral recovery falls together with default, so fixed-recovery valuation understates senior-tranche expected loss. Under exponential depreciation, required overcollateralization grows exponentially with tenor.
  - A ten-experiment simulation suite is reproducible from a single script.
- **Full text: not accessed, so not confirmed.**

### 3c. Schwartz, E. & Smith, J.E. (2000)

**Citation:** "Short-Term Variations and Long-Term Dynamics in Commodity Prices", *Management Science* 46(7):893–911, July 2000. **DOI 10.1287/mnsc.46.7.893.12034.**
- Verified [V-P] through Crossref (https://api.crossref.org/works/10.1287/mnsc.46.7.893.12034).
- The equations below were **verified [V-P] against the published PDF on J.E. Smith's site**: https://jimsmith.host.dartmouth.edu/wp-content/uploads/2022/04/Short-term_Long-term_Model.pdf (robots allows; Smith is now at Dartmouth, formerly Duke). Equation numbers follow the paper.

**True (physical) process.** $\chi$ is the short-term deviation and $\xi$ the equilibrium level:
$$\ln S_t=\chi_t+\xi_t \tag{decomposition}$$
$$d\chi_t=-\kappa\chi_t\,dt+\sigma_\chi\,dz_\chi \tag{1}$$
$$d\xi_t=\mu_\xi\,dt+\sigma_\xi\,dz_\xi \tag{2}$$
$$dz_\chi\,dz_\xi=\rho_{\chi\xi}\,dt$$
The half-life of a deviation is $-\ln(0.5)/\kappa$.

Distribution of the state:
$$E[(\chi_t,\xi_t)]=\big[e^{-\kappa t}\chi_0,\ \xi_0+\mu_\xi t\big] \tag{3a}$$
$$\mathrm{Cov}[(\chi_t,\xi_t)]=\begin{bmatrix}(1-e^{-2\kappa t})\dfrac{\sigma_\chi^2}{2\kappa} & (1-e^{-\kappa t})\dfrac{\rho_{\chi\xi}\sigma_\chi\sigma_\xi}{\kappa}\\[6pt] (1-e^{-\kappa t})\dfrac{\rho_{\chi\xi}\sigma_\chi\sigma_\xi}{\kappa} & \sigma_\xi^2 t\end{bmatrix} \tag{3b}$$
$$E[\ln S_t]=e^{-\kappa t}\chi_0+\xi_0+\mu_\xi t,\qquad \mathrm{Var}[\ln S_t]=(1-e^{-2\kappa t})\frac{\sigma_\chi^2}{2\kappa}+\sigma_\xi^2 t+2(1-e^{-\kappa t})\frac{\rho_{\chi\xi}\sigma_\chi\sigma_\xi}{\kappa} \tag{4a,b}$$
$$\ln E[S_t]=E[\ln S_t]+\tfrac12\mathrm{Var}[\ln S_t] \tag{5}$$
As $t\to\infty$:
$$\ln E[S_t]\to \xi_0+\frac{\sigma_\chi^2}{4\kappa}+\frac{\rho_{\chi\xi}\sigma_\chi\sigma_\xi}{\kappa}+\left(\mu_\xi+\tfrac12\sigma_\xi^2\right)t \tag{6}$$

**Risk-neutral process.** The risk premia $\lambda_\chi$ and $\lambda_\xi$ are constant reductions in drift, and $\mu^*_\xi\equiv\mu_\xi-\lambda_\xi$:
$$d\chi_t=(-\kappa\chi_t-\lambda_\chi)\,dt+\sigma_\chi\,dz^*_\chi \tag{7a}$$
$$d\xi_t=(\mu_\xi-\lambda_\xi)\,dt+\sigma_\xi\,dz^*_\xi,\qquad dz^*_\chi dz^*_\xi=\rho_{\chi\xi}dt \tag{7b}$$
$$E^*[(\chi_t,\xi_t)]=\big[e^{-\kappa t}\chi_0-(1-e^{-\kappa t})\lambda_\chi/\kappa,\ \xi_0+\mu^*_\xi t\big],\qquad \mathrm{Cov}^*=\mathrm{Cov}$$
$$E^*[\ln S_t]=e^{-\kappa t}\chi_0+\xi_0-(1-e^{-\kappa t})\frac{\lambda_\chi}{\kappa}+\mu^*_\xi t,\qquad \mathrm{Var}^*[\ln S_t]=\mathrm{Var}[\ln S_t] \tag{8a,b}$$

**Futures price** for maturity $T$:
$$\ln F_{T,0}=\ln E^*[S_T]=e^{-\kappa T}\chi_0+\xi_0+A(T) \tag{9}$$
$$A(T)=\mu^*_\xi T-(1-e^{-\kappa T})\frac{\lambda_\chi}{\kappa}+\frac12\left[(1-e^{-2\kappa T})\frac{\sigma_\chi^2}{2\kappa}+\sigma_\xi^2T+2(1-e^{-\kappa T})\frac{\rho_{\chi\xi}\sigma_\chi\sigma_\xi}{\kappa}\right]$$
- The instantaneous variance of $\ln F_{T,t}$ is $e^{-2\kappa T}\sigma_\chi^2+\sigma_\xi^2+2e^{-\kappa T}\rho_{\chi\xi}\sigma_\chi\sigma_\xi$, independent of the state (the Samuelson effect). It tends to $\sigma_\xi^2$ as $T\to\infty$.
- Futures at time $t$: $\ln F_{T,t}=e^{-\kappa(T-t)}\chi_t+\xi_t+A(T-t)$.

**European option on a futures contract** (§3.2), with option expiry $t$ and futures maturity $T$:
$$\sigma^2_\phi(t,T)=e^{-2\kappa(T-t)}(1-e^{-2\kappa t})\frac{\sigma_\chi^2}{2\kappa}+\sigma_\xi^2 t+2e^{-\kappa(T-t)}(1-e^{-\kappa t})\frac{\rho_{\chi\xi}\sigma_\chi\sigma_\xi}{\kappa}$$
$$C=e^{-rt}\big(F_{T,0}N(d)-K\,N(d-\sigma_\phi)\big),\quad d=\frac{\ln(F/K)}{\sigma_\phi}+\tfrac12\sigma_\phi$$
In the extracted PDF text the put reads $e^{-rt}\big(-F_{T,0}N(d)+K\,N(d-\sigma_\phi)\big)$. Minus signs inside $N(\cdot)$ may have been lost in extraction; I could not check this visually. The standard Black-76 put is $e^{-rt}\big(K\,N(-(d-\sigma_\phi))-F_{T,0}N(-d)\big)$. Check the original page 899 if the put is needed.

**State-space (Kalman filter) form used for estimation** (§5.1). Time step $\Delta t$; observations are log futures prices.

Transition equation, which uses the **true** drift $\mu_\xi$:
$$x_t=c+Gx_{t-1}+\omega_t,\quad x_t=\begin{bmatrix}\chi_t\\ \xi_t\end{bmatrix},\quad c=\begin{bmatrix}0\\ \mu_\xi\Delta t\end{bmatrix},\quad G=\begin{bmatrix}e^{-\kappa\Delta t}&0\\0&1\end{bmatrix},\quad \omega_t\sim N(0,W),\ W=\mathrm{Cov}[(\chi_{\Delta t},\xi_{\Delta t})]\ \text{from (3b)} \tag{14}$$

Measurement equation, which uses the **risk-neutral** $A(\cdot)$:
$$y_t=d_t+F_t'x_t+v_t,\quad y_t=\begin{bmatrix}\ln F_{T_1}\\ \vdots\\ \ln F_{T_n}\end{bmatrix},\quad d_t=\begin{bmatrix}A(T_1)\\ \vdots\\ A(T_n)\end{bmatrix},\quad F_t'=\begin{bmatrix}e^{-\kappa T_1}&1\\ \vdots&\vdots\\ e^{-\kappa T_n}&1\end{bmatrix},\quad v_t\sim N(0,V) \tag{15}$$
Note on dimensions: the paper labels $F_t$ as "n × 2", but its own recursions require $F_t$ to be $2\times n$ (so $F_t'$ is $n\times2$).

Kalman recursions:
$$m_t=a_t+A_t(y_t-f_t),\qquad C_t=R_t-A_tQ_tA_t' \tag{16a,b}$$
$$a_t=c+Gm_{t-1},\quad R_t=GC_{t-1}G'+W,\quad f_t=d_t+F_t'a_t,\quad Q_t=F_t'R_tF_t+V,\quad A_t=R_tF_tQ_t^{-1}$$

Estimation details:
- Maximum likelihood over the seven parameters $(\kappa,\sigma_\chi,\mu_\xi,\sigma_\xi,\rho_{\xi\chi},\lambda_\chi,\mu^*_\xi)$, plus $V$, which is assumed **diagonal** $(s_1^2,\dots,s_n^2)$.
- The authors used the Gauss "maxlik" routine. The prior $(m_0,C_0)$ comes from the sample means and covariances.

Reported estimates (Table 2):

| Parameter | Futures data | Enron data |
|---|---|---|
| $\kappa$ | 1.49 | 1.19 |
| $\sigma_\chi$ | 28.6% | 15.8% |
| $\lambda_\chi$ | 15.7% | 1.4% |
| $\mu_\xi$ | −1.25% | −3.86% |
| $\sigma_\xi$ | 14.5% | 11.5% |
| $\mu^*_\xi$ | 1.15% | 1.61% |
| $\rho_{\xi\chi}$ | 0.300 | 0.189 |

The two data sets (§6):
- **Futures data:** weekly NYMEX crude oil futures maturing in about 1, 5, 9, 13 and 17 months, from 1990-01-02 to 1995-02-17 (259 weekly sets). Estimated half-life is about 6 months.
- **Enron data:** proprietary crude forward curves at 2, 5 and 8 months and 1, 1.5, 2, 3, 5, 7 and 9 years, from 1993-01-15 to 1996-05-16 (163 sets). Estimated half-life is about 7 months.

The paper also shows the model is equivalent to the Gibson–Schwartz (1990) stochastic convenience-yield model (Table 1 maps the parameters).

### 3d. Other directly relevant, freely accessible papers (all [V-P] via arxiv.org/abs)

1. **arXiv 2603.21690**, Xing, Y. (2026-03-23), "AI Token Futures Market: Commoditization of Compute and Derivatives Contract Design".
   - Proposes a standardized token futures design (settlement, margin, market makers).
   - Uses a **mean-reverting jump-diffusion** with Monte Carlo hedging-efficiency tests (62–78% cost-volatility reduction in its scenario).
   - Discusses GPU compute futures.
2. **arXiv 2212.06888**, He, Manela, Ross & von Wachter, "Fundamentals of Perpetual Futures" (v1 2022-12-13; latest online 2026-09-17).
   - No-arbitrage pricing of perpetual futures.
   - Relevant because the CFTC RFC asks specifically about *perpetual compute futures*, and Bandi & Su cite this paper.
3. **arXiv 1809.03110**, Shastri & Irwin (2018), "Cloud Index Tracking: Enabling Predictable Costs in Cloud Spot Markets".
   - Shows that aggregating cloud spot prices into an index makes the price stable and predictable.
   - A close antecedent for compute-price indexation and index-tracking hedges.
4. **arXiv 2511.23455**, Gundlach, Lynch, Mertens & Thompson (v2 2026-03-23), "The Price of Progress: Price Performance and the Future of AI".
   - Finds the price for a given benchmark performance falls about 5–10x per year, and estimates algorithmic efficiency at about 3x per year.
   - Relevant to the deterministic decline and obsolescence drift in rental prices.
5. **arXiv 1807.10507**, Ekwe-Ekwe & Barker (2018), "Location, Location, Location: Exploring Amazon EC2 Spot Instance Pricing Across Geographical Regions".
   - Empirical regional dispersion in cloud rental prices.
   - Relevant to geography basis, since GPU1/GPU2 specify "Geography: United States".

---

## 4. Hardware launch calendar for a "scheduled jump at each launch window" model

Event types:
- **Ann** = announced, with the stated availability window
- **Prod** = in production
- **Ship/GA** = shipped or generally available
- **Index** = start of Silicon Data's neocloud coverage, which marks when enough neocloud listings existed

| Generation | Date | Type | What the source says | Source | Status |
|---|---|---|---|---|---|
| H100 (Hopper) | **2022-03-22** (GTC) | Ann | "NVIDIA H100 will be available starting in the third quarter" | https://nvidianews.nvidia.com/news/nvidia-announces-hopper-architecture-the-next-generation-of-accelerated-computing | [V-P] |
| H100 | **2022-09-20** (GTC) | Prod | "in full production"; partner products roll out "in October"; AWS, Google, Azure and OCI H100 instances "starting next year" | https://nvidianews.nvidia.com/news/nvidia-hopper-in-full-production | [V-P] |
| H100 | **2023-03-21** (GTC) | Ship/GA | H100 in the cloud: "available now from Azure in private preview, Oracle Cloud Infrastructure in limited availability, and generally available from Cirrascale and CoreWeave"; AWS limited preview "in the coming weeks"; "The H100 began shipping in the fall" | https://nvidianews.nvidia.com/news/nvidia-hopper-gpus-expand-reach-as-demand-for-ai-grows | [V-P] |
| H100 | **2023-07-26** | GA (hyperscaler) | AWS "officially switched on" EC2 P5 (H100) | https://blogs.nvidia.com/blog/aws-cloud-h100/ | [V-P] |
| H100 | 2024-09-01 | Index | SDH100RT history start | Silicon Data docs | [V-P] |
| H200 | **2023-11-13** (SC23) | Ann | "available from global system manufacturers and cloud service providers starting in the second quarter of 2024"; CoreWeave, Lambda and Vultr among the first | https://nvidianews.nvidia.com/news/nvidia-supercharges-hopper-the-worlds-leading-ai-computing-platform | [V-P] |
| H200 | 2024-04 (reported as Apr 24) | Ship | First DGX H200 hand-delivered to OpenAI | e.g. https://www.tomshardware.com/tech-industry/artificial-intelligence/nvidia-ceo-hand-delivers-worlds-fastest-ai-system-to-openai-again-first-dgx-h200-given-to-sam-altman-and-greg-brockman | [SNIP] |
| H200 | 2024-Q3 | Ship (volume) | Large-scale deliveries "from Q3" | https://www.trendforce.com/news/2024/07/02/news-nvidias-h200-order-delivered-from-q3-boosting-server-supply-chain-with-strong-demand/ | [SNIP] |
| H200 | 2026-05-04 (launched 2026-07-15) | Index | H200 neocloud index history start | Silicon Data docs | [V-P] |
| B200 / GB200 (Blackwell) | **2024-03-18** (GTC) | Ann | "Blackwell-based products will be available from partners starting later this year" (2024) | https://nvidianews.nvidia.com/news/nvidia-blackwell-platform-arrives-to-power-a-new-era-of-computing | [V-P] |
| GB200 NVL72 | **2025-02-04** | GA (neocloud) | CoreWeave is "the first cloud service provider to make the NVIDIA Blackwell platform generally available" | https://blogs.nvidia.com/blog/blackwell-coreweave-gb200-nvl72-instances-cloud/ | [V-P] |
| Blackwell | **2025-02-26** (Q4 FY25 results; quarter ended 2025-01-26) | Ship (volume) | "We've successfully ramped up the massive-scale production of Blackwell AI supercomputers, achieving billions of dollars in sales in its first quarter." The "$11.0B Blackwell revenue" figure is from the CFO commentary [SNIP] | https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-fourth-quarter-and-fiscal-2025 | [V-P] |
| Blackwell | **2025-03-18** (GTC 2025) | Prod | "NVIDIA Blackwell is in full production" | https://blogs.nvidia.com/blog/nvidia-keynote-at-gtc-2025-ai-news-live-updates/ | [V-P] |
| B200 (HGX) | **2025-05-15** | GA (hyperscaler) | AWS EC2 P6-B200 generally available (Capacity Blocks, US West (Oregon)) | https://aws.amazon.com/about-aws/whats-new/2025/05/amazon-ec2-p6-b200-instances-nvidia-b200-gpus/ | [V-P] |
| B200 | 2025-08 (2025-08-01) | Index | SDB200RT history start; public launch 2025-12-04 | Silicon Data blog and docs [V-P]; Bandi & Su Table 1 [V-S] | [V-P]/[V-S] |
| B300 / GB300 (Blackwell Ultra) | **2025-03-18** (GTC) | Ann | "expected to be available from partners starting from the second half of 2025" | https://nvidianews.nvidia.com/news/nvidia-blackwell-ultra-ai-factory-platform-paves-way-for-age-of-ai-reasoning | [V-P] |
| GB300 NVL72 | **2025-07-03** | Ship (first cloud deployment) | CoreWeave "first AI cloud provider to deploy the latest NVIDIA GB300 NVL72 systems" (with Dell, Switch, Vertiv) | https://www.prnewswire.com/news-releases/coreweave-becomes-first-hyperscaler-to-deploy-nvidia-gb300-nvl72-platform-302497802.html | [V-P] |
| Blackwell Ultra | **2025-08-27** (Q2 FY26) | Prod/ramp | "production of Blackwell Ultra is ramping at full speed" | https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-second-quarter-fiscal-2026 | [V-P] |
| B300 | 2026-04-23 (launched 2026-09-14) | Index | B300 neocloud index start date | Silicon Data docs | [V-P] |
| Rubin / Vera Rubin | **2024-06-02** (Computex keynote) | Ann (roadmap) | "Revealed for the first time, the Rubin platform will succeed the upcoming Blackwell platform"; "one-year rhythm". The "2026" timing appears only in secondary coverage | https://blogs.nvidia.com/blog/computex-2024-jensen-huang/ | [V-P] (reveal); 2026 timing [SNIP] |
| Vera Rubin NVL144 | **2025-03-18** (GTC 2025) | Ann (roadmap) | Verbatim from NVIDIA's blog: "Systems built on Rubin Ultra, including the Vera Rubin NVL 144, will arrive in the second half of next year. And due for the second half of 2027: systems built on Rubin Ultra." ("next year" = 2026; the blog's own wording mixes Rubin and Rubin Ultra) | https://blogs.nvidia.com/blog/nvidia-keynote-at-gtc-2025-ai-news-live-updates/ | [V-P] |
| Rubin | **2026-01-05** (CES) | Prod (announced) | "NVIDIA Rubin is in full production, and Rubin-based products will be available from partners the second half of 2026"; CoreWeave to integrate Rubin "beginning in the second half of 2026" | https://nvidianews.nvidia.com/news/rubin-platform-ai-supercomputer | [V-P] |
| Vera Rubin | **2026-03-16** (GTC 2026) | Ann (availability) | "Vera Rubin-based products will be available from partners starting the second half of this year" | https://nvidianews.nvidia.com/news/nvidia-vera-rubin-platform | [V-P] |
| Vera Rubin | **2026-08-26** (Q2 FY27 results; quarter ended 2026-07-26) | Ship (at partners) | "the NVIDIA Vera Rubin platform is ramping into full production with racks running at partners including CoreWeave, Google Cloud, Microsoft Azure, Oracle Cloud Infrastructure and Nebius"; "Vera Rubin, now in full production" | https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-second-quarter-fiscal-2027 | [V-P] |
| Feynman | 2026-03 (GTC 2026) | Ann (roadmap) | "NVIDIA's next major architecture is Feynman" after Vera Rubin. A 2028 date appears in secondary coverage of GTC 2025 | https://blogs.nvidia.com/blog/gtc-2026-news/ | [V-P] (named); 2028 [SNIP] |

There is no Silicon Data Rubin index as of the latest announcement log (2026-09-11). [V-P]

---

## 5. Confirmed facts

| # | Fact | Value | Source URL | Status |
|---|---|---|---|---|
| 1 | Contract names | Silicon Data H100 Rental Index Futures; Silicon Data B200 Rental Index Futures | https://www.cftc.gov/filings/ptc/ptc08112615405.pdf | V-P |
| 2 | Globex/ClearPort codes | GPU1 (H100), GPU2 (B200) | same | V-P |
| 3 | Exchange; rule chapters | NYMEX; 1045 (H100), 1047 (B200) | same | V-P |
| 4 | Contract unit | 730 GPU-hours | same | V-P |
| 5 | Quotation | USD and cents per GPU-hour | same | V-P |
| 6 | Tick / tick value | $0.01 per GPU-hour = $7.30; $0.005 for Globex inter-commodity spreads | same | V-P |
| 7 | Settlement | Financial (cash) against the Floating Price | same | V-P |
| 8 | Floating price | Arithmetic average of SD-H100 / SD-B200 "on-demand settlement prices" for each Business Day of the contract month | same | V-P |
| 9 | Index technical configuration | Geography: United States | same | V-P |
| 10 | Termination of trading | Last Business Day of the contract month | same | V-P |
| 11 | Listing schedule | 36 consecutive monthly contracts; first listing October 2026 | same | V-P |
| 12 | Intended first trade date | 2026-10-05 (Globex open Sunday 2026-10-04), subject to approval | same | V-P |
| 13 | Hours | Globex Sun 5 pm – Fri 4 pm CT, 4–5 pm CT maintenance; ClearPort same span | same | V-P |
| 14 | Matching algorithm | FIFO | same | V-P |
| 15 | Block minimum | 5 contracts; 15-minute reporting | same | V-P |
| 16 | Non-reviewable range | $0.20 per GPU-hour (20 ticks) | same | V-P |
| 17 | Position limits GPU1 | Spot month 7,500 (from close 3 business days before the last trading day); single-month accountability 15,000; all-month 22,500; reportable 25 | https://www.cftc.gov/filings/ptc/ptc08112615406.xlsx | V-P |
| 18 | Position limits GPU2 | Spot month 5,500; single-month 11,000; all-month 16,500; reportable 25 | same | V-P |
| 19 | Exchange fees | Globex $3.65 member / $5.50 non-member; block $6.00 / $7.30; cash settlement $0.90 / $1.35; plus facilitation, give-up and position-transfer fees | https://www.cftc.gov/filings/ptc/ptc08112615405.pdf | V-P |
| 20 | Regulatory route | CFTC Reg. 40.3(a) voluntary approval, Submission 26-370 (+26-370S), filed 2026-08-11 | same | V-P |
| 21 | Review extended | 45 more days, "until the end of November 9, 2026"; "novel or complex issues" | https://www.cftc.gov/filings/documents/2026/orgdcmnymexcompcontr260921.pdf | V-P |
| 22 | Status on 2026-10-05 | "Approval Pending (90)", dated 2026-09-21, for both products, so not trading | https://www.cftc.gov/IndustryOversight/IndustryFilings/TradingOrganizationProducts/62544 ; .../62545 | V-P |
| 23 | CFTC compute RFC | Issued 2026-08-19; 91 FR 54259 (2026-08-21); RIN 3038-AF77; comments due 2026-10-20 | https://www.cftc.gov/PressRoom/PressReleases/9286-26 ; https://www.govinfo.gov/content/pkg/FR-2026-08-21/pdf/2026-17163.pdf | V-P |
| 24 | Launch press release | 2026-08-11; launch "on October 5, 2026, pending regulatory review"; one contract = "a month's worth of rent" | https://www.prnewswire.com/news-releases/cme-group-and-silicon-data-to-launch-compute-futures-on-october-5-to-unlock-new-way-to-hedge-ai-risks-302848593.html | V-P |
| 25 | Index publisher | Silicon Derivatives Inc. ("Silicon Data"), backed by DRW | filing; PR | V-P |
| 26 | Index tickers | SDH100RT / .SDH100RT; SDB200RT / .SDB200RT ("Neocloud Index") | https://docs.silicondata.com/products/gpu-index-announcements | V-P |
| 27 | GPU1 references neocloud only | "GPU1 settles exclusively against an index of independent neocloud providers" | https://www.silicondata.com/blog/practitioners-guide-compute-future-hedge-step-by-step | V-P (Silicon Data) |
| 28 | CME description of the index | "neocloud indices (non-hyperscaler) measuring hourly on-demand rental GPU costs" | https://www.cmegroup.com/markets/energy/power/compute-futures.html | SNIP |
| 29 | Index steps | Preprocess (USD/GPU-h), filter, basis-adjust (rental type, country, CPU, GPU variant), provider means, weighted average with "market relevance" weights | https://www.silicondata.com/documents/silicon-data-index-methodology.pdf | V-P |
| 30 | Recalibration | Pricing model recalibrated weekly | same | V-P |
| 31 | Publication cadence | "processed and published once per business day" | https://www.silicondata.com/products/silicon-index | V-P |
| 32 | History start | H100 and A100 2024-09-01; B200 Aug 2025 | docs; https://www.silicondata.com/blog/b200-rental-price-august-2026-update | V-P |
| 33 | Index level breaks | 2025-03-01, 2025-12-04 (restated), 2026-04-06, 2026-07-15, 2026-09-25 (see §2.6) | https://docs.silicondata.com/products/gpu-index-announcements | V-P |
| 34 | Latest values (2026-10-05) | SDH100RT 2.81; SDB200RT 5.87 USD/GPU-h | https://www.silicondata.com/products/silicon-index/h100 ; .../b200 | V-P |
| 35 | Realized annualized vol through 2026-08-14 | B200 30.2%; H100 26.2%; A100 14.7% | https://www.silicondata.com/blog/cash-settled-compute-futures | V-P |
| 36 | arXiv 2607.12156 | Bandi & Su, "(Early) AI Compute Asset Pricing", q-fin.PR, v3 2026-09-10 | https://arxiv.org/abs/2607.12156 | V-P |
| 37 | Bandi & Su risk-premium estimate | All-in hold-to-maturity averages 4.18% / 13.43% / 4.28% (A100/H100/B200); annualized 7.46% / 26.22% / 11.16% | https://arxiv.org/pdf/2607.12156v3 | V-P |
| 38 | Bandi & Su content | No SDE, jump or depreciation state model | same | V-P |
| 39 | SSRN 6926798 metadata | Assody, "Pricing Compute Futures: …"; Schwartz–Smith + scheduled jumps; jump about −0.22 log; depreciation 15–20%/yr | https://api.crossref.org/works/10.2139/ssrn.6926798 | V-P (abstract only) |
| 40 | SSRN 7342241 metadata | Lee & Nagaraj, "Pricing, Hedging, and Securitizing AI Compute …"; seasonal Schwartz–Smith + upward spikes; token layer with downward jumps | https://api.crossref.org/works/10.2139/ssrn.7342241 | V-P (abstract only) |
| 41 | Schwartz–Smith citation | Mgmt Sci 46(7):893–911, July 2000, DOI 10.1287/mnsc.46.7.893.12034 | https://api.crossref.org/works/10.1287/mnsc.46.7.893.12034 | V-P |
| 42 | Schwartz–Smith equations | (1)–(9), (14)–(16) as transcribed in §3c | https://jimsmith.host.dartmouth.edu/wp-content/uploads/2022/04/Short-term_Long-term_Model.pdf | V-P |
| 43 | H100 dates | Announced 2022-03-22; full production 2022-09-20; cloud 2023-03-21; AWS P5 2023-07-26 | §4 URLs | V-P |
| 44 | H200 dates | Announced 2023-11-13; availability from Q2 2024 | §4 URL | V-P |
| 45 | B200 dates | Announced 2024-03-18; CoreWeave GB200 GA 2025-02-04; full production (GTC) 2025-03-18; AWS P6-B200 GA 2025-05-15 | §4 URLs | V-P |
| 46 | B300/GB300 dates | Announced 2025-03-18 (H2 2025); first CoreWeave deployment 2025-07-03; "ramping at full speed" 2025-08-27 | §4 URLs | V-P |
| 47 | Rubin dates | Revealed 2024-06-02; H2 2026 target (2025-03-18); "in full production" 2026-01-05; racks running at partners 2026-08-26 | §4 URLs | V-P |

---

## 6. Not confirmed

- **Initial and maintenance margins** for GPU1/GPU2. They are not in the CFTC filing, and CME's margin pages are off-limits.
- **What happens on a missing or late index day.** No fallback appears in chapters 1045/1047 as filed. The NYMEX general rules and the definition of "Business Day" were not reviewed (cmegroup.com off-limits).
- **The meaning of "Diminishing Balance Contract: Y"** in Exhibit B for these contracts.
- **Any CME-announced new listing date** after the CFTC extension. Whether the CFTC will approve on or before 2026-11-09 is unknown.
- **CME clearing notice 26-274** ("New Product Summary … Effective October 5, 2026"): seen only as a snippet title; contents not read.
- **Silicon Data publication time and time zone** for SDH100RT and SDB200RT.
- **Whether weekend and holiday index values are produced.** There is suggestive evidence (the API example dated a Saturday, and a calendar-day observation count [INF]), but nothing confirms it. Business-day publication is stated.
- **Exact inclusion rules for SDH100RT and SDB200RT:**
  - whether reserved or spot records enter after basis adjustment;
  - whether any hyperscaler, colocation or private-market records enter (the B200 product page says the index "blends" them, while other Silicon Data pages say neocloud);
  - the list of providers;
  - the weights $w_j(t)$.
- **Baseline GPU variant** (SXM vs PCIe) for SDH100RT after the 2026-09-25 change, and for SDB200RT.
- **Full texts of SSRN 6926798 and 7342241.** Their SDE specifications, parameter tables and calibration details are not confirmed; only the Crossref abstracts were read. The date, page count and affiliation details are snippet-only.
- **NVIDIA's "$11.0B Blackwell revenue" in Q4 FY25.** Snippet only; the CFO commentary on sec.gov was not fetched, because SEC requires a contact-bearing User-Agent.
- **H200 first-shipment and volume dates** (April 2024 OpenAI delivery; Q3 2024 volume). Secondary snippets only.
- **"Rubin in 2026" as stated at Computex 2024, and "Feynman in 2028".** Snippet only; the NVIDIA pages I fetched confirm the Rubin reveal and that Feynman is the next architecture, but not those dates.
- ***The Information*'s 2026-09-25 report.** Seen only via FinanceFeeds (secondary).
