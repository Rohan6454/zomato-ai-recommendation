from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from .schema import Restaurant


def build_indexes(restaurants: List[Restaurant]) -> Dict[str, Dict[str, List[str]]]:
    """
    Build simple indices for fast filtering in later phases.

    Output structure:
    - city_to_ids: { "Delhi": ["id1", "id2", ...] }
    - cuisine_to_ids: { "Italian": ["id3", ...] }
    """
    city_to_ids: Dict[str, List[str]] = defaultdict(list)
    cuisine_to_ids: Dict[str, List[str]] = defaultdict(list)

    for r in restaurants:
        city_to_ids[r.location_city].append(r.restaurant_id)
        for c in r.cuisines:
            cuisine_to_ids[c].append(r.restaurant_id)

    # Convert defaultdict to dict for JSON serialization stability
    return {
        "city_to_ids": dict(city_to_ids),
        "cuisine_to_ids": dict(cuisine_to_ids),
    }

