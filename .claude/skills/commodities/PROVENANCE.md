# Provenance

- Source: https://github.com/joellewis/finance_skills/tree/5c498eacf7057e31238c4c5a8012a1afe9ec7c8a/plugins/wealth-management/skills/commodities
- Commit: `5c498eacf7057e31238c4c5a8012a1afe9ec7c8a` (fetched 2026-10-15)
- Licence: MIT; the upstream licence file is copied alongside.
- Review: SKILL.md read in full and scanned for network calls, shell execution,
  install commands, secret handling and prompt-injection phrasing; nothing found
  beyond the script usage section. See docs/decisions.md D61.
- Changes from upstream (this is a modified copy):
  - Did not vendor scripts/; removed the "Running the script" section (it
    suggested `pip install`; dependencies come from uv.lock).
  - Added the compute-curve note after the title.
