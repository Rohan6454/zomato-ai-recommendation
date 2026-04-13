## Phase 4 – LLM Integration & Prompt Orchestration

### 1. Goals
- Integrate an LLM to:
  - Re-rank filtered candidate restaurants.
  - Generate human-like explanations for each recommendation.
  - Optionally summarize the overall set of choices.
- Keep prompts compact and structured to control cost and ensure reliable parsing.

### 2. LLM Client Abstraction
Create a thin wrapper around the chosen LLM provider in `llm/client.py`:

- Interface example:
  - `generate(prompt: str, *, model: str, temperature: float, max_tokens: int) -> str`
- Responsibilities:
  - Add provider-specific headers, authentication, and params.
  - Load the **Gemini API key** from a `.env` file (do not hardcode secrets).
  - Retry on transient errors (e.g., network issues, rate limits).
  - Log request metadata (not full user content, for privacy).

This abstraction allows you to swap providers or models with minimal changes.

**LLM choice for this project**
- We will use **Google Gemini** as the LLM provider.
- The API key will be stored in `.env` (e.g., `GEMINI_API_KEY=...`) and read at runtime.

### 3. Prompt Builder
Implement a `prompt_builder` in `llm/prompting.py`:

- **Input**
  - User preferences object.
  - Candidate restaurant list (already filtered and heuristically ranked).

- **Structure**
  - **System message**
    - Explain the assistant’s role, e.g.:
      - “You are an expert restaurant recommendation assistant. You must choose the best restaurants given user preferences and the structured data provided.”
  - **User message**
    - Summarize user preferences in natural language.
    - Provide the candidate restaurants as a concise table or list, e.g.:
      - `ID | Name | City | Cuisine(s) | Rating | CostBucket | Key Tags`
    - Provide explicit instructions:
      - Rank the top `K` restaurants (e.g., 5–10).
      - For each, return:
        - `id`
        - `rank`
        - `short_explanation` (1–3 sentences explaining why it fits).
      - Return the result in a machine-readable JSON-like structure.

### 4. Response Format & Parsing
Implement a parser in `llm/parsing.py`:

- **Expected response format**
  - Ask the LLM to respond with JSON inside markdown code fences, e.g.:
    - ```json
      [
        {"id": "123", "rank": 1, "short_explanation": "..."},
        ...
      ]
      ```
- **Parsing steps**
  - Extract the JSON block from the LLM output (strip code fences if present).
  - Parse into Python objects.
  - Validate:
    - Each item has `id`, `rank`, and `short_explanation`.
    - `id` corresponds to a known candidate restaurant.
  - Map each parsed entry back to the full restaurant object.

- **Robustness**
  - If parsing fails:
    - Attempt simple cleanup (fix trailing commas, stray text).
    - If still failing, fall back to:
      - A simpler non-LLM ranking (heuristic only), or
      - A second, more constrained LLM call.

### 5. Recommendation Orchestrator
Create a central orchestration function in `recommendation/engine.py`:

- `recommend(preferences) -> List[Recommendation]`

Where `Recommendation` contains:
- `restaurant` (full restaurant object).
- `rank`.
- `explanation` (LLM-generated text).

**Pipeline steps:**
1. Call `filter_candidates(preferences)` to get candidate restaurants.
2. If the candidate list is empty:
   - Return an appropriate “no results” response or trigger a fallback strategy.
3. Build the LLM prompt with `build_prompt(preferences, candidates)`.
4. Call `llm_client.generate(...)` to get the response text.
5. Parse the response into structured recommendations.
6. Sort recommendations by `rank` (ascending).
7. Return the final list of `Recommendation` objects.

### 6. Cost & Token Management
- **Input size control**
  - Limit number of candidates (e.g., 30–50 max).
  - Use short field names and omit non-essential details.

- **Output size control**
  - Ask for a small, fixed number of recommendations (e.g., top 5–10).
  - Encourage short explanations (1–3 sentences).

### 7. Testing Strategy
- **Unit tests**
  - Test prompt construction with mocked candidates and preferences.
  - Test response parsing with hand-crafted sample responses (including slightly malformed ones).

- **Integration tests**
  - Use a mocked LLM client that returns deterministic JSON.
  - Test the full `recommend(preferences)` flow without external calls.

### 8. Deliverables
- **Code**
  - `llm/client.py` – provider-agnostic client.
  - `llm/prompting.py` – prompt builder.
  - `llm/parsing.py` – robust response parser.
  - `recommendation/engine.py` – orchestrator combining filtering + LLM.

- **Docs**
  - Brief explanation of prompt design and rationale.
  - Guidelines on tuning temperature, max tokens, and candidate counts.

