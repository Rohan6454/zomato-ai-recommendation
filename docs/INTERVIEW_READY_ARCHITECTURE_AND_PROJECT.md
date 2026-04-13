# Interview-Ready Architecture and Project Draft

## Project Snapshot

Built an AI-powered restaurant recommendation platform (Zomato use case) using a phase-wise architecture:

- **Backend:** FastAPI (Python)
- **Data pipeline:** Hugging Face dataset ingestion + normalization + indexed processed store
- **Recommendation core:** deterministic filtering + scoring + LLM re-ranking/fallback
- **LLM integration:** Gemini-compatible chat completions API with robust parsing/fallback
- **Frontend:** Next.js, preference-driven search + paginated recommendations
- **Observability:** metrics endpoint, request telemetry, feedback capture (SQLite)

## Problem We Solved

Users need personalized, locality-aware restaurant recommendations with explainable reasons, fast response, and usable UI controls (budget, rating, cuisine, locality), while remaining resilient when LLM output is unavailable or imperfect.

## High-Level Architecture

1. **Data Layer**
   - Ingest raw restaurant data.
   - Normalize fields (rating, cuisine lists, cost formats, locality fields).
   - Persist processed artifacts:
     - `restaurants.jsonl`
     - `indexes.json`
     - `meta.json`

2. **Domain/Filtering Layer**
   - Hard filters: locality, optional budget, cuisine, minimum rating.
   - Heuristic pre-ranking using rating, votes, cost penalty, cuisine match score.
   - Progressive relaxation strategy for low-recall cases.
   - Candidate cap for controlled prompt size.

3. **LLM Orchestration Layer**
   - Prompt built from user preferences + pre-filtered candidates.
   - Gemini-compatible client call with retries.
   - Structured JSON parsing and validation.
   - Safe fallback to heuristic results when parsing or LLM call fails.
   - Backfill mechanism ensures stable response size when LLM returns too few items.

4. **API Layer (FastAPI)**
   - `GET /health`
   - `GET /localities`
   - `GET /cuisines` (optionally filtered by locality)
   - `GET /budget-suggestion`
   - `POST /recommendations`
   - `GET /metrics`
   - `POST /feedback`, `GET /feedback`
   - TTL cache for recommendation requests.

5. **Frontend Layer (Next.js)**
   - Landing page for preferences.
   - Results page with pagination (20/page).
   - Query-param-based state transfer and restoration.
   - Locality-aware cuisine suggestions and auto-budget assistance.
   - User-centric explanation cards.

## Recommendation Flow (End-to-End)

1. User selects locality, cuisines, min rating, budget.
2. Frontend fetches helper data (`/localities`, `/cuisines`, `/budget-suggestion`).
3. On `Start Exploring`, frontend calls `POST /recommendations`.
4. Backend:
   - normalizes input,
   - filters + scores candidates,
   - optionally re-ranks with LLM,
   - applies fallback/backfill,
   - returns ranked explanations.
5. Frontend renders paginated cards and lets user return to pre-filled preferences.

## Key Engineering Decisions

- **Hybrid ranking (heuristic + LLM):** stable baseline quality with explainability, plus LLM personalization.
- **LLM failure resilience:** parse guards + deterministic fallback prevent broken user flows.
- **Data-first normalization:** corrected rating/cost parsing avoids empty results and improves filter accuracy.
- **API-driven UI options:** localities/cuisines are not hardcoded, avoiding stale frontend lists.
- **Query-param state:** enables reproducible searches, shareability, and smooth edit-and-return behavior.

## Scalability and Reliability Considerations

- In-memory TTL cache for repeated recommendation requests.
- Candidate capping to limit LLM token/cost overhead.
- Metrics for latency, status classes, cache hit/miss, no-result counts.
- Feedback loop for offline evaluation and future model/ranking tuning.
- Containerized backend path via Dockerfile and deployment notes.

## Notable Challenges and Fixes

- **Sparse/dirty source fields:** handled mixed formats like `4.1/5` and `₹1,500 for two`.
- **Duplicate recommendations:** deduped by normalized identity key.
- **Inconsistent counts:** separated budget estimation sample from unique eligible count.
- **Short LLM outputs:** added heuristic backfill to maintain response size targets.
- **Local dev setup issues:** addressed runtime/tooling constraints and stabilized app startup.

## Interview Talking Points

- I designed for **correctness first** (clean data + deterministic filtering), then layered **personalization** (LLM) safely.
- I implemented **progressive degradation** so the product remains usable even when LLM or external services fail.
- I focused on **human-centered UX iteration** through real user feedback loops (inputs, copy, flow, pagination, trust signals).
- I built **observability and feedback capture** early to support objective iteration beyond anecdotal testing.
- The final system balances **practical product UX**, **engineering reliability**, and **AI-enhanced relevance**.

## 60-Second Interview Pitch

I built an AI restaurant recommendation system with a robust hybrid architecture: deterministic filtering and scoring for reliability, plus Gemini-based re-ranking for personalization and natural explanations. The backend is FastAPI with clean domain modeling, caching, metrics, and feedback capture. The data ingestion pipeline normalizes noisy ratings/cost fields and creates indexed processed artifacts for fast retrieval. The Next.js frontend is API-driven and user-friendly: locality-based cuisine suggestions, auto-budget guidance, and paginated results with preserved search state. The design prioritizes resilience, so if LLM output is malformed or short, the system gracefully falls back and still returns meaningful recommendations.

