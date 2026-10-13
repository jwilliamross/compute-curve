# Round 6: trading-relevant tests on archived list prices (plan)

_Written 2026-10-13 and committed before any statistic below was computed.
Owner request: "model that data, test previous theories on it, find new
algorithms, I need a profitable trading model". Simulation and research
only. No orders._

## 0. What had been seen before this plan

- The verified archive rows (D58).
- The latest captures per provider, checked against the live collectors.
- The Verda pilot rows.
- The yearly median H100 on-demand list price per provider
  (docs/exploration_round5.md).
- Round 5's two statistics.
- Coverage counts by GPU, term and year.

**Not computed before this plan:**

- any monthly change series;
- any B200/H100 ratio;
- any relation to stock returns;
- any autocorrelation.

## 1. Data (frozen)

- **Prices.** Month-end prices are built exactly as in round 5:
  - the median verified on-demand per-GPU price per capture;
  - the latest capture at most 92 days old;
  - providers lambda, coreweave, nebius, hyperstack and verda.
- **GPUs.** H100, and B200 for R6-01.
- **Stocks.** Daily closes from the cached Alpaca bars, as used by claim 6.
  - Month-end close = the last session of the month.
  - Universe: the claim-4 universe, 21 names, equally weighted over the
    names with both month-end closes.
  - Benchmark: XLK.
  - Stock months: 2024-09 to 2026-09.
- **Spot prices are not used.** They exist only in 2026 (coverage count),
  too short for any test.

## 2. Tests

All are one-sided. Holm is applied over the three tests at 5%.

| ID | Question | Predictor at month-end m | Outcome | Expected sign | Inference |
|---|---|---|---|---|---|
| R6-01 | **GPU1/GPU2 relative value:** does the B200/H100 price ratio mean-revert? | `d(m) = L(m) − mean(L(k), k < m)`, where `L(m) = median_p ln(B200_p/H100_p)` over providers with both; at least 3 prior months | `L(m+3) − L(m)` | negative | OLS slope, Newey-West lag 3 |
| R6-02 | **Rental prices → stocks:** does a rise in H100 list prices predict compute-stock outperformance next month? | `Δ ln median_p H100_p(m)`, from m−1 to m | equal-weight universe return minus XLK return over month m+1 | positive | OLS slope, Newey-West lag 1 |
| R6-03 | **Forecasting GPU1's underlying:** does last month's H100 price change predict the next month's better than a random walk? | walk-forward AR(1) on monthly `Δ ln median H100`, refit each month on data up to m, with at least 12 months before the first forecast | `Δ ln median H100(m+1)` | the model beats zero-change | Clark-West against the random walk |

**Minimum data.** Each test needs at least 10 usable observations, else it
is reported as "too little history to conclude".

**Honest power.** Very low.

- With about 24 monthly observations, only a correlation above about 0.45
  is likely to pass.
- R6-01 has about 15 months (B200 pages start in 2025).
- A pass would be a lead for a forward test, not a tradable model. A
  non-pass will be weak evidence.

**No look-ahead.**

- Prices at month-end m use captures with `ts_observed` at or before the
  end of m.
- Stock outcomes start after m.
- R6-03 refits using data up to m only.

## 3. Descriptive (no test)

- **D1. Volatility of list prices.** The annualised volatility of monthly
  log changes of the median H100 and B200 on-demand price.
- **D2. Price-change frequency.** The share of provider-months with any
  change in the month-end price.

These are for futures risk sizing (VaR) once GPU1/GPU2 list. They are not
findings.

## 4. Variants

+5 (3 tests and 2 descriptive). Project total 299 → 304.
