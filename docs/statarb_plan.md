# Claim 6: statistical arbitrage on compute-linked equities (plan)

_Written 2026-10-10, before any strategy return was computed. Owner request: "go
ahead with the stock stat arb first". Simulation and shadow mode only. No order is
sent unless a later gate passes and the owner agrees. Paper only (D30)._

## 1. Question

Do the 20 compute-linked stocks of claim 4 contain short-term mispricings that a
market-neutral strategy can capture after realistic costs? Two classic methods
are used:

- **SA1, pairs trading on cointegrated pairs.** Engle and Granger (1987); the
  trading rule follows Gatev, Goetzmann and Rouwenhorst (2006, *RFS* 19(3)).
  Two stocks whose prices are tied in the long run drift apart, then come back.
  When the gap is unusually wide, buy the cheap one and sell the rich one.
- **SA2, residual mean reversion.** This is the ETF version of Avellaneda and
  Lee (2010, *Quantitative Finance* 10(7)).
  - Each stock's daily return is split into a part explained by the technology
    ETF XLK and a residual.
  - The cumulative residual is modelled as an Ornstein-Uhlenbeck (OU) process.
  - When it is far from its mean, the stock is traded against XLK, betting on a
    snap-back.

**Why these.** They are the textbook statistical-arbitrage methods. They use
only prices we already hold. Being market-neutral, they do not need a view on
AI stocks going up.

**Mechanism (why it might pay).** Liquidity-driven price pressure in volatile
names reverts. A stock pushed away from related stocks by flows, not news, tends
to come back (Lehmann 1990; Avellaneda and Lee 2010). The other side of the
trade is the impatient trader who pays for immediacy.

**Falsifier.** The confirmation set shows no positive net return after costs.

## 2. Data

| Item | Value |
|---|---|
| Prices | Alpaca daily bars, SIP feed, adjustment "all", cached under `var/` (never committed, D29) |
| Universe | claim-4 universe: CRWV, NBIS, IREN, WYFI, NVDA, AMD, AVGO, TSM, MU, MRVL, SMCI, CBRS, VST, CEG, TLN, VRT, BE, APLD, CORZ, CIFR, WULF; hedge XLK |
| Membership | A name trades only after 60 sessions of its own history, and NBIS only from 2024-10-21 (`[claim5.member_start]`) |
| Exploration set | sessions 2024-09-03 to 2026-02-19 (round-1 equity split, unchanged) |
| Confirmation set | sessions 2026-02-20 to 2026-10-05, one shot |
| Forward shadow | 60 sessions after the confirmation, if anything confirms |

**Inputs and outcomes.** Prices before a session are inputs and may be used.
Profit and loss is counted only for positions opened inside the set being
evaluated. Positions still open at a set's last session are closed at that
session's close.

**Contamination disclosure.** Equity returns in both sets were used before, in
claims 4 and 5 and round-1 H11/H12. Those tests regressed returns on GPU-price
signals. No stat-arb signal, spread or pair has been computed on these prices.

**Survivorship and selection.** The universe was chosen in 2026 because the
stocks are AI-related. A market-neutral strategy is less exposed to that choice,
but it is not immune. This is disclosed in every result.

## 3. Execution and costs (assumptions, labelled)

- **Timing.** Signals use closes up to session t. Trades happen at the open of
  t+1, positions are marked close to close, and exits happen at the open after
  the exit signal.
- **Stock costs.** 15 bps per side, plus 1 bp fee on sells (`[claim4.costs]`,
  ASSUMPTION).
- **XLK costs.** 3 bps per side.
- **Short borrow.** 3% per year on the short notional (ASSUMPTION; small miners
  can be hard to borrow).
- **Stress.** Double costs: 30 bps per side and 10% per year borrow.
- **Sizing.** Each strategy runs a book with gross exposure 1. Open positions
  share it equally, up to a maximum number of positions (SA1: 10 pairs; SA2: 10
  names), with an XLK hedge for SA2. The daily return is net P&L divided by
  capital.

## 4. Strategies and the parameter grid (21 cells, fixed now)

**SA1 pairs.**

- **Candidate pairs.** All pairs within a claim-4 group (neocloud 6, GPU semis
  28, power and capacity 36; 70 in total).
- **Formation, every 20 sessions.** On the trailing L sessions of log prices,
  fit the hedge ratio by OLS. Run the Engle-Granger cointegration test
  (`statsmodels.tsa.stattools.coint`) and keep pairs with p < 0.05.
- **Half-life filter.** Keep pairs whose OU half-life of the spread (from an
  AR(1) fit) is between 1 and 20 sessions. Then take up to 10 pairs, lowest p
  first.
- **Trading, next 20 sessions.** z = (spread − formation mean) / formation sd.
  - Enter when |z| ≥ e, selling the rich leg and buying the cheap leg in
    dollar-neutral, hedge-ratio-weighted amounts.
  - Exit when |z| ≤ 0.5, when |z| ≥ 4 (stop), or after 20 sessions.
- **Grid.** L ∈ {60, 120, 250} × e ∈ {1.5, 2.0, 2.5}, 9 cells.

**SA2 residual reversal.**

- **Daily, per stock.** Regress the last W daily returns on XLK returns to get
  the residuals ε and the cumulative residual X.
- **OU fit.** Fit AR(1) X_{k+1} = a + b·X_k + ζ, so that:
  - κ = −ln(b)·252;
  - m = a/(1 − b);
  - σ_eq = sd(ζ)/√(1 − b²);
  - s-score s = (X_W − m)/σ_eq.
- **Eligibility.** Only names with 0 < b < 1 and mean-reversion time 252/κ < W/2
  sessions trade.
- **Entry.** Long the stock and short β·XLK when s ≤ −e; short the stock and
  long β·XLK when s ≥ e.
- **Exit.** Close a long when s ≥ −0.5, close a short when s ≤ 0.75 (Avellaneda
  and Lee's closing levels), or after 20 sessions.
- **Grid.** W ∈ {40, 60, 90} × e ∈ {1.0, 1.25, 1.5, 2.0}, 12 cells.

## 5. Exploration: map the surface, pool the region (the quant-research skill)

On the exploration set, for each strategy:

1. Run every cell and compute the net daily returns.
2. **Smooth.** Each cell's annualized net Sharpe is averaged with its grid
   neighbours.
3. **Region.** The cells whose smoothed Sharpe lies within one standard error
   of the best smoothed cell, with SE(S) ≈ √((1 + S²/2)/T).
4. **Pool.** The strategy's candidate is the equal-weight average of the region
   cells' daily returns. The argmax cell is never used.

**Survival (all required).**

- The pooled net Sharpe is above 0.
- The deflated Sharpe ratio (Bailey and López de Prado 2014) is at least 0.90,
  with N = 21 trials, the variance of Sharpe across the 21 cells, and the
  returns' skew and kurtosis.
- The effective observation count is at least 30, counting overlapping
  positions as one bet.
- The region has at least 2 cells.

**Monte Carlo checks (reported, descriptive).**

- **Random-entry null.** 1,000 simulations keep each pooled candidate's trade
  count, holding periods and long-short mix, but draw entry dates and names at
  random. Reported: where the real Sharpe falls in that distribution.
- **Drawdown tail.** A 20-session block bootstrap of the daily returns, 10,000
  paths, gives the 5% tail of maximum drawdown. A realized drawdown is never
  used as a risk budget.
- **Cost breakeven.** The cost per side at which the net return reaches 0.

## 6. Confirmation (one shot, survivors only, at most 2)

The frozen pooled candidate (region cells and parameters) runs on the
confirmation set.

- **C1.** Mean daily net return above 0, with a one-sided Newey-West p
  (lag 10) of at most 0.05, Holm-adjusted across the survivors.
- **C2.** The mean net return is still above 0 at double costs.
- **Confirmed** = C1 and C2.

A confirmed strategy runs 60 sessions in shadow mode, with a daily log and no
orders. Then the claim-4-style gate applies, and the owner decides about paper
orders.

**Power, stated now.** The confirmation set has about 158 sessions (0.63
years). The SE of the annualized Sharpe is about 1.3 at a Sharpe of 1. Only a
net Sharpe above about 2.5 is likely to confirm. A null result means "no
evidence", not "no edge".

## 7. Variants

24 are declared:

- 21 grid cells;
- 2 confirmations;
- 1 forward test.

The project total rises from 231 to 255.

## 8. What is reported

For every result:

- costs used;
- the number of variants;
- bootstrap 95% CIs;
- effective N;
- deflated Sharpe;
- the region, not a champion;
- survivorship and contamination notes.
