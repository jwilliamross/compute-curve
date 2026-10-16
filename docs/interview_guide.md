# Interview guide: talking about compute-curve

## 30-second pitch

"CME is launching futures on GPU rental prices, GPU1 for H100s and GPU2 for
B200s. Like megawatt-hours, GPU-hours can't be stored, so I approached them
the way a power desk would.

I built an automated research system:

- it collects GPU rental prices daily from many providers;
- it built two years of per-provider history from licensed data;
- it tests ideas under strict anti-overfitting rules: hypotheses written
  down before the data, every variant counted, one-shot tests.

The data says rental prices are a sticky, roughly driftless random walk, and
list prices haven't fallen in two years. Yet Silicon Data's forward curve
prices declines. That's the normal-backwardation setup, where longs earn a
hedging premium.

I've pre-registered a book of seven futures rules, including balance-of-month,
backwardation carry and a GPU2/GPU1 spread. They run nightly in shadow mode
and start logging decisions the day the contracts list."

## Ten likely questions

1. **Why treat GPU futures like power, not like oil or stocks?**
   - You can't store a GPU-hour, so cost of carry doesn't link futures to
     spot. The futures price is the market's risk-adjusted expectation of
     the monthly average.
   - The gap between that and the true expectation is a risk premium. That
     is the Bessembinder–Lemmon story for electricity.

2. **What does "settles on a monthly average" change?**
   - Halfway through the month, half the settlement is already known.
   - Fair value = (days done × realised average + days left × today's
     level) ÷ days in the month. The uncertainty shrinks to zero by month
     end.
   - That is the balance-of-month calculation in our nightly fair-value
     sheet.

3. **What's your best GPU1/GPU2 strategy idea, and why?**
   - Balance-of-month (FP-C). It's low-risk by construction, and if a thin
     new contract misprices the locked-in part, about nine trades confirm
     it.
   - The bigger but slower idea is long the backwardation (FP-D).

4. **Isn't long the backwardation just betting prices go up?**
   - No. It's betting prices fall less than the futures curve says.
   - Our two years of data show list prices flat to rising, while the
     forward curve prices declines. The premium is the gap, and hedgers (GPU
     owners locking in revenue) pay it.

5. **How do you know you're not overfitting?**
   - Every rule and test is committed to git before the data is seen.
   - All 336 variants are counted.
   - Holm correction, Newey-West errors and one-shot confirmations.
   - When a pre-registered test turned out badly designed (R7-02), I
     reported it as broken rather than redefining it on the same data.

6. **What did you find that didn't work?**
   - GPU prices don't predict AI stocks.
   - Prices aren't predictable from their own past.
   - The B200/H100 spread rule loses on proxy data, because the ratio
     trended up all year.
   - Negative results are most of the work.

7. **What's basis risk here?**
   - Only Silicon Data's index pays.
   - Using the same providers, index method alone moves the B200 price from
     USD 6.25 to 8.30. Silicon Data's H100 sits about 20% below list-price
     medians.
   - So the edge isn't "a better fair value". It's predicting Silicon Data's
     number.

8. **What's the statistical bottleneck?**
   - Monthly decisions give about 24 trades a year.
   - A 5% premium needs about 180 trades to confirm; a 10% premium needs
     about 17. I computed that before launch so expectations are honest.

9. **Is anything tradable today?**
   - A stock stat-arb (residual reversal on 20 compute-linked names) passed
     a held-out test: Sharpe 1.8 after real quoted spreads. It's fragile,
     and it's in a live forward test.
   - Kalshi lists GPU price binaries. There I'm testing the
     favourite-longshot bias forward. The market looks under-confident, but
     the sample is too small yet.

10. **How did you use AI?**
    - As a research lead directing an agent. I set the question, the
      guardrails (no look-ahead, pre-registration, licensing rules) and the
      standards, and handled data access: I negotiated free API access from
      GetDeploying.
    - The agent implemented the work inside those rules: about 50 test
      files, 60+ recorded decisions, nightly automation.

## Numbers to remember

- **Contract:** 730 GPU-hours. Costs about USD 60 per contract per leg,
  about 2.8% of an H100 contract.
- **Prices:** H100 about USD 3.50 on list; Silicon Data 2.81. B200 about
  USD 7.80 on list.
- **Confirmed findings:** R7-01 provider gaps close (p 0.003); R7-04
  B200/H100 ratio reverts (p 0.002).
- **Drift 2024–26:** H100 +3%/yr, B200 +13%/yr.
