# Claim 13 results: does residual reversal pay only in volatile markets?

Plan: docs/regime_plan.md. One shot on universe B, 2019-01-02 to 2024-08-30 (never fetched before). Frozen SA2-M, weights accounting. Costs (ASSUMPTIONS): universe-B quoted spreads (claim 6d) + 2 bps, sell fee 1 bp, borrow 3%/yr.

| Sample | Days | High-vol days | Mean high (bps) | Mean low (bps) | Diff p (N13-1) | High mean p (N13-2) |
|---|---|---|---|---|---|---|
| Universe B 2019-24 (test) | 1392 | 658 | +1.19 | -0.35 | 0.215 | 0.217 |
| AI universe 2019-24 | 1392 | 658 | +0.91 | -4.36 | 0.041 | 0.317 |
| AI universe 2026 confirm window | 157 | 151 | +11.22 | -6.05 | 0.173 | 0.010 |

Holm p: N13-1 0.430, N13-2 0.430. **Verdict: fails.** Rows after the first are descriptive and contaminated (plan section 1).
