# Engine validation on SYNTHETIC data

> **SYNTHETIC DATA - ENGINE VALIDATION ONLY - NOT A RESULT.** Prices are simulated from a Schwartz-Smith process with invented parameters. Nothing here says anything about the real GPU1/GPU2 market or about the three claims.

## Engine checks

| Check | Pass |
|---|---|
| Flat strategy has zero PnL and zero costs | yes |
| Cash-flow ledger sums to equity change | yes |
| PnL falls as costs rise (stops and margin non-binding, trades held fixed) | yes |
| Gross position never exceeds limit | yes |
| Signals strategy ran end to end | yes |

## Tearsheet (toy momentum rule): momentum_toy_x1.0

> **SYNTHETIC DATA - ENGINE VALIDATION ONLY - NOT A RESULT.**

Cost multiplier: 1.0. Variants tried project-wide: 9.

| Metric | Value | 95% CI |
|---|---|---|
| Days processed (trading) | 730 (522) | |
| Total PnL (USD) | -5,511 | |
| Mean daily PnL (USD) | | [-22.8, 1.0] |
| Sharpe (annualized) | -1.20 | [-2.54, 0.10] |
| Max drawdown (USD) | 7,554 | |
| Contracts traded | 144 | |
| Turnover (contracts/trading day) | 0.28 | |
| Total costs (USD) | 8,510 | |
| Capacity estimate | unknown (no volume data) | |

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

## Sensitivity to costs

| cost_multiplier | total_pnl | sharpe | sharpe_ci_low | sharpe_ci_high | total_costs |
|---|---|---|---|---|---|
| 0.00 | 7,539.00 | 0.91 | -0.36 | 2.14 | -0.00 |
| 0.50 | -6,016.36 | -0.92 | -2.13 | 0.23 | 13,829.40 |
| 1.00 | -5,511.41 | -1.20 | -2.54 | 0.10 | 8,510.40 |
| 2.00 | -6,391.94 | -1.46 | -2.88 | 0.09 | 8,510.40 |
| 4.00 | -8,028.66 | -1.55 | -2.87 | 0.35 | 10,401.60 |


With loss stops and margin active, the trade path changes with costs, because a stop fires or margin runs out at different times. The sensitivity table above therefore need not be monotone. With stops and margin made non-binding, trades are identical across rows:

| cost_multiplier | total_pnl | sharpe | sharpe_ci_low | sharpe_ci_high | total_costs |
|---|---|---|---|---|---|
| 0.00 | 7,539.00 | 0.91 | -0.36 | 2.14 | -0.00 |
| 0.50 | -21,419.99 | -2.49 | -3.91 | -1.17 | 28,959.00 |
| 1.00 | -50,379.00 | -5.26 | -6.77 | -3.81 | 57,918.00 |
| 2.00 | -108,297.01 | -8.42 | -9.84 | -6.97 | 115,836.00 |
| 4.00 | -224,133.00 | -10.38 | -11.59 | -9.11 | 231,672.00 |

## Signals strategy on synthetic inputs

Shadow predictions logged: 1173. Fills: 72. The synthetic market has no own-index series, so the nowcast model cannot form a prediction and only the relative-value rule can act.
