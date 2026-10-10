# Provenance

- Source: https://github.com/terrylica/cc-skills/tree/b592ad8d044a8c301a8998e58e66746a819cf19a/plugins/quant-research/skills/sharpe-ratio-non-iid-corrections
- Commit: `b592ad8d044a8c301a8998e58e66746a819cf19a` (2026-10-10; fetched 2026-10-10)
- Licence: MIT (repository root LICENSE, "Copyright (c) 2025-2026 terrylica"); copied alongside.
- Review: SKILL.md and `references/sharpe-paper-tracker.md` read in full;
  `references/sharpe_numba.py` scanned (imports math, numpy, numba; no network,
  subprocess or file writes) but not vendored. The Exhibit 1 values and the
  SFDR example were recomputed independently with numpy and scipy: all Exhibit 1
  rows agree to three decimals; the SFDR example's 0.760 could not be
  reproduced (0.862 with the stated inputs). See docs/decisions.md D52.
- Changes from upstream (a modified copy):
  - Removed `allowed-tools: Read, Grep, Glob, Bash` from the frontmatter and
    rewrote the description (no Numba; narrower trigger).
  - Removed the "Self-Evolving Skill" block and the "Post-Execution Reflection"
    section, which tell the agent to edit the skill file itself during use.
  - Removed the Quick Start (`uv run --with numba` of a non-vendored script) and
    the "Implementation Architecture" section (Numba tiers).
  - Did not vendor `references/sharpe_numba.py` (needs numba, not in the
    project stack), `references/lopez-de-prado-sharpe-2026.pdf`,
    `references/how-to-use-the-sharpe-ratio-2026.md` (a full transcription of a
    third-party paper whose licence is not stated) or `references/media/`;
    removed links to them.
  - Replaced upstream's project default ("use SFDR; our strategies are survivors
    of hundreds of regime explorations", crypto range-bar Sharpe values, git
    history and signal-archaeology lookups) with the compute-curve default (DSR
    with K from `docs/variants_log.md`; SFDR only as a sensitivity check).
  - Relabelled the example preflight output as illustrative, corrected its SFDR
    threshold to the recomputed 0.862 with a note, and added a note that pFDR
    may never reach q.
  - Marked the independently recomputed Exhibit 1 rows; added the note that SR
    is per observation period and defined γ and V in Eq 28.
  - Marked the paper title and date as unverified: the authors' replication
    repository titles SSRN 5520741 differently.
  - Replaced the related-skills table (upstream skills not vendored) with links
    to `quant-research` and `compute-curve-research`.
  - `references/equation-map.md` is the upstream tracker with its frontmatter
    (links to non-vendored files) and summary removed, the "Test" and check
    columns dropped, and a compute-curve note added.
  - Added the compute-curve note after the title.
