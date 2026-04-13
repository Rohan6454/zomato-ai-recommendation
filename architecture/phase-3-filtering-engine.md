## Phase 3 – Core Filtering Engine (Non-LLM)

### 1. Goals
- Implement deterministic, structured filtering of restaurants before invoking the LLM.
- Reduce the number of restaurants passed to the LLM to control cost and latency.
- Provide a clear, testable function that transforms user preferences into a candidate list.

### 2. User Preferences Model
Define a preferences object used across the backend, for example:

- `location_city`: city name (required).
- `location_area`: optional area or locality.
- `budget_bucket`: one of `low | medium | high | any`.
- `cuisines`: list of preferred cuisines (can be empty).
- `min_rating`: minimum acceptable rating (e.g., 3.5).
- `extras`: list of extra constraints (e.g., `["family_friendly", "quick_service"]`).

This model should be shared between the API layer and the recommendation engine.

### 3. Filtering Pipeline
Implement a module like `core/filtering/engine.py` with a main function:

- `filter_candidates(preferences) -> List[Restaurant]`

Steps inside the function:

1. **Location filter**
   - Start with all restaurants in `location_city`.
   - If `location_area` is provided, further restrict to that area (if available in data).

2. **Budget filter**
   - If `budget_bucket != "any"`, filter restaurants to those whose derived `budget_bucket` matches.

3. **Cuisine filter**
   - If `cuisines` list is non-empty:
     - Keep restaurants where at least one cuisine matches (case-insensitive).
   - Optionally, prioritize restaurants that match more than one requested cuisine.

4. **Rating filter**
   - Keep only restaurants with `rating >= min_rating` (if rating present).
   - Decide whether to allow restaurants with missing ratings (likely exclude).

5. **Extras filter (optional/heuristic)**
   - For each extra constraint (e.g., `family_friendly`, `quick_service`):
     - If tags/metadata are available, filter or down-rank restaurants that do not match.
   - If tags are not explicit, this may be deferred to LLM reasoning.

### 4. Pre-LLM Ranking Heuristic
After filtering, compute a simple heuristic score to sort candidates before sending them to the LLM:

- Example scoring formula:
  - `score = rating * alpha + log(votes + 1) * beta - cost_penalty`
  - Where:
    - `alpha`, `beta` are tunable weights.
    - `cost_penalty` increases with `avg_cost_for_two` if the user wants budget-friendly options.

- Steps:
  - Compute `score` for each candidate.
  - Sort in descending order of score.
  - Keep only the top `N` (e.g., 30–50) for the LLM.

### 5. Edge Cases & Fallbacks
- **No candidates found**
  - Relax filters progressively, e.g.:
    - Drop `extras` constraints.
    - Lower `min_rating`.
    - Expand beyond `location_area` to entire `location_city`.
  - Return a smaller candidate set and let the LLM explain trade-offs (e.g., “these are slightly below your requested rating”).

- **Too many candidates**
  - After ranking, cap at `N` to limit prompt size.
  - Consider capping per cuisine or per area to maintain diversity.

### 6. Testing Strategy
- Unit tests for `filter_candidates`:
  - Different combinations of preferences (only city, city + budget, city + cuisine + rating, etc.).
  - Edge cases: no matches, many matches, all filters off.

- Property-style checks:
  - All results satisfy the hard constraints (city, rating, budget).

### 7. Deliverables
- **Code**
  - `core/filtering/engine.py` (or equivalent):
    - Implements the full filtering and pre-LLM ranking pipeline.

- **Tests**
  - Test module like `tests/test_filtering_engine.py` with:
    - Synthetic small dataset or fixtures.
    - Clear checks of filter behavior.

