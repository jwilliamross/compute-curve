# Claim 6c SA2-M: paper-trading readiness (proposal, not executed)

_2026-10-11. A proposal for the owner to approve or decline. Nothing here
sends an order. Paper trading may start only if **all** preconditions in
section 1 hold **and** the owner approves in writing (in this chat or an
issue). Alpaca's paper endpoint only (D30). Never a live endpoint or real
money._

## 1. Preconditions

1. **Forward test passes.** SA2-M passes C1 and C2 under **both**
   accountings, the engine's weights and fixed shares (D56), in either:
   - the 60-session forward shadow test (docs/statarb_plan3.md sections 6
     and 7), expected around the end of December 2026; or
   - the 250-session extension (D57), expected around 2027-10-01.

   The 60-session test has low power: about 0.28 even if the full edge
   persists (docs/statarb_forward_power.md). A fail there is likely even if
   the edge is real, so the extension decides in that case.
2. **Shortability check.** Every name traded short must be `shortable` and
   `easy_to_borrow` on Alpaca on the day of the trade.
   - On 2026-10-11 every universe name met this **except WYFI**, which is
     not shortable on Alpaca.
   - WYFI short trades are therefore skipped. WYFI may still be bought.
3. **Owner approval of the sizing and kill criteria below.**

## 2. Tradability effect (descriptive, confirmation set, fixed shares)

| Version | Mean daily net | Sharpe | One-sided p |
|---|---|---|---|
| SA2-M as tested | 10.36 bps | 1.80 | 0.010 |
| SA2-M without WYFI shorts (tradable on Alpaca) | 9.49 bps | 1.61 | 0.018 |

## 3. Sizing within the existing claim-4 risk limits

The limits in `[claim4.risk]` are:

- USD 10,000 per symbol;
- USD 20,000 gross;
- USD 1,000 daily loss limit;
- USD 3,000 maximum drawdown.

The pooled SA2-M book without WYFI shorts uses an average gross exposure of
0.92 per dollar of capital, at most 1.88. Its largest single-symbol weight
is 1.17, which is the netted XLK hedge.

| Item | Value |
|---|---|
| Capital that keeps every symbol within USD 10,000 (the binding limit) | **about USD 8,600** |
| Max drawdown, 95th / 99th percentile (10,000 block-bootstrap paths) | 8.5% / 10.1% → about USD 720 / 870 |
| 1% worst day / worst day seen | 1.85% / 2.53% → about USD 160 / 220 |
| Expected P&L at that size, **if the confirmation edge persisted** | about USD 8 a day |

**Kelly.** Full Kelly on the in-sample estimate is about 11× leverage. That
is not used: the estimate is noisy, and the binding limit is far below it.
The quant-research skill's rule applies: never size on the in-sample
estimate, and let the simulated tail set the cap.

## 4. Kill criteria (fixed before any paper trade)

Stop the strategy, close every position and report, if any of these happens:

1. **Drawdown.** It reaches USD 1,500. That is half the hard limit, and
   about twice the 95% bootstrap drawdown.
2. **Daily loss limit.** It is breached twice in 20 sessions.
3. **Underperformance.** After 60 paper sessions the cumulative net return
   is below zero.
4. **Data or execution fault.** Fills differ from the open price by more
   than 3× the assumed cost on more than 10% of orders. Or the borrow on any
   short is recalled.
5. **Owner request.** At any time.

## 5. Execution plan (to build only after approval)

- **Signal.** Decided at the close, from the same SA2 code and frozen
  regions.
- **Orders.** Market-on-open orders on Alpaca **paper**, sized as above.
- **Hedge.** XLK, netted.
- **Checks.** Before each order, `shortable` and `easy_to_borrow` are
  checked, and the claim-4 risk layer enforces the limits and the kill
  switch.
- **Logging.** Paper fills are logged against the model's expected fills to
  measure real costs.

## 6. Honest expectations

- **Fragile result.** The confirmation's profit came mostly from a few days
  and three volatile names. The edge may be smaller in the future, or gone.
- **Small at this size.** Even if the edge holds, the money is small: about
  USD 2,000 a year on about USD 8,600, before any decay. The aim of paper
  trading is to **measure real costs and fills**, not to make money.
