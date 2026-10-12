# Claim 6d: frozen SA2-M on out-of-universe stocks (universe B), one shot

Sessions 2024-09-03 to 2026-10-05, frozen pooled regions. Costs: per-symbol quoted-spread costs (half the median NBBO spread + 2 bps slippage, ASSUMPTION; reports/statarb/claim6d_spreads.json), sell fee 1 bp, borrow 3%/yr on shorts. Stress: all costs x2, borrow 10%/yr.

## SA2-M on universe B (weights)

- Sessions / trades: 524 / 2741
- Mean daily net return -1.91 bps, 95% CI [-6.78, 2.34] bps
- Annualized net Sharpe -0.55 (SE 0.67), bootstrap CI [-1.86, 0.72]
- C1: one-sided Newey-West p 0.799, Holm 0.799: fail
- C2: mean at stress costs -3.38 bps: fail
- **Verdict: does not replicate.**

## SA2-M on universe B (shares)

- Sessions / trades: 524 / 2741
- Mean daily net return -2.18 bps, 95% CI [-7.25, 2.06] bps
- Annualized net Sharpe -0.60 (SE 0.68), bootstrap CI [-1.92, 0.61]
- C1: one-sided Newey-West p 0.822, Holm 0.822: fail
- C2: mean at stress costs -3.69 bps: fail
- **Verdict: does not replicate.**


## Quoted spreads, universe B (Alpaca NBBO, sampled sessions)

| Symbol | Median quoted spread (bps) |
|---|---|
| XLK | 0.85 |
| AAPL | 1.00 |
| MSFT | 1.54 |
| CSCO | 1.58 |
| LRCX | 3.91 |
| MCHP | 4.13 |
| ORCL | 4.15 |
| QCOM | 4.23 |
| ON | 4.47 |
| INTC | 4.50 |
| CRM | 5.15 |
| IBM | 5.38 |
| ADBE | 5.77 |
| TXN | 5.99 |
| AMAT | 6.25 |
| PANW | 6.67 |
| ADI | 9.02 |
| INTU | 10.96 |
| NXPI | 11.23 |
| NOW | 13.24 |
| KLAC | 17.18 |
