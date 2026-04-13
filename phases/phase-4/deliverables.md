## Phase 4 Deliverables Manifest

### Docs (copied into this phase bundle)
- `phases/phase-4/docs/phase-4-llm-integration.md`

### Implementation files (runtime locations)
- `backend/requirements.txt` (adds `httpx`)
- `backend/app/llm/`
  - `__init__.py`
  - `client.py`
  - `prompting.py`
  - `parsing.py`
- `backend/app/recommendation/`
  - `__init__.py`
  - `engine.py`
- `backend/tests/`
  - `test_llm_prompting_parsing.py`
  - `test_recommendation_engine_phase4.py`

