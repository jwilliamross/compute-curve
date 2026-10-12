# Claim 6d: out-of-universe replication of frozen SA2-M (plan)

_Written 2026-10-11, before any price, quote or return of these stocks was
fetched. Simulation only._

## 1. Why

SA2-M passed a one-shot confirmation (claim 6c; audited, D56). Two worries
remain:

- the universe was chosen in 2026 for its AI exposure;
- the signal was found on the third attempt.

A strong check is to apply the **frozen** strategy, unchanged, to stocks it
has never seen.

## 2. Universe B (fixed now, not chosen from any return)

These are 20 large, liquid US technology and semiconductor stocks, none of
which is in the claim-4 universe. The list was written from general
knowledge of large-cap US tech, before any of their data was looked at:

AAPL, MSFT, ORCL, CRM, ADBE, CSCO, INTC, QCOM, TXN, AMAT, LRCX, KLAC, ADI,
NXPI, ON, MCHP, IBM, NOW, INTU, PANW.

The hedge is XLK, as before.

**Grouping.** SA2 does not use groups, so there is one group.

**Membership.** As in claim 6: a name trades only after 60 sessions of its
own history.

## 3. Test (one shot)

- **Strategy.** SA2-M frozen: all 12 cells, W ∈ {40, 60, 90} ×
  e ∈ {1.0, 1.25, 1.5, 2.0}, pooled equally. Every other rule is claim 6's
  SA2.
- **Costs.** Measured exactly as in claim 6c, from the median quoted NBBO
  spread on the same sampled sessions and times (docs/statarb_plan3.md,
  section 2). Per side, half the spread plus 2 bps, a 1 bp sell fee and 3% a
  year borrow. Stress: 2× costs and 10% a year borrow.
- **Window.** All sessions from 2024-09-03 to 2026-10-05. Entries start once
  a name has 60 sessions; P&L counts from the first session.
- **Accounting.** Both engine weights and fixed shares (D56).
- **Criteria.**
  - C1: one-sided Newey-West p (lag 10) ≤ 0.05 under **both** accountings.
  - C2: the mean is still above 0 at stress costs under both.
  - Replicates = C1 and C2.

## 4. Reading, fixed now

**If it replicates.** The edge is not specific to the AI names chosen. That
strengthens SA2-M.

**If it fails, it is consistent with either of two explanations:**

- the edge is specific to volatile, retail-heavy AI names;
- the original result was partly luck.

It does **not** cancel the pending forward test of SA2-M, which stays the
deciding test for the original universe.

## 5. Variants

- 1 replication test;
- 1 descriptive quote measurement.

The project total rises from 293 to 295.
