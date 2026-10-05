# Backtest on real data

Not run: there is no CME settlement history in `data/manual/cme_settlements/`. GPU1/GPU2 did not list on 2026-10-05: the CFTC extended its review to 2026-11-09 (docs/contract_specs.md, docs/blockers.md B8). Settlements must be added by hand because cmegroup.com may not be scripted (B2). No backtest result exists.

Historical index data (our index, the Computable GPU Index, GetDeploying) cannot stand in for futures: trading it would require inventing a futures price. Those series are analysed descriptively in `reports/evaluation.md`. The engine itself is validated on labelled synthetic data in `reports/engine_validation_SYNTHETIC.md`.
