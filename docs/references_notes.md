# Reference notes

Notes on the papers the brief cited. Bibliographic details and abstracts come
from Crossref and arXiv; full texts of the two SSRN papers could not be read
from this environment (docs/blockers.md B3).

## Schwartz and Smith (2000)

"Short-Term Variations and Long-Term Dynamics in Commodity Prices",
*Management Science* 46(7):893-911, doi:10.1287/mnsc.46.7.893.12034. Read in
full from the author-hosted PDF. Equations used are in
docs/term_structure_model.md.

## Bandi and Su (2026), arXiv:2607.12156

"(Early) AI Compute Asset Pricing", Johns Hopkins, v3 2026-09-10. Read in full.

- Compute cannot be stored, so cost-of-carry fails.
- Term-rental contracts give a no-arbitrage reference for synthetic futures,
  probably an upper bound because physical term rentals bundle an access
  option (their "physical access wedge").
- Futures equal expected spot minus a risk premium. Their synthetic futures
  returns suggest large premia, for example H100 hold-to-maturity returns of
  13.4% on average across 1 to 12 months (26.2% annualized).
- Their Table 2 gives the dense 8-bit throughput figures used in
  docs/relative_value.md.
- It contains no state-variable model, depreciation process or launch jumps.

## Assody (2026), SSRN 6926798 (abstract only)

"Pricing Compute Futures: Forward Curve and Volatility for a Non-Storable,
Depreciating Commodity". The abstract describes a Schwartz-Smith model with a
scheduled jump at each announced hardware launch window, priced with Black-76.
It reports a jump size clustering at about -0.22 in log terms per generational
transition, incumbent depreciation of 15 to 20% a year, structural
backwardation, and implied-volatility bumps at launch windows. These figures
are our priors.

## Lee and Nagaraj (2026), SSRN 7342241 (abstract only)

"Pricing, Hedging, and Securitizing AI Compute: A Non-Storable Commodity
Framework for Infrastructure Risk". A seasonal Schwartz-Smith process with
upward, fast-reverting spikes, plus a token-price layer with downward
efficiency jumps. Not used.

## To complete these notes

Download the two SSRN PDFs in a browser and save them in `references/`
(git-ignored), or paste the model equations and parameter tables here. A
later session can then check our specification against Assody's.
