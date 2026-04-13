## Phase 2 – Data Ingestion & Preprocessing

### What this phase delivers
- A reproducible loader that pulls the Zomato dataset from Hugging Face.
- Normalization into an internal schema and data cleaning.
- Derived fields (e.g., `budget_bucket`).
- Simple indices to speed up filtering (city/cuisine lookups).
- Outputs written to `backend/data/processed/` so later phases can load quickly.

### Architecture doc
- `architecture/phase-2-data-ingestion.md`

### Key backend files (implemented in this phase)
- `backend/app/data_ingestion/`
  - `dataset_client.py`
  - `schema.py`
  - `cleaning.py`
  - `index_builder.py`
  - `load_dataset.py` (CLI entry)

### Outputs
- `backend/data/processed/restaurants.jsonl`
- `backend/data/processed/indexes.json`

### Phase bundle (this folder)
- `docs/phase-2-data-ingestion.md` (copy of the phase spec)
- `deliverables.md` (manifest of implementation files + outputs)

