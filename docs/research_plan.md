# Research plan

Pre-registered on 2026-10-05, before any test result existed. Changing a
primary metric, baseline or threshold after seeing results counts as a new
variant and must be logged in `docs/variants_log.md` and
`src/compute_curve/backtest/variants.py`.

## Setting

GPU1 and GPU2 are cash-settled monthly futures on the business-day average
of Silicon Data's US-geography H100 and B200 on-demand rental indices
(docs/contract_specs.md). On 2026-10-05 they are **not trading**: the CFTC
extended its review to 2026-11-09. No futures history exists, and the
settlement index's history is paid and may not be stored without a licence.

## Notation

- `I_d`: settlement index value on business day `d`.
- `F_M = mean(I_d for business days d in month M)`: final settlement of
  contract month `M`.
- `P_t(M)`: futures settlement price of month `M` on trade date `t`.
- `J_d`: our own index (docs/index_methodology.md).
- Decision time: 23:59:59 UTC on day `t`. Inputs must carry
  `ts_available <= t`. Fills happen at the next settlement after `t`.

## Claim 1: nowcast edge

**Hypothesis H1.** Our independently collected listings predict `F_M` before
month-end better than naive forecasts.

| Item | Pre-registered choice |
|---|---|
| Model (primary) | `own_bridge`: known business days at published values; all unknown days at the latest published value scaled by the change in our fixed-panel index since that value's date. No fitted parameters |
| Baselines | `mtd_carry` (month-to-date mean carried forward, from the brief) and `last_value` (unknown days at the latest published value). The model must beat the **stronger** of the two |
| Decision points | every calendar day from 5 days before month start to the day before the last business day |
| Loss | squared log error, `(ln pred - ln F_M)^2` |
| Test | mean paired loss difference, model minus stronger baseline; 95% CI from a bootstrap that resamples whole months |
| Validation (signal may trade) | at least 6 complete months and the CI upper bound below 0 |
| Economic check | the median absolute improvement must exceed the round-trip cost in USD/GPU-hour (about 0.16 at default costs), or the signal is not tradable even if valid |
| **Kill criterion** | after 12 complete months: CI upper bound at or above 0, so H1 is rejected. Also rejected if our index's daily changes are uncorrelated with the settlement index's (correlation CI includes 0) |
| Data needed | daily settlement-configuration index values (licensed) overlapping our index |
| Earliest test | our fixed-panel index starts 2026-08-18, so the first complete month is September 2026. With licensed history in hand, 6 months are available in early March 2027 |

Supporting diagnostic, not a pass/fail test: tracking error of `J` against
`I` (mean log error, RMSE, correlation of daily changes, each with a block
bootstrap CI).

## Claim 2: model edge

**Hypothesis H2.** A Schwartz-Smith two-factor model of log price, extended
with a deterministic depreciation drift and a scheduled jump at each hardware
launch window and estimated by Kalman filter (docs/term_structure_model.md),
forecasts final settlements better than the market's own futures prices.

| Item | Pre-registered choice |
|---|---|
| Model (primary) | `ss.panel`: walk-forward maximum likelihood on the futures panel (months not yet in their averaging period), re-estimated monthly with an expanding window |
| Forecast | real-world expected `F_M` from the filtered state, for horizons of 1 to 6 months |
| Baselines | (a) the futures settlement `P_t(M)` itself; (b) random walk: the latest index value for every month. The model must beat **both** |
| Loss | squared log error against realized `F_M`, per horizon and pooled |
| Test | paired loss difference with a block bootstrap 95% CI (blocks of one contract month) |
| Validation | at least 12 realized monthly settlements per horizon bucket and the pooled CI upper bound below 0 against both baselines |
| **Kill criterion** | after 24 realized settlements: no CI below 0 against the futures price, so H2 is rejected. The extensions (depreciation, jumps) are dropped if the plain two-factor model does at least as well (likelihood-ratio and out-of-sample loss) |
| Data needed | GPU1/GPU2 daily settlements with realized finals; the settlement index for the current-month nowcast |
| Earliest test | listing no earlier than November 2026; 12 realized finals by about end-2027 |

Spot-only fits on our own index are descriptive. Simulation shows the long-run
factor is weakly identified from spot data alone (docs/term_structure_model.md),
so no spot-only fit is used for trading.

## Claim 3: survivability

**Hypothesis H3.** Strategies built only from validated signals earn more than
realistic trading costs at small size with hard loss limits.

| Item | Pre-registered choice |
|---|---|
| Strategies | `strategy.nowcast_front` (trade the front month when the nowcast edge exceeds 2x round-trip cost) and `strategy.rv_fade` (fade the performance-normalized B200/H100 spread at abs(z) > 2) |
| Gate | a strategy runs in shadow mode until its signal is validated under H1 or H4 |
| Costs | 5 ticks half-spread and 2 ticks slippage per side, exchange fee USD 5.50 plus USD 2.50 broker per side, USD 1.35 cash-settlement fee |
| Limits | 5 contracts per month, 10 gross, USD 2,000 daily loss halt, USD 7,500 drawdown kill, on USD 100,000 |
| Metrics | net PnL, Sharpe with block-bootstrap 95% CI, max drawdown, turnover, capacity at 5% of average daily volume |
| Multiple testing | two strategies, so each uses a 97.5% CI (Bonferroni) |
| **Kill criterion** | after 12 months of forward paper trading or a 12-month real-data backtest: Sharpe CI lower bound at or below 0, **or** net PnL at or below 0 at 2x costs, **or** capacity below 1 contract per day. Any of these rejects H3 for that strategy |
| Earliest test | 12 months after listing |

## Relative value (supports claim 3)

**Hypothesis H4.** The performance-normalized log spread
`s = ln P_B200 - ln r - ln P_H100` mean-reverts: walk-forward AR(1)
forecasts of the 5-day change beat the random walk.

- Precursor test on our fixed-panel index: needs at least 120 days.
- Tradable test on second-month futures: needs at least 250 trade days.
- **Kill criterion:** CI of the loss difference not below 0 after 250 futures
  trade days.
- `r` is an assumption: 2.5 central, 1.8 to 3.0 range (docs/relative_value.md).
  Conclusions must hold across the range.

## What is testable on 2026-10-05

Nothing in H1 to H4. The engine, the models and the data pipeline are
validated on labelled synthetic data only. Real data supports descriptive
statements only (reports/evaluation.md).
