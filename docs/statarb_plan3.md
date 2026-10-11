# Claim 6c: residual reversal with quoted-spread costs, straight to confirmation (plan)

_Written 2026-10-11, before any quote was fetched and before any return on
the confirmation set was computed. This is the **last** test of the SA2
residual-reversal signal. Whatever it shows, SA2 is not tuned again on
these data._

## 1. Why

Claim 6b's Corwin-Schultz costs overstate large-cap spreads by an order of
magnitude: NVDA came out at 53 bps, against about 1 bp quoted. Claim 6c
measures costs from real quotes instead and goes straight to the one-shot
confirmation. There is no new exploration and no screen. The exploration set
is already well known for SA2, and screening it again would only fit it.

## 2. Costs (fixed now)

**Quoted spreads.** From Alpaca's historical NBBO quotes (SIP feed). This is
market data under D29: it is never committed, and only the per-symbol medians
are stored.

- **Sampled sessions.** Every 18th session of the exploration set,
  2024-09-03 to 2026-02-19, starting with the first.
- **Sampled times.** 10:00, 12:00, 14:00 and 15:30 New York time.
- **Spread at a sample point.** The first valid quote (bid > 0, ask > bid)
  in the 2-second window starting at that time:
  spread = (ask − bid) / mid.
- **A stock's spread.** The median over all its sample points.

**Cost per side.** Half the median quoted spread, plus 2 bps for slippage and
impact (ASSUMPTION), plus claim 6's 1 bp sell fee and 3% a year borrow. XLK
is measured the same way.

**Stress (C2).** All costs doubled, with 10% a year borrow.

## 3. Frozen strategies (from claim 6b, reports/statarb/claim6b_exploration.md)

| ID | Universe | Pooled region (W, entry) |
|---|---|---|
| SA2-M | all 20 stocks | all 12 cells: W ∈ {40, 60, 90} × e ∈ {1.0, 1.25, 1.5, 2.0} |
| SA2-L | MU, TSM, VRT, AMD, CRWV, AVGO, SMCI, NVDA, TLN, VST (claim 6b's frozen list) | W ∈ {60, 90} × e ∈ {1.0, 1.25, 1.5, 2.0}, 8 cells |

All other rules are claim 6's SA2, unchanged.

## 4. Confirmation (one shot)

- **Set.** Sessions 2026-02-20 to 10-05, unspent.
- **C1.** A one-sided Newey-West p (lag 10) of the mean daily net return,
  Holm-adjusted over the 2 strategies, of at most 0.05.
- **C2.** The mean is still above 0 at stress costs.
- **Confirmed.** C1 and C2. A confirmed strategy goes to a 60-session
  shadow test with no orders.
- **Power.** About 158 sessions, so only a net Sharpe above about 2.5 is
  likely to confirm.

## 5. Variants

- 2 confirmation tests;
- 1 descriptive spread measurement.

The project total rises from 289 to 292.

## 6. Addendum (2026-10-11, after the confirmation): the forward shadow test

Both strategies confirmed (docs/statarb_results.md, section "Claim 6c").
As section 4 says, they now run a 60-session forward shadow test. It is
fixed now, before any forward session's return was computed.

- **Window.** The first 60 sessions on or after 2026-10-06; positions are
  opened only from then. The window is truncated at its 60th session before
  anything is computed.
- **Frozen inputs.** Strategies, regions and costs as in sections 2 and 3:
  - the quoted-spread medians in `reports/statarb/claim6c_spreads.json`;
  - the strategy code as of the commit that adds this addendum.
- **Criteria.** C1 and C2 as in section 4, with Holm over the 2 strategies.
- **Run.** Daily in the workflow (`statarb forward`). The step fetches bars
  through the previous session and reports the session count. It evaluates
  once, when 60 sessions exist. No order is sent at any point.
- **Outcome.**
  - **Pass.** Paper trading would still need the owner's explicit approval
    and a claim-4-style risk gate.
  - **Fail.** The signal is reported as not robust out of sample.
- **Variants.** One forward test, `statarb.forward`, already declared. The
  project total is unchanged.

## 7. Addendum (2026-10-11): stricter forward criterion (D56)

After an independent audit, the forward test requires each strategy to pass
C1 and C2 under **both** accountings:

- the engine's constant weights;
- fixed shares (`run_book_shares`).

Holm is applied within each accounting. This only makes the test stricter.
It was fixed before any forward-session statistic was computed.
