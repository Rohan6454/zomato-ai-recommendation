from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .cleaning import (
    budget_thresholds_from_costs,
    derive_budget_bucket,
    extract_tags,
    normalize_area,
    normalize_bool,
    normalize_city,
    normalize_cost,
    normalize_cuisines,
    normalize_float,
    normalize_int,
    normalize_rating,
    normalize_str,
)
from .dataset_client import DATASET_ID, iter_records, load_hf_dataset
from .index_builder import build_indexes
from .schema import Restaurant


def _pick_first_present(record: Dict[str, Any], keys: List[str]) -> Any:
    for k in keys:
        if k in record and record[k] not in (None, ""):
            return record[k]
    return None


def map_record_to_restaurant(record: Dict[str, Any], *, fallback_id: str) -> Optional[Restaurant]:
    """
    Best-effort mapping from dataset row to internal `Restaurant` schema.

    Since public datasets often differ in column naming, we use a flexible mapping:
    each internal field tries multiple likely source keys.
    """
    name = normalize_str(_pick_first_present(record, ["name", "restaurant_name", "Restaurant Name", "Restaurant"]))
    if not name:
        return None

    restaurant_id = normalize_str(
        _pick_first_present(record, ["restaurant_id", "id", "res_id", "Restaurant ID", "Restaurant_Id"])
    ) or fallback_id

    city = normalize_city(_pick_first_present(record, ["city", "location", "Location", "City"]))
    if not city:
        # city is required for the Phase 3 filtering model
        return None

    area = normalize_area(_pick_first_present(record, ["area", "locality", "Locality", "Area"]))
    address = normalize_str(_pick_first_present(record, ["address", "Address"]))

    cuisines = normalize_cuisines(_pick_first_present(record, ["cuisines", "Cuisines", "cuisine"]))

    avg_cost_for_two = normalize_cost(
        _pick_first_present(
            record,
            [
                "avg_cost_for_two",
                "average_cost_for_two",
                "Average Cost for two",
                "Average_Cost_For_Two",
                "cost_for_two",
                "Cost for two",
                "approx_cost(for two people)",
                "Approx cost(for two people)",
                "Approx Cost(For Two People)",
                "average_cost",
            ],
        )
    )

    rating = normalize_rating(
        _pick_first_present(record, ["rating", "rate", "Rate", "Aggregate rating", "Aggregate_Rating", "Rating"])
    )
    votes = normalize_int(_pick_first_present(record, ["votes", "Votes", "rating_count", "Rating count", "Rating_Count"]))
    is_delivery = normalize_bool(_pick_first_present(record, ["is_delivery", "Has Online delivery", "online_delivery"]))

    tags = extract_tags(record)

    return Restaurant(
        restaurant_id=str(restaurant_id),
        name=name,
        location_city=city,
        location_area=area,
        address=address,
        cuisines=cuisines,
        avg_cost_for_two=avg_cost_for_two,
        rating=rating,
        votes=votes,
        is_delivery=is_delivery,
        budget_bucket=None,  # derived after thresholds computed
        tags=tags,
    )


def load_and_process(
    *,
    dataset_id: str = DATASET_ID,
    split: str = "train",
) -> Dict[str, Any]:
    ds = load_hf_dataset(split=split, dataset_id=dataset_id)

    restaurants: List[Restaurant] = []
    costs: List[float] = []

    for idx, record in enumerate(iter_records(ds)):
        r = map_record_to_restaurant(record, fallback_id=str(idx))
        if r is None:
            continue
        restaurants.append(r)
        if r.avg_cost_for_two is not None:
            costs.append(r.avg_cost_for_two)

    low_max, medium_max = budget_thresholds_from_costs(costs)

    restaurants_derived: List[Restaurant] = []
    for r in restaurants:
        bucket = derive_budget_bucket(r.avg_cost_for_two, low_max=low_max, medium_max=medium_max)
        restaurants_derived.append(
            Restaurant(
                restaurant_id=r.restaurant_id,
                name=r.name,
                location_city=r.location_city,
                location_area=r.location_area,
                address=r.address,
                cuisines=r.cuisines,
                avg_cost_for_two=r.avg_cost_for_two,
                rating=r.rating,
                votes=r.votes,
                is_delivery=r.is_delivery,
                budget_bucket=bucket,
                tags=r.tags,
            )
        )

    indexes = build_indexes(restaurants_derived)

    return {
        "dataset_id": dataset_id,
        "split": split,
        "budget_thresholds": {"low_max": low_max, "medium_max": medium_max},
        "restaurant_count": len(restaurants_derived),
        "restaurants": restaurants_derived,
        "indexes": indexes,
    }


def write_outputs(
    result: Dict[str, Any],
    *,
    output_dir: Path,
) -> Dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)

    restaurants_path = output_dir / "restaurants.jsonl"
    indexes_path = output_dir / "indexes.json"
    meta_path = output_dir / "meta.json"

    restaurants: List[Restaurant] = result["restaurants"]
    indexes = result["indexes"]

    with restaurants_path.open("w", encoding="utf-8") as f:
        for r in restaurants:
            f.write(json.dumps(r.to_dict(), ensure_ascii=False) + "\n")

    with indexes_path.open("w", encoding="utf-8") as f:
        json.dump(indexes, f, ensure_ascii=False, indent=2)

    meta = {
        "dataset_id": result["dataset_id"],
        "split": result["split"],
        "budget_thresholds": result["budget_thresholds"],
        "restaurant_count": result["restaurant_count"],
    }
    with meta_path.open("w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    return {
        "restaurants_jsonl": str(restaurants_path),
        "indexes_json": str(indexes_path),
        "meta_json": str(meta_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Load and preprocess the Zomato dataset (Phase 2).")
    parser.add_argument("--dataset-id", default=DATASET_ID, help="Hugging Face dataset id.")
    parser.add_argument("--split", default="train", help="Dataset split name (e.g., train).")
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parents[2] / "data" / "processed"),
        help="Directory to write processed outputs (restaurants + indexes).",
    )
    args = parser.parse_args()

    result = load_and_process(dataset_id=args.dataset_id, split=args.split)
    paths = write_outputs(result, output_dir=Path(args.output_dir))

    print(json.dumps({"status": "ok", "outputs": paths, "meta": result["budget_thresholds"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

