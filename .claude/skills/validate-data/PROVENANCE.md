# Provenance

- Source: https://github.com/anthropics/knowledge-work-plugins/tree/95bdacc803aa5cfdb10f35e5b9fb2d4b11100133/data/skills/validate-data
- Commit: `95bdacc803aa5cfdb10f35e5b9fb2d4b11100133` (fetched 2026-10-09)
- Licence: Apache-2.0; the upstream licence file is copied alongside.
- Review: SKILL.md read in full; every kept file scanned for network calls,
  shell execution, install commands, secret handling and prompt-injection
  phrasing; reference files spot-read. See docs/decisions.md D43.
- Changes from upstream (this is a modified copy):
  - Replaced the pointer to the plugin's CONNECTORS.md (not vendored) with a note on local data access.
  - Added the compute-curve note after the title.
