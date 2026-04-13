## Phase 5 Deliverables Manifest

### Docs (copied into this phase bundle)
- `phases/phase-5/docs/phase-5-backend-api.md`

### Implementation files (runtime locations)
- `backend/app/main.py` (CORS + route registration)
- `backend/app/api/`
  - `__init__.py`
  - `models.py`
  - `dependencies.py`
  - `routes/__init__.py`
  - `routes/recommendations.py`
- `backend/tests/test_api_phase5.py`

### Test cases executed
- `GET /health` returns 200 with status `ok`
- `POST /recommendations` returns recommendation list for valid input
- `POST /recommendations` returns validation error for invalid `min_rating`

