from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class BudgetBucket(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    any = "any"


class RecommendationRequest(BaseModel):
    location_city: str = Field(..., min_length=1, description="Target city for restaurant recommendations.")
    location_area: Optional[str] = Field(default=None, description="Optional locality/area.")
    max_budget: Optional[float] = Field(default=None, ge=0.0, description="Maximum budget (cost for two).")
    budget_bucket: BudgetBucket = Field(default=BudgetBucket.any, description="Budget preference bucket.")
    cuisines: List[str] = Field(default_factory=list, description="Preferred cuisines.")
    min_rating: float = Field(default=0.0, ge=0.0, le=5.0, description="Minimum acceptable rating (0-5).")
    extras: List[str] = Field(default_factory=list, description="Additional constraints/tags.")
    notes: Optional[str] = Field(default=None, description="Optional free-form user notes.")

    @field_validator("location_city", "location_area", mode="before")
    @classmethod
    def normalize_strings(cls, v):
        if v is None:
            return None
        return str(v).strip()

    @field_validator("cuisines", "extras", mode="before")
    @classmethod
    def normalize_lists(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            values = [v]
        else:
            values = list(v)
        return [str(x).strip() for x in values if str(x).strip()]


class RecommendationResponse(BaseModel):
    restaurant_name: str
    cuisines: List[str]
    rating: Optional[float]
    estimated_cost_for_two: Optional[float]
    location_city: str
    location_area: Optional[str]
    explanation: str
    rank: int


class FeedbackLabel(str, Enum):
    helpful = "helpful"
    not_helpful = "not_helpful"


class RecommendationFeedbackRequest(BaseModel):
    location_city: str = Field(..., min_length=1)
    cuisines: List[str] = Field(default_factory=list)
    min_rating: float = Field(default=0.0, ge=0.0, le=5.0)
    max_budget: Optional[float] = Field(default=None, ge=0.0)
    top_restaurant_names: List[str] = Field(default_factory=list)
    label: FeedbackLabel

