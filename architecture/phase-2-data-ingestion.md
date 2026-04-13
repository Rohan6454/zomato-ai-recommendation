## Phase 2 – Data Ingestion & Preprocessing

### 1. Goals
- **Load** the Zomato dataset from Hugging Face.
- **Normalize and clean** the data into a consistent internal schema.
- **Index** the data to support fast filtering by location, budget, cuisine, and rating.

### 2. Dataset Access
- **Source**
  - Hugging Face dataset: `ManikaSaini/zomato-restaurant-recommendation`.
- **Access Approach**
  - Use the `datasets` Python library or direct HTTP download.
  - Provide a small CLI script to pull and cache the dataset locally.

### 3. Internal Restaurant Schema
Define a consistent internal representation for each restaurant, for example:

- **Core fields**
  - `restaurant_id`: unique identifier.
  - `name`: restaurant name.
  - `location_city`: city (e.g., Delhi, Bangalore).
  - `location_area`: area or locality (if available).
  - `address`: full address or short description.
  - `cuisines`: list of cuisines (e.g., `["Italian", "Chinese"]`).
  - `avg_cost_for_two`: numeric average cost.
  - `rating`: float rating (e.g., 4.1).
  - `rating_count` / `votes`: number of ratings or reviews.
  - `is_delivery`: boolean flag for delivery support (if present).

- **Derived fields (optional)**
  - `budget_bucket`: `low | medium | high`, derived from `avg_cost_for_two`.
  - `tags`: list capturing special attributes (e.g., `family_friendly`, `quick_service`, `romantic`), derived from text fields if available.

### 4. Ingestion Pipeline Modules
Implement a small pipeline in a directory such as `data_ingestion/`:

- **`dataset_client`**
  - Functions to:
    - Download/load the raw dataset.
    - Cache locally to avoid repeated downloads.

- **`schema_mapper`**
  - Map raw dataset columns to the internal schema fields.
  - Handle renaming, type casting, and field extraction.

- **`cleaning`**
  - Normalize values:
    - Coerce ratings to floats, handle missing ratings.
    - Split cuisines text into a list of standardized strings.
    - Normalize city and area names (trim spaces, consistent casing).
  - Handle missing data:
    - Drop unusable rows (e.g., missing key identifiers).
    - Provide sensible defaults when appropriate.

- **`index_builder`**
  - Build indices or helper structures for fast lookup, e.g.:
    - Map from `city → list[restaurant_id]`.
    - Map from `cuisine → list[restaurant_id]`.
    - Pre-computed lists of restaurants sorted by rating within each city.

### 5. Storage Strategy
- **Prototype**
  - Load the cleaned data into memory at application startup.
  - Represent as:
    - `restaurants_by_id: Dict[restaurant_id, Restaurant]`.
    - `index_city: Dict[city, List[restaurant_id]]`.
    - `index_cuisine: Dict[cuisine, List[restaurant_id]]`.

- **Next Step (Optional)**
  - Persist into SQLite/Postgres:
    - `restaurants` table with core fields.
    - Optional `restaurant_tags` table for derived tags.
  - Use simple SQL queries to support filters.

### 6. Budget Buckets & Rating Normalization
- **Budget buckets**
  - Example mapping (tune thresholds based on dataset distribution):
    - `low`: `avg_cost_for_two <= X`.
    - `medium`: `X < avg_cost_for_two <= Y`.
    - `high`: `avg_cost_for_two > Y`.
  - Store these thresholds as configuration.

- **Rating normalization**
  - Ensure all ratings are:
    - Floats between 0 and 5.
    - Replace non-numeric or missing ratings with `None` or a default.

### 7. Deliverables
- **Code**
  - `data_ingestion/load_dataset.py` (or similar):
    - Download and cache the raw dataset.
    - Convert to internal schema.
    - Serialize cleaned data (e.g., to JSON, parquet, or DB).

- **Documentation**
  - Short README in `data_ingestion/` explaining:
    - How to run the ingestion script.
    - The internal restaurant schema.
    - Any assumptions or thresholds (e.g., budget ranges).

