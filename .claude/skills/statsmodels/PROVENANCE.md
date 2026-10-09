# Provenance

- Source: https://github.com/K-Dense-AI/scientific-agent-skills/tree/92ace75ac21efe19a620434e0ca4e356081fe807/skills/statsmodels
- Commit: `92ace75ac21efe19a620434e0ca4e356081fe807` (fetched 2026-10-09)
- Licence: MIT (repository); per-skill licence in SKILL.md frontmatter; the upstream licence file is copied alongside.
- Review: SKILL.md read in full; every kept file scanned for network calls,
  shell execution, install commands, secret handling and prompt-injection
  phrasing; reference files spot-read. See docs/decisions.md D43.
- Changes from upstream (this is a modified copy):
  - Removed `allowed-tools: Read Write Edit Bash` from the frontmatter (it pre-approves tools).
  - Replaced the pinned `uv pip install` line with a pointer to uv.lock.
  - Removed the instruction to fetch an arXiv record before citing.
  - Removed the cross-reference to the non-vendored statistical-analysis skill.
  - Added a pointer to compute_curve.claim4.stats and the compute-curve note.
