## Phase 2 Deliverables Manifest

### Docs (copied into this phase bundle)
- `phases/phase-2/docs/phase-2-data-ingestion.md`

### Implementation files (runtime locations)
- `backend/requirements.txt` (adds `datasets`, `pandas`)
- `backend/app/__init__.py`
- `backend/app/data_ingestion/`
  - `__init__.py`
  - `README.md`
  - `schema.py`
  - `dataset_client.py`
  - `cleaning.py`
  - `index_builder.py`
  - `load_dataset.py`

### Outputs produced by Phase 2 loader
- `backend/data/processed/restaurants.jsonl`
- `backend/data/processed/indexes.json`
- `backend/data/processed/meta.json`

