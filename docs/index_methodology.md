# Our H100 and B200 on-demand index: methodology

Code: `src/compute_curve/index/own_index.py`. Output: `reports/own_index.csv`
and `reports/own_index.md`, rebuilt by `uv run compute-curve index`.

## Purpose

An independent daily reading of neocloud on-demand rental prices for H100 and
B200, built only from listings we collect or are licensed to use. It is the
input to the nowcast (claim 1) and the relative-value analysis. It is not the
settlement index and is not calibrated to it.

## Inputs

Approved sources only (docs/data_sources.md). Each row is one listing price
in USD per GPU-hour. Instance prices are divided by the GPU count. Provider
names are canonicalized (for example `datacrunch` becomes `verda`).

## Construction (pre-registered 2026-10-05)

1. **Date each snapshot.** A snapshot's time is the latest observation time
   among its rows: our receive time for direct fetches, or the publisher's
   own fetch time for aggregator files. Every row in a snapshot gets that
   date, including stale rows the publisher carried forward, because that is
   what a reader saw on that day. For each source and date only the latest
   snapshot is kept.
2. **Filter.** Keep a listing if all of these hold:
   - term is on-demand;
   - availability is not "unavailable";
   - GPU variant is allowed (H100: SXM, PCIe, NVL, NVLink, unknown; B200:
     SXM, unknown);
   - the provider is not a hyperscaler (AWS, Azure, GCP, OCI), because the
     settlement index is neocloud-only;
   - the provider's terms do not forbid index use (Vast.ai and RunPod are
     dropped at collection);
   - the region is US, North America or unknown. The contracts specify
     "Geography: United States", but most sources state no region, so unknown
     is kept.
3. **One source per provider per day.** When several sources report the same
   provider, keep the highest-priority source: direct provider pages first,
   then Lium, gpurentalprices.com, and the Computable GPU Index receipts last.
4. **Aggregate (primary method).** Provider-weighted median. Each provider
   carries a total weight of 1, split equally across its listings, and the
   index is the weighted median of listing prices. A marketplace with dozens
   of listings therefore counts as much as a provider with one list price.
5. **Coverage.** A day counts only with at least 3 providers and 5 listings.

## Two series

| Series | Sources | Use |
|---|---|---|
| `headline` | All approved sources | Best coverage. Its composition changes when sources are added (it jumped on 2026-10-05 when our direct collectors started), so it is not used for time-series models |
| `history_panel` | gpurentalprices.com archive and live feed only, on a provider panel fixed from the first 30 days (providers present on at least 90% of those days) | Stable composition from 2026-08-18. Models and evaluations use this series |

The panel is chosen from the first 30 days only, and those days are dropped
from the series. Choosing it from the full sample would use knowledge of which
providers survive, which is look-ahead.

## Comparison with Silicon Data's method

| Step | Silicon Data (public methodology summary) | Ours |
|---|---|---|
| Inputs | 10,000+ daily records from 40+ providers, including marketplaces; the B200 page also mentions colocation and private-market observations | 9 approved sources, about 20 H100 and 10 B200 providers |
| Normalization | Proprietary basis adjustment to a benchmark contract (rental type, country, CPU platform, GPU variant), recalibrated weekly | None beyond per-GPU-hour pricing and the filters above |
| Aggregation | Weighted mean of provider means; weights reflect "market relevance" and are not disclosed | Provider-weighted median with equal provider weights |
| Geography | Settlement configuration: United States | US, North America or unknown |
| Calendar | Published every business day; the settlement average uses Business Days | Every calendar day; the contract arithmetic uses Business Days |

Expect a persistent level difference (basis) and different dynamics.

## Tracking error against the published index

Planned method (`src/compute_curve/index/tracking.py`): on days with both
values, the log error `ln J_d - ln I_d`, its mean and RMSE, and the correlation
of daily log changes, each with a circular block bootstrap 95% CI. At least
20 overlapping days are required.

**Status: not computable.** No settlement-index history can be stored without
a licence (docs/blockers.md B7). For context only, on 2026-10-05 the public
Silicon Data pages showed 2.81 (H100) and 5.87 (B200). Our headline index read
3.20 and 6.25, which is 14% and 6% higher. This is one observation, and the
public figure is not the US-geography settlement configuration. It supports
no conclusion about tracking error.

## Known limitations

- **List prices, not transactions.** Most inputs are posted prices. Realized
  prices and discounts are unobserved.
- **Sticky prices.** The H100 history-panel index is unchanged on 88% of
  days; daily changes come from a handful of providers repricing.
- **Small B200 panel.** The fixed B200 panel has 8 providers, so one
  provider's repricing can move the median.
- **No basis adjustment.** SXM and PCIe listings are pooled, which a
  benchmark-contract adjustment would correct.
- **Region mostly unknown.** The US-geography restriction is only partly
  enforced.

## Declared variants

Primary: `index.provider_weighted_median`. Robustness variants:
`index.pooled_median` and `index.trimmed_mean_10`. Neither variant has been
run. Any variant run is logged in `docs/variants_log.md`.
