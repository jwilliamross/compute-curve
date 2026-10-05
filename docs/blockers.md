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
- **Impact:** This session cannot verify the GPU1 and GPU2 contract specs
  against the CME rulebook, cannot confirm whether trading started on
  2026-10-05, and cannot fetch tick size, fees, margin or daily settlements.
- **Workaround:** The paper trading engine reads CME settlements from a
  manual CSV drop folder. Contract parameters live in config and are marked
  unverified. No settlement data exists in the repo.
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
