# Relative value: H100 versus B200 per unit of compute

Code: `src/compute_curve/models/relative_value.py`.

## Definition

Let `r` be the throughput of one B200 relative to one H100. One H100-hour of
compute bought on B200 costs `P_B200 / r`. The log spread

```
s_t = ln P_B200,t - ln r - ln P_H100,t
```

is zero when both deliver compute at the same price. It is positive when B200
is the dearer way to buy compute. The break-even ratio is
`r* = P_B200 / P_H100`: B200 is cheaper per unit of compute exactly when the
true `r` exceeds `r*`.

## The throughput ratio is an assumption

| Basis | B200 / H100 | Source |
|---|---|---|
| Peak dense 8-bit tensor throughput, 5.000 vs 1.979 POPS | 2.53 | Bandi and Su (2026), Table 2 |
| HGX B200 dense FP8 (4.5 PF per GPU) vs H100 SXM (1.979 PF) | about 2.27 | NVIDIA datasheets (values recalled, not re-fetched this session) |
| HBM bandwidth, 8 vs 3.35 TB/s | about 2.39 | NVIDIA datasheets (same caveat) |

Real workloads differ: memory-bound inference gains more from capacity and
bandwidth, and small models may not use the extra compute. The config uses
**2.5 central, 1.8 to 3.0 range**. A conclusion counts only if it holds across
the whole range.

## Trading rule (shadow until validated)

Fade large deviations of `s` on second-month futures: when the z-score of `s`
against its previous 60 values exceeds 2, short GPU2 and buy GPU1 in matching
notional (and the reverse below -2); exit when the z-score falls back inside
0.5. It runs only after hypothesis H4 (mean reversion beats a random walk out
of sample) is validated on futures data (docs/research_plan.md).

## What the data say today

Descriptive only; see `reports/evaluation.md` for the current numbers. The
break-even ratio from our indices lies inside the assumed 1.8 to 3.0 range.
So whether B200 is the cheaper way to buy compute **depends on the
workload's true ratio**: it is cheaper at the central 2.5, but not at the low
end of the range. The spread history is shorter than the 120 days the
forecast test requires.
