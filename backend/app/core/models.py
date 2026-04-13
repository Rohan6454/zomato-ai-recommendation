from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


BudgetBucket = str  # "low" | "medium" | "high" | "any"


@dataclass(frozen=True)
class UserPreferences:
    """
    Shared preferences model between API layer and recommendation logic.
    """

    location_city: str
    location_area: Optional[str] = None
    max_budget: Optional[float] = None
    budget_bucket: BudgetBucket = "any"
    cuisines: List[str] = field(default_factory=list)
    min_rating: float = 0.0
    extras: List[str] = field(default_factory=list)

