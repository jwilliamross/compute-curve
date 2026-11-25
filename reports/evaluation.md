# Evaluation of the three claims (real data only)

Generated 2026-11-25T05:39:18.391597+00:00. Variants declared project-wide: 66.
No synthetic data is used in this report.

## Bottom line

None of the three claims can be tested on 2026-10-05. GPU1/GPU2 are not listed (CFTC review extended to 2026-11-09), so there are no futures prices. History of the settlement index cannot be stored without a licence. Everything below except the data-availability table is descriptive.

## Data available

| product | own_headline_days | own_panel_days | settlement_index_days | settlement_trade_days | complete_published_months |
|---|---|---|---|---|---|
| GPU1 | 143 | 110 | 0 | 0 | 0 |
| GPU2 | 143 | 110 | 0 | 0 | 0 |

## Descriptive statistics of the price series held

Annualized volatility of log changes (calendar days for daily series, weeks for weekly), with a circular block-bootstrap 95% CI. `share_unchanged` is the share of periods with no change. Silicon Data reports realized volatility through 2026-08-14 of 26.2% (H100) and 30.2% (B200) for its own indices (cited, not computed here).

| series | gpu | first | last | n_obs | last_value | share_unchanged | ann_vol | ann_vol_ci_low | ann_vol_ci_high |
|---|---|---|---|---|---|---|---|---|---|
| own headline | H100 | 2026-07-06 | 2026-11-25 | 143 | 3.140 | 0.634 | 0.514 | 0.379 | 0.645 |
| own headline | B200 | 2026-07-06 | 2026-11-25 | 143 | 6.250 | 0.634 | 0.493 | 0.383 | 0.586 |
| own history panel | H100 | 2026-08-04 | 2026-11-24 | 110 | 3.640 | 0.817 | 0.593 | 0.386 | 0.763 |
| own history panel | B200 | 2026-08-04 | 2026-11-24 | 110 | 8.550 | 0.651 | 0.252 | 0.050 | 0.400 |
| Computable GPU Index (daily close) | H100 | 2026-08-30 | 2026-11-25 | 88 | 3.769 | 0.000 | 0.289 | 0.224 | 0.361 |
| Computable GPU Index (daily close) | B200 | 2026-08-30 | 2026-11-25 | 88 | 8.218 | 0.000 | 0.144 | 0.094 | 0.186 |
| GetDeploying weekly median | H100 | 2025-10-06 | 2026-11-23 | 60 | 4.240 | 0.220 | 0.256 | 0.183 | 0.315 |
| GetDeploying weekly median | B200 | 2025-10-06 | 2026-11-23 | 60 | 8.345 | 0.339 | 0.362 | 0.237 | 0.475 |

Computable GPU Index data: (c) 2026 Computable, CC BY-NC 4.0. GetDeploying data: CC BY 4.0. gpurentalprices.com data: CC BY 4.0.

## Our index versus an independent index (Computable GPU Index)

A construction cross-check, not a tracking error against the settlement index.

- H100: 84 overlapping days. Mean log difference (ours minus CGI) -0.097 [-0.123, -0.069]; RMSE 0.116; correlation of daily changes -0.11.
- B200: 84 overlapping days. Mean log difference (ours minus CGI) +0.026 [+0.004, +0.048]; RMSE 0.054; correlation of daily changes 0.06.

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

- headline, 2026-11-25: H100 USD 3.140, B200 USD 6.250 per GPU-hour; break-even ratio 1.99 (min 1.85, median 2.09, max 2.28 over 143 days). B200 is cheaper per unit of compute at the central ratio; not robust: the break-even ratio lies inside the assumed range.
- history panel, 2026-11-24: H100 USD 3.640, B200 USD 8.550 per GPU-hour; break-even ratio 2.35 (min 2.00, median 2.19, max 2.44 over 110 days). B200 is cheaper per unit of compute at the central ratio; not robust: the break-even ratio lies inside the assumed range.
- Computable GPU Index, 2026-11-25: break-even ratio 2.18. B200 is cheaper per unit of compute at the central ratio; not robust: the break-even ratio lies inside the assumed range.
- GetDeploying weekly median, 2026-11-23: break-even ratio 1.97. B200 is cheaper per unit of compute at the central ratio; not robust: the break-even ratio lies inside the assumed range.

- Spread mean-reversion test (H4): insufficient history (110 days on the fixed panel; minimum 120). Not run.

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
