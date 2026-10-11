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
