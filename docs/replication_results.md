# Claims 12 and 13: replications and the final candidate (results)

_Run once each on 2026-10-18. Plans: docs/replication_plan.md (commit d94aa39) and
docs/regime_plan.md (commit 148e3ce), each written before its data was fetched.
Tables: `reports/replication/claim12.md` and `claim13.md`. Simulation only: no orders._

## Bottom line

**Neither lead replicates on data it had never seen, so the final candidate is
FP-C, the GPU1/GPU2 balance-of-month rule.**

| Test | Data never used before | Result | Verdict |
|---|---|---|---|
| R12-A: frozen SA2-M, 2019–2024 | AI universe, 1,426 sessions | −1.65 bps/day (CI −4.44 to +1.08); Sharpe −0.42; stress −3.03 | **fails** |
| R12-B: rates → GPU rents, on AWS spot | AWS spot H100 and A100, 2024–26 | H100 slope −0.20 (corr −0.13); A100 +0.07; Holm p 0.72 / 0.44 | **fails** |
| N13: reversal pays when volatility is high (Nagel 2012) | Universe B large-cap tech, 2019–2024 | High-vol days +1.19 bps against −0.35 on low; Holm p 0.43 | **fails** |

**Costs** (ASSUMPTIONS):

- per symbol, half the median quoted spread plus 2 bps;
- a 1 bp sell fee and 3% a year borrow;
- stress case: costs ×2 and borrow at 10% a year.

Ranges are 95% block-bootstrap intervals.

## 1. SA2-M is a regime bet, not a lasting edge

**By year** (weights accounting, descriptive):

| | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 (to Aug) | 2026 confirmation |
|---|---|---|---|---|---|---|---|
| bps/day | −2.6 | +0.5 | −1.5 | +3.6 | −5.8 | −5.3 | +11.2 |

- **Five of six earlier years lost money.** The 2026 result (Sharpe 1.8) is the
  exception, not the rule.
- **The volatility explanation fits the direction but is not proven.**
  - In every sample, volatile days beat calm days:
    - universe B: +1.2 against −0.4 bps;
    - AI universe 2019–24: +0.9 against −4.4;
    - 2026: +11.2 against −6.1.
  - 151 of the 157 sessions in 2026 were in the high-volatility regime.
  - But the clean test (universe B) is not significant. The other rows were
    contaminated before testing.
- **Consequences, as fixed in the plans:**
  - SA2-M stays a regime bet with no identified regime signal.
  - No further SA2 variant is tested on historical data. Every SA2 question is
    now forward-only.
  - The paper account keeps running with its kill switches. It is fake money
    and still informative, but its size is never increased.

## 2. The rates effect does not carry over to AWS spot

- On AWS spot auctions the H100 slope has the wrong sign. A100 is positive but
  far from significant.
- **What it does not show.** AWS spot is a different market, with fewer usable
  weeks (72), so this does not kill the claim-11 result on list prices.
- **What it does show.** One year of one dataset is not enough to build on.
  - FP-M (the rates filter) is **dropped**, per the plan.
  - MD-4F (the forward check on our own index) still runs and reports in
    October 2027.

## 3. The final candidate: FP-C, balance of month (docs/bom_plan.md)

**The rule.**

- Mid-month, compare the GPU1 (or GPU2) current-month futures price with its fair
  value:

      fair value = (days done × realised average + days left × today's index)
                   ÷ days in the month

- Trade when the gap exceeds the band: twice the per-leg cost, plus one standard
  deviation of the unknown remainder.

**Why it is the final candidate:**

1. **It rests on an accounting identity, not a statistical pattern.** Half the
   settlement is known by mid-month. Nothing here can be over-fit to history,
   which is exactly what sank SA2-M.
2. **The risk is small and computable.** The unknown part's standard deviation
   follows from the index's daily volatility (`bom.rw_average_sd`). H100's
   monthly average has stayed within 0.23% of its first-Monday value (median).
3. **It is fast to confirm.** If a new, thin contract misprices the known part by
   about 4%, about 9 trades confirm it (strategy book §2).
4. **It is the textbook trade for this market.** Power desks trade balance of
   month on monthly-average electricity contracts.

**What it still needs (owner actions):**

- **The contracts must list** (CFTC review to about 2026-11-09). Then, each day,
  drop CME settlements into `data/manual/cme_settlements/`.
- **Silicon Data's daily index** (SDH100RT, SDB200RT). It is the settlement
  index; Bloomberg or LSEG through SMU (B7) is the route.
- **Until then,** FP-C runs nightly in shadow mode and logs "waiting".

**The other GPU rules** (FP-D, FP-A/B, SP, FP-K) also stay in shadow. They are
second-tier because their edges are risk premia or relative value, the kind of
statistical effect that has not survived replication here.

## 4. Variants

- **Claim 12:** 4 (R12-A, R12-B for H100 and A100, per-year descriptive).
- **Claim 13:** 3 (N13-1, N13-2, descriptive).
- **Project total: 374.**
