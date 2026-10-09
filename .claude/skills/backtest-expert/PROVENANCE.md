# Provenance

- Source: https://github.com/tradermonty/claude-trading-skills/tree/eab8d5cb97b9982d915944cdaa2df972fa396b22/skills/backtest-expert
- Commit: `eab8d5cb97b9982d915944cdaa2df972fa396b22` (fetched 2026-10-09)
- Licence: MIT; the upstream licence file is copied alongside.
- Review: SKILL.md read in full; every kept file scanned for network calls,
  shell execution, install commands, secret handling and prompt-injection
  phrasing; reference files spot-read. See docs/decisions.md D43.
- Changes from upstream (this is a modified copy):
  - Did not vendor scripts/ (a scorer of self-reported metrics that writes into reports/) or requirements.txt; removed the Prerequisites and Output sections and the script usage.
  - Added a note that the long-history and trade-count minimums do not fit this repository's short data.
  - Added the compute-curve note after the title.
