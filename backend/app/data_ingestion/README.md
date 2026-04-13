## Data Ingestion (Phase 2)

This package loads and preprocesses the Zomato dataset from Hugging Face and writes:

- `backend/data/processed/restaurants.jsonl`
- `backend/data/processed/indexes.json`
- `backend/data/processed/meta.json`

### Run (Windows / PowerShell)

From the `backend/` directory:

```bash
python -m app.data_ingestion.load_dataset
```

Optional arguments:

```bash
python -m app.data_ingestion.load_dataset --split train --output-dir .\data\processed
```

### Notes
- Hugging Face caching is handled automatically by the `datasets` library.
- The mapper is "best-effort" across common column names; if the dataset schema differs,
  we can tighten the mapping after inspecting the dataset columns.

