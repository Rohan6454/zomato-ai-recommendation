## Phase 7 – Observability, Evaluation & Iteration

### 1. Goals
- Gain visibility into how the system behaves in production-like environments.
- Measure recommendation quality and user satisfaction.
- Use insights to iteratively improve filters, prompts, and UX.

### 2. Logging Strategy
- **What to log (server-side)**
  - Request metadata:
    - Timestamp.
    - Approximate location (city only).
    - High-level preferences summary (e.g., budget, min rating, cuisines).
  - Internal processing:
    - Number of candidates after filtering.
    - Number of restaurants sent to the LLM.
    - LLM call duration and token usage (if available).
  - Outcomes:
    - Top N restaurant IDs returned.
    - Whether the response was successful or had errors.

- **What NOT to log**
  - Full free-text notes from the user (or log only in anonymized/hashed form).
  - Any user identifiers if you later add accounts (unless explicitly needed and protected).

### 3. Metrics & Monitoring
- **System metrics**
  - API response time (`/recommendations`).
  - Error rate (HTTP 4xx/5xx).
  - LLM latency and failure rate.

- **Application metrics**
  - Average number of candidates per request.
  - Distribution of ratings among recommended restaurants.
  - Frequency of “no results” cases.

- **Implementation**
  - Start with simple logging and basic counters.
  - Optionally integrate a metrics library (e.g., Prometheus client) for richer dashboards.

### 4. User Feedback Loop
- **UI feedback controls**
  - Optionally include simple feedback buttons on each recommendation:
    - “Helpful” / “Not Helpful”.
  - Or a general “Was this set of recommendations useful?” prompt.

- **Data captured**
  - Recommendation context:
    - Top recommended restaurants.
    - High-level preference summary.
  - Feedback label (`helpful` / `not_helpful`).
  - Store in a lightweight store (e.g., SQLite table).

- **Usage**
  - Analyze feedback periodically to:
    - Identify patterns (e.g., some cuisines or locations consistently underperform).
    - Tweak filter thresholds and prompt wording.

### 5. Offline Evaluation
- **Evaluation scripts**
  - Implement a small module under `evaluation/`:
    - Predefined preference scenarios (e.g., “budget-friendly in Delhi”, “family dinner in Bangalore with high rating”).
    - For each scenario:
      - Run the full recommendation pipeline.
      - Collect outputs (top restaurants and explanations).

- **Quality checks**
  - Manual inspection: sanity check that results roughly match expectations.
  - Quantitative signals (approximate, since we lack explicit labels):
    - Average rating of recommended restaurants.
    - Distribution of costs vs requested budget.
    - Coverage of requested cuisines.

### 6. Prompt & Filter Iteration
- **Prompt iteration**
  - Use evaluation scenarios and live feedback to:
    - Refine prompt instructions.
    - Adjust how candidate data is presented to the LLM.
    - Encourage diversity in recommendations (not just the same top restaurants).

- **Filter iteration**
  - Adjust:
    - Budget bucket thresholds.
    - Heuristic scoring weights (`alpha`, `beta`, cost penalties).
    - Fallback behaviors when no candidates match strict filters.

### 7. Deliverables
- **Code**
  - Logging setup integrated into the backend.
  - `evaluation/` scripts to run scenarios and store results.

- **Artifacts**
  - Simple reports (e.g., Jupyter notebooks or markdown summaries) showing:
    - Example scenarios and outputs.
    - Observed distribution of ratings/costs in recommendations.
  - Notes on any prompt or filter adjustments made based on findings.

