from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional


BudgetBucket = str  # expected: "low" | "medium" | "high" | "any" (any used mainly in querying)


@dataclass(frozen=True)
class Restaurant:
    restaurant_id: str
    name: str
    location_city: str
    location_area: Optional[str]
    address: Optional[str]
    cuisines: List[str]
    avg_cost_for_two: Optional[float]
    rating: Optional[float]
    votes: Optional[int]
    is_delivery: Optional[bool]
    budget_bucket: Optional[BudgetBucket]
    tags: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

