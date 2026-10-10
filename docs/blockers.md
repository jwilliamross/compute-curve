# Blockers

Each entry records what is blocked, the evidence, what the project does
instead, and what would unblock it. Newest entries at the bottom.

## B1. No network allowlist is active

- **Found:** Step 0, 2026-10-05.
- **Evidence:** `https://example.com` returned HTTP 200. Agent proxy status
  reports `"selective": false`.
- **Impact:** None on the work. It means the environment is less locked down
  than you expected.
- **Workaround:** The code only contacts sources approved in
  `docs/data_sources.md`.
- **Unblock:** Switch the environment's network policy to a custom allowlist
  if that was the intent. See `docs/env_check.md` for the domain list.

## B2. CME Group website prohibits automated access

- **Found:** Step 0, 2026-10-05.
- **Evidence:** `https://www.cmegroup.com` returned HTTP 403 from Akamai with
  the message: "Use of scripts, software, spiders, robots, avatars, agents,
  tools or other scraping mechanisms is strictly prohibited by CME Group's
  website Data Terms of Use."
- **Impact:** CME's own rulebook pages, margins and settlements cannot be
  read. Contract terms, fees and the listing status were verified instead from
  NYMEX's filing with the CFTC (docs/contract_specs.md). Margins remain
  unconfirmed.
- **Workaround:** The paper trading engine reads CME settlements from a
  manual CSV drop folder. Each contract field in config records whether it
  is verified. No settlement data exists in the repo.
- **Unblock:** Download settlements by hand in a browser, or license CME
  DataMine or a vendor feed. Do not scrape cmegroup.com.

## B3. SSRN papers cannot be retrieved

- **Found:** Step 0, 2026-10-05.
- **Evidence:** `https://papers.ssrn.com` returned HTTP 403 with a Cloudflare
  managed challenge and the header `tdm-reservation: 1`.
- **Impact:** SSRN 7342241 and SSRN 6926798 were not read. The model is
  built from Schwartz and Smith (2000) and the reachable arXiv paper only.
- **Unblock:** Download the PDFs yourself and place them in `references/`
  (git-ignored) or summarize them in `docs/references_notes.md`.

## B4. FLOPS Index app requires login

- **Found:** Step 0, 2026-10-05.
- **Evidence:** `https://app.flopsindex.com` returned HTTP 401 with
  `x-flops-login-required: 1`.
- **Impact:** FLOPS Index data is not collected.
- **Unblock:** Create an account yourself if its terms allow research use,
  then decide whether to add a collector. No account was created here.

## B5. Vast.ai terms prohibit collection and index use

- **Found:** data-source audit, 2026-10-05.
- **Evidence:** Terms of Use (version dated 2026-09-01) ban "any robot, spider,
  crawler, scraper, script ... or any other automated method" and use of its
  data "to construct, publish, or maintain any index, benchmark, pricing-
  comparison service, market-data product". The public price feed's licence
  requires a data licence for bulk collection or index use.
- **Impact:** the largest GPU marketplace is absent from our index.
- **Workaround:** none. Vast rows are dropped even when aggregators carry them.
- **Unblock:** a research data licence from data@vast.ai; then add `vast` to
  `collectors.licensed`.

## B6. RunPod terms prohibit automated access

- **Evidence:** Terms of Service (2026-03-24) §6 and §9 ban access "through
  automated or non-human means" and systematic retrieval to build a database.
- **Impact and workaround:** as B5; RunPod rows are dropped everywhere.
- **Unblock:** written permission from RunPod.

## B7. Settlement index history is paid and may not be stored

- **Evidence:** Silicon Data terms forbid storing site content in a database
  without written consent. Full history needs the Pro plan (USD 998/month) or
  a free Basic account (30 days, sign-up required). Redistribution or use to
  settle a product needs a separate index licence.
- **Impact:** blocks the tracking-error test, claim 1 (nowcast) and the
  random-walk baseline for claim 2. **This is the most important blocker.**
- **Unblock (your choice):** research access from Silicon Data, a Bloomberg
  export of `SDH100RT Index` / `SDB200RT Index`, or a paid plan whose licence
  permits storing the data. Then add CSVs under
  `data/manual/published_index/` (format in README). Ask specifically for the
  US-geography, business-day configuration that settles the contracts.

## B8. GPU1/GPU2 are not listed

- **Evidence:** CFTC extended its 40.3 review to 2026-11-09; product records
  read "Approval Pending" on 2026-10-05 (docs/contract_specs.md).
- **Impact:** no futures prices exist, so claims 2 and 3 cannot be tested and
  the paper account has nothing to trade.
- **Unblock:** wait for approval and listing; then download daily settlements
  by hand (README).

## B9. FLOPS Index terms are not public

- **Evidence:** `https://app.flopsindex.com/terms` returns 401; the README
  calls the data proprietary.
- **Unblock:** written confirmation from team@flopsindex.com.

## B10. Ornn Compute Price Index is unreachable here

- **Evidence:** `data.ornn.com` is blocked by this environment's egress
  policy.
- **Unblock:** review it manually; add the host to the allowlist only if its
  terms permit collection.

## B11. github.com is restricted to this repository

- **Evidence:** the session proxy returns 403 for other repositories on
  github.com and api.github.com. raw.githubusercontent.com works.
- **Impact:** small. Archived snapshots were fetched from
  raw.githubusercontent.com instead.

## B12. CGI per-provider receipts: licence unclear

- **Evidence:** CGI's LICENSE-DATA.md (github.com/getcomputable/gpu-index,
  commit 528b639) says receipts are included "solely for verification and
  provenance". Historical receipts exist as day files on
  `data.getcomputable.com`. That host is not in docs/data_sources.md, and its
  files carry `restatements` fields.
- **Impact:** round 3 cannot test which seats drive the CGI reversal
  directly (the mechanism agent's M1 to M3). It tests index-level proxies
  instead.
- **Conservative choice:** receipts are not collected or used. Even with
  permission, Vast and RunPod seats would still be dropped everywhere.
- **Owner action:** ask Computable whether non-commercial research use of
  the receipts (live `/latest?include=receipts` and the published day
  files) is permitted. If yes, record it in docs/data_sources.md and plan a
  forward-only receipt collector.
