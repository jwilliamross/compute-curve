# Claim 6: statistical arbitrage on compute-linked equities (results)

_2026-10-10. Plan: docs/statarb_plan.md (commit c86c7ec, written before any
strategy return). Full tables: reports/statarb/exploration.md. Simulation only._

## Bottom line

**Neither strategy survived the exploration rules, so no strategy goes to
confirmation.** The confirmation set (2026-02-20 to 10-05) stays unspent.
This is a clean "no significant edge" after costs.

| | SA1 pairs (cointegration) | SA2 residual reversal vs XLK |
|---|---|---|
| Pooled net Sharpe (non-IID SE) | −1.55 (1.11) | +0.18 (0.80) |
| 95% bootstrap CI of the Sharpe | [−3.28, 1.20] | [−1.05, 1.25] |
| Mean daily net return, 95% CI | −2.8 bps [−8.9, 1.2] | +0.9 bps [−4.6, 6.4] |
| Deflated Sharpe (K = 21) | 0.03 | 0.07 |
| Break-even stock cost per side | negative (loses before costs) | 23 bps (assumed 15) |
| Mean at double costs | −3.5 bps a day | −1.6 bps a day |
| Max drawdown, 95th percentile (bootstrap) | 27% | 19% |
| Trades / sessions | 699 / 367 | 1,746 / 367 |
| Survives | no | no |

Costs are ASSUMPTIONS: 15 bps per side for stocks, 3 bps for XLK, a 1 bp
sell fee and 3% a year borrow. There are 21 grid cells; the project total is
256 variants.

## What the numbers say

**1. Pairs trading loses money here, even before costs.**

- In this universe, stocks that looked tied together over the formation
  window kept drifting apart.
- 2024 to 2026 was a period of strong, news-driven trends in AI stocks:
  earnings, contracts, capacity deals. A spread that widens on news does not
  come back.
- The surface is negative everywhere. The least bad cells use the longest
  lookback (250 sessions).

**2. Residual reversal has a little timing information, but no tradable
edge.**

- After costs it is about break-even: Sharpe +0.18, with an interval from −1
  to +1.25.
- The pooled region is all 12 cells. With 1.5 years of data the Sharpe
  standard error is about 0.8 to 1, so the whole surface sits inside one SE
  of its best cell. The parameter ranking is noise. This is exactly the case
  the quant-research skill warns about.
- **Random-entry Monte Carlo** (descriptive):
  - each trade keeps its stocks, direction and holding length, but is moved
    to a random date;
  - the real entry dates did better than 99.3% of 300 random-date versions
    before costs, and than all of them after costs.
  - So the s-score picks better-than-random moments to trade. The edge is
    just too small to beat costs and the 21-trial penalty: the deflated
    Sharpe is 0.07 against a required 0.90.
- **Caveat on that Monte Carlo.**
  - The frozen exploration report's null (1,000 paths, "1.000") could place
    random trades before a stock listed, which biases it downward.
  - A post-hoc diagnostic restricted placements to listed periods. It is
    logged as variant `statarb.null_valid`, and the conclusion held.
  - The code now always does this (D53).
- **Not a signal.** This is a lead about timing. Under the plan it cannot be
  traded, and it is not re-tuned on the same data.

## What would change the answer

- **Lower costs.** The break-even is 23 bps per side. Large liquid names
  (NVDA, AMD, AVGO, TSM, MU) trade far below 15 bps, but the small miners
  and power names do not. A pre-registered liquid-only version with measured
  spreads is a fair next test.
  - Even then it would need the confirmation set, and the confirmation set
    is short: 158 sessions.
- **More data.** With 1.5 years, only a Sharpe above about 2.5 can be told
  apart from zero. Every extra year narrows the interval by about a third.

## Disclosures

- **Survivorship and selection.** The universe was picked in 2026 for its AI
  exposure.
- **Earlier use of the returns.** Equity returns were used earlier, with
  GPU-price signals, in claims 4 and 5 and in H11/H12.
- **Pair weights.** Pairs use hedge-ratio weights, (1, β) scaled to the
  pair's gross. That is dollar-neutral only when β = 1. The plan said
  "dollar-neutral, hedge-ratio weighted", and only one of the two can hold;
  the Engle-Granger hedge ratio was used.
- **Rebalancing approximation.** Weights are target weights each session.
  Drift between rebalances is not charged as turnover, which is a small
  approximation.

## Claim 6b: residual reversal with measured costs (2026-10-11)

Plan: docs/statarb_plan2.md (commit a583c5d). Full tables:
reports/statarb/claim6b_exploration.md.

**Result: nothing survives, so the confirmation set is still unspent.**

| | SA2-M (all 20, measured costs) | SA2-L (10 lowest-spread names) |
|---|---|---|
| Pooled net Sharpe (SE) | −0.15 (0.81) | +0.21 (0.81) |
| 95% bootstrap CI of the Sharpe | [−1.41, 0.95] | [−1.07, 1.23] |
| Deflated Sharpe (K = 45) | 0.01 | 0.03 |
| Break-even, as a multiple of the measured costs | 0.8× | 1.4× |
| Random-entry Monte Carlo: share of null Sharpes below the real one | 1.00 | 0.98 |
| Max drawdown, 95th percentile (bootstrap) | 23% | 7% |

**The measured costs are unreliable, and too high for large caps.**

- The Corwin-Schultz estimator, applied to these daily bars, gives median
  spreads of 13 to 156 bps. NVDA's is 53 bps.
- NVDA's real quoted spread is about one cent on a share price near $180,
  under 1 bp.
- The estimator is known to overstate spreads for highly volatile stocks: it
  attributes part of the intraday range to the spread (Corwin and Schultz
  2012, section IV; Abdi and Ranaldo 2017, *Review of Financial Studies*).
- So claim 6b is a valid test, as pre-registered, but its costs are too
  harsh for the large caps.
- The timing signal again beats random entry, as in claim 6. Still, no cost
  assumption so far makes the pooled strategy pass the deflated Sharpe.

**What would settle it.** Costs from **real quoted spreads** (NBBO) instead
of an estimate, and one shot on the unspent confirmation set, with no
further exploration. See docs/statarb_plan3.md if written.

## Claim 6c: quoted-spread costs, one-shot confirmation (2026-10-11)

Plan: docs/statarb_plan3.md (commit 64c270c), written before any quote was
fetched and before any confirmation-set return. Report:
reports/statarb/claim6c_confirmation.md.

**Result: both strategies passed the pre-registered one-shot confirmation**
(sessions 2026-02-20 to 10-05, 157 sessions, never used before). This is
the first strategy in the project to pass a pre-registered out-of-sample
test.

| | SA2-M (all 20) | SA2-L (10 liquid) |
|---|---|---|
| Mean daily net return, 95% CI | 10.6 bps [3.0, 18.1] | 4.9 bps [−1.4, 10.8] |
| Annualized net Sharpe (SE), bootstrap CI | 1.80 (1.13), [0.53, 3.20] | 1.73 (1.16), [−0.46, 4.22] |
| One-sided Newey-West p, Holm | 0.011, **0.023** | 0.049, **0.049** |
| Mean at stress costs (2× costs, 10% borrow) | +7.4 bps | +3.6 bps |
| Trades | 1,194 | 365 |

**Measured quoted spreads.** Alpaca NBBO, sampled on the exploration set;
only the medians are stored (D29).

- Large caps: 0.75 bp (NVDA) to about 4 bps.
- Small miners and power names: 7 to 18 bps.
- TLN: 39 bps; WYFI: 55 bps.

Corwin-Schultz had overstated these by 10 to 70 times.

### Robustness (POST-HOC, descriptive; not part of the pre-registered test)

| Check | SA2-M | SA2-L |
|---|---|---|
| Gross vs net return | 12.1 vs 10.6 bps | 5.5 vs 4.9 bps |
| Without the 5 best days (of 157) | 1.1 bps, Sharpe 0.22 | 1.0 bps, Sharpe 0.39 |
| Long-stock trades / short-stock trades | +4.1 / +6.3 bps | +1.0 / +3.9 bps |
| Profitable months | 6 of 9 | 6 of 9 |
| Share of profit from the top 3 names | 63% (SMCI, CIFR, NBIS) | over 100% (SMCI, MU, TLN; VRT loses) |
| Correlation with XLK | 0.07 | −0.21 |

**Reading.**

- **The result is fragile.** The pre-registered test passed, but the profit
  comes from a few large reversals in a few volatile names. Without the five
  best days, little is left.
- **Both legs earn and market exposure is low.** That is consistent with
  real mean reversion, not a hidden market bet.
- **Ways it could be overstated:**
  - trading at the open, where spreads are wider than at the midday quotes
    sampled (market-on-open orders avoid the spread but face impact);
  - borrow costs for hard-to-borrow small names (WYFI, CIFR, WULF), which
    can exceed the 10% stress;
  - the universe chosen in 2026 for its AI exposure;
  - this being the third test of SA2. The confirmation set was used once,
    but the decision to try quoted costs followed two failures, and K = 45
    cells is counted.
- **Next.** The 60-session forward shadow test (plan section 6) runs
  automatically and evaluates when 60 sessions after 2026-10-06 exist
  (about the end of December). No orders are sent. Paper trading would need
  the owner's approval and a risk gate.

### Independent audit (2026-10-11, D56)

An agent reviewed the code adversarially. It reproduced the report exactly.

**Verified, with no issue found:**

- no look-ahead: truncation tests on real data gave zero mismatches;
- execution timing and P&L, costs (hand-checked to the basis point), the
  hedge sign, exits, pooling and the statistics;
- placebo with random trade signs: −0.25 ± 1.80 bps a day, against
  +12.8 real.

**One upward bias found:** constant-weight accounting, where rebalancing is
free.

| Under fixed shares | Mean | Holm p | Verdict |
|---|---|---|---|
| SA2-M | 10.36 bps a day | 0.020 | still passes |
| SA2-L | 4.66 bps a day | 0.058 | **fails** |

**Updated verdict.**

- **SA2-M:** confirmed, and robust to accounting, Newey-West lag (10 to 30)
  and 2× costs.
- **SA2-L:** borderline. Its p is above 0.05 at other lags, at 1.5× costs,
  and under fixed shares.
- **Forward test:** both strategies must now pass under both accountings
  (D56).

## Claim 6d: out-of-universe replication (2026-10-12)

Plan: docs/statarb_plan4.md (commit 200065d), written before any of these
stocks' data was fetched. Report: reports/statarb/claim6d.md.

**Result: frozen SA2-M does not replicate** on 20 large-cap US tech names
outside the universe (AAPL, MSFT, … PANW), over 2024-09-03 to 2026-10-05
(524 sessions, 2,741 trades), with quoted-spread costs.

| Accounting | Mean daily net | Sharpe (bootstrap CI) | One-sided p | At stress costs |
|---|---|---|---|---|
| Weights | −1.9 bps | −0.55 [−1.86, 0.72] | 0.80 | −3.4 bps |
| Fixed shares | −2.2 bps | −0.60 [−1.92, 0.61] | 0.82 | −3.7 bps |

**Reading, as fixed in the plan.** The edge, if real, is not a general
property of tech stocks. Two explanations fit:

- it is specific to the volatile, retail-heavy AI names of the original
  universe, which matches the profit's concentration in SMCI, CIFR and NBIS;
- the original result was partly luck.

This lowers confidence in SA2-M. The 60-session forward test on the
original universe stays the deciding test, and the paper-trading proposal
still requires it to pass.
