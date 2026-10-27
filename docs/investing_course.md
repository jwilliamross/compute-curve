# Investing with evidence: an 8-week course

_For one learner, Calgary, MFin. About 3 hours a week. Education only, not personal
financial or tax advice. Practise on paper first: the course's rules come from the
same discipline as the rest of this repository._

**How every week works**

1. **Read:** the lesson below.
2. **Do:** the exercise, written in your journal (template at the end).
3. **Check:** answer the self-check questions. Answers are at the bottom of each
   module.

**The one rule of the course.** Write your reason, your exit and your size *before*
you act. If you can't write it, don't do it.

---

## Week 0: set up the account structure (one evening)

### Core and satellite

| Part | Share | What | Why |
|---|---|---|---|
| Core | 80–90% | A broad, low-cost index ETF (all-world or North American) | Most active investors trail the index after fees; the core makes sure you don't |
| Satellite | 10–20% | Your own stock picks, from this course | Where you learn and test whether you have an edge |

### Accounts in Canada (in this order, typically)

- **TFSA.** Growth and withdrawals are tax-free, and withdrawn room comes back
  the next calendar year. Check your contribution room in CRA My Account.
- **FHSA,** if you may buy a first home: a deduction going in and tax-free coming
  out for a home.
- **RRSP.** The deduction is worth more once your income is higher, often after
  school.

A professional should confirm the tax details for your situation.

### Tools

| Tool | What it gives you |
|---|---|
| A broker with low commissions on ETFs | Somewhere to hold the core and the satellite |
| A spreadsheet journal | Your record of every decision |
| The Alpaca **paper** account, already set up in this project | Practice trades with fake money |
| `reports/insiders/latest.md` | The insider tracker, updated each weekday |

---

## Week 1: read the three financial statements

### The lesson

| Statement | Question it answers | Look at |
|---|---|---|
| **Income statement** | Did the company make money this period? | Revenue growth, gross margin, operating margin, net income, diluted EPS |
| **Balance sheet** | What does it own and owe right now? | Cash, debt, equity; debt ÷ EBITDA; current ratio |
| **Cash-flow statement** | Did real cash come in? | Operating cash flow, capital spending, **free cash flow** (operating cash flow − capex) |

**Rule of thumb.** Profits that never turn into cash are a warning sign. Compare
net income with operating cash flow over 3 years.

**Where to get them.**

- US companies: their 10-K (annual) and 10-Q (quarterly) on SEC EDGAR.
- Canadian companies: SEDAR+.

### Exercise

Pick one company you know.

1. Pull its latest 10-K.
2. Write one page:
   - what it sells;
   - 3-year revenue growth;
   - operating margin;
   - free cash flow;
   - net debt;
   - the single biggest risk from the "Risk Factors" section.

### Self-check

1. Revenue rose 20%, but operating cash flow fell. Name two possible causes.
2. Why is diluted EPS used, not basic EPS?

**Answers.**

1. Receivables or inventory growing faster than sales (customers paying slower,
   unsold stock), or rising prepaid costs. Revenue booked isn't cash received.
2. Diluted EPS counts options, warrants and convertibles that could become
   shares. It is the conservative per-share number.

---

## Week 2: valuation ratios, and what they really say

### The lesson

| Ratio | Formula | Use it for | Trap |
|---|---|---|---|
| **P/E** | Price ÷ EPS | Profitable, stable companies | Low P/E is often low because earnings are about to fall (a "value trap") |
| **Forward P/E** | Price ÷ next year's expected EPS | What the market expects | Estimates are often too optimistic |
| **EV/EBITDA** | (Market cap + debt − cash) ÷ EBITDA | Comparing companies with different debt | EBITDA ignores capital spending |
| **FCF yield** | Free cash flow ÷ market cap | Cash return on the price you pay | One-off swings in working capital |
| **Earnings yield** | 1 ÷ P/E | Comparing stocks with bonds | Earnings aren't paid out like a coupon |

**How to use P/E properly.**

- **Compare like with like:** the company against its own 10-year range, and
  against its industry. A bank at 10× and a software company at 30× can both be
  fair.
- **Ask what growth the price implies.** At P/E 30 with no growth, you'd wait 30
  years to earn your price back. Growth is what justifies a high P/E.
- **Compare with bonds.** Earnings yield (1/PE) against the 10-year bond yield
  is a crude "are stocks paying me to take the risk?" check.

**Evidence.**

- Cheap stocks have beaten expensive ones over long history (Fama and French 1992,
  the value premium).
- The effect was weak or negative from about 2007 to 2020.
- So a low P/E alone is a starting filter, not a strategy.

### Exercise

1. Pick 5 companies in one industry.
2. Fill in a table with P/E, forward P/E, EV/EBITDA, FCF yield, revenue growth
   and net debt/EBITDA.
3. Pick the "cheapest" one and write why it might *deserve* to be cheap.

### Self-check

1. Company A: P/E 12, earnings falling 15% a year. Company B: P/E 25, earnings
   growing 20% a year. Which is "cheaper" in 3 years if prices don't move?
2. Why does EV/EBITDA handle debt better than P/E?

**Answers.**

1. After 3 years:
   - A's earnings fall to 0.85³ ≈ 0.61 of today's, so its P/E rises to
     12 ÷ 0.61 ≈ 19.6.
   - B's earnings grow to 1.2³ ≈ 1.73 of today's, so its P/E falls to
     25 ÷ 1.73 ≈ 14.5.
   - B is cheaper.
2. EV includes debt, and EBITDA is before interest, so two companies with the
   same business but different debt look comparable.

---

## Week 3: valuing a company yourself

### The lesson: a simple discounted cash flow (DCF)

    value per share = [ Σ FCF_t / (1+r)^t  +  terminal value / (1+r)^N  −  net debt ] / diluted shares
    terminal value  = FCF_(N+1) / (r − g)

**The inputs:**

- **r,** the required return: about 8–10% for a typical large company. It is an
  ASSUMPTION; justify it in your write-up.
- **g,** long-run growth: no higher than nominal GDP, about 3–4%.
- **The key habit:** run three cases (bear, base, bull) and look at the *range*,
  not one number. Small changes to r and g move the answer a lot. That is the
  lesson, not a bug.

**Free course.** Aswath Damodaran (NYU Stern) puts his valuation course online at
no cost. His *The Little Book of Valuation* is the short version.

### Exercise

1. Build a 5-year DCF for your Week-1 company in a spreadsheet.
2. Write your **buy price** before looking at today's price. Use your base case
   with a 20–30% margin of safety (Graham, *The Intelligent Investor*, ch. 20).
3. Only then compare it with the market price.

### Self-check

1. If r rises from 8% to 9% and g stays at 3%, what happens to the
   terminal-value multiple 1/(r−g)?
2. What does a "margin of safety" protect you from?

**Answers.**

1. It goes from 1/0.05 = 20× to 1/0.06 ≈ 16.7×, about −17%. The discount rate
   dominates DCFs.
2. Your own estimation errors, and bad luck.

---

## Week 4: following insiders (with our tracker)

### The lesson

**The filing.** Company officers, directors and 10% owners must report trades in
their company's stock.

- **US:** SEC Form 4, within 2 business days of the trade.
- **Canada:** SEDI.

**What matters:**

| Signal | Why | Evidence |
|---|---|---|
| **Open-market purchases** (code "P") | Insiders sell for many reasons (taxes, houses, diversification) but buy for one: they think the stock is cheap | Purchases have come before modest outperformance (Lakonishok and Lee 2001) |
| **Clusters** (several insiders buying within weeks) | Independent agreement | Strongest in smaller companies |
| **CEO/CFO buys** | The most informed insiders | – |
| **"Opportunistic" buys,** not routine annual ones | Routine buyers' trades carry no information | Cohen, Malloy and Pomorski (2012), *J. Finance* |
| **Big increase in holdings** (e.g. +50%) | Real conviction | – |

**What to ignore:**

- sales;
- option exercises (code "M");
- grants (code "A");
- 10b5-1 plan trades, which are scheduled in advance;
- tiny purchases.

**Caveats.**

- Everyone watches Form 4s now. The edge is smaller than in old studies and may
  not survive costs.
- That is why we will test it before trusting it.

### Our tracker (D69)

**What it does.** Every weekday morning before the open, a GitHub Action:

1. reads the previous day's Form 4 filings on EDGAR;
2. keeps open-market purchases;
3. flags:
   - **clusters** (3 or more insiders buying at least USD 25k each within 14 days);
   - **C-suite buys** (USD 100k or more);
   - **pairs** (2 insiders);
   - **large buys** (USD 1M or more);
4. opens a GitHub issue labelled `insider-alert`, which notifies you.

The full list is in `reports/insiders/latest.md`.

### Exercise

1. For two weeks, log every **cluster** alert: ticker, P/E, price, and your
   one-line thesis.
2. Then record the price 1 month and 3 months later, against the index (XIC or
   SPY).
3. Do not trade them yet.

### Self-check

1. A CEO's Form 4 shows code "M" for 50,000 shares and "S" for 50,000 shares on
   the same day. Signal?
2. Why might a cluster in a USD 300M company mean more than one in a USD 300B
   company?

**Answers.**

1. Usually none. That is an option exercise and sale, routine compensation.
2. Smaller companies have less analyst coverage, so insiders' information is
   less likely to be already priced in.

---

## Week 5: the Fed and interest rates

### The lesson

**The calendar.**

- The FOMC meets 8 times a year.
- At 2:00 pm ET it releases the statement. A press conference follows at 2:30.
- Four times a year it also publishes the **Summary of Economic Projections,**
  including the "dot plot" of members' rate forecasts.
- Three weeks later come the **minutes**.

**The key idea: markets move on the surprise.** Before each meeting, find out
what's priced in:

| Source | What it tells you |
|---|---|
| **CME FedWatch** | The probabilities of each rate decision, from fed funds futures |
| **The 2-year Treasury yield** (FRED series DGS2) | The best single gauge of where markets expect rates over the next two years |

**How rates reach stocks:**

1. Higher rates raise r in your Week-3 DCF, so long-duration growth stocks fall
   the most.
2. Rates change borrowing costs for companies and consumers.

**From our own research.** Claim 11 found the 2-year yield even leads GPU rental
prices a little, because GPUs are financed assets. It did not replicate on a
second dataset (claim 12). That is a good example of why one study isn't enough.

**Evidence.** Stocks used to rise in the 24 hours before FOMC decisions (Lucca and
Moench 2015, *J. Finance*). The effect weakened after publication. Most published
edges shrink once known.

**Canada.** The Bank of Canada has 8 decision dates a year, and Canadian 2-year
yields behave the same way.

### Exercise

For the next FOMC (or BoC) meeting, in your journal:

1. **Before:** what FedWatch and the 2-year yield say is priced in.
2. **After:**
   - the decision;
   - the surprise, if any (did the dots or the tone change?);
   - how the 2-year yield, the S&P 500 and your 5 Week-2 stocks moved by the
     close.

### Self-check

1. The Fed cuts by 0.25 pp, and stocks fall. How can that be?
2. Why does a rate rise hurt a company with P/E 60 more than one with P/E 10?

**Answers.**

1. Markets had priced 0.50 pp, or the statement signalled fewer cuts ahead. The
   news was hawkish *relative to expectations*.
2. Most of the high-P/E company's value sits in far-future cash flows. Those are
   discounted more heavily when r rises: higher duration.

---

## Week 6: earnings season

### The lesson

**What to watch:**

- **Results vs consensus estimates,** for EPS and revenue. A "beat" is normal:
  companies guide low.
- **Guidance,** the outlook for next quarter or year. It often moves the stock
  more than the results.
- **Margins** and their trend.
- **The call (Q&A).** Analysts' questions show what the market worries about.

**Post-earnings drift.**

- Stocks with big positive surprises have tended to keep drifting up for weeks
  (Bernard and Thomas 1989).
- The effect is weaker now in large caps.

### Exercise

Follow 3 earnings reports from your list: before (consensus), during (headline,
guidance) and after (1-day and 2-week moves). Write one paragraph each.

### Self-check

1. EPS beat by 10% and the stock fell 8%. Name two reasons.
2. Why are "beats" so common?

**Answers.**

1. The guidance was cut, the beat came from one-offs or a lower tax rate, or
   margins fell. Or expectations ("whisper numbers") were higher than consensus.
2. Companies guide conservatively and analysts anchor on that guidance.

---

## Week 7: sizing, risk and costs

### The lesson

**Position size before entry.**

- No single stock should be more than 5% of the satellite, so one disaster
  can't sink you.
- Scale by risk: size = (amount you'll risk) ÷ (distance to your exit price).
- The repository's `bet-sizing` skill covers Kelly sizing; use a quarter of
  Kelly at most.

**Exits are part of the plan.**

- A thesis exit: "if margins fall two quarters running, I sell".
- A time exit: "review after 12 months".
- Price stops are optional; thesis exits are not.

**Costs and taxes.**

- Commissions and spreads.
- Currency conversion: CAD to USD can cost 1–2% each way at some brokers.
- Withholding tax on US dividends: generally withheld in a TFSA, generally
  treaty-exempt in an RRSP. Confirm for your case.

**Base rates.**

- Most professional fund managers trail their index over 15 years (S&P SPIVA
  reports).
- Your satellite is an experiment with a control group: the core.

### Exercise

1. Write your rules: maximum position, sizing formula, exit rules, maximum number
   of positions, and what makes you stop the satellite.
2. Paper-trade them for two weeks, using the paper account or a spreadsheet.

### Self-check

1. You'll risk USD 200 on a trade; your exit is 10% below entry. Position size?
2. Why judge the satellite against the index, not against zero?

**Answers.**

1. USD 2,000.
2. The index is the free alternative. Beating zero in a rising market proves
   nothing.

---

## Week 8: review, and test a rule like a quant

### The lesson

**Score yourself honestly:**

- your journal calls against the index;
- your hit rate;
- your average gain on winners against your average loss on losers;
- whether your best results came from skill or one lucky name.

**Then do what this repository does:**

1. **Pre-register** one rule in writing, before testing it. For example: "buy
   when 3 or more insiders buy USD 25k or more within 14 days, P/E under 25; hold
   3 months".
2. **Test it on history,** with costs. The SEC's Form 4 data goes back decades.
3. **Paper-trade it forward** for 3 months.
4. **Only then use real money, and small amounts.**

This mirrors claims 12–13: our stock strategy looked great on 2026 data and then
lost money on 2019–2024. Testing first is what saved real money.

### Exercise

1. Write your rule.
2. Ask for the historical test. The insider tracker's data and the
   compute-curve tools can run it.

---

## Journal template (one row per decision)

| Date | Ticker | Action | Size (% of satellite) | Price | Thesis in one line | Signal (insider / valuation / Fed / earnings) | Exit plan | Index level | Outcome at 1m / 3m / 12m | Lesson |
|---|---|---|---|---|---|---|---|---|---|---|

## Reading list

| Book | Why |
|---|---|
| Benjamin Graham, *The Intelligent Investor*, chapters 8 and 20 | Mr. Market and the margin of safety |
| Burton Malkiel, *A Random Walk Down Wall Street* | The honest case for indexing |
| Aswath Damodaran, *The Little Book of Valuation* | Plus his free online course |
| Antti Ilmanen, *Expected Returns* | The evidence behind value, momentum and carry, for the quant in you |
| CFA Level I | Equity and fixed-income readings, which your MFin overlaps |
