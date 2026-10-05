# Evaluation of the three claims (real data only)

Generated 2026-10-05T18:50:48.428356+00:00. Variants declared project-wide: 9.
No synthetic data is used in this report.

## Bottom line

None of the three claims can be tested on 2026-10-05. GPU1/GPU2 are not listed (CFTC review extended to 2026-11-09), so there are no futures prices. History of the settlement index cannot be stored without a licence. Everything below except the data-availability table is descriptive.

## Data available

| product | own_headline_days | own_panel_days | settlement_index_days | settlement_trade_days | complete_published_months |
|---|---|---|---|---|---|
| GPU1 | 79 | 49 | 0 | 0 | 0 |
| GPU2 | 79 | 49 | 0 | 0 | 0 |

## Descriptive statistics of the price series held

Annualized volatility of log changes (calendar days for daily series, weeks for weekly), with a circular block-bootstrap 95% CI. `share_unchanged` is the share of periods with no change. Silicon Data reports realized volatility through 2026-08-14 of 26.2% (H100) and 30.2% (B200) for its own indices (cited, not computed here).

| series | gpu | first | last | n_obs | last_value | share_unchanged | ann_vol | ann_vol_ci_low | ann_vol_ci_high |
|---|---|---|---|---|---|---|---|---|---|
| own headline | H100 | 2026-07-19 | 2026-10-05 | 79 | 3.200 | 0.808 | 0.241 | 0.145 | 0.326 |
| own headline | B200 | 2026-07-19 | 2026-10-05 | 79 | 6.250 | 0.538 | 0.549 | 0.407 | 0.660 |
| own history panel | H100 | 2026-08-18 | 2026-10-05 | 49 | 3.209 | 0.875 | 0.146 | 0.047 | 0.204 |
| own history panel | B200 | 2026-08-18 | 2026-10-05 | 49 | 7.041 | 0.750 | 0.324 | 0.040 | 0.530 |
| Computable GPU Index (daily close) | H100 | 2026-08-30 | 2026-10-05 | 37 | 3.621 | 0.000 | 0.200 | 0.155 | 0.233 |
| Computable GPU Index (daily close) | B200 | 2026-08-30 | 2026-10-05 | 37 | 6.945 | 0.000 | 0.095 | 0.064 | 0.121 |
| GetDeploying weekly median | H100 | 2025-10-06 | 2026-10-05 | 53 | 3.409 | 0.250 | 0.238 | 0.161 | 0.298 |
| GetDeploying weekly median | B200 | 2025-10-06 | 2026-10-05 | 53 | 6.790 | 0.385 | 0.361 | 0.221 | 0.486 |

Computable GPU Index data: (c) 2026 Computable, CC BY-NC 4.0. GetDeploying data: CC BY 4.0. gpurentalprices.com data: CC BY 4.0.

## Our index versus an independent index (Computable GPU Index)

A construction cross-check, not a tracking error against the settlement index.

- H100: 37 overlapping days. Mean log difference (ours minus CGI) -0.123 [-0.133, -0.111]; RMSE 0.124; correlation of daily changes -0.17.
- B200: 37 overlapping days. Mean log difference (ours minus CGI) -0.077 [-0.093, -0.055]; RMSE 0.083; correlation of daily changes 0.15.

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

- headline, 2026-10-05: H100 USD 3.200, B200 USD 6.250 per GPU-hour; break-even ratio 1.95 (min 1.95, median 2.10, max 2.28 over 79 days). B200 is cheaper per unit of compute at the central ratio; not robust: the break-even ratio lies inside the assumed range.
- history panel, 2026-10-05: H100 USD 3.209, B200 USD 7.041 per GPU-hour; break-even ratio 2.19 (min 1.96, median 2.00, max 2.19 over 49 days). B200 is cheaper per unit of compute at the central ratio; not robust: the break-even ratio lies inside the assumed range.
- Computable GPU Index, 2026-10-05: break-even ratio 1.92. B200 is cheaper per unit of compute at the central ratio; not robust: the break-even ratio lies inside the assumed range.
- GetDeploying weekly median, 2026-10-05: break-even ratio 1.99. B200 is cheaper per unit of compute at the central ratio; not robust: the break-even ratio lies inside the assumed range.

- Spread mean-reversion test (H4): insufficient history (49 days on the fixed panel; minimum 120). Not run.

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
