## Phase 7 – Observability, Evaluation & Iteration

### What this phase delivers
- Server-side logging/metrics for:
  - Request counts, latency, error rates
  - LLM latency/token usage (if available)
- Optional user feedback capture (“Helpful/Not helpful”)
- Offline evaluation scripts and scenario runs

### Architecture doc
- `architecture/phase-7-observability-evaluation.md`

### Key implemented files
- `backend/app/observability/metrics.py`
- `backend/app/observability/feedback_store.py`
- `backend/app/api/routes/recommendations.py` (`/metrics`, `/feedback`)
- `backend/evaluation/run_scenarios.py`
- `backend/tests/test_observability_phase7.py`

### Phase bundle (this folder)
- `docs/phase-7-observability-evaluation.md` (copy of phase spec)
- `deliverables.md` (manifest of implementation + outputs)

