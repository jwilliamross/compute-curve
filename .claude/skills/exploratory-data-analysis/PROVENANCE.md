# Provenance

- Source: https://github.com/K-Dense-AI/scientific-agent-skills/tree/92ace75ac21efe19a620434e0ca4e356081fe807/skills/exploratory-data-analysis
- Commit: `92ace75ac21efe19a620434e0ca4e356081fe807` (fetched 2026-10-09)
- Licence: MIT (repository); per-skill licence in SKILL.md frontmatter; the upstream licence file is copied alongside.
- Review: SKILL.md read in full; every kept file scanned for network calls,
  shell execution, install commands, secret handling and prompt-injection
  phrasing; reference files spot-read. See docs/decisions.md D43.
- Changes from upstream (this is a modified copy):
  - Removed `allowed-tools: Read Write Edit Bash Glob` from the frontmatter.
  - Rewrote the description for general tabular data; dropped the compatibility line.
  - Removed the version baseline with pinned `uv pip install` commands, the capability matrix, the CLI workflow and the source list; did not vendor scripts/, assets/ or the domain format references (biology, chemistry, imaging).
  - Removed image/sequence-specific interpretation notes and the arXiv-fetch citation instruction.
  - Kept the scope rules, required EDA reasoning and output interpretation verbatim; added a local-tools note and the compute-curve note.
