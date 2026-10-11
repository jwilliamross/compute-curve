# Claim 6c: residual reversal with quoted-spread costs, one-shot confirmation

Sessions 2026-02-20 to 2026-10-05, frozen pooled regions. Costs: per-symbol quoted-spread costs (table below; half the median NBBO spread + 2 bps slippage, ASSUMPTION), sell fee 1 bp, borrow 3%/yr on shorts. Stress: all costs x2, borrow 10%/yr. (Header corrected 2026-10-11: the generated line showed claim 6's flat costs, which were not used.)

## SA2-M

- Sessions / trades: 157 / 1194
- Mean daily net return 10.56 bps, 95% CI [3.01, 18.13] bps
- Annualized net Sharpe 1.80 (SE 1.13), bootstrap CI [0.53, 3.20]
- C1: one-sided Newey-West p 0.011, Holm 0.023: pass
- C2: mean at stress costs 7.35 bps: pass
- **Verdict: confirmed: forward shadow test next.**

## SA2-L

- Sessions / trades: 157 / 365
- Mean daily net return 4.93 bps, 95% CI [-1.39, 10.81] bps
- Annualized net Sharpe 1.73 (SE 1.16), bootstrap CI [-0.46, 4.22]
- C1: one-sided Newey-West p 0.049, Holm 0.049: pass
- C2: mean at stress costs 3.56 bps: pass
- **Verdict: confirmed: forward shadow test next.**


## Quoted spreads (Alpaca NBBO, sampled exploration sessions)

Per-side cost = half the median quoted spread + 2 bps (ASSUMPTION).

| Symbol | Median quoted spread (bps) | Per-side cost (bps) |
|---|---|---|
| NVDA | 0.75 | 2.38 |
| XLK | 0.85 | 2.43 |
| AMD | 2.06 | 3.03 |
| MU | 2.92 | 3.46 |
| TSM | 3.21 | 3.60 |
| MRVL | 3.50 | 3.75 |
| AVGO | 3.84 | 3.92 |
| SMCI | 3.85 | 3.93 |
| CORZ | 7.50 | 5.75 |
| VRT | 9.65 | 6.82 |
| IREN | 9.74 | 6.87 |
| CRWV | 10.55 | 7.28 |
| BE | 10.99 | 7.49 |
| VST | 11.36 | 7.68 |
| APLD | 11.83 | 7.92 |
| NBIS | 12.97 | 8.48 |
| CIFR | 16.60 | 10.30 |
| CEG | 17.56 | 10.78 |
| WULF | 18.40 | 11.20 |
| TLN | 39.26 | 21.63 |
| WYFI | 55.10 | 29.55 |
