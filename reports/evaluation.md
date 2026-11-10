# Evaluation of the three claims (real data only)

Generated 2026-11-10T04:46:50.183051+00:00. Variants declared project-wide: 66.
No synthetic data is used in this report.

## Bottom line

None of the three claims can be tested on 2026-10-05. GPU1/GPU2 are not listed (CFTC review extended to 2026-11-09), so there are no futures prices. History of the settlement index cannot be stored without a licence. Everything below except the data-availability table is descriptive.

## Data available

| product | own_headline_days | own_panel_days | settlement_index_days | settlement_trade_days | complete_published_months |
|---|---|---|---|---|---|
| GPU1 | 128 | 95 | 0 | 0 | 0 |
| GPU2 | 128 | 95 | 0 | 0 | 0 |

## Descriptive statistics of the price series held

Annualized volatility of log changes (calendar days for daily series, weeks for weekly), with a circular block-bootstrap 95% CI. `share_unchanged` is the share of periods with no change. Silicon Data reports realized volatility through 2026-08-14 of 26.2% (H100) and 30.2% (B200) for its own indices (cited, not computed here).

| series | gpu | first | last | n_obs | last_value | share_unchanged | ann_vol | ann_vol_ci_low | ann_vol_ci_high |
|---|---|---|---|---|---|---|---|---|---|
| own headline | H100 | 2026-07-06 | 2026-11-10 | 128 | 3.200 | 0.646 | 0.502 | 0.339 | 0.644 |
| own headline | B200 | 2026-07-06 | 2026-11-10 | 128 | 6.250 | 0.654 | 0.481 | 0.370 | 0.583 |
| own history panel | H100 | 2026-08-04 | 2026-11-09 | 95 | 3.640 | 0.830 | 0.523 | 0.276 | 0.717 |
| own history panel | B200 | 2026-08-04 | 2026-11-09 | 95 | 8.345 | 0.617 | 0.269 | 0.045 | 0.430 |
| Computable GPU Index (daily close) | H100 | 2026-08-30 | 2026-11-10 | 73 | 3.833 | 0.000 | 0.236 | 0.197 | 0.272 |
| Computable GPU Index (daily close) | B200 | 2026-08-30 | 2026-11-10 | 73 | 7.983 | 0.000 | 0.148 | 0.092 | 0.195 |
| GetDeploying weekly median | H100 | 2025-10-06 | 2026-11-09 | 58 | 3.990 | 0.246 | 0.257 | 0.181 | 0.315 |
| GetDeploying weekly median | B200 | 2025-10-06 | 2026-11-09 | 58 | 8.080 | 0.351 | 0.368 | 0.239 | 0.481 |

Computable GPU Index data: (c) 2026 Computable, CC BY-NC 4.0. GetDeploying data: CC BY 4.0. gpurentalprices.com data: CC BY 4.0.

## Our index versus an independent index (Computable GPU Index)

A construction cross-check, not a tracking error against the settlement index.

- H100: 69 overlapping days. Mean log difference (ours minus CGI) -0.106 [-0.133, -0.075]; RMSE 0.123; correlation of daily changes -0.09.
- B200: 69 overlapping days. Mean log difference (ours minus CGI) +0.022 [-0.003, +0.047]; RMSE 0.055; correlation of daily changes 0.08.

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

- headline, 2026-11-10: H100 USD 3.200, B200 USD 6.250 per GPU-hour; break-even ratio 1.95 (min 1.85, median 2.09, max 2.28 over 128 days). B200 is cheaper per unit of compute at the central ratio; not robust: the break-even ratio lies inside the assumed range.
- history panel, 2026-11-09: H100 USD 3.640, B200 USD 8.345 per GPU-hour; break-even ratio 2.29 (min 2.00, median 2.17, max 2.39 over 95 days). B200 is cheaper per unit of compute at the central ratio; not robust: the break-even ratio lies inside the assumed range.
- Computable GPU Index, 2026-11-10: break-even ratio 2.08. B200 is cheaper per unit of compute at the central ratio; not robust: the break-even ratio lies inside the assumed range.
- GetDeploying weekly median, 2026-11-09: break-even ratio 2.03. B200 is cheaper per unit of compute at the central ratio; not robust: the break-even ratio lies inside the assumed range.

- Spread mean-reversion test (H4): insufficient history (95 days on the fixed panel; minimum 120). Not run.

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
