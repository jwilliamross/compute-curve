# Claim 1b: does the gap between our index and Silicon Data's predict Silicon Data's next move? (plan)

_Written 2026-10-13, before any Silicon Data history is held. Owner idea:
"if our index differs from Silicon Data's … use statistical arbitrage on the
gap". This extends claim 1 (docs/research_plan.md). Research only._

## 1. The economics, stated carefully

GPU1/GPU2 settle on Silicon Data's own numbers (the monthly average of
SD-H100 / SD-B200, US configuration, business days). They do not settle on a
"true" market price.

- **What does not pay.** Our index being closer to fair value earns nothing
  by itself. The futures pay Silicon Data's number even if that number is
  "wrong".
- **What can pay.** Our index must tell us where Silicon Data's index is
  going before the futures price does.

That happens if Silicon Data lags the market, which is plausible from its
methodology:

- a weighted mean of provider means;
- a basis adjustment recalibrated weekly;
- more providers, some slower to update.

Claim 1's `own_bridge` nowcast already uses our index's *changes*. This
plan adds two sharper questions:

- **GAP-1, lead-lag.** Do our index's last 5 business-day changes predict
  Silicon Data's next 5?
- **GAP-2, error correction.** Beyond that, when the log gap
  `g = ln J − ln I` is wider than usual, does Silicon Data's index move to
  close it? This is the "statistical arbitrage on the gap" idea. A
  persistent level gap (basis; e.g. 3.20 vs 2.81 on 2026-10-05) is
  removed by measuring the gap against its own past mean.

## 2. Data (frozen)

- **I.** Silicon Data `SDH100RT` / `SDB200RT` daily values, licensed (B7).
  - Format: `data/manual/published_index/`, git-ignored (D59).
  - Usable after the configured publication lag.
- **J.** Our `history_panel` index (`reports/own_index.csv`, rows with
  `meets_coverage = true`), which starts 2026-08-04.
- **Days.** Business days where both exist at decision time t.
- **Silicon Data breaks are excluded.** No observation's window may
  overlap ±5 business days of a known restatement or membership change:
  2025-12-04, 2026-04-06, 2026-07-15 and 2026-09-25, plus any later date
  Silicon Data announces. Those jumps come from methodology, not the market.

## 3. Tests (frozen)

For each GPU, at decision day t:

| Item | Definition |
|---|---|
| Target | `y = ln I(t+5) − ln I(t)` |
| `dJ` | `ln J(t) − ln J(t−5)` |
| `dI` | `ln I(t) − ln I(t−5)` |
| `dev` | `g(t) − mean(g over all prior days)`, needing at least 20 prior days |

**Models:**

- GAP-1: `y ~ dJ + dI`.
- GAP-2: `y ~ dJ + dI + dev`. Expected: `dev` positive, because a wider
  ours-above-Silicon-Data gap means Silicon Data rises.

**Fitting.** Walk-forward OLS. At t, the model is refit on rows whose target
was known by t (target day ≤ t). At least 40 rows are needed before the
first prediction.

**Baseline.** The random walk `y = 0`.

**Test.**

- Clark-West, one-sided, Newey-West lag 4 (5-day targets overlap).
- H100 and B200 predictions are pooled.
- Holm over GAP-1 and GAP-2 at 5%.
- It runs once, when at least 60 pooled out-of-sample predictions exist.

**Economic check (descriptive).** The out-of-sample mean absolute error
reduction, in USD per GPU-hour, against the futures round-trip cost (about
USD 0.16, claim 1). A pass that is smaller than the cost is not tradable.

## 4. What a pass would and would not mean

- **A pass:** our data carries information about Silicon Data's next week.
  It becomes an input to claim 1's nowcast and, once GPU1/GPU2 list, to a
  futures signal. It would then also be tested against the futures price
  itself (claim 2): the market may already know what we know.
- **A non-pass:** the gap is noise or methodology. Model futures on Silicon
  Data's own series with a random walk (rounds 5 and 6).

## 5. Variants

+2 (GAP-1 and GAP-2). Project total 307 → 309.
