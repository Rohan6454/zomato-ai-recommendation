## Phase 7 Deliverables Manifest

### Docs (copied into this phase bundle)
- `phases/phase-7/docs/phase-7-observability-evaluation.md`

### Implementation files (runtime locations)
- `backend/app/observability/`
  - `__init__.py`
  - `metrics.py`
  - `feedback_store.py`
- `backend/app/api/routes/recommendations.py`
  - observability logs
  - `GET /metrics`
  - `POST /feedback`
  - `GET /feedback`
- `backend/app/main.py`
  - request-latency/status middleware
- `backend/tests/test_observability_phase7.py`
- `backend/evaluation/`
  - `__init__.py`
  - `run_scenarios.py`
- `backend/evaluation/reports/`
  - `scenario_results.json`
  - `scenario_summary.md`

### Verification
- Backend tests pass including observability tests.
- Evaluation script runs and produces report artifacts.

