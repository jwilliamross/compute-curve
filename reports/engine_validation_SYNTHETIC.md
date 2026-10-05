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
| Total PnL (USD) | -6,148 | |
| Mean daily PnL (USD) | | [-25.4, 1.7] |
| Sharpe (annualized) | -1.16 | [-2.52, 0.16] |
| Max drawdown (USD) | 7,925 | |
| Contracts traded | 196 | |
| Turnover (contracts/trading day) | 0.38 | |
| Total costs (USD) | 10,996 | |
| Capacity estimate | unknown (no volume data) | |

## Cost assumptions

| Assumption | Value | Status |
|---|---|---|
| Half-spread | 5.0 ticks per side | assumption |
| Slippage | 2.0 ticks per side | assumption |
| All-in fee | USD 5.00 per contract per side | assumption |
| GPU1 tick | USD 0.01/GPU-h = USD 7.30/contract | unverified |
| GPU1 contract size | 730 GPU-hours | unverified |
| GPU2 tick | USD 0.01/GPU-h = USD 7.30/contract | unverified |
| GPU2 contract size | 730 GPU-hours | unverified |

## Sensitivity to costs

| cost_multiplier | total_pnl | sharpe | sharpe_ci_low | sharpe_ci_high | total_costs |
|---|---|---|---|---|---|
| 0.00 | 7,539.00 | 0.91 | -0.36 | 2.14 | -0.00 |
| 0.50 | -6,137.64 | -0.92 | -2.14 | 0.24 | 14,473.80 |
| 1.00 | -6,147.96 | -1.16 | -2.52 | 0.16 | 10,995.60 |
| 2.00 | -5,959.94 | -1.39 | -2.81 | 0.13 | 8,078.40 |
| 4.00 | -7,500.66 | -1.51 | -2.87 | 0.38 | 9,873.60 |


With loss stops and margin active, the trade path changes with costs, because a stop fires or margin runs out at different times. The sensitivity table above therefore need not be monotone. With stops and margin made non-binding, trades are identical across rows:

| cost_multiplier | total_pnl | sharpe | sharpe_ci_low | sharpe_ci_high | total_costs |
|---|---|---|---|---|---|
| 0.00 | 7,539.00 | 0.91 | -0.36 | 2.14 | -0.00 |
| 0.50 | -19,949.99 | -2.33 | -3.75 | -1.01 | 27,489.00 |
| 1.00 | -47,439.00 | -5.02 | -6.53 | -3.58 | 54,978.00 |
| 2.00 | -102,417.01 | -8.21 | -9.64 | -6.76 | 109,956.00 |
| 4.00 | -212,373.00 | -10.29 | -11.50 | -9.01 | 219,912.00 |

## Signals strategy on synthetic inputs

Shadow predictions logged: 1176. Fills: 72. The synthetic market has no own-index series, so the nowcast model cannot form a prediction and only the relative-value rule can act.
