# Evaluation of the three claims (real data only)

Generated 2026-10-21T01:58:08.320238+00:00. Variants declared project-wide: 66.
No synthetic data is used in this report.

## Bottom line

None of the three claims can be tested on 2026-10-05. GPU1/GPU2 are not listed (CFTC review extended to 2026-11-09), so there are no futures prices. History of the settlement index cannot be stored without a licence. Everything below except the data-availability table is descriptive.

## Data available

| product | own_headline_days | own_panel_days | settlement_index_days | settlement_trade_days | complete_published_months |
|---|---|---|---|---|---|
| GPU1 | 108 | 78 | 0 | 0 | 0 |
| GPU2 | 108 | 78 | 0 | 0 | 0 |

## Descriptive statistics of the price series held

Annualized volatility of log changes (calendar days for daily series, weeks for weekly), with a circular block-bootstrap 95% CI. `share_unchanged` is the share of periods with no change. Silicon Data reports realized volatility through 2026-08-14 of 26.2% (H100) and 30.2% (B200) for its own indices (cited, not computed here).

| series | gpu | first | last | n_obs | last_value | share_unchanged | ann_vol | ann_vol_ci_low | ann_vol_ci_high |
|---|---|---|---|---|---|---|---|---|---|
| own headline | H100 | 2026-07-06 | 2026-10-21 | 108 | 3.490 | 0.720 | 0.364 | 0.235 | 0.472 |
| own headline | B200 | 2026-07-06 | 2026-10-21 | 108 | 6.840 | 0.617 | 0.543 | 0.424 | 0.643 |
| own history panel | H100 | 2026-08-04 | 2026-10-20 | 78 | 3.490 | 0.857 | 0.451 | 0.173 | 0.677 |
| own history panel | B200 | 2026-08-04 | 2026-10-20 | 78 | 8.149 | 0.584 | 0.296 | 0.043 | 0.475 |
| Computable GPU Index (daily close) | H100 | 2026-08-30 | 2026-10-21 | 53 | 3.807 | 0.000 | 0.228 | 0.183 | 0.264 |
| Computable GPU Index (daily close) | B200 | 2026-08-30 | 2026-10-21 | 53 | 7.721 | 0.000 | 0.144 | 0.085 | 0.204 |
| GetDeploying weekly median | H100 | 2025-10-06 | 2026-10-19 | 55 | 3.842 | 0.241 | 0.255 | 0.184 | 0.313 |
| GetDeploying weekly median | B200 | 2025-10-06 | 2026-10-19 | 55 | 7.763 | 0.370 | 0.372 | 0.239 | 0.491 |

Computable GPU Index data: (c) 2026 Computable, CC BY-NC 4.0. GetDeploying data: CC BY 4.0. gpurentalprices.com data: CC BY 4.0.

## Our index versus an independent index (Computable GPU Index)

A construction cross-check, not a tracking error against the settlement index.

- H100: 52 overlapping days. Mean log difference (ours minus CGI) -0.125 [-0.153, -0.093]; RMSE 0.136; correlation of daily changes -0.09.
- B200: 52 overlapping days. Mean log difference (ours minus CGI) +0.009 [-0.020, +0.039]; RMSE 0.052; correlation of daily changes 0.09.

## Our index versus the settlement index

- GPU1 (H100): insufficient overlap (0 days with both our index and the published index; need 20). No tracking error reported.
- GPU2 (B200): insufficient overlap (0 days with both our index and the published index; need 20). No tracking error reported.

## Claim 1: nowcast edge

- GPU1: insufficient data. 0 complete months of published index history with our index alongside; the pre-registered minimum is 6.
- GPU2: insufficient data. 0 complete months of published index history with our index alongside; the pre-registered minimum is 6.

## Claim 2: model edge (term structure)

- GPU1: spot-only fit skipped: 0 published index days, minimum 180.
- GPU1: model-versus-market test needs futures settlements and realized final settlements. Available: 0 settlement days, minimum 180. Not testable yet.
- GPU2: spot-only fit skipped: 0 published index days, minimum 180.
- GPU2: model-versus-market test needs futures settlements and realized final settlements. Available: 0 settlement days, minimum 180. Not testable yet.

## Claim 3: survivability after costs

Backtests on real futures history require CME settlements; see `reports/backtest_real.md`.

### Relative value (descriptive)

Assumed B200/H100 throughput ratio 2.5 (range 1.8-3.0; docs/relative_value.md).

- headline, 2026-10-21: H100 USD 3.490, B200 USD 6.840 per GPU-hour; break-even ratio 1.96 (min 1.92, median 2.09, max 2.28 over 108 days). B200 is cheaper per unit of compute at the central ratio; not robust: the break-even ratio lies inside the assumed range.
- history panel, 2026-10-20: H100 USD 3.490, B200 USD 8.149 per GPU-hour; break-even ratio 2.34 (min 2.00, median 2.15, max 2.34 over 78 days). B200 is cheaper per unit of compute at the central ratio; not robust: the break-even ratio lies inside the assumed range.
- Computable GPU Index, 2026-10-21: break-even ratio 2.03. B200 is cheaper per unit of compute at the central ratio; not robust: the break-even ratio lies inside the assumed range.
- GetDeploying weekly median, 2026-10-19: break-even ratio 2.02. B200 is cheaper per unit of compute at the central ratio; not robust: the break-even ratio lies inside the assumed range.

- Spread mean-reversion test (H4): insufficient history (78 days on the fixed panel; minimum 120). Not run.

## Cost assumptions

| Assumption | Value | Status |
|---|---|---|
| Half-spread | 5.0 ticks per side | assumption |
| Slippage | 2.0 ticks per side | assumption |
| Broker + clearing | USD 2.50 per contract per side | assumption |
| GPU1 exchange fee | USD 5.50 per contract per side (non-member Globex) | verified (CFTC filing) |
| GPU1 cash-settlement fee | USD 1.35 per contract | verified (CFTC filing) |
| GPU1 tick | USD 0.01/GPU-h = USD 7.30/contract | verified (CFTC filing) |
| GPU1 contract size | 730 GPU-hours | verified (CFTC filing) |
| GPU1 initial margin | USD 400 per contract | assumption |
| GPU1 listing status | not listed: CFTC 40.3 review extended to 2026-11-09 | as of 2026-10-05 |
| GPU2 exchange fee | USD 5.50 per contract per side (non-member Globex) | verified (CFTC filing) |
| GPU2 cash-settlement fee | USD 1.35 per contract | verified (CFTC filing) |
| GPU2 tick | USD 0.01/GPU-h = USD 7.30/contract | verified (CFTC filing) |
| GPU2 contract size | 730 GPU-hours | verified (CFTC filing) |
| GPU2 initial margin | USD 900 per contract | assumption |
| GPU2 listing status | not listed: CFTC 40.3 review extended to 2026-11-09 | as of 2026-10-05 |

## Validation status used by the paper account

- nowcast: not validated (shadow mode)
- relative_value: not validated (shadow mode)
