## Processed Data Catalog Schema

The current project uses a **file-based processed dataset** (not a SQL database yet).

Processed artifacts are stored in:
- `backend/data/processed/restaurants.jsonl`
- `backend/data/processed/indexes.json`
- `backend/data/processed/meta.json`

---

### 1) `restaurants.jsonl` (JSON Lines)

- **Format**: one JSON object per line.
- **Row count**: see `meta.json` (`restaurant_count`).
- **Purpose**: canonical restaurant records used by the API/recommendation engine.

#### Record schema

| Field | Type | Nullable | Description |
|---|---|---|---|
| `restaurant_id` | string | No | Internal unique id (from source or fallback index). |
| `name` | string | No | Restaurant name. |
| `location_city` | string | No | Normalized locality/city bucket used in filtering. |
| `location_area` | string | Yes | Optional finer-grained area/locality. |
| `address` | string | Yes | Address text from source dataset. |
| `cuisines` | string[] | No | Normalized cuisine list. |
| `avg_cost_for_two` | number | Yes | Estimated average cost for two. |
| `rating` | number | Yes | Rating normalized to 0.0-5.0. |
| `votes` | integer | Yes | Review/vote count. |
| `is_delivery` | boolean | Yes | Delivery availability flag (if present in source). |
| `budget_bucket` | `"low" \| "medium" \| "high"` | Yes | Derived from `avg_cost_for_two` thresholds. |
| `tags` | string[] | No | Derived tags (currently mostly empty). |

#### Example line

```json
{"restaurant_id":"0","name":"Jalsa","location_city":"Banashankari","location_area":null,"address":"942, 21st Main Road, 2nd Stage, Banashankari, Bangalore","cuisines":["North Indian","Mughlai","Chinese"],"avg_cost_for_two":null,"rating":4.1,"votes":775,"is_delivery":null,"budget_bucket":null,"tags":[]}
```

---

### 2) `indexes.json` (Lookup indexes)

- **Format**: single JSON object.
- **Purpose**: precomputed lookups for faster filtering.

#### Top-level schema

| Field | Type | Description |
|---|---|---|
| `city_to_ids` | object<string, string[]> | Map of locality/city -> list of `restaurant_id`. |
| `cuisine_to_ids` | object<string, string[]> | Map of cuisine -> list of `restaurant_id`. |

#### Example

```json
{
  "city_to_ids": { "Banashankari": ["0","1","2"] },
  "cuisine_to_ids": { "North Indian": ["0","1"] }
}
```

---

### 3) `meta.json` (Dataset metadata)

- **Format**: single JSON object.
- **Purpose**: traceability and preprocessing summary.

#### Schema

| Field | Type | Description |
|---|---|---|
| `dataset_id` | string | Source dataset id. |
| `split` | string | Source split used (e.g., `train`). |
| `budget_thresholds.low_max` | number | Upper bound for `low` budget bucket. |
| `budget_thresholds.medium_max` | number | Upper bound for `medium` budget bucket. |
| `restaurant_count` | integer | Number of records in `restaurants.jsonl`. |

---

### Notes

- This is currently a **processed file catalog**; SQL tables are not created yet.
- If you want, I can also create a **SQL-compatible schema** (`CREATE TABLE` statements) for a future Postgres/SQLite migration.

