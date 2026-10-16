# Claim 9 results: Kalshi GPU price binaries (2026-10-16)

Plan: docs/kalshi_plan.md, committed before any price was read
(commit c8af24a). Data: Kalshi's public API, raw in `var/kalshi/` (D62).
Source indices: Ornn's GPU compute price indices, not Silicon Data's.

- **Costs.** Kalshi taker fee, rounded up to the cent.
- **Stress.** 2× fee plus 1 cent.
- **Variants.** 3, for a project total of 333.

## 1. KB-1R retrospective: too little history to conclude

- **Coverage.** 526 finalized markets across 8 series (August to October
  2026). Only 118 had a two-sided quote two days before close; the rest had
  no bid or no ask.
- **Trades.** 37 qualified, over 9 close dates. The pre-registered minimum
  is 10, so **no test was run**.
- **Descriptive only, not a result:**

  | Side | Trades | Mean P&L per contract | Hit rate | Mean price |
  |---|---|---|---|---|
  | NO on longshots (YES bid 3–20¢) | 25 | −4.8¢ | 0.88 | 91.7¢ |
  | YES on favourites (YES ask 80–97¢) | 12 | +8.8¢ | 1.00 | 90.1¢ |
  | **All** | 37 | −0.4¢ | – | – |

- **Total.** −USD 0.14 at normal costs and −USD 0.92 at stress costs. Three
  long shots came in, and each cost about 92¢.

## 2. KB-2 calibration (descriptive)

- **Scores.** 118 quotes; Brier 0.082, against 0.25 for a coin. Logit slope
  1.57 (SE 0.30).
  - A slope above 1 means prices sit too close to 50%: an under-confident
    market. That is the favourite-longshot pattern.
  - It is about 1.9 SEs from 1, which is suggestive, not conclusive.
- **Reliability.**
  - Mid prices under 10¢: 0 of 31 paid.
  - 10–20¢: 1 of 11 paid.
  - Over 80¢: 38 of 38 paid.

## 3. The implied forward curve today (descriptive)

**Method.** From active monthly-average markets, the strike where the YES
mid crosses 0.5 is the implied median of the monthly average. Snapshot of
2026-10-16.

| Month | H100 | B200 | H200 | Median bid-ask spread (H100) |
|---|---|---|---|---|
| 2026-10 | 2.88 | 7.74 | 6.00 | 5¢ |
| 2026-11 | 3.13 | 7.91 | 6.30 | 38¢ |
| 2026-12 | 3.46 | 8.92 | 5.89 | 52¢ |

- **Shape.** Kalshi's H100 and B200 curves slope **up** (contango) over the
  next three months.
- **Thin markets.** From 2027 on, the markets have no real quotes (bid 0, ask
  about 1), so they say nothing.
- **The contrast with Silicon Data.** Silicon Data's own forward curves are
  reported to be in **backwardation** (Crypto Briefing, 2026-10-15). The two
  sources disagree about the near-term direction of compute prices.
  - Part of that is the index: Ornn uses live spot transactions, Silicon
    Data neo-cloud rental rates.
  - Part is thin liquidity.

## 4. What happens next

- **KB-1F (forward confirmation).** Runs nightly (`compute-curve kalshi`)
  and evaluates once at 30 close dates or on 2027-04-01.
  - At about 4 weekly events a week, that is around early 2027.
- **Liquidity is the binding constraint.** Most markets had no two-sided
  quote two days before close.
  - A strategy here would be small, a few dollars per event.
  - Its value is as a rehearsal for GPU1/GPU2: the same kind of underlying,
    a monthly-average settlement and a real order book.
