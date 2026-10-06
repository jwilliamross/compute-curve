# Claim 4 pre-registration: do GPU rental prices lead compute-linked equities?

**Pre-registered on 2026-10-06, before any test-window return was seen.**
No return of a universe stock or of the benchmark over the test window had
been fetched or computed when this file was committed. The commit that adds
this file timestamps the plan. Two things had been looked at:

- **Signal side.** Our own index series, its timing, and how often each
  signal changes.
- **Pre-sample liquidity.** Pass or fail only, over June and July 2026,
  which is before the test window starts.

After results exist, any change to a choice below counts as a new variant.
It must be logged in `docs/variants_log.md` and
`src/compute_curve/backtest/variants.py` with its date and reason. The
config values that implement this plan live in `config/default.toml` under
`[claim4]`.

## 0. Bottom line, fixed before any result

There is far too little history to confirm or reject claim 4.

- 32 sessions have a clean signal and a known next-day outcome (2026-08-20
  to 2026-10-05).
- The H100 level signal changed on only 5 of them, and there are 4 large
  index moves in total.
- With 32 observations, the smallest correlation that can be detected with
  80% power at the 5% level is about 0.48. After the multiple-testing
  correction it is about 0.61.
- Realistic predictive correlations for daily equity returns are 0.1 or
  less. Detecting those would need roughly 3 to 6 years of sessions.

The tests below are still run, reported and logged, because the owner asked
for them and they set up the record that later evaluations extend. The
validation gate cannot pass on today's data: it requires at least 120
out-of-sample forecasts (G4). Paper trading therefore starts in **shadow
mode**.

## 1. Hypothesis

**H5 (claim 4).** Changes in our own H100 and B200 rental index predict the
subsequent return of a basket of compute-linked US equities relative to a
broad technology ETF. The changes are in three things: the index level, the
dispersion of provider prices, and listing availability.

- **Null.** For every signal and horizon, the predictive slope is zero.
- **Direction.** Two-sided. Rising rental prices could signal strong
  demand, which is good for GPU sellers and makers. They could also signal
  scarce supply, which is ambiguous for buyers of capacity. No prior is
  strong enough for a one-sided test.

## 2. Universe

### Rule

A stock is in the universe if it meets all five conditions below on
2026-10-06.

**R1. Listing.** A US-listed common stock or ADR on NYSE or Nasdaq. Alpaca
must show the asset as active and tradable.

**R2. Business dependence on GPU compute.** The company falls in one of
three categories, judged from its own public description of its business:

1. **Neocloud.** It owns GPUs and sells GPU compute (GPU-hours or GPU
   clusters) to third parties as a primary, self-described business line.
2. **GPU and AI-semiconductor maker.** It designs or makes data-center GPUs
   or AI accelerators. Or it supplies one of the inputs GPU servers cannot
   ship without: leading-edge foundry capacity, HBM memory, or GPU server
   systems as its main product. In either case the data-center or AI
   business must be its largest segment or its stated primary growth
   driver.
3. **Data-center power and capacity.** It generates power or builds power
   and cooling infrastructure with AI data-center demand as its stated
   primary growth driver. Or it builds and leases AI or high-performance
   computing data-center capacity as its primary growth business.

**R3. Liquidity.** Median daily dollar volume (volume × VWAP) of at least
USD 50 million, and a last close of at least USD 5. Both are measured from
2026-06-01 to 2026-07-31, which is before the test window.

**R4. Seasoning.** At least 40 sessions of bars in that window.

**R5. Exclusions.**
- Hyperscalers and diversified mega-caps whose GPU-compute exposure is a
  minority of revenue: Microsoft, Amazon, Alphabet, Meta, Oracle, Apple,
  Tesla. Our index excludes hyperscalers for the same reason.
- ETFs, warrants and leveraged single-stock products.

### Candidates and verdicts

The candidates were enumerated by hand, and Alpaca's asset list was searched
by name for recent listings (Lambda, Crusoe, Cerebras, Fluidstack, Together,
Vultr, TensorWave, Nscale, Firmus, Voltage Park, Groq, SambaNova). Only
Cerebras was found listed.

| Ticker | Company | Category | R2 reason | R3–R4 screen | In universe |
|---|---|---|---|---|---|
| CRWV | CoreWeave | Neocloud | GPU cloud is the business | pass | yes |
| NBIS | Nebius Group | Neocloud | GPU cloud is the business | pass | yes |
| IREN | IREN | Neocloud | Self-described AI cloud provider with owned GPUs | pass | yes |
| WYFI | WhiteFiber | Neocloud | GPU cloud plus AI data centers | pass | yes |
| NVDA | NVIDIA | GPU/AI semis | Data-center GPUs | pass | yes |
| AMD | AMD | GPU/AI semis | Data-center GPUs; data center is the largest segment | pass | yes |
| AVGO | Broadcom | GPU/AI semis | Custom AI accelerators; AI is the primary growth driver | pass | yes |
| TSM | TSMC (ADR) | GPU/AI semis | Leading-edge foundry for all leading GPUs; HPC is the largest platform | pass | yes |
| MU | Micron | GPU/AI semis | HBM; data center is the primary growth driver | pass | yes |
| MRVL | Marvell | GPU/AI semis | Custom AI accelerators; data center is most of revenue | pass | yes |
| SMCI | Super Micro Computer | GPU/AI semis | GPU servers are the main product | pass | yes |
| CBRS | Cerebras Systems | GPU/AI semis | AI accelerators are the whole business | pass | yes |
| VST | Vistra | Power and capacity | Power producer; data-center demand is the stated growth driver | pass | yes |
| CEG | Constellation Energy | Power and capacity | Nuclear power sold to data centers is the stated growth driver | pass | yes |
| TLN | Talen Energy | Power and capacity | Power producer with a data-center campus contract | pass | yes |
| VRT | Vertiv | Power and capacity | Data-center power and cooling are most of sales | pass | yes |
| BE | Bloom Energy | Power and capacity | Fuel cells; AI data centers are the stated growth driver | pass | yes |
| APLD | Applied Digital | Power and capacity | Builds and leases AI data centers | pass | yes |
| CORZ | Core Scientific | Power and capacity | AI and HPC colocation is the growth business | pass | yes |
| CIFR | Cipher Digital | Power and capacity | AI and HPC data-center leases are the growth business | pass | yes |
| WULF | TeraWulf | Power and capacity | AI and HPC data-center leases are the growth business | pass | yes |
| INTC | Intel | – | AI accelerators are a minor line; client computing is largest | – | no (R2) |
| QCOM, ARM | Qualcomm, Arm | – | Data center is not the largest segment | – | no (R2) |
| DELL, HPE | Dell, HPE | – | GPU servers are one line in broad hardware businesses | – | no (R2) |
| ANET, CRDO, ALAB, COHR, LITE | Networking and optics | – | Component suppliers outside the R2 list | – | no (R2) |
| ASML, AMAT, LRCX, KLAC | Equipment | – | Indirect exposure | – | no (R2) |
| GEV, ETN, NRG, PWR | Diversified power and industrials | – | Data centers are not the stated primary driver | – | no (R2) |
| OKLO | Oklo | – | No operating business yet | – | no (R2) |
| DOCN | DigitalOcean | – | General cloud is primary; GPU is a minor line | – | no (R2) |
| HUT, GLXY | Hut 8, Galaxy Digital | – | Mining or digital-asset finance remains primary | – | no (R2) |
| MARA, RIOT, CLSK, BTDR | Bitcoin miners | – | Mining is primary | – | no (R2) |
| MSFT, AMZN, GOOGL, META, ORCL | Hyperscalers | – | R5 | – | no (R5) |

The screen printed pass or fail only; no dollar-volume value was recorded.
All 21 candidates that met R2 passed R3 and R4. WYFI is not shortable on
Alpaca, which matters only for the paper strategy (section 9).

### Final universe (frozen)

| Bucket | Members | Count |
|---|---|---|
| Neocloud | CRWV, NBIS, IREN, WYFI | 4 |
| GPU and AI semiconductors | NVDA, AMD, AVGO, TSM, MU, MRVL, SMCI, CBRS | 8 |
| Data-center power and capacity | VST, CEG, TLN, VRT, BE, APLD, CORZ, CIFR, WULF | 9 |

**Primary basket weighting: category-balanced.** Each bucket gets one third,
split equally within the bucket. Equal weight across all 21 names would give
the power and capacity bucket, the one most loosely linked to rental prices,
the largest weight just because it has the most names. Category balance
avoids that.

R2 involves judgment. The protection against bias is that the list was
frozen before any test-window return was seen, and the primary test uses
the whole basket. No member can be dropped later for performing badly.

## 3. Benchmark

**XLK**, the Technology Select Sector SPDR ETF: the most liquid broad US
technology ETF. XLK holds some universe members (NVDA, AVGO, AMD, MU). That
mutes the semiconductor bucket's excess return. This is accepted: the
question is whether compute-linked names move differently from technology
broadly.

## 4. Signals

### Data and panels

The signals come from the fixed-panel history series of our index
(docs/index_methodology.md, D21): gpurentalprices.com archive and live
feed, on-demand, US or unknown region, hyperscalers excluded. The provider
panels are frozen here, as computed on 2026-10-06 from the first 30 days
(2026-07-19 to 2026-08-17). A later backfill cannot change them.

- **H100 (19 providers):** coreweave, crusoe, digitalocean, gmicloud,
  hyperstack, jarvislabs, lambda, latitude, massedcompute, nebius, ovh,
  primeintellect, scaleway, spheron, tensordock, thundercompute, together,
  verda, voltagepark.
- **B200 (8 providers):** coreweave, gmicloud, hyperstack, lambda, nebius,
  primeintellect, together, verda.

### Daily features for each GPU model and index day `d`

| Feature | Definition |
|---|---|
| `level` | The history-panel index: provider-weighted median of eligible panel listings (`claim4.signals.panel_features`) |
| `dispersion` | Interquartile range, across panel providers present that day, of the log of each provider's median price |
| `n_listings` | Number of eligible panel listings; listings flagged unavailable are excluded. This is the availability proxy, because the sources rarely flag availability (5,216 of 5,259 archived rows are "unknown") |

A day is used only if it meets coverage: at least 3 providers and 5
listings.

### Timing (decision D31)

Index day `d` becomes usable at `ts_usable = max(ts_available + 60 min,
23:30 UTC on d)`.

23:30 UTC is when the live cycle runs (section 9). So a backtest sees
exactly what the scheduled live cycle would have seen, and no more. The
60-minute margin covers publication delays after the publisher's fetch.

Session `t`, with official open `O_t` from Alpaca's calendar, sees `d*(t)`:
the latest covered day with `ts_usable <= O_t - 5 min`. In practice a
weekday's index is acted on at the next session's open. Monday's signal
spans Thursday's to Sunday's index.

### Signals for session `t`

| Signal | Definition |
|---|---|
| `level_h100`, `level_b200` | `ln level[d*(t)] - ln level[d*(t-1)]` |
| `disp_h100`, `disp_b200` | `dispersion[d*(t)] - dispersion[d*(t-1)]` |
| `avail_h100`, `avail_b200` | `ln n_listings[d*(t)] - ln n_listings[d*(t-1)]` |

If no new index day arrived between the two opens, the change is 0.

### Sample

The 30 formation days are in-sample for the panel choice and are dropped,
as in D21. A session is in the sample only if both `d*(t)` and `d*(t-1)` are
after 2026-08-17. **The first session is 2026-08-20.**

### Signal-side facts at pre-registration

Sessions 2026-08-20 to 2026-10-05:

| Signal | Sessions | Non-zero |
|---|---|---|
| level_h100 | 32 | 5 |
| level_b200 | 32 | 11 (8 of them +0.5% steps) |
| disp_h100 | 32 | 26 |
| disp_b200 | 32 | 6 |
| avail_h100 | 32 | 3 |
| avail_b200 | 32 | 1 |

Large level moves of 2% or more: H100 on 09-04 (−3.3%) and 10-01 (+2.4%);
B200 on 09-04 (−5.5%) and 10-05 (+10.4%).

**Known caveat.** Providers in the panel are fixed but their listings are
not. The B200 move of +10.4% on 10-05 came with panel listings rising from
8 to 11, when gpurentalprices.com widened its coverage. Part of that move
is probably composition, not price. The plan does not filter it out: the
hypothesis is about our index as built.

## 5. Outcome

Bars are Alpaca daily bars from the consolidated (SIP) feed with
`adjustment=all` (splits and dividends). Each bar is usable from its
session's close plus 20 minutes. The free plan withholds the latest 15
minutes; 5 minutes are margin.

For session `t` and horizon `h` in {1, 5, 20} sessions:

- `r_i(t,h) = close_i[t+h-1] / open_i[t] - 1`: enter at the open after the
  signal, exit at a close.
- `B(t,h)`: the category-balanced basket, the mean of the three bucket
  means. A bucket counts only if at least half its members have bars.
- `R(t,h) = B(t,h) - r_XLK(t,h)`: the excess return.

`R(t,h)` is known only after the close of `t+h-1` plus 20 minutes. Overlap
between windows for `h > 1` is handled by the HAC lag and the block length
below.

## 6. Tests

All bootstraps use the circular block bootstrap (`backtest/bootstrap.py`)
with block length `max(5, h)`, 2,000 resamples and seed 20261005, unless
stated otherwise.

### 6.1 Family P: lead-lag (primary, 18 tests)

For each of the 6 signals `S` and 3 horizons `h`, fit
`R(t,h) = a + b S_t + e`.

- **Statistics.** Slope `b` with Newey-West HAC standard error (lag `h`,
  Bartlett weights). Two-sided p-value from Student's t with `n-2` degrees
  of freedom. Pearson correlation with a 95% block-bootstrap CI over
  resampled pairs.
- **Robustness p-value.** Circular-shift permutation: the outcome series is
  rotated against the signal by every shift `k` with `h <= k <= n-h`. Then
  `p = (1 + #{|rho_k| >= |rho|}) / (1 + K)`. This keeps the
  autocorrelation of both series.
- **Multiple testing.** Holm adjustment of the 18 HAC p-values (family-wise
  error 5%).
- **A test passes only if all three hold:**
  - the Holm-adjusted p-value is below 0.05;
  - the permutation p-value is below 0.05;
  - the signal has at least 10 non-zero values in the sample.

  Otherwise it is reported as not significant, and, where relevant, as
  "insufficient variation".

### 6.2 Reverse direction (diagnostic, not a test)

Do equities lead our index instead? Correlations are reported between
`S_t` and `R(t+k,1)` for `k` from -5 to +5. `k < 0` means returns realized
before the signal. Each comes with a block-bootstrap CI. They are
descriptive, uncorrected, and never used for trading.

### 6.3 Family E: event study (6 tests)

- **Events.** Sessions with `|level_g(t)| >= 2%` for `g` in {H100, B200}.
- **Measure.** Signed abnormal return `CAR(t,h) = sign(level_g(t)) × R(t,h)`.
- **Overlap.** Within each GPU model and horizon, an event within `h-1`
  sessions of a kept event is dropped.
- **Statistics.** Mean signed CAR. 95% CI from an iid bootstrap over events
  (2,000 resamples). Two-sided p-value from a sign-flip randomization test:
  exact for 16 events or fewer, otherwise 20,000 random flips with a fixed
  seed. Holm adjustment across the 6 tests.
- **Minimum.** At least 10 events. Below that the result is reported as
  descriptive and "insufficient events". Today there are 2 per GPU.

### 6.4 Family W: walk-forward forecast against naive baselines (18 tests)

For each `S` and `h`, at each session `t`:

- **Training data.** An expanding-window OLS of `R(t',h)` on `S_{t'}`,
  using only windows already known at `O_t`: those with
  `close[t'+h-1] + 20 min <= O_t - 5 min`.
- **Forecast.** `f_t = a + b S_t`, made once there are at least 20 training
  windows.
- **Baselines.** B0, a zero forecast (no predictability); B1, the expanding
  mean of the training outcomes.
- **Metrics.** Out-of-sample MSFE and `R2_OS = 1 - MSFE_model / MSFE_base`
  against each baseline. Clark and West (2007) adjusted-MSPE statistic
  against each baseline, HAC lag `h`, one-sided normal p-value. Directional
  hit rate.
- **A model passes only if all of these hold:**
  - `R2_OS > 0` against both baselines;
  - the larger of its two Clark-West p-values, Holm-adjusted across the 18
    models, is below 0.05;
  - there are at least 120 out-of-sample forecasts.

  Today there are about 12 for `h=1`, 4 for `h=5` and none for `h=20`.

### 6.5 Family S: bucket baskets (secondary, 54 tests)

The analysis in 6.1 is repeated on each bucket's equal-weight basket minus
XLK: 3 buckets × 6 signals × 3 horizons. P-values are adjusted with
Benjamini-Hochberg (false discovery rate 10%). These results are descriptive
and can never open the gate.

### 6.6 Count

96 declared tests: P 18, E 6, W 18, S 54. On top of those come 18
strategy evaluations, used only as gate condition G3 for a pair that has
already passed G1 and G2, and one descriptive cross-correlogram. That makes
114 entries in `docs/variants_log.md`. Per-stock tests are **not** run: they
would add hundreds of tests and invite picking winners after the fact.

## 7. Trading cost assumptions

All values are assumptions, not findings.

| Item | Value | Note |
|---|---|---|
| Half-spread plus slippage, universe stocks | 15 bps per side | ASSUMPTION; conservative for a mix of mega-caps and volatile mid-caps |
| Half-spread plus slippage, XLK | 3 bps per side | ASSUMPTION |
| Regulatory fees on sells | 1 bp | ASSUMPTION; covers SEC and FINRA fees |
| Commission | USD 0 | ASSUMPTION: Alpaca's published stock pricing, not re-verified this run |
| Borrow, short stocks | 5% a year | ASSUMPTION; conservative because some names are hard to borrow |
| Borrow, short XLK | 0.5% a year | ASSUMPTION |
| Sensitivity | 0×, 0.5×, 1×, 2×, 4× | Every strategy result is shown at each multiple |

A round trip of the long-short pair, per unit of notional per leg, costs
about 0.38% (`2×15 + 2×3 + 2×1` bps) plus borrow for `h` sessions. A daily
signal must forecast more than that to trade.

## 8. Validation gate

Paper orders are allowed for a signal and horizon only if all of G1 to G5
hold. The gate is re-evaluated on every run.

| Gate | Condition |
|---|---|
| G1 | The family P test passes (6.1) |
| G2 | The family W model passes (6.4) |
| G3 | The walk-forward strategy (section 9 rule, out-of-sample forecasts only) has a net Sharpe whose 95% block-bootstrap lower bound is above 0 at 1× costs, and a positive mean net return at 2× costs |
| G4 | At least 120 out-of-sample forecasts and at least 30 non-zero signal values in the out-of-sample window |
| G5 | The kill switch is off, no kill criterion has fired (section 10), and the index day used is covered and at most 3 calendar days old |

If several pairs pass, only the one with the smallest Holm-adjusted G1
p-value trades. If a pair that traded fails the gate later, its positions
are closed and the cycle returns to shadow mode.

## 9. Paper trading and shadow mode

### Strategy

The strategy trades a long-short pair: the category-balanced basket against
XLK.

- **Direction.** At the open of session `t`, direction is `sign(f_t)` if
  `|f_t|` exceeds the round-trip cost. Otherwise there is no position.
- **Holding.** Each daily cohort holds for `h` sessions with weight `1/h`.
  Target positions sum the active cohorts, so a missed run cannot leave a
  position open indefinitely.
- **Notional.** USD 10,000 per leg at full position (config).
- **Basket weights.** One third per bucket, equal within a bucket.
- **Short basket leg.** Names Alpaca marks as not shortable (today WYFI) are
  left out for that session and the leg is re-weighted. This is logged.
- **Orders.** Market orders with `time_in_force=day`, sent after the close.
  Alpaca queues them for the next open. Long stock legs use notional
  (fractional) orders where the asset is fractionable. Short legs use whole
  shares.

### Hard limits (from `[claim4.risk]` in config)

| Limit | Value |
|---|---|
| Maximum position | USD 10,000 market value per symbol |
| Maximum gross exposure | USD 20,000 |
| Daily loss limit | USD 1,000. On a breach, all claim-4 positions are closed and no new entries are made for 1 session |
| Maximum drawdown | USD 3,000 from peak equity. On a breach, all positions are closed and the kill switch latches; only the owner can reset it |
| Kill switch | `kill_switch = true` in config, or `COMPUTE_CURVE_KILL_SWITCH=1` in the environment. Either closes positions and blocks all orders |

Orders that would breach a limit are scaled down proportionally on both
legs, so the pair stays balanced. If they cannot be scaled to fit, they are
not sent.

### Shadow mode (today)

Each run appends to `reports/claim4/predictions.csv`. That file is
append-only and committed. Each row records:

- the decision time;
- the target session;
- the six signal values and the index days they used;
- each signal-horizon forecast fitted on data known at the decision time;
- the gate status;
- the action: `shadow` or `paper`.

In shadow mode no order is sent. The realized outcomes are computed later,
from re-fetched bars, at evaluation time. They are not stored.

### Decision timing

The live cycle runs after the US close, at about 23:30 UTC. A run makes the
decision for the next session only if no later scheduled run comes before
that session's open, which means the next open is less than 24 hours away.
Otherwise it records "deferred". A Friday-evening run therefore defers to
Sunday's run for Monday's open.

## 10. Kill criteria

| Code | Criterion | Consequence |
|---|---|---|
| K1 | At 250 sessions after 2026-08-20 (about August 2027), no family P test passes | Claim 4 is reported "not supported" |
| K1b | At 500 sessions (about August 2028), still none | Claim 4 is rejected and the claim-4 cycle is retired; index collection continues for claims 1 to 3 |
| K2 | Paper drawdown of USD 3,000 or more from peak | Positions closed; the kill switch latches |
| K3 | Daily paper loss of USD 1,000 or more | Positions closed; no entries for 1 session |
| K4 | A previously passing gate fails | Positions closed; back to shadow mode |
| K5 | The index day for a session is not covered or is more than 3 days old | No new positions that session |

## 11. Statistical power

The minimum detectable correlation uses the Fisher z approximation, with
two-sided tests and 80% power: `n = ((z_{1-alpha/2} + z_{0.8}) / atanh(rho))^2 + 3`.

| Horizon | Windows today | Minimum detectable correlation at alpha = 0.05 | Same, after Holm (alpha = 0.05/18) |
|---|---|---|---|
| 1 day | 32 | 0.48 | 0.61 |
| 5 days | 28 (overlapping) | 0.51 | 0.64 |
| 20 days | 13 (overlapping; fewer than 2 independent windows) | 0.71 | 0.84 |

Sessions needed for a dense signal:

| True correlation | Sessions at alpha = 0.05 | Sessions after Holm (alpha = 0.05/18) |
|---|---|---|
| 0.05 | 3,138 (about 12.5 years) | 5,870 (about 23 years) |
| 0.10 | 783 (about 3.1 years) | 1,463 (about 5.8 years) |
| 0.15 | 347 (about 1.4 years) | 647 (about 2.6 years) |
| 0.20 | 194 (about 0.8 years) | 361 (about 1.4 years) |
| 0.30 | 85 (about 0.3 years) | 157 (about 0.6 years) |

Sparse signals are worse. If an effect exists only on the non-zero days, a
signal that is non-zero on 15% to 20% of sessions dilutes the all-session
correlation by a factor of about 0.4. The level signals behave like this.

- **Event study.** It needs 10 events per GPU and horizon. There are 2.
- **Walk-forward.** There are about 12 out-of-sample forecasts for `h=1`,
  4 for `h=5` and none for `h=20`, against the 120 required.

**Conclusion, written before any result:** the current data cannot support
or reject H5. Any pattern in the first evaluation is noise until the
sample grows by an order of magnitude.

## 12. Data terms and reproducibility

- Alpaca bars are fetched at run time and cached only under `var/`
  (decision D29). The committed manifest `reports/claim4/data_manifest.json`
  records symbols, dates, feed, row counts and a SHA-256 of the bar table.
- All computations are deterministic given the bars, the committed index
  data and the seed.
- Reports carry aggregate statistics only: no prices, no per-stock return
  series.

## 13. Changes after registration

Anything that changes a definition, threshold, universe member, weighting,
cost or test above, after results exist, is a new variant. It gets a dated
entry with its reason in `docs/variants_log.md`. A bug fix that does not
change a definition is recorded in `docs/decisions.md` instead.
