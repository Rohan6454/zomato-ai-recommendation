from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from ..core.cache import TTLCache
from ..data_ingestion.schema import Restaurant
from ..llm.client import LLMClient


def _backend_root() -> Path:
    # backend/app/api/dependencies.py -> backend
    return Path(__file__).resolve().parents[2]


def _normalize_float(v):
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _normalize_int(v):
    if v is None:
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _normalize_bool(v):
    if isinstance(v, bool):
        return v
    if v is None:
        return None
    s = str(v).strip().lower()
    if s in {"true", "1", "yes", "y"}:
        return True
    if s in {"false", "0", "no", "n"}:
        return False
    return None


def _restaurant_from_dict(data: dict) -> Restaurant:
    return Restaurant(
        restaurant_id=str(data.get("restaurant_id", "")),
        name=str(data.get("name", "")).strip(),
        location_city=str(data.get("location_city", "")).strip(),
        location_area=(str(data["location_area"]).strip() if data.get("location_area") else None),
        address=(str(data["address"]).strip() if data.get("address") else None),
        cuisines=[str(x).strip() for x in data.get("cuisines", []) if str(x).strip()],
        avg_cost_for_two=_normalize_float(data.get("avg_cost_for_two")),
        rating=_normalize_float(data.get("rating")),
        votes=_normalize_int(data.get("votes")),
        is_delivery=_normalize_bool(data.get("is_delivery")),
        budget_bucket=(str(data["budget_bucket"]).strip() if data.get("budget_bucket") else None),
        tags=[str(x).strip() for x in data.get("tags", []) if str(x).strip()],
    )


@lru_cache(maxsize=1)
def get_restaurants() -> List[Restaurant]:
    """
    Load processed restaurants from Phase 2 output.
    Returns an empty list if data file is missing (API still works, returns no recommendations).
    """
    path = _backend_root() / "data" / "processed" / "restaurants.jsonl"
    if not path.exists():
        print(f"[api] processed dataset not found: {path}")
        return []

    restaurants: List[Restaurant] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            r = _restaurant_from_dict(obj)
            if r.restaurant_id and r.name and r.location_city:
                restaurants.append(r)
    print(f"[api] loaded_restaurants={len(restaurants)} source={path}")
    return restaurants


def get_llm_client() -> Optional[LLMClient]:
    """
    Phase 5 default: return None to allow heuristic fallback in recommendation engine.
    Gemini wiring can be enabled in a later pass with provider-specific client integration.
    """
    _ = os.getenv("GEMINI_API_KEY")
    return None


@lru_cache(maxsize=1)
def get_recommendation_cache() -> TTLCache:
    # Phase 8: in-memory cache for repeated recommendation requests.
    return TTLCache(ttl_seconds=90, max_items=1024)

