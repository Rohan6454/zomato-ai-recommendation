# Frontend UX Change Log (User-Requested Improvements)

This document captures all major frontend changes requested during implementation to improve usability, trust, and recommendation clarity.

## 1) Input and Preference Collection

- Replaced free-text locality with a locality dropdown sourced from backend unique values (`GET /localities`).
- Removed duplicate locality entries by using backend deduplicated list.
- Set and later removed default locality behavior based on updated UX direction.
- Replaced budget tier dropdown with numeric input: `Max cost for two`.
- Removed `Location Area (optional)` input to reduce friction.
- Removed `Extras` input from UI to keep preferences focused and simple.
- Updated location prompt text to `Where do you wanna go today?`.
- Removed Step labels (`Step 1/2/3/4`) for cleaner, less instructional layout.
- Removed location image/map block from location card to reduce visual clutter.
- Tightened spacing around location section and card content.

## 2) Culinary Focus UX

- Replaced hardcoded cuisine chips with backend-driven cuisine values (`GET /cuisines`).
- Ensured cuisine options are only those available in dataset.
- Added locality-aware cuisine suggestions by filtering cuisines with selected locality.
- Replaced clustered cuisine selector with free-text cuisine input + suggestion list.
- Added multi-selection workflow:
  - click suggestion to add cuisine,
  - press Enter to add best match,
  - use `Add cuisine` action button,
  - remove selected cuisines via chips.

## 3) Budget Assist and Transparency

- Added automatic budget suggestion (`GET /budget-suggestion`) based on selected filters.
- Budget auto-fills when user has not manually edited budget.
- Once user edits budget, manual value is respected (no forced overwrite).
- Improved budget hint text to clearly distinguish:
  - priced sample used for estimation,
  - unique restaurants eligible for the same filter set.

## 4) Recommendation Experience

- Created dedicated second page for results (`/results`) instead of rendering inline on landing page.
- `Start Exploring` now navigates with query params (shareable/replayable search state).
- `Update preferences` preserves previous filters by routing back with same query string.
- Added result cards with rank, rating, cost, cuisines, and personalized reason text.
- Added empty-state guidance when no recommendations match.

## 5) Results Quantity and Pagination

- Increased backend recommendation cap from 8 to 50 to support broader browsing.
- Added results pagination with 20 restaurants per page.
- Added Previous/Next controls and current range display (`Showing X-Y of Z`).

## 6) Personalization and Trust Signals in Cards

- Removed explicit `heuristic ranking` wording from customer-facing explanations.
- Added personalized reasoning using:
  - matched or prominent cuisines,
  - vote volume as confidence/trust signal.
- Updated cost display fallback from confusing `N/A` wording to customer-friendly `Not listed`.

## 7) Reliability and Consistency Fixes

- Fixed duplicate restaurant display via deduplication before response rendering.
- Improved recommendation count consistency by:
  - clarifying estimation sample vs unique eligible count,
  - backfilling results when LLM output is short.
- Ensured return-to-search keeps user context and reduces repeat input.

## Outcome

These changes transformed the UI from a basic prototype into a clearer, lower-friction recommendation workflow with:

- better discoverability,
- less input confusion,
- more trustworthy recommendation explanations,
- and stronger continuity between search and results.

