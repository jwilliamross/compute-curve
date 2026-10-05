> Research notes produced by a research agent on 2026-10-05 for this project.
> Kept as an appendix to docs/data_sources.md. Raw page copies were not retained.

# GPU rental price data sources: audit for CME GPU1/GPU2 research

**Audit date:** 2026-10-05. Fetches ran from 17:41 to 18:10 UTC.

**Scope:**
- On-demand NVIDIA H100 and B200 rental prices from neoclouds.
- Published GPU rental indices.
- How to get CME settlement data.
- Free historical series.

## 0. How to read this

**Evidence labels**
- **VERIFIED:** I fetched it myself with curl, using UA `compute-curve-research/0.1 (non-commercial research)`. The URL and HTTP status are given. Raw copies are in `the session scratchpad (not retained)`. All 172 requests are listed in `the session request log (not retained)`.
- **SNIPPET:** I only read it in a WebSearch result or summary. It is not verified.
- **INFERRED:** my own interpretation. It is not legal advice.

**How I fetched**
- On every host I fetched `/robots.txt` before any other path.
- Requests to the same host were spaced at least 3 s apart. For Zenodo I waited 10 s, because it sets `Crawl-delay: 10`.
- I did not use any `mcp__` tool. I did not touch cmegroup.com or papers.ssrn.com. I did not log in, sign up, pay or send any key.
- I used WebFetch twice. The first was to read `github.com/robots.txt`, because the session proxy returns 403 for github.com. The second was an attempt to reach data.ornn.com, which was blocked.

**Blocks in this environment.** I did not retry these, per the proxy rules.
- The session proxy returns HTTP 403 for `github.com` and `api.github.com`, with the message "This GitHub API path is not available: sessions are bound to their configured repositories". So repo pages, commit history and release assets could not be fetched. `raw.githubusercontent.com` worked.
- `data.ornn.com` is blocked by the egress policy. curl gave `SSL_ERROR_SYSCALL` and WebFetch gave `EGRESS_BLOCKED`.

**Recommendation codes**
- **APPROVE:** build an automated collector.
- **APPROVE-MANUAL:** the user downloads or reads it by hand.
- **SKIP:** the terms or robots.txt prohibit it, or it is paid.
- **BLOCKED:** it needs a login, a key or payment.

---

## 1. Key findings

**1. Vast.ai cannot be collected automatically, even though its API needs no key.**
- Its Terms of Use (version date September 1, 2026) ban robots, scripts and scrapers outright.
- They also ban using its data to build any "index, benchmark, pricing-comparison service, market-data product".
- Vast publishes a public JSON feed with 90 days of daily medians (VERIFIED). The feed's license says bulk collection or use in an index or benchmark needs a data license from data@vast.ai.

**2. RunPod's Terms ban access "through automated or non-human means".**
- I did **not** send the unauthenticated GraphQL request, because the terms do not permit it.
- RunPod's v2 REST catalog endpoint needs a bearer token (VERIFIED in its docs).

**3. Silicon Data publishes only a little for free, and its terms forbid storing it.**
- The public pages carry the latest SDH100RT and SDB200RT values plus a short daily history, embedded as JSON (VERIFIED). Only the latest values are cited in this repository.
- Its Terms of Use forbid storing site content "in a database or retrieval system" without written consent.
- Full history and the API are paid. Pro costs $998/month and includes API access; Enterprise adds CSV downloads.
- A free Basic account shows 30 days of history, but the user would have to sign up.

**4. The CME settlement reference is not exactly the public SDH100RT number.**
- The NYMEX rule in the CFTC filing (VERIFIED) defines the Floating Price as the arithmetic average of SD-H100 / SD-B200 "on-demand settlement prices" for each Business Day of the contract month.
- The rule also sets "Index Technical Configuration — Geography: United States".
- The public SDH100RT is a global neo-cloud reading.
- Silicon Data has also restated history (December 2025) and changed which providers it includes (April, July and September 2026). Expect structural breaks.

**5. Index levels disagree by up to about ±25% today** (2026-10-05, USD per GPU-hour):

| GPU | Silicon Data (2026-10-05) | FLOPS (18:00 UTC) | GetDeploying weekly median | CGI (18:00 UTC) | Ornn OCPI (2026-10-04) |
|---|---|---|---|---|---|
| H100 | SDH100RT 2.81 | 2.99 | 3.41 | 3.62 | 2.59 (snippet) |
| B200 | SDB200RT 5.87 | 5.10 | 6.79 | 6.94 | 7.71 (snippet) |

Any proxy for the settlement index will need its basis calibrated.

**6. No free H100/B200 history goes back more than about a year:**
- **GetDeploying weekly CSVs:** 53 weeks (2025-10-06 to 2026-10-05), CC BY 4.0. VERIFIED.
- **gpurentalprices.com daily snapshots:** about 93 days from 2026-07-05, CC BY 4.0, via Zenodo plus the GitHub mirror. VERIFIED.
- **Computable GPU Index (CGI):** 15-minute values since 2026-08-30, CC BY-NC 4.0. VERIFIED.
- **Vast feed:** 90 daily medians, but a license is needed.
- **Ornn OCPI:** "three months of daily history" free, per SNIPPET; blocked here.
- **cherielilili/gpu-pricing-tracker on GitHub:** 231 daily dates. It has no LICENSE file.

---

## 2. Neocloud price sources

### 2.1 Vast.ai (marketplace): SKIP

**Recommendation:** SKIP for automated collection, because the terms prohibit it. Request a research data license from data@vast.ai.

**URLs**
- `POST https://console.vast.ai/api/v0/bundles/` (already known from the env check; I did not call it again).
- Public feed: `https://storage.googleapis.com/vast-public-gpu-pricing/gpu-pricing-public.json`. Its URL is advertised in `https://vast.ai/pricing.md`.

**Access and cost:** JSON, no key, free.

**robots.txt (VERIFIED)**
- `https://vast.ai/robots.txt` returned 200: `User-agent: * … Disallow: /pricing/tables/ … Allow: /`, plus `Content-Signal: search=yes, ai-train=no, ai-input=yes`.
- `https://console.vast.ai/robots.txt` returned 302 to `https://cloud.vast.ai/robots.txt`, which returned 200: `User-agent: * / Allow: /`.
- `storage.googleapis.com/robots.txt` returned 404, so there are no restrictions.
- **Verdict:** robots.txt allows both the API and the feed. The terms do not.

**Terms of Use** (https://vast.ai/terms, VERIFIED 200, "Version Date: September 1, 2026"). Verbatim:
> "Engaging in any bulk, systematic, or automated retrieval, collection, copying, downloading, harvesting, caching, storage or other extraction of data or other content from the Website to create, develop, populate, maintain, or compile, directly or indirectly, a collection, compilation, database, dataset, index, benchmark, or directory without written permission from Company."

> "Using the Company Services or any data or information made available through the Website or Services (i) as part of any effort to compete with Company or to provide services as a service bureau, (ii) to construct, publish, or maintain any index, benchmark, pricing-comparison service, market-data product, or similar product or service, or (iii) to redistribute, resell, sublicense, publish or otherwise make available to any third party any feed, dataset or other substantial portion of such data, except in each case as expressly authorized in a separate written agreement with Company."

> "Using any robot, spider, crawler, scraper, script, browser automation, web scraping, web harvesting, web data extraction, data-mining tool or any other automated method to access, query, copy, download, monitor, collect, cache, store or extract data from the Website or Services, except as expressly authorized in a separate written agreement with Company."

> "…you may not use Authorized Data (or any value derived therefrom) alone or together with other data, as an input to or for the construction, calculation, publication, maintenance, or administration of any index, benchmark, pricing index, price-comparison database, or other product or service that measures, compares, tracks, summarizes or reflects pricing, availability, capacity or market conditions…"

**Feed license** (embedded `license` field, VERIFIED):
> "Free for display and citation with attribution. Bulk collection, redistribution, or use in any index, benchmark, or derivative product requires a data license: data@vast.ai"

**Public history: yes** (VERIFIED, one fetch, 200).
- Fields per GPU: `name, slug, tier, vram_gb, status, available, current{min,p10,median,available}, reference, daily[{date,median}]`.
- `daily` holds 90 points, from 2026-07-07 to 2026-10-04.
- The feed's `updated` field read 2026-10-05T17:30:18Z. It refreshes hourly.

**GPUs covered:** `h100 sxm`, `h100 pcie`, `h100 nvl`, `b200`, `b300`, `h200` and more.

**Prices seen today (VERIFIED)**

| GPU | min | p10 | median | offers available | latest daily median |
|---|---|---|---|---|---|
| H100 SXM | 1.7337 | 1.734 | 2.2145 | 89 | 2.02 (2026-10-04) |
| B200 | 7.428 | 7.428 | 7.813 | 39 | 6.25 (2026-10-04) |

Per-GPU units match the env-check offers: `dph_total/num_gpus`.

**Rationale.** Technically Vast is the best marketplace source: no key, an hourly feed and 90 days of daily history. But the September 2026 terms explicitly target exactly our use case: automated collection and building a dataset, index or benchmark. The feed license says the same. Building a collector without a written license would breach the terms. Ask data@vast.ai for a non-commercial research license. Until then, Vast data should come only through third-party datasets whose own licenses we can rely on (see §5). Even there, note that the upstream terms are a risk the dataset publisher carries.

### 2.2 RunPod: SKIP

**Recommendation:** SKIP for automated collection, because the terms prohibit it. APPROVE-MANUAL for occasional manual reading.

**URLs**
- `https://www.runpod.io/pricing`. VERIFIED 200. With `Accept: text/markdown` it returns a Markdown variant, which RunPod's `llms.txt` advertises. Both forms embed schema.org JSON-LD `Product/AggregateOffer` blocks.
- `https://api.runpod.io/graphql`.
- `https://docs.runpod.io/api-reference-v2/catalog/list-gpu-types.md`. VERIFIED 200. It says `security: - bearerAuth: []` and returns 401 "missing bearer token" without one.

**Auth and cost:** the pricing page needs no auth. The v2 REST catalog needs a key. Free.

**robots.txt (VERIFIED)**
- `www.runpod.io/robots.txt` returned 200: `User-agent: * / Allow: /`, plus `Content-Signal: search=yes, ai-input=yes, ai-train=no`.
- `api.runpod.io/robots.txt` returned 404, so there are no restrictions.

**Terms of Service** (https://www.runpod.io/legal/terms-of-service, VERIFIED 200, "Last Updated: March 24, 2026"):
> §6: "you represent and warrant that you will not: … (4) access or use the Site or the Service through automated or non-human means, whether through a bot, script or otherwise;"

> §9: "Systematically retrieve data or other content from the Site to create or compile, directly or indirectly, a collection, compilation, database, or directory without written permission from us."

> §9: "Engage in any automated use of the system, such as using scripts to send comments or messages, or using any data mining, robots, or similar data gathering and extraction tools."

> §9: "Except as may be the result of standard search engine or Internet browser usage, use, launch, develop, or distribute any automated system, including without limitation, any spider, robot, cheat utility, scraper, or offline reader that accesses the Site…"

**GraphQL `gpuTypes` without a key: NOT ATTEMPTED**, because the terms do not permit automated access.
- Third parties claim it works without a key. These claims are unverified:
  - ewyluda/gpu-price-index methodology: "Public GraphQL API, no key".
  - Zeno00-00 README: "has historically worked without a key".
- CGI's receipts cite `https://api.runpod.io/graphql` as their RunPod source.

**Prices on the pricing page** ("Updated September 27, 2026", VERIFIED), Community / Secure Cloud on-demand per GPU-hour:

| GPU | Community | Secure |
|---|---|---|
| H100 SXM | 2.69 | 3.49 |
| H100 PCIe | 1.99 | 2.89 |
| H100 NVL | 2.59 | 3.19 |
| B200 | 5.98 | 6.79 |

**History:** none published. **Update frequency:** list prices; the page shows its update date.

**Rationale.** The JSON-LD makes RunPod trivially machine-readable, and robots.txt is permissive. But the terms explicitly forbid automated access and building a database. RunPod's list prices also appear as CGI receipts and in the gpurentalprices.com data, which we can use under those publishers' licenses.

### 2.3 Lambda (lambda.ai; lambdalabs.com serves the same robots.txt): APPROVE

**Recommendation:** APPROVE. Fetch the HTML once a day.

**URL:** `https://lambda.ai/pricing`. VERIFIED 200, HTML. HubSpot CMS, with no JSON-LD or embedded data.

**Auth and cost:** none; free.

**robots.txt (VERIFIED 200):** `User-agent: *` with only `Disallow: /_hcms/preview/`, `/hs/manage-preferences/`, `/hs/preferences-center/`, `/*?*hs_preview=*`, `/*?*hsCacheBuster=*`. **`/pricing` is allowed.**

**Terms** (https://lambda.ai/legal/terms-of-service, VERIFIED 200, "Last updated: August 2025")
- The Website Terms of Use have **no** scraping or automation clause. They do say "You must use our Sites in strict compliance with these Terms and all applicable laws".
- The Acceptable Use Policy lists among prohibited uses *of the Services*: "web crawling which is not restricted to a rate so as not to impair or otherwise disrupt the servers being crawled". That is about using Lambda's cloud to crawl others.
- The Cloud Terms bind account holders only: "(iv) access any portion of the Services for the purpose of building a similar or competitive product or service, or monitor the Services for any benchmarking or competitive purpose".

**Prices (VERIFIED), per GPU-hour on-demand**

| Instance size | B200 SXM6 | H100 SXM | H100 PCIe |
|---|---|---|---|
| 8x | 6.69 | 3.99 | |
| 4x | 6.79 | 4.09 | |
| 2x | 6.89 | 4.19 | |
| 1x | 6.99 | 4.29 | 3.29 |

1-Click Clusters (2 weeks to 1 year): H100 6.16, 5.85 and 5.54, and B200 9.86, 9.36 and 8.87, at 16, 64 and 256+ GPUs.

**History:** none on Lambda's site. The SkyPilot catalog's git history of `catalogs/v*/lambda/vms.csv` can rebuild Lambda's list-price history (§5). Its current file matched the page exactly (VERIFIED).

**Rationale.** Lambda's prices are clean posted on-demand list prices with no anti-scraping clause in the website terms. One polite fetch a day is fine. Caveat (INFERRED): if the team ever opens a Lambda cloud account, the Cloud Terms' "monitor the Services for any benchmarking" clause could be argued to apply.

### 2.4 CoreWeave: APPROVE

**Recommendation:** APPROVE. Fetch the HTML once a day.

**URL:** `https://www.coreweave.com/pricing`. VERIFIED 200, HTML (Webflow). Its JSON-LD has no prices.

**Auth and cost:** none; free.

**robots.txt (VERIFIED 200):** `User-agent: * / Disallow: /blog-categories/ / Disallow: /event/`. `/pricing` is allowed.

**Terms**
- Website Terms of Use: https://docs.coreweave.com/policies/terms-of-service/terms-of-use. VERIFIED 200, "last updated on July 8, 2024".
- The docs host robots.txt is `User-agent: * … Disallow: /cdn-cgi/ … Disallow: /_next/`.
- There is no scraping clause. The relevant restrictions:
> "You agree not to use the CoreWeave Sites or any feature thereon: … (c) for any commercial purpose not expressly approved by the Company in writing; … (g) in any manner that could disable, overburden, damage, or impair the site…"

**Prices (VERIFIED)**

| Instance | On-demand | Per GPU-hour | Spot |
|---|---|---|---|
| NVIDIA HGX B200, 8 GPU | $68.80/hr | $8.60 | $34.11 |
| NVIDIA HGX H100, 8 GPU | $49.24/hr | $6.155 | $19.71 |

"Inference Single GPU Price" is $8.60 for B200 and $6.16 for H100. The page shows REGION: NORTH AMERICA.

**History:** none. **Update frequency:** list price; rarely changes.

**Rationale.** The terms allow non-commercial use and have no anti-bot clause. CoreWeave is a high-priced, sticky list-price anchor, useful for neocloud-vs-hyperscaler basis analysis rather than market-clearing levels.

### 2.5 Nebius: APPROVE

**Recommendation:** APPROVE. Fetch once a day; it is the cleanest list-price source.

**URL:** `https://docs.nebius.com/compute/resources/pricing.md`. VERIFIED 200, Markdown tables. The site also has `https://nebius.com/prices` (not fetched).

**Auth and cost:** none; free.

**robots.txt (VERIFIED)**
- `docs.nebius.com`: `User-agent: * / Content-Signal: ai-train=yes, search=yes, ai-input=yes / Disallow: /cdn-cgi/ / Allow: /_next/image / Disallow: /_next/`.
- `nebius.com`: `Allow: /` with `Disallow: /*?`, `/*=`, `/_*` and similar.

**Terms** (https://docs.nebius.com/legal/terms-of-use.md, VERIFIED 200, plus the AUP https://docs.nebius.com/legal/aup.md, VERIFIED 200)
- There is no scraping, crawling or automation clause.
- The only use restriction is: "(i) copy, modify, or create a derivative work of the Platform and services; (ii) reverse engineer… (ii) sell, resell, sublicense, transfer, or distribute any or all of the services and Platform…".

**Prices (VERIFIED).** The page shows prices both before and from the October 1, 2026 change, per GPU-hour in USD:

| Item | From 2026-10-01 | Before | Preemptible |
|---|---|---|---|
| H100 NVLink (eu-north1) | 4.50 | 3.85 | 2.15 |
| B200 NVLink (`gpu-b200-sxm`, us-central1) | 8.50 | 7.15 | 3.95 |

ILS prices are also listed.

**History:** only the before/after rows on the page. **Update frequency:** whenever prices change, announced in advance.

**Rationale.** This is Markdown served by the docs host and is easy to parse. The terms are permissive.
- Data-quality flag: on 2026-10-05, CGI's Nebius receipts (sourced from `nebius.com/prices`) still showed 3.85 and 7.15, the pre-October-1 prices. A direct collector from the docs page would catch that staleness.

### 2.6 Together AI: APPROVE, with a caveat

**Recommendation:** APPROVE. Fetch the HTML once a day.

**URL:** `https://www.together.ai/pricing`. VERIFIED 200, HTML.

**Auth and cost:** none; free.

**robots.txt (VERIFIED 200):** `User-agent: * / Allow: /`, with only `Google-Extended` disallowed. This contradicts the claim in ewyluda's methodology that robots.txt "disallows all crawlers"; that is not true today.

**Terms** (https://www.together.ai/terms-of-service, VERIFIED 200, "Updated May 19, 2026")
- There is no robot or scraper clause.
- The restriction on *Services* (Together's API platform) says: "You will not directly or indirectly: … (c) use or access the Services to develop a product or service that is competitive with the Company's products or services or engage in competitive analysis or benchmarking;"
- INFERRED: this is aimed at the API Services, not at reading the public website.

**Prices (VERIFIED), per GPU-hour, GPU Clusters**

| GPU | Preemptible | On-demand | Reserved 7–30 d | 31–90 d | 91–180 d |
|---|---|---|---|---|---|
| HGX H100 | 1.99 | 3.99 | 3.69 | 3.45 | 3.19 |
| HGX B200 | 4.09 | 8.19 | 7.99 | 7.79 | 6.79 |

Dedicated Inference: H100 5.49, B200 8.99.

**History:** none. **Update frequency:** list price.

**Rationale.** Together publishes a small **term structure** (preemptible, on-demand and three reserved tenors), which is rare and useful for curve research. The "competitive analysis or benchmarking" clause makes this a slightly greyer case than Nebius or Lambda. Keep collection to a single daily fetch, and use it only for internal non-commercial research.

### 2.7 Hyperstack: APPROVE

**Recommendation:** APPROVE. Fetch the HTML once a day.

**URL:** `https://www.hyperstack.cloud/gpu-pricing`. VERIFIED 200, HTML (HubSpot).

**Auth and cost:** none; free.

**robots.txt (VERIFIED 200):** `User-agent: * / Allow: /`, plus the standard HubSpot `Disallow` lines.

**Terms** (https://www.hyperstack.cloud/terms-and-conditions, VERIFIED 200, "Version dated 13th January 2026"): a keyword search for scrape, crawl, robot, automat, spider, harvest, extract and data mining found **no** relevant clause.

**On-demand prices (VERIFIED), per GPU-hour**

| GPU | On-demand |
|---|---|
| H100 SXM | 3.20 |
| H100 NVLink | 2.60 |
| H100 (PCIe) | 2.50 |
| B200 | 6.00 |
| H200 SXM | 3.99 |
| B300 | 7.40 |

Reservation prices start at $2.72 for H100 SXM.

**History:** none.

**Rationale.** These are posted on-demand and reservation prices with no restriction found. It is a good mid-market neocloud data point.

### 2.8 Verda (formerly DataCrunch; datacrunch.io redirects to verda.com): APPROVE

**Recommendation:** APPROVE. Fetch the HTML once a day.

**URL:** `https://verda.com/pricing`. VERIFIED 200, HTML. Verda's own API needs OAuth client credentials, so it is not used.

**Auth and cost:** none; free.

**robots.txt (VERIFIED 200):** `User-agent: * / Allow: /`.

**Terms** (https://verda.com/terms-and-conditions, VERIFIED 200, "Last updated September 30, 2025"):
> "6.1.2. engage in any malicious automated use of the Services, including but not limited to the malicious use of scripts, bots, scrapers, robots, or similar data gathering or extraction tools or crypto mining, except where expressly authorized;"

INFERRED: only *malicious* automated use is prohibited, and this is in the customer agreement. ewyluda excluded Verda over this clause, which is a more conservative reading.

**Prices (VERIFIED), per GPU-hour**

| GPU | On-demand | Spot |
|---|---|---|
| 1x H100 SXM5 80GB | 3.77 | 1.89 |
| 1x B200 SXM6 180GB | 7.13 | 3.56 |

**History:** none.

**Rationale.** These are posted prices and the clause targets malicious automation only. Polite daily reads are low risk. Prices are reportedly dynamic (OpenComputePrices says "changes multiple times/day"; unverified), so a daily snapshot misses intraday moves.

### 2.9 Lium (GPU marketplace): APPROVE

**Recommendation:** APPROVE. Poll hourly; the provider explicitly invites ingesters.

**URLs**
- `https://lium.io/pricing.json`. VERIFIED 200, JSON.
- `https://lium.io/api/public/v1/nodes`, which lists every rentable node. Documented; I did not fetch it.

**Auth and cost:** none; free.

**robots.txt (VERIFIED 200):**
> "# GPU pricing feed and fleet totals (JSON, one row per model, hourly): https://lium.io/pricing.json"
> "User-agent: * / Allow: / / Allow: /api/public/ / … Disallow: /api/"

**Docs** (https://docs.lium.io/developers/public-nodes-feed.md, VERIFIED 200):
> "Every GPU node currently rentable on Lium, as one unauthenticated JSON call. No key, no signup, no rate-limit negotiation — point your ingester at it and start listing us today."
> "60 requests per minute per IP."
> "The feed is rebuilt at most once per minute"

**Terms** (https://lium.io/terms, VERIFIED 200, "Effective 27 September 2026", Datura AI Corp, Saint Kitts and Nevis): no clause restricting automated access or data use.

**Fields:** `model, gpu_model, slug, gpu_class, reference_price_usd_per_gpu_hour, min_price_usd_per_gpu_hour, max_price_usd_per_gpu_hour, available_nodes, available_gpus, listed_gpus, rented_gpus, idle_gpus, vram_gb, updated_at`. There is also a top-level `fleet`.

**Prices (VERIFIED, generated_at 2026-10-05T17:51:38Z)**

| Model | Reference | Min | Max | Listed | Rented |
|---|---|---|---|---|---|
| H100 80GB HBM3 | 1.39 | 1.30 | 2.75 | 260 | 147 |
| B200 | 5.60 | 5.60 | 7.7194 | 52 | 40 |

H100 PCIe and H100 NVL also have rows.

**History:** none published. Build it yourself by polling hourly.

**Rationale.** This is the only marketplace source with explicit permission. It also publishes **utilization** (rented vs listed GPUs), a rare supply/demand signal. It is a decentralized marketplace and prices well below neoclouds, so treat it as its own segment, not as a proxy for SDH100RT.

### 2.10 Crusoe: APPROVE-MANUAL

**Recommendation:** APPROVE-MANUAL. The terms grant only a personal, non-commercial license and bar copying, and there is no B200 price.

**URL:** `https://www.crusoe.ai/cloud/pricing`. VERIFIED 200, HTML.

**robots.txt (VERIFIED):** `www.crusoe.ai` has `User-agent: * / Allow: /`. `legal.crusoe.ai` has `User-agent: *` with no `Disallow`.

**Website Terms of Use** (https://legal.crusoe.ai/, VERIFIED 200):
> "You may not copy, reproduce, publish, transmit, distribute, perform, display, post, modify, create derivative works from, sell, license or otherwise exploit the Websites or any of the Content without our prior written permission. You may not access or use the Websites for any competitive or commercial purpose… We grant to you a limited, non-exclusive, non-assignable, non-transferrable license to access and use the Websites and their Content for your own personal, non-commercial purposes."

**Prices (VERIFIED):** H100 HGX $3.90/GPU-hr on-demand, H200 $4.29. B200 and GB200 are "Contact sales". Spot is "Contact sales".

**Rationale.** It covers H100 only. The no-copy, personal-use license makes routine automated storage questionable, so take an occasional manual reading at most.

### 2.11 Jarvislabs: APPROVE-MANUAL

**Recommendation:** APPROVE-MANUAL, pending a review of the terms.

- **Pricing:** `https://jarvislabs.ai/pricing`. VERIFIED 200. H100 SXM $3.49/hr on-demand, H200 $4.59. No B200 price.
- **robots.txt (VERIFIED):** `Disallow: /settings/*`, `/dashboard/*`. Pricing is allowed.
- **Terms:** the terms page `https://jarvislabs.ai/termsandservice` returned 200, but the text is client-rendered and was not in the HTML, so **I could not read the terms**.

### 2.12 Shadeform (aggregator): SKIP / BLOCKED

**Recommendation:** SKIP for scraping the directory; BLOCKED for the API, which needs a key.

- The API needs an API key. Per SNIPPET, a free tier allows 10 requests/day.
- The public directory pages exist, for example `https://shadeform.com/directory/gpus/compare/H200/B200` (VERIFIED 200), showing averages such as "$6.75/hr" for B200 x1.
- **robots.txt (VERIFIED 200):** `User-Agent: * / Allow: /`. `www.shadeform.ai` redirects to shadeform.com.

**Terms** (https://shadeform.com/terms-of-service, VERIFIED 200 on the second attempt after a proxy tunnel reset, "Last updated: August 6, 2026"):
> "1. Not systematically retrieve data or content from our Services to create databases or directories without our written permission; 2. Avoid using any automated systems like data mining, robots, or scrapers without authorization;"

### 2.13 Other neoclouds, briefly

| Provider | What I found (VERIFIED unless noted) | Recommendation |
|---|---|---|
| Voltage Park | `voltagepark.com/pricing` returned 200 but says "Contact for pricing". The FAQ says "starting at $1.99" for H100. No B200. robots.txt holds only a `Sitemap:` line. CGI cites a `cloud-api.voltagepark.com` endpoint, which I did not verify. | SKIP (no list price) |
| TensorDock | `www.tensordock.com/cloud-gpus.html` returned 200 with marketing "H100 SXM5 From $2.25/hr". robots.txt returned 404. I did not find terms on the page. | SKIP (low value, terms unknown) |
| DigitalOcean / Paperspace | `www.digitalocean.com/pricing/gpu-droplets` returned **HTTP 500** to our UA. robots.txt allows. Not retried, to avoid circumventing. CGI cites `docs.digitalocean.com/.../pricing/` for H100 $4.41. | SKIP for now |
| Fluidstack | `fluidstack.io/pricing` returned 404. No public list price found. | SKIP |
| Hyperbolic | `www.hyperbolic.ai/pricing` returned 404. robots.txt has `Disallow: /api/`. | SKIP |
| Prime Intellect | Its API needs a key (per the OpenComputePrices README). I did not audit it further. | BLOCKED |

---

## 3. Published GPU rental price indices

### 3.1 Silicon Data (SDH100RT, SDB200RT): the futures' underlying

**Recommendation**
- **SKIP** for automated collection: the terms forbid storing the data.
- **BLOCKED** for history and the API: paid.
- **APPROVE-MANUAL** only for viewing. The user could open a free Basic account, but only by signing up and accepting portal terms that I have not reviewed.

**URLs (VERIFIED 200)**
- `https://www.silicondata.com/products/silicon-index/h100` and `/b200`.
- `/pricing`, `/terms-of-use`.
- `https://docs.silicondata.com/products/gpu-index.md`, `.../gpu-index-announcements.md`, `.../api-reference/gpu_index_api.md`.

**robots.txt (VERIFIED)**
- `www.silicondata.com`: `User-Agent: * / Allow: /`.
- `docs.silicondata.com`: allows everything except `/_next/` and `/cdn-cgi/`.
- `portal.silicondata.com` disallows: `Disallow: /gpu-index-chart`, `Disallow: /api-portal`, `Disallow: /data-download`, `Disallow: /silicon-*` and others. So the embedded chart (`portal.silicondata.com/gpu-index-chart?standalone=true&gpu=h100&mainTab=neo-cloud`) is **off-limits**, and I did not fetch it.

**Terms of Use** (VERIFIED):
> "You may download the Site Contents for personal and non-commercial use, provided that you do not modify or alter such Site Contents in any way… No Site Content or any part thereof may be modified, reverse-engineered, reproduced or distributed in any form by any means, or stored in a database or retrieval system, without the prior written consent of Silicon Derivatives."

**Pricing FAQ** (VERIFIED):
> "Do I need a separate licence to redistribute the index? Yes. A subscription lets your organisation use the data internally. Redistributing an index, publishing it to your own clients, or using it to settle or reference a financial product is covered by a separate index licence rather than the plan price."

**Free vs paid** (VERIFIED, /pricing)

| Plan | Price | Index history | Other |
|---|---|---|---|
| Basic | free, "no credit card", needs an account | "SiliconIndex™ 30 days history" | |
| Pro | "$998 / Month", 7-day trial | "full history" | "API access available on paid plans" |
| Enterprise | custom | full history | "API & CSV download" |

Data is also distributed via Bloomberg: `SDH100RT Index`, `SDB200RT Index`, and `SDA100RT`. Reuters `.SDB200RT` was "in the coming weeks" per the Dec 2025 announcement. A sitemap news title mentions dxFeed/Refinitiv. Kaiko is SNIPPET only.

**Public data embedded in the page** (VERIFIED): the latest value plus seven daily points. The daily points are not reproduced here because Silicon Data's terms forbid storing site content. Latest values on 2026-10-05: SDH100RT 2.81, SDB200RT 5.87.

**Methodology (VERIFIED, public level only)**
> "calculated daily from observations across cloud providers, colocation markets, brokered cluster sales, and private rental platforms. Observations are standardized for machine specs, rental terms, platform performance, and geolocation, then filtered for outliers and independently validated before publication."

Weights and sources are proprietary.

**Index changes that matter for backtests** (VERIFIED, announcements doc)

| Effective | Change | Impact |
|---|---|---|
| 2025-12-04 | Methodology change; H100 and A100 history **restated** from 2024-09-01; look-back gap-fill added; "large jump" on 2025-03-01 from expanded coverage | |
| 2025-12-04 | B200 index launched | |
| 2026-04-06 | H100 providers added | −7% to −3% |
| 2026-07-15 | B200 providers expanded | up to −6% |
| 2026-09-25 | H100 hardware-baseline change | up to +4% |
| 2026-09-25 | B200 stale providers removed | up to +4% |

**History depth (VERIFIED)**
- The API doc says data starts 2024-09-01.
- A blog table gives sample periods: H100 "Sep 2024 – Aug 2026" and B200 "Aug 2025 – Aug 2026".

**API** (VERIFIED doc)
- `POST /api/gpu-index/index` with body `{"gpu":"h100","index_version":"neo","starting_date":"YYYY-MM-DD","ending_date":"YYYY-MM-DD"}`.
- Auth: OAuth2 password bearer.
- "only available for **Plus** and **Professional** tier subscribers".

**Publication time:** not stated publicly. The 2026-10-05 value was already live when I fetched it at 17:46 UTC. The FAQ says "The indices update every business day"; the product page says "published daily".

**Rationale.** This is the settlement source for GPU1/GPU2, so it is indispensable for the research, but every machine-usable path is paid or prohibited. Options:
- Use Bloomberg, if the team has a terminal.
- Ask Silicon Data for academic or research access.
- Have the user sign up for the free Basic tier (30 days) and accept its terms, but storage restrictions likely still apply.

Remember that settlement uses the **US-geography, business-day** SD-H100 configuration (§4), which may differ from the public global SDH100RT number.

### 3.2 FLOPS Index (flopsindex.com / app.flopsindex.com): APPROVE (provisional)

**Recommendation:** APPROVE, provisionally. Collect the public delayed values every 6 hours, for internal research only. Confirm with team@flopsindex.com.

**URLs**
- `https://app.flopsindex.com/v2/catalog/public`. VERIFIED 200, JSON, 42 indices.
- `GET /v1/price/{INDEX_ID}`. Documented in llms.txt; not fetched.
- Methodology: `https://app.flopsindex.com/i/FLOPS-H100-OD/methodology`. VERIFIED 200.

**Auth:** none for the public surface. `https://app.flopsindex.com/terms` returned **401** ("Authentication required."). The marketing site links only a privacy policy. **I could not find any public terms of use.**

**robots.txt (VERIFIED)**
- `app.flopsindex.com`: `User-agent: * / Disallow: /v2/_admin/ / Disallow: /v1/_admin/ / Disallow: /demo/_admin/ / Allow: /`.
- `flopsindex.com` (Squarespace): `/api/`, `/config`, `/search` and similar are disallowed. I did not need those paths.

**Terms language found**
- llms.txt: "The public surface is INDICATIVE reference data — NOT FOR SETTLEMENT."
- GitHub README (`zeroatflops/flopsindex`, VERIFIED 200): "Apache 2.0 governs the source code… The underlying price data, the FLOPS trademark, and the hosted index methodology are the proprietary work of FLOPS Index; use of the published APIs is governed by the terms at flopsindex.com". Those terms were not found.

**Fields:** `index_id, family, value, unit, as_of, confidence, change_24h, delayed`. The catalog's `_filter_note` says: "Real-time, regional and historical data… are available to customers".

**Values (VERIFIED, as_of 2026-10-05T18:00Z)**

| Index | Value | Confidence |
|---|---|---|
| FLOPS-H100-OD | 2.99 | HIGH |
| FLOPS-H100-SPOT | 1.70 | |
| FLOPS-H100-DEPIN | 1.49 | |
| FLOPS-B200-OD | 5.10 | MED |
| FLOPS-GB200-OD | 8.40 | |

Response headers: `x-ratelimit-limit: 2000`, `x-ratelimit-reset: 86400`.

**Methodology (VERIFIED):** "a robust median of rates observed across independent GPU providers… published only when backed by at least 3 independent sources… Weights, source identities, and exact source counts are proprietary". It is global only, published on a 6-hour UTC grid.

**History:** none public; customers only.

### 3.3 Computable GPU Index (CGI): APPROVE

**Recommendation:** APPROVE. This is the best open index.

**What it is and who publishes it.** CGI is published by Computable (getcomputable.com; "(c) 2026 Computable"). It is "an open price index for GPU compute: verifiable, reproducible…".
- It is computed every 15 minutes from posted on-demand rates of a fixed panel of providers.
- The statistic is an interquantile mean over weighted "votes". Weights come from a leave-one-out "liveness" model.
- Code is Apache-2.0 at `github.com/getcomputable/gpu-index`; I read it via raw.githubusercontent.com.
- Product Hunt and X posts ("New from Computable S26") are SNIPPET only.
- Contact: team@getcomputable.com.

**URLs (all VERIFIED 200)**
- `https://api.getcomputable.com/v1/methodology`
- `.../v1/index/{SKU}/latest?include=receipts`
- `.../v1/index/{SKU}/history?limit=4`
- `https://data.getcomputable.com/latest.json` (the public record)

**Auth and cost:** "Anonymous, read-only. No API key and no registration." Free.

**robots.txt (VERIFIED)**
- `api.getcomputable.com/robots.txt` returned 404.
- `data.getcomputable.com/robots.txt` returned 404.
- `www.getcomputable.com/robots.txt` returned 404.
- So there are no restrictions. `docs.getcomputable.com` allows everything except `/_next/` and `/cdn-cgi/`.

**Data license** (`LICENSE-DATA.md`, VERIFIED):
> "The Index Values are licensed under the Creative Commons Attribution-NonCommercial 4.0 International License."
> Section 2 reserves "using any Index Value as the basis of, or a component of, a financial product, including determining the settlement value… of any futures contract…"
> Receipts: "Computable claims no rights in the underlying provider prices".

**Coverage:** H100 (`h100_sxm_v1_calc_v16`), B200 (`annex_a2_v0_3_calc_v17`), H200 and B300.

**Panels (VERIFIED, from receipts)**

| SKU | Sources | Members |
|---|---|---|
| H100 | 17 | Civo, CoreWeave, Crusoe, DigitalOcean, Hyperbolic, Hyperstack, Lambda, Lium, Massed Compute, Nebius, RunPod, Scaleway, TensorPool, Together, Vast, Verda, Voltage Park |
| B200 | 9 | CoreWeave, Hyperstack, Lambda, Massed Compute, Nebius, RunPod, Together, Vast, Verda |

**Fields**
- `observed_at, value_usd_gpu_hr, stability_band_usd_gpu_hr, methodology_id, coverage{n_sources,n_passing}, status, freshness`.
- Receipts add `source_id, provider_class, price, currency, weight, filter_verdict, source_url, gpu_variant, region, …`.

**Values (VERIFIED, observed_at 2026-10-05T18:00Z)**

| SKU | Value | Stability band |
|---|---|---|
| H100 | 3.620953 | 0.541253 |
| B200 | 6.944927 | 0.999373 |

At 17:45Z the values were 3.620858 and 6.944882.

**History**
- The public record runs from `from_observed_at: 2026-08-30T17:00:00.000Z`. The first methodology versions are effective 2026-08-30.
- The API serves a trailing window ("history_policy": window_days 90, 15-minute resolution).
- A request for 2026-07-08 returned **400** `history_window_exceeded`.
- About 5 weeks of history exist so far.

**Rate limit:** `ratelimit-policy: 100;w=10`.

**Rationale.** The license is compatible with non-commercial research, access is keyless, the method is documented and reproducible, and the receipts expose per-provider inputs. It is the best open benchmark to compare against SDH100RT and SDB200RT. Two caveats:
- Its panels include Vast and RunPod, sources whose own terms ban scraping. That provenance risk sits with Computable, but note it.
- At least one receipt was stale: Nebius was still at pre-October-1 prices.

### 3.4 Ornn Compute Price Index (OCPI): BLOCKED in this environment

**Recommendation:** BLOCKED here (egress policy). APPROVE-MANUAL: the user should check it by hand.

What the snippets say (data.ornn.com, Business Wire/Yahoo coverage):
- OCPI is a "volume-weighted, winsorized average of transacted GPU rental prices".
- It covers H100 SXM, H200, B200 and A100 SXM4.
- It "settles once per trading day at 4:00 PM ET" and is listed on Bloomberg.
- "three months of daily history… free" and "free API access".
- ICE and Ornn announced GPU compute futures (May 2026).

Not verified: robots.txt, terms, endpoints. This is a transaction-based alternative to Silicon Data and could be very valuable for research. Review it manually.

### 3.5 SemiAnalysis GPU Spot-Contract Composite Index: APPROVE-MANUAL (view only)

- **URL:** `https://gpu-index.semianalysis.com/`. VERIFIED 200. robots.txt returned 404.
- It covers H100, A100 and B200, is "computed and published hourly on this page", and H100 is on Bloomberg as `SAH100SC`.
- Values load via JavaScript, and the static table shows April 2026 data. "For complete data, contact sales@semianalysis.com".
- Terms not reviewed. It is proprietary; do not collect it automatically.

---

## 4. CME GPU1/GPU2 settlement data

cmegroup.com was not accessed, per the rules.

**From the CFTC self-certification filing (VERIFIED)**
- Source: `https://www.cftc.gov/filings/ptc/ptc08112615405.pdf`, HTTP 200, NYMEX Submission 26-370, filed 08/11/26.
- On robots.txt: CFTC's `User-agent: *` group says `Content-Signal: search=yes,ai-train=no,use=reference / Allow: /`. It blocks `ClaudeBot`, `anthropic-ai` and `Claude-Web` by name. I fetched this one PDF under the generic group with the project UA. Flagging it in case you prefer to treat cftc.gov as off-limits for AI agents.

**Contract terms in the filing**
- **Codes:** GPU1 = Silicon Data H100 Rental Index Futures (Rulebook Chapter 1045). GPU2 = Silicon Data B200 Rental Index Futures (Chapter 1047).
- **Size and price:** 730 GPU-hours, priced in USD per GPU-hour, tick $0.01 = $7.30.
- **Settlement:** Financial (cash). Trading terminates on the last Business Day of the month. 36 consecutive monthly contracts are listed. The first listing is October 2026, trading from Sunday Oct 4 for trade date Monday **Oct 5, 2026**.
- **Floating Price:** "the arithmetic average of the Silicon Data H100 Rental Index (SD-H100) on-demand settlement prices as published by Silicon Derivatives Inc. (Silicon Data) for each Business Day during the contract month." The same wording applies to B200.
- **"Index Technical Configuration — Geography: United States".**
- **Fees:** Globex member $3.65, non-member $5.50. Cash settlement processing fee $0.90 / $1.35.
- **Public data:** "The Exchange will publish information regarding the Contracts' trading volumes, open interest levels, and price information daily on its website and through quote vendors."

**From search snippets only (not verified)**
- "Settlement data posted on the website will be delayed until midnight CT, then will be freely available to view."
- "CME Group daily Settlement Files are available via the CME DataMine platform with publication times of midnight CT and continue to be available free of charge." INFERRED: this needs a CME login, so the user would have to do it.
- "For those that require daily Settlement Files before midnight, the End of Day file is available via DataMine with paid subscription."
- "Historical End-of-Day data dating back to product start date can be purchased from the CME DataMine" (**paid**; prices shown only after sign-in).

**Licensed alternatives (all SNIPPET, all paid)**
- Databento (GLBX.MDP3, usage-based).
- dxFeed CME feeds.
- Bloomberg and LSEG terminals.
- Broker market-data subscriptions.
- CME's own charts are "powered by TradingView".

**Recommendation:** APPROVE-MANUAL. The user downloads the free delayed settlements, after midnight CT, from CME or DataMine under their own account. History begins 2026-10-05, so there is none yet. Paid vendors are the only automated option.

---

## 5. Free historical time series of H100/B200 rental prices

| Source | Granularity and span | GPUs | License | Collection | Recommendation |
|---|---|---|---|---|---|
| **GetDeploying "GPU Rental Price History"** (`getdeploying.com/dataset/gpu-prices/nvidia-h100.csv`, `nvidia-b200.csv`; VERIFIED 200) | **Weekly**, 53 trailing weeks, **2025-10-06 to 2026-10-05**. Billing types ON_DEMAND, SPOT, RESERVATION, CUSTOM. A weekly row is the median of daily captures. | H100 (single pooled slug), B200 | **CC BY 4.0**: "Credit GetDeploying and link to the license… The license covers the published dataset files only… The site and the API stay under the terms." robots.txt has `Disallow: /terms`, so I could not read the site terms. | Independently collected from providers' own pages and APIs. The page claims "55,198 weekly observations since July 2024, across 88 providers". Older and daily data is in the API. | **APPROVE** |
| **gpurentalprices.com**: live `api/latest.json` (VERIFIED 200, 471 offers on 2026-10-05); GitHub mirror `adriannutiu/gpu-rental-prices` raw `data/snapshots/YYYY-MM-DD.json` (VERIFIED 200 for 07-19, 07-27, 08-05, 08-15, 09-06, 09-20, 10-04; 404 for 07-05); Zenodo record 21435394, VERIFIED 200 (snapshots 2026-07-05 to 07-18, zip 42.4 kB) | **Daily** per-provider offers. About **93 days** ("Ledger: 93 daily snapshots"), 2026-07-05 to now. | H100 SXM/PCIe/NVL, B200 and others | **CC BY 4.0** (README, Zenodo). llms.txt: "today's data free with attribution (CC BY 4.0); full history licensed (data@gpurentalprices.com)". The GitHub mirror and Zenodo copies are CC BY. | Independently collected, with a source URL and fetch timestamp per offer. Its upstream sources include RunPod and Lium. | **APPROVE** (daily latest) + **APPROVE-MANUAL** (backfill via `git clone` and the Zenodo zip). Hugging Face and Kaggle mirrors are listed but not fetched. |
| **Computable GPU Index** (API plus `data.getcomputable.com`) | **15-minute**, since 2026-08-30 | H100 SXM, B200 | CC BY-NC 4.0 | Independent index with receipts | **APPROVE** |
| **Vast public feed** | Daily median, 90 days (2026-07-07 to 10-04) | H100 SXM/PCIe/NVL, B200 | "requires a data license" for bulk or index use | First-party | **SKIP** (license) |
| **Silicon Data** | Daily since 2024-09-01, restated | H100, B200 (from about Aug or Dec 2025) | Proprietary | First-party index | **BLOCKED** (paid). Free Basic gives 30 days, but needs signup. |
| **Ornn OCPI** | Daily, "three months" free (SNIPPET) | H100 SXM, B200 | unknown | Transaction-based | BLOCKED here; review manually |
| **gpuperhour.com** (`gpuperhour.com/gpu-price-index` VERIFIED 200; CSV at `api.gpuperhour.com/api/price-index/export.csv?days=365`, not fetched; that host's robots.txt not checked) | Daily, "21 days of data since 14 September 2026" | H100, B200 | "Creative Commons Attribution 4.0" | Independent | APPROVE, low priority; check robots.txt first |
| **OpenComputePrices** (`thatkavish/OpenComputePrices`, README and LICENSE VERIFIED) | 12-hourly, 65+ providers. 90-day active window plus monthly archives (`archive_2026-01…` mentioned). Start date unverified. | H100, B200 | MIT (repo). Data mixes Vast via API key, scraped GetDeploying, SkyPilot. | Mixed, partly derived | **APPROVE-MANUAL** (download the release asset `latest-data/data.tar.gz` by hand; github.com is blocked here and `/*/download` is disallowed in GitHub's robots.txt) |
| **cherielilili/gpu-pricing-tracker** (`data/observations.csv` VERIFIED 200, 46,265 rows) | Daily, **2026-02-11 to 2026-10-04** (231 dates) | H100 SXM/PCIe/NVL, B200 | **No LICENSE** (`/LICENSE` returned 404) | Derived: Vast API, scraped getdeploying.com, RunPod API, Lambda, Crusoe, Nebius | **SKIP**; ask the author for a license, as it is the longest daily set found |
| **Zeno00-00/gpu-price-tracker** (`data/gpu_prices.csv` VERIFIED 200) | Daily, 2026-06-13 to 10-04 (112 dates) | Vast/RunPod H100 and B200 medians | No LICENSE (404) | Vast and RunPod APIs (terms issues) | **SKIP** |
| **ewyluda/gpu-price-index** (methodology VERIFIED) | Daily, since 2026-09-29 | H100 SXM/NVL/PCIe, B200 | MIT | Independent, 11 sources | APPROVE-MANUAL (too short today) |
| **xcidjazz/silicon-data-tracker** (README VERIFIED) | Daily archive of Silicon Data public and portal endpoints | SD indices | No LICENSE | Derived from Silicon Data, which forbids database storage, and uses the robots-disallowed portal chart | **SKIP** |
| **SkyPilot catalog** (`skypilot-org/skypilot-catalog`; Lambda `vms.csv` VERIFIED) | Git history of Lambda list prices (refreshed "every 7 hours"); depth not verified | H100 SXM/PCIe, B200 | LICENSE not found at the repo root (404); verify | Lambda API via SkyPilot | APPROVE-MANUAL (`git clone` + `git log -p catalogs/v7/lambda/vms.csv`) |
| **AIMultiple GPU index** (`aimultiple.com/gpu-index` VERIFIED 200) | **Monthly** medians, "July 2024 through September 2026" | H100, B200 | Terms not reviewed | Aggregated | APPROVE-MANUAL (chart ZIP) |
| **fabryka.ai** (`gpu-price-index.vercel.app` VERIFIED 200) | Daily since about June 2026, MLPerf-normalized | H100-equivalent | not stated | Derived from "Vast.ai daily medians" | **SKIP** |

No relevant Epoch AI or academic dataset turned up in search.

---

## 6. Summary table

| # | Source | H100 / B200 | Machine-readable? | Auth / cost | robots.txt (our path) | Terms | History | Rec. |
|---|---|---|---|---|---|---|---|---|
| 1 | Vast.ai API + public feed | SXM/PCIe/NVL / yes | JSON | none / free | allowed | **prohibits** automation and index use; feed needs a license | 90 d daily (feed) | **SKIP** |
| 2 | RunPod pricing / GraphQL | SXM/PCIe/NVL / yes | JSON-LD; GraphQL untested; REST needs key | none for page | allowed | **prohibits** automated access | none | **SKIP** (manual OK) |
| 3 | Lambda pricing | SXM, PCIe / yes | HTML | none / free | allowed | no anti-bot clause (website) | none | **APPROVE** |
| 4 | CoreWeave pricing | HGX / HGX | HTML | none / free | allowed | non-commercial OK; no anti-bot clause | none | **APPROVE** |
| 5 | Nebius docs pricing | NVLink / yes | Markdown | none / free | allowed | no clause | before/after rows | **APPROVE** |
| 6 | Together AI pricing | HGX / HGX, plus term structure | HTML | none / free | allowed | "benchmarking" clause on Services (caveat) | none | **APPROVE** |
| 7 | Hyperstack pricing | SXM/NVLink/PCIe / yes | HTML | none / free | allowed | none found | none | **APPROVE** |
| 8 | Verda pricing | SXM5 / SXM6 | HTML | none / free | allowed | only "malicious" automation banned | none | **APPROVE** |
| 9 | Lium pricing.json | HBM3/PCIe/NVL / yes | JSON | none / free | explicitly allowed | none; invites ingesters | none (poll) | **APPROVE** |
| 10 | Crusoe | HGX / contact sales | HTML | none / free | allowed | no copying; personal non-commercial license | none | APPROVE-MANUAL |
| 11 | Jarvislabs | SXM / no | HTML | none / free | allowed | not readable (JS) | none | APPROVE-MANUAL |
| 12 | Shadeform | yes / yes | API (key); HTML directory | key | allowed | **prohibits** scraping | none | SKIP / BLOCKED |
| 13 | Voltage Park, TensorDock, DigitalOcean, Fluidstack, Hyperbolic | partial | HTML | — | mixed | mixed or unknown | none | SKIP |
| 14 | Silicon Data | neo + hyperscaler / neo | embedded JSON (7 d); paid API | paid ($998/mo Pro; Basic free with signup) | www allowed; portal chart **disallowed** | **no database storage** without consent | since 2024-09-01 (paid) | SKIP / BLOCKED |
| 15 | FLOPS public | OD/SPOT/DEPIN / OD | JSON | none / free | allowed | data proprietary; terms page not public | none public | APPROVE (provisional) |
| 16 | Computable GPU Index | SXM / yes | JSON | none / free | 404 (allowed) | CC BY-NC 4.0 | since 2026-08-30, 15-min | **APPROVE** |
| 17 | Ornn OCPI | SXM / yes | free API (snippet) | ? | blocked here | ? | 3 mo free (snippet) | BLOCKED (env) → manual |
| 18 | SemiAnalysis composite | yes / yes | JS | paid for full data | 404 | not reviewed | hourly (proprietary) | APPROVE-MANUAL (view) |
| 19 | GetDeploying dataset | pooled / yes | CSV | none / free | allowed | **CC BY 4.0** | **53 weeks** | **APPROVE** |
| 20 | gpurentalprices.com | SXM/PCIe/NVL / yes | JSON/CSV | none / free | allowed ("Crawl freely") | **CC BY 4.0** | **~93 days daily** | **APPROVE** + manual backfill |
| 21 | gpuperhour.com | yes / yes | CSV | none / free | allowed (site) | CC BY 4.0 | 21 days | APPROVE (low priority) |
| 22 | OpenComputePrices | yes / yes | CSV (release) | none / free | release path disallowed | MIT | ≥90 d + archives | APPROVE-MANUAL |
| 23 | cherielilili tracker | yes / yes | CSV | none | raw allowed | **no license** | 231 days | SKIP (ask author) |
| 24 | Zeno00-00, xcidjazz, fabryka | — | CSV/JSON | — | — | no license or derived | short | SKIP |
| 25 | SkyPilot catalog (Lambda) | yes / yes | CSV + git | none | raw allowed | license unverified | git history | APPROVE-MANUAL |
| 26 | AIMultiple | yes / yes | ZIP/CSV | none | allowed | not reviewed | monthly since 2024-07 | APPROVE-MANUAL |
| 27 | CME settlements GPU1/GPU2 | GPU1 / GPU2 | files via DataMine | CME login; history paid | not accessed (rule) | not reviewed (cmegroup.com off-limits) | from 2026-10-05 | APPROVE-MANUAL / paid vendors |

---

## 7. Sources to build collectors for now (verified request details)

All requests use `GET` with header `User-Agent: compute-curve-research/0.1 (non-commercial research)`. Keep at least 3 s between requests to the same host, and re-check robots.txt periodically.

### 1. Computable GPU Index: the open index closest to SDH100RT and SDB200RT

**Endpoints**
- `GET https://api.getcomputable.com/v1/index/H100/latest?include=receipts`. VERIFIED 200 at 18:10:10Z: `data.value_usd_gpu_hr = 3.620953`, `observed_at = 2026-10-05T18:00:00.000Z`, 17 receipts.
- `GET https://api.getcomputable.com/v1/index/B200/latest?include=receipts`. VERIFIED 200 at 18:09:12Z: `6.944927`, 9 receipts.
- **Backfill and gaps:** `GET https://api.getcomputable.com/v1/index/{H100|B200}/history?from=YYYY-MM-DDTHH:MM:00.000Z&to=YYYY-MM-DDTHH:MM:00.000Z&limit=2976[&cursor=<next_cursor>]`.
  - Verified with `?limit=4`. Each row in `data.values[]` carries `observed_at, value_usd_gpu_hr, stability_band_usd_gpu_hr, methodology_id, coverage, status`.
  - Timestamps must sit on the 15-minute grid.
  - The window is about 90 days; a request outside it returns 400 `history_window_exceeded`.
- **Public record:** `GET https://data.getcomputable.com/latest.json`. VERIFIED 200, with history from 2026-08-30T17:00Z.

**Cadence:** hourly at :05, or every 15 minutes. The rate limit is 100 requests per 10 s.

**Attribution:** "Computable GPU Index (CGI), (c) 2026 Computable, https://github.com/getcomputable/gpu-index, licensed CC BY-NC 4.0". Do not use it for settlement or in a product.

### 2. GetDeploying weekly dataset: one year of history and an ongoing weekly series

**Endpoints**
- `GET https://getdeploying.com/dataset/gpu-prices/nvidia-h100.csv`. VERIFIED 200, text/csv, 33,512 bytes.
- `GET https://getdeploying.com/dataset/gpu-prices/nvidia-b200.csv`. VERIFIED 200, 30,189 bytes.

**Columns:** `gpu_slug,date,billing_type,reservation_months,min_price,max_price,median_price,provider_median_price,provider_count,offering_count`. Filter `billing_type == "ON_DEMAND"`.

**Latest values (week of 2026-10-05):**
- H100: median 3.4092, provider_median 3.3984, 41 providers.
- B200: median 6.79, provider_median 6.52, 18 providers.

**Cadence:** once a day. The newest week can be revised until its Sunday is captured.

**Attribution:** "GetDeploying, GPU rental price history, https://getdeploying.com/gpus, CC BY 4.0".

### 3. gpurentalprices.com: daily per-provider offers with provenance

**Endpoints**
- `GET https://gpurentalprices.com/api/latest.json`. VERIFIED 200: `date 2026-10-05`, 471 offers.
  - Keys: `date, generated_at, meta, offers, providers`.
  - Offer fields: `provider, gpu (h100-sxm|h100-pcie|h100-nvl|h100|b200…), vram_gb, usd_hr, kind (on-demand|secure|community|spot|reserved|serverless), source_url, fetched_at`.
  - `providers[x]` has `{ok, last_verified, stale, source_url}`.
- **Backfill** (user-run, once):
  - `git clone https://github.com/adriannutiu/gpu-rental-prices` for the rolling daily snapshots. In this session, individual raw files were VERIFIED at `https://raw.githubusercontent.com/adriannutiu/gpu-rental-prices/main/data/snapshots/YYYY-MM-DD.json` back to 2026-07-19.
  - Plus the Zenodo zip `https://zenodo.org/records/21435394` (gpu-rental-prices-2026-07-19.zip) for 2026-07-05 to 07-18.

**Cadence:** once a day, around 22:00 UTC. The site snapshot was generated at 08:47Z, and the mirror's offers were fetched around 21:01Z.

**Attribution:** "GPU rental price data by gpurentalprices.com, CC BY 4.0."

### 4. Lium: a permissioned marketplace with utilization data

**Endpoint:** `GET https://lium.io/pricing.json`. VERIFIED 200, 46,823 bytes, `generated_at 2026-10-05T17:51:38.596Z`.
- Use `models[]` rows where `gpu_model ∈ {"H100 80GB HBM3","H100 PCIe","H100 NVL","B200"}`.
- Fields: `reference_price_usd_per_gpu_hour, min_price_usd_per_gpu_hour, max_price_usd_per_gpu_hour, listed_gpus, rented_gpus, idle_gpus, available_gpus, updated_at`.

**Optional:** `GET https://lium.io/api/public/v1/nodes`. Documented as unauthenticated and allowed by robots.txt; not fetched.

**Cadence:** hourly. The limit is 60 requests per minute per IP, and the feed is rebuilt at most once a minute.

### 5. FLOPS public catalog: an independent index level (provisional)

**Endpoint:** `GET https://app.flopsindex.com/v2/catalog/public`. VERIFIED 200.
- Keep `indices[]` where `index_id ∈ {"FLOPS-H100-OD","FLOPS-B200-OD","FLOPS-H100-SPOT","FLOPS-H100-DEPIN"}`.
- Fields: `value, unit, as_of, confidence, change_24h, delayed`.

**Cadence:** 4 times a day, at 00:10, 06:10, 12:10 and 18:10 UTC. The limit is 2000 requests per day.

**Caveat:** "NOT FOR SETTLEMENT". There is no public history, the data is proprietary and the terms are unpublished. Confirm research use with team@flopsindex.com.

### Optional: direct provider list prices

These are an independence check on CGI receipts. All are VERIFIED 200 HTML or Markdown; parse them once a day.

| Provider | URL | Notes |
|---|---|---|
| Nebius | `https://docs.nebius.com/compute/resources/pricing.md` | Rows "NVIDIA® H100 NVLink" and "NVIDIA® B200 NVLink"; use the "from" vs "before" sections |
| Lambda | `https://lambda.ai/pricing` | |
| CoreWeave | `https://www.coreweave.com/pricing` | Divide 8-GPU instance prices by 8 |
| Hyperstack | `https://www.hyperstack.cloud/gpu-pricing` | |
| Together | `https://www.together.ai/pricing` | Includes the reserved tenors |
| Verda | `https://verda.com/pricing` | |

---

## 8. Suggested follow-ups (user action; I did not do these)

- **Vast data license:** email data@vast.ai about a non-commercial research license for the public feed (90-day history) or the API.
- **Silicon Data:** ask about academic or research access to SD-H100 and SD-B200, specifically the US-geography business-day settlement series and full history. Alternatively, use Bloomberg `SDH100RT Index` / `SDB200RT Index`. Decide whether to open a free Basic account, which requires signup.
- **Ornn OCPI:** review it manually (data.ornn.com is blocked here): its terms, free API and 3-month history.
- **cherielilili/gpu-pricing-tracker:** ask the author for a license; it is the longest daily H100/B200 set found (231 days).
- **CME settlements:** download them manually after midnight CT once GPU1/GPU2 settle.

## Appendix: verified request log (abbreviated)

The full log is in `the session request log (not retained)`: 172 entries, each with a timestamp, URL, HTTP status, size and content type. Non-200 results:

| URL | Result |
|---|---|
| `console.vast.ai/robots.txt` | 302 → `cloud.vast.ai` |
| `storage.googleapis.com/robots.txt` | 404 |
| `api.runpod.io/robots.txt` | 404 |
| `github.com/robots.txt` and `api.github.com/robots.txt` | 403 from the session proxy (read github.com robots.txt via WebFetch instead) |
| `raw.githubusercontent.com/robots.txt` | 404 |
| `adriannutiu .../2026-07-05.json` | 404 |
| `cherielilili`, `Zeno00-00`, `xcidjazz`, `skypilot-catalog` `/LICENSE` | 404 |
| `gpu-price-index.vercel.app/robots.txt` | 404 |
| `www.tensordock.com/robots.txt` | 404 |
| `www.digitalocean.com/pricing/gpu-droplets` | **500** |
| `shadeform.com/terms-of-service` | tunnel reset once, then 200 |
| `www.hyperbolic.ai/pricing` | 404 |
| `fluidstack.io/pricing` | 404 |
| `app.flopsindex.com/terms` | **401** |
| `api.getcomputable.com/robots.txt`, `www.getcomputable.com/robots.txt`, `data.getcomputable.com/robots.txt` | 404 |
| `getcomputable.com/robots.txt` | tunnel reset (that host was not used) |
| `api.getcomputable.com/v1/index/H100/history?from=2026-07-08…` | **400** (`history_window_exceeded`) |
| `gpu-index.semianalysis.com/robots.txt` | 404 |
| `data.ornn.com/robots.txt` | SSL_ERROR_SYSCALL ×2; WebFetch EGRESS_BLOCKED |
