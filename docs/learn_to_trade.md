# Learn to trade: a two-week practice plan

Practice only. Use a paper or simulator account, or a spreadsheet, never real
money. The aim is to learn the mechanics and the discipline on a strategy
with real (but unproven) evidence, then compare your results with the
system's.

## The strategy you will practise: SA2-M residual reversal

**Idea.** Each AI-infrastructure stock moves partly with the tech sector
(XLK) and partly on its own. When the part that is its own (the
"residual") stretches unusually far, it tends to snap back within days.
Avellaneda and Lee (2010) published this method, and quant desks use
versions of it.

**The s-score.** It measures how stretched a stock is against XLK, in
standard deviations.

- Below about −1.25: cheap, so buy the stock and short a matching amount of
  XLK.
- Above about +1.25: rich, so short the stock and buy XLK.
- Exit when the score comes back toward zero, or after 20 days.

**Why short XLK at the same time.** It removes the market's direction, so
you are betting only on the snap-back, not on tech going up. This is called
"hedging the beta".

**Evidence.**

- On held-out data (Feb–Oct 2026) it made 10.6 bps a day after realistic
  costs, Sharpe 1.8, Holm p 0.023.
- It is fragile: a few days carry the result, and it failed on large-cap
  tech.
- A 60-session live forward test is running and ends around late December.

## Daily routine (about 15 minutes)

1. **Evening, after the US close.**
   - Open `reports/statarb/practice/latest.md` on GitHub. The nightly run
     writes it.
   - It lists the positions to hold at the next open, with dollar amounts
     for a USD 10,000 practice account.
2. **Next morning, at the open (09:30 ET, 07:30 in Calgary).**
   - Adjust your paper positions to match the sheet: open new names, close
     dropped names, resize the rest.
3. **Journal every trade.** Use one line per trade with these columns:

   | Date | Symbol | Side | Shares | Price | Reason (s-score) | Planned exit | Fees assumed |
   |---|---|---|---|---|---|---|---|

4. **End of day.** Record the account value and one sentence on what
   surprised you.

## Weekly review (Sunday, 30 minutes)

- Your P&L against the system's: are they the same? If not, why? Possible
  reasons are fills, timing, missed trades and rounding shares.
- Your worst trade: was it a bad decision or a bad outcome?
- Your costs: about 15 bps per stock trade, each side, is assumed. Did your
  fills match that?

## Two-week concept plan (one idea a day)

| Day | Concept | Where it shows up |
|---|---|---|
| 1 | Long, short, P&L, a basis point | Every line of the sheet |
| 2 | Beta and hedging (why XLK is on the sheet) | The XLK line |
| 3 | Mean reversion vs momentum | The s-score |
| 4 | Position sizing (0.1 of capital per position) | The weights |
| 5 | Transaction costs and slippage | Your weekly review |
| 6 | Sharpe ratio and drawdown | `docs/statarb_results.md` |
| 7 | Overfitting, and why rules are written before testing | `docs/variants_log.md` |
| 8 | Statistical significance and multiple testing | Holm p-values |
| 9 | Futures basics: margin, settlement, contract months | `config/default.toml` [contracts] |
| 10 | Non-storable commodities: power and GPU-hours | `.claude/skills/nonstorable-futures` |
| 11 | Balance-of-month valuation | `reports/fair_value/sheet.md` |
| 12 | Risk premia and normal backwardation | `docs/carry_plan.md` |
| 13 | Basis risk | `docs/kalshi_results.md` section 5 |
| 14 | Writing your own pre-registered rule | `docs/spread_plan.md` as a template |

## A GPU exercise: forecast Ornn's H100 index each Friday

- **Each Friday.** Write your forecast for **next** Friday's Ornn H100 index
  value: a central number and a 90% range. Today's value is about USD 2.79;
  it moves about 3.4% a week.
- **The following week.** Check the settled value: Kalshi's KXH100WS
  settlement, or ask a session to read it from
  `var/kalshi/markets/KXH100WS.json`.
- **After 8 weeks, score yourself.**
  - Was the truth inside your range about 9 times in 10?
  - Were your central forecasts better than "no change"?
- **Why it matters.** This is the forecasting skill GPU1 needs, and it
  teaches calibration.

## Rules to keep

- Never trade real money on a strategy that hasn't passed its forward test.
- Decide position size before entering, never after.
- If you change a rule, write down why before you see the result.
