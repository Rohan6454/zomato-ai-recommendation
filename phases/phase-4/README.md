## Phase 4 – LLM Integration & Prompt Orchestration

### What this phase delivers
- LLM client abstraction (provider-agnostic).
- Prompt builder to send user preferences + candidate restaurants.
- Robust response parsing into structured ranked recommendations with explanations.
- Recommendation orchestrator that combines:
  - Phase 3 filtering + heuristic pre-ranking
  - Phase 4 LLM re-ranking + explanation generation
  - Heuristic fallback if LLM output is invalid/unparseable

### Architecture doc
- `architecture/phase-4-llm-integration.md`

### Key backend files (implemented in this phase)
- `backend/app/llm/`
  - `client.py` (LLM client abstraction + OpenAI-compatible HTTP client + test mock)
  - `prompting.py` (prompt builder)
  - `parsing.py` (robust JSON extraction/parsing/validation)
- `backend/app/recommendation/engine.py`
  - `recommend(...)` orchestrator combining filtering + LLM

### Tests added in this phase
- `backend/tests/test_llm_prompting_parsing.py`
- `backend/tests/test_recommendation_engine_phase4.py`

### Phase bundle (this folder)
- `docs/phase-4-llm-integration.md` (copy of the phase spec)
- `deliverables.md` (manifest of implementation files)

### How to run tests (from `backend/`)

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

