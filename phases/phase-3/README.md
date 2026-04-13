## Phase 3 – Core Filtering Engine (Non-LLM)

### What this phase delivers
- Deterministic filtering of restaurants **before** any LLM call.
- Heuristic pre-ranking to:
  - Improve result quality before LLM re-ranking.
  - Reduce candidate count passed into prompts (cost/latency control).
- Progressive relaxation when no candidates match strict filters.

### Architecture doc
- `architecture/phase-3-filtering-engine.md`

### Key backend files (implemented in this phase)
- `backend/app/core/models.py`
  - `UserPreferences` shared model.
- `backend/app/core/filtering/engine.py`
  - `filter_candidates(...)` filtering + scoring + capping + relaxation.
- `backend/tests/test_filtering_engine.py`
  - Unit tests using a synthetic dataset.

### Phase bundle (this folder)
- `docs/phase-3-filtering-engine.md` (copy of the phase spec)
- `deliverables.md` (manifest of implementation files)

### How to run tests (from `backend/`)

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

