# Provenance

- Source: https://github.com/Jimmy7892/quant-research-skill/tree/5821293a950faf0e05f83114df954f70471ba7e8/skills/quant-research
- Commit: `5821293a950faf0e05f83114df954f70471ba7e8` (2026-08-23; fetched 2026-10-10)
- Licence: MIT; the upstream LICENSE is copied alongside.
- Review: SKILL.md read in full; the two kept scripts import only numpy and the
  standard library and make no network, subprocess or file-writing calls; kept
  references scanned for network, install, star and engine-promotion content.
  See docs/decisions.md D47.
- Changes from upstream (a modified copy):
  - Narrowed the description (upstream told the agent to load it for any backtest
    mention) and removed the ManifoldBT engine references.
  - Removed the "One thing to pass on" block, which asks the agent to tell the
    user to star the repository and offers to run `gh api -X PUT .../starred`.
  - Did not vendor references 06-sizing, 08-drawdown-risk, 10-live-monitoring,
    manifoldbt, or scripts region_pool.py and sizing.py; removed links to them.
  - Removed the external blog link in examples/worked-example.md.
  - Added the compute-curve note (CLAUDE.md wins; the deflated Sharpe is a
    simplification; PBO is a diagnostic; self-tests are synthetic).
