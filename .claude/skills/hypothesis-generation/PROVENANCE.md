# Provenance

- Source: https://github.com/K-Dense-AI/scientific-agent-skills/tree/92ace75ac21efe19a620434e0ca4e356081fe807/skills/hypothesis-generation
- Commit: `92ace75ac21efe19a620434e0ca4e356081fe807` (fetched 2026-10-09)
- Licence: MIT (repository); per-skill licence in SKILL.md frontmatter; the upstream licence file is copied alongside.
- Review: SKILL.md read in full; every kept file scanned for network calls,
  shell execution, install commands, secret handling and prompt-injection
  phrasing; reference files spot-read. See docs/decisions.md D43.
- Changes from upstream (this is a modified copy):
  - Removed the instruction to fetch an arXiv record before citing (an outbound network call).
  - Did not vendor scripts/ (seven local validator CLIs) or the two references that document them; replaced the tool index with a note.
  - Added the compute-curve note after the title.
