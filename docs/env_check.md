# Environment check

Run at 2026-10-05 17:38 UTC in the Claude Code cloud container.

## Summary

**What works.** Python 3.11, uv, git, pytest and ruff are installed. PyPI is
reachable and numpy installed in about two seconds. Git commit and push to
`claude/quirky-allen-b87nkb` works. The Vast.ai offers endpoint returned 47
live H100 and B200 offers without this session adding any credential. arXiv,
Silicon Data's public site, RunPod's site, Vast.ai docs and
api.financialdatasets.ai all respond.

**What is misconfigured or blocked.**

1. **No network allowlist is active.** `example.com` returned HTTP 200. The
   agent proxy reports `"selective": false`, meaning outbound traffic is not
   restricted to a domain list. If you intended a restricted allowlist, the
   environment's network policy is set to unrestricted.
2. **CME Group website blocks automated access.** `www.cmegroup.com` returned
   HTTP 403 from Akamai with a message that automated access is "strictly
   prohibited by CME Group's website Data Terms of Use". This is a terms
   prohibition, not an allowlist problem. This project will not scrape
   cmegroup.com. Settlement prices must come from a licensed channel or a
   file you download by hand.
3. **SSRN blocks automated access.** `papers.ssrn.com` returned HTTP 403 with
   a Cloudflare JavaScript challenge. It also sends `tdm-reservation: 1`,
   which reserves text-and-data-mining rights for the publisher (Elsevier).
   The two SSRN references cannot be read from this session.
4. **FLOPS Index app requires login.** `app.flopsindex.com` returned HTTP 401
   with `x-flops-login-required: 1`. No account will be created.

**What you should change.**

1. Decide on the network policy. To enforce an allowlist, switch the
   environment from unrestricted to a custom allowlist in the Claude Code on
   the web environment settings
   (<https://code.claude.com/docs/en/claude-code-on-the-web>). The minimum
   list this project needs is:
   `pypi.org`, `files.pythonhosted.org`, `github.com`, `console.vast.ai`,
   `docs.vast.ai`, `cloud.vast.ai`, `www.runpod.io`, `runpod.io`,
   `www.silicondata.com`, `arxiv.org`, `export.arxiv.org`, plus any provider
   pricing pages approved in `docs/data_sources.md`.
2. Provide CME settlement data by hand. Download GPU1 and GPU2 daily
   settlements from CME in a browser and save them as CSV under
   `data/manual/cme_settlements/` using the format in `README.md`. Do not
   ask an agent to scrape cmegroup.com.
3. Download the two SSRN papers (7342241 and 6926798) yourself in a browser.
   Keep the PDFs in the git-ignored `references/` folder, or paste the key
   equations into `docs/references_notes.md`, so a later session can use
   them.
4. Optional: the Vast.ai search endpoint works without a key, so the
   collector does not use `VAST_API_KEY`. You may remove that secret from
   the environment if nothing else needs it.

## Results

| # | Check | Result | Detail |
|---|-------|--------|--------|
| 1 | python | PASS | Python 3.11.15 (`/usr/local/bin/python3`) |
| 1 | uv | PASS | uv 0.8.17 |
| 1 | git | PASS | git 2.43.0 |
| 1 | pytest | PASS | pytest 9.1.1 (global); project pins its own in the dev group |
| 1 | ruff | PASS | ruff 0.15.20 (global); project pins its own in the dev group |
| 2 | uv project created | PASS | `uv init --lib --name compute-curve --python 3.11` |
| 2 | PyPI reachable | PASS | `uv add numpy` installed numpy 2.4.6 in 2.2 s |
| 3 | console.vast.ai | PASS | 302, then 200 at `https://cloud.vast.ai/` |
| 3 | docs.vast.ai | PASS | 308, then 200 at `/guides/get-started` |
| 3 | api.financialdatasets.ai | PASS | 200 (3.7 kB landing response) |
| 3 | app.flopsindex.com | FAIL | 401 `Authentication required.` (`x-flops-login-required: 1`) |
| 3 | www.cmegroup.com | FAIL | 403 from AkamaiGHost; automated access prohibited by CME Data Terms of Use |
| 3 | www.silicondata.com | PASS | 200 (161 kB) |
| 3 | arxiv.org | PASS | 200 (38 kB) |
| 3 | papers.ssrn.com | FAIL | 403 Cloudflare managed challenge; `tdm-reservation: 1` |
| 3 | runpod.io | PASS | 301, then 200 at `https://www.runpod.io/` |
| 3 | example.com (should be blocked) | FAIL | 200; allowlist is **not** active (`selective: false` in proxy status) |
| 4 | git commit and push | PASS | This file was committed and pushed to `origin/claude/quirky-allen-b87nkb` |
| 5 | `VAST_API_KEY` set | PASS | Set and non-empty. Value not read, printed or logged. |
| 5 | Vast.ai offers endpoint, no key added | PASS | `POST https://console.vast.ai/api/v0/bundles/` returned 200 with 47 offers (H100 SXM, H100 PCIE, H100 NVL, B200). The session did not send an `Authorization` header. It cannot tell whether the proxy attached one or the endpoint is public. |
| 6 | MCP connector tools available | INFO | Yes. See below. None were called. |

### Network check method

Each URL was requested once with `curl -sS -m 20` and a descriptive
`User-Agent`, without following redirects, then redirecting URLs were
re-requested with `-L` to record the final status. Response headers for the
non-200 results were inspected to tell a proxy denial from an origin block.
All three failures came from the origin site (Akamai, Cloudflare, Fly.io),
not from the session's egress proxy.

### Connectors (not called)

The session exposes MCP tools from these servers: Claude_Docs, Composio,
Figma, Firecrawl, Gmail, Google Calendar, Google Cloud BigQuery, Google
Drive, Google Sheets, Shopify, Spotify, Supabase, Vercel, Vibe_Prospecting,
Zapier, GitHub and claude-code-remote. Canva is listed but needs
authorization. Per your instruction none of these were called at any point.
Git operations use the `git` CLI only.

### Other environment variables of note

Names only. The container also carries `GH_TOKEN`, `GITHUB_TOKEN`,
`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `CLOUDSDK_AUTH_ACCESS_TOKEN`.
This project does not use any of them.
