# Claim 10: modern strategies on the SA2 universe (plan)

_Written 2026-10-16, before any return of these strategies was computed. Simulation
and shadow only: none of them sends an order. The Alpaca paper account belongs to
SA2-M (D63)._

## 1. Why

SA2-M passed a one-shot confirmation, but its edge is concentrated in 2026. That
looks like regime risk (docs/statarb_paper_readiness.md §7). This plan tests four
recent, published ideas on the same 20 compute-linked stocks against XLK:

- two **overlays** that could make SA2-M more robust: volatility management and
  volume conditioning;
- two **new signal families**: statistical factors, and a walk-forward
  machine-learning forecast.

Each idea comes from a published paper. Every parameter is fixed below and none is
tuned.

## 2. Data, windows and costs (all fixed now)

**Data.**

- Universe: the claim-4 members plus XLK, using `[statarb]` eligibility
  (`min_history` 60 and member start dates).
- Daily Alpaca SIP bars, including volume, cached under `var/market_data` (D29).

**Windows.**

| Window | Dates |
|---|---|
| Exploration | `[statarb] explore`, 2024-09-03 to 2026-02-19 |
| Confirmation | `[statarb] confirm`, 2026-02-20 to 2026-10-05 |
| Forward shadow | The 60 sessions from **2026-10-19** (the first session after this plan) |

The forward shadow skips 2026-10-06 to 10-16, because those sessions were looked
at while explaining the paper book.

**The confirmation window is not blind.** SA2-M's confirmation used it, so we
already know reversal paid in 2026.

- For the overlays (MX1, MX2), the confirmation still tests something unseen:
  whether the overlay adds anything to SA2-M.
- For MX3 and MX4, a pass there is weaker evidence than SA2-M's pass was. **The
  forward shadow is the deciding test for every MX strategy.**

**Costs** (ASSUMPTIONS, as claim 6c):

- per side: half the median quoted spread plus 2 bps for each symbol
  (`reports/statarb/claim6c_spreads.json`);
- a 1 bp sell fee and 3% a year borrow;
- stress case: all costs ×2 and borrow at 10% a year.

**Engine.** `statarb.engine` with weights accounting:

- signals at the close of t;
- trades at the open of t+1;
- the SA2 sizing of 0.1 of capital per position, with max_positions 10 and
  max_hold 20.

## 3. Strategies

### MX1: volatility-managed SA2-M

Source: Moreira and Muir (2017), *J. Finance* 72(4); Barroso and Santa-Clara
(2015), *JFE* 116.

**Rule.**

- Start from the SA2-M pooled book (the 12 frozen cells, weights averaged as the
  paper account holds them).
- The weights held from the open of d are scaled by
  `c_d = clip(σ_target,d / σ_d, 0, 2)`.
  - σ_d is the standard deviation of the unmanaged book's net daily returns
    over the 20 sessions up to d−1.
  - σ_target,d is the standard deviation over every session up to d−1.
- Before 60 return observations exist, `c = 1`.
- Costs are charged on the scaled weights, so scaling turnover is paid.

**Test.**

- Moreira–Muir alpha: regress the managed returns on the unmanaged returns,
  `r_m = α + β r_u + e`.
- One-sided HAC p (lag 10) that α > 0.
- The managed mean must be > 0.

### MX2: volume-conditioned reversal (Medhat and Schmeling short-term momentum)

Source: Medhat and Schmeling (2022), *RFS* 35(3). Also Gervais, Kaniel and
Mingelgrin (2001), and Chan (2003).

**Abnormal volume.** `AV_t = mean(volume, t−4..t) / mean(volume, t−64..t−5)`.

**Classifying a move.** An SA2-M entry candidate at close t is:

- **quiet** if its AV_t is at or below the median AV_t over all eligible names
  that day;
- **loud** otherwise.

**Variants.**

- **MX2a, quiet reversal.** The SA2 rules (12 cells pooled), entering on quiet
  candidates only.
- **MX2b, loud momentum.** On loud candidates, trade in the opposite direction
  to SA2: short a name stretched low, long a name stretched high, beta-hedged
  with XLK. Hold for max_hold (20) sessions, with no s-score exit.

**Test.** For each variant, a one-sided HAC p that the pooled net mean is above 0.

### MX3: statistical-factor residual reversal (Avellaneda and Lee eigenportfolios)

Source: Avellaneda and Lee (2010), *Quantitative Finance* 10(7), §2.1.

**Signal.**

- s-scores are computed exactly as SA2 does, except the residual is taken
  against the top k principal components of the universe's standardized
  returns over the window (plus an intercept) instead of against XLK.
- Names with a gap in the window are left out of that window's PCA.

**Execution.** As SA2-M: the stock against β·XLK, with β from the XLK
regression.

**Variants.** k ∈ {1, 2, 3}, each pooled over the 12 SA2-M cells.

**Test.** A one-sided HAC p that the pooled net mean is above 0.

### MX4: walk-forward ridge forecast (machine learning, linear-penalised)

Source: Gu, Kelly and Xiu (2020), *RFS* 33(5). Ridge is their penalised linear
benchmark, and the only learner used here. Features include the overnight
residual of Lou, Polk and Skouras (2019), *JFE* 134.

**Residual.** `e_s = r_s − β_{s−1} m_s`, where β is the 60-session OLS slope on
XLK ending at s−1.

**Features.** Seven per name at close t, each cross-sectionally z-scored and
clipped to ±3:

1. e over the last 1 session;
2. e over the last 5 sessions;
3. e over the last 20 sessions;
4. the overnight residual summed over 20 sessions;
5. the 60-session s-score;
6. log AV_t;
7. log of the 20-session standard deviation of r.

**Target.** The cross-sectionally demeaned sum of e over t+1..t+5.

**Fit.**

- Ridge on all rows whose target ends at or before t (purged).
- λ = 0.1 × the number of training rows.
- Refit every 20 sessions.
- First forecast after 120 sessions of training rows.

**Book.**

- Each session with at least 8 eligible names: long the top 3 forecasts and
  short the bottom 3, each beta-hedged with XLK.
- Each tranche is held 5 sessions.
- Each position is 0.1/5 of capital, so five overlapping tranches give
  SA2-like gross.

**Baselines first.** The model is used only if it beats a naive forecast.

- Daily IC is the Spearman correlation of the forecast with the realized target.
- Test: a one-sided HAC p (lag 5) that the mean daily IC difference, ridge minus
  the baseline (−1 × the 5-session residual alone), is above 0.

**Test.**

- The IC gate must pass.
- Then a one-sided HAC p that the net mean is above 0.

## 4. Decisions, fixed now

**Exploration screen (lenient).** A strategy goes to confirmation only if, on the
exploration window, all of these hold:

- its test p ≤ 0.20;
- its net mean > 0;
- effective N ≥ 30;
- for MX4, the IC gate p ≤ 0.20.

**Confirmation (one shot).** Applies to survivors only.

- **Correction:** Holm across the survivors' test p-values, α = 0.05.
- **Pass:**
  - C1: Holm p ≤ 0.05 and mean > 0;
  - C2: stress-case mean > 0;
  - MX4: the IC gate must also have p ≤ 0.05.
- **If it passes:** the forward shadow.
- **If it fails:** stop, and report the result.

**Forward shadow.** Starts after 60 sessions from 2026-10-19 (about mid-January
2027).

- Every MX strategy is logged nightly. Non-survivors are logged as descriptive
  only.
- The verdict counts for confirmed strategies only:
  - the same tests, one-sided α = 0.05;
  - Holm across the confirmed strategies;
  - stress mean > 0.

**Every result reports:** mean, Sharpe, block-bootstrap 95% CIs, the stress-case
mean, trade counts, and the costs used.

**If a strategy passes the forward shadow,** trading it with paper money needs:

- a second Alpaca paper account (one strategy per account, D63);
- an owner decision.

## 5. Variants

Eight are declared:

- MX1;
- MX2a and MX2b;
- MX3 with k = 1, 2 and 3;
- MX4, plus MX4's IC gate.

The nightly lab sheet is descriptive and adds none.

## 6. What could go wrong (written before the results)

- MX1 may simply cut exposure in the 2026 burst where SA2-M made its money. Nagel
  (2012, *RFS* 25(7)) argues that reversal pays more when volatility is high,
  which is the opposite timing.
- MX2's split uses volume as a proxy for news. Volume is not turnover, and loud
  moves in small AI names may be squeezes, not information.
- MX3's first factor may be "the AI trade". Removing it makes residuals cleaner
  but costs more trades.
- MX4 has about 20 names × 300 training sessions: little data for even a linear
  learner. A null result is the most likely outcome.
