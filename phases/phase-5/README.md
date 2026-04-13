## Phase 5 – Backend API Layer

### What this phase delivers
- REST API endpoints for recommendations (e.g., `POST /recommendations`).
- Request validation and response schema.
- CORS setup and dependency wiring to recommendation engine.
- Processed-data dependency for restaurant loading from Phase 2 output.

### Architecture doc
- `architecture/phase-5-backend-api.md`

### Key backend files (implemented in this phase)
- `backend/app/main.py`
- `backend/app/api/`
  - `models.py`
  - `dependencies.py`
  - `routes/recommendations.py`
- `backend/tests/test_api_phase5.py`

### Phase bundle (this folder)
- `docs/phase-5-backend-api.md` (copy of the phase spec)
- `deliverables.md` (manifest of implementation files + tested cases)

