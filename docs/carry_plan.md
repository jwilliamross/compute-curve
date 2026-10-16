# FP-D plan: long the backwardation (hedging-pressure carry) on GPU1/GPU2

Pre-registered 2026-10-16, before GPU1/GPU2 list. No futures prices and no
Silicon Data history are held. Research and simulation only.

## 1. Thesis

- **Normal backwardation.** Keynes (1930) and Hicks (1939) argued that
  producers hedge by selling forward. Speculators who take the long side
  must be paid a risk premium, so futures sit below the expected future spot
  price. de Roon, Nijman & Veld (2000, *Journal of Finance* 55(3)) find that
  hedging pressure explains futures risk premia across commodities.
- **Who hedges in GPU compute.**
  - Natural shorts: neoclouds and other GPU owners, carrying
    debt-financed fleets and wanting to lock in rental revenue.
  - Natural longs: AI labs, which mostly buy on multi-year contracts and
    have less need for monthly futures.
  - If the shorts dominate, GPU1/GPU2 futures should trade below the
    expected monthly average.
- **Evidence so far (descriptive, exploratory, list prices).** On
  per-provider GetDeploying history, 2024-08 to 2026-10:
  - the provider-median H100 price trended +3.0% a year (95% block-bootstrap
    CI −0.9% to +6.3%);
  - B200 +13% a year (CI +0.9% to +28%);
  - H200 +25% a year;
  - no B200 provider in the sample cut its list price.
- **The market's view.** Silicon Data's forward curves are reported to be in
  backwardation (Crypto Briefing, 2026-10-15): they price declines that list
  prices have not shown.
- **Against this.**
  - Kalshi's near-term Ornn-index curves slope up
    (docs/kalshi_results.md).
  - Silicon Data's index is transaction-based and sits below list prices
    (2.81 against our 3.5).
  - Past list-price drift may not carry over to the settlement index.

## 2. Rules (fixed)

- **Decision day.** The first business day of each month.
- **Contract.** M3, the contract month three months after the decision
  month.
- **FP-D-I (index-based, needs licensed SD history).**
  - I is the latest usable SD index value; F3 is the latest usable M3
    settlement.
  - Go long one contract of each product whose `ln(F3/I) < −0.05`.
  - Long only: the thesis is one-sided.
- **FP-D-F (futures only).** As FP-D-I, with I replaced by the front-month
  (M1) settlement.
- **Holding and P&L.**
  - Hold to final settlement.
  - P&L: `(S3 − F3) · 730 − leg_cost`, with claim 7's costs and 2× stress.
- **Risk limits.** Within `config/default.toml`. There are at most three
  open positions per product at once, since the holds overlap.

## 3. Test (one-shot)

- **Trigger.** 12 settled trades in a variant, or 2028-07-01.
- **Pass.** Mean net P&L > 0, one-sided Newey-West lag 2 (holds overlap by
  two decisions), Holm over FP-D-I and FP-D-F, α = 0.05. The mean must also
  stay > 0 at 2× costs.
- **Descriptive alongside.** The average realised premium
  `ln(S3/F3)` over every decision day, traded or not.

## 4. Variants

FP-D-I, FP-D-F and the drift descriptive (computed before this plan, on list
prices): 3 variants. Project total 336.
