from __future__ import annotations

import hashlib
import json
import time
import math
from typing import List

from fastapi import APIRouter, Depends, Query

from ...core.cache import TTLCache
from ...core.filtering.engine import filter_candidates
from ...core.models import UserPreferences
from ...data_ingestion.schema import Restaurant
from ...llm.client import LLMClient
from ...observability.feedback_store import fetch_feedback, insert_feedback
from ...observability.metrics import metrics
from ...recommendation.engine import RecommendConfig, recommend
from ..dependencies import get_llm_client, get_recommendation_cache, get_restaurants
from ..models import RecommendationFeedbackRequest, RecommendationRequest, RecommendationResponse


router = APIRouter(prefix="", tags=["recommendations"])


@router.get("/localities", response_model=List[str], summary="Get unique localities for dropdown")
def get_localities(
    restaurants: List[Restaurant] = Depends(get_restaurants),
) -> List[str]:
    values = {r.location_city.strip() for r in restaurants if r.location_city and r.location_city.strip()}
    return sorted(values)


@router.get("/cuisines", response_model=List[str], summary="Get unique cuisines for dropdown")
def get_cuisines(
    location_city: str | None = Query(default=None, description="Optional locality/city to filter cuisines."),
    restaurants: List[Restaurant] = Depends(get_restaurants),
) -> List[str]:
    target = location_city.strip().lower() if location_city and location_city.strip() else None
    values = {
        c.strip()
        for r in restaurants
        if (not target or (r.location_city and r.location_city.strip().lower() == target))
        for c in (r.cuisines or [])
        if c and str(c).strip()
    }
    return sorted(values)


@router.get("/budget-suggestion", summary="Suggest budget based on locality and cuisine filters")
def get_budget_suggestion(
    location_city: str = Query(..., min_length=1, description="Selected locality/city."),
    cuisines: str | None = Query(default=None, description="Comma-separated preferred cuisines."),
    min_rating: float | None = Query(default=None, ge=0.0, le=5.0, description="Optional min rating filter."),
    max_budget: float | None = Query(default=None, ge=0.0, description="Optional max budget filter."),
    restaurants: List[Restaurant] = Depends(get_restaurants),
) -> dict:
    target_city = location_city.strip().lower()
    preferred = {c.strip().lower() for c in (cuisines or "").split(",") if c.strip()}

    costs: List[float] = []
    unique_keys = set()
    for r in restaurants:
        if not (r.location_city and r.location_city.strip().lower() == target_city):
            continue
        if preferred:
            restaurant_cuisines = {c.strip().lower() for c in (r.cuisines or []) if c and c.strip()}
            if not (restaurant_cuisines & preferred):
                continue
        if min_rating is not None:
            if r.rating is None or r.rating < min_rating:
                continue
        if max_budget is not None:
            # Match recommendation filter behavior: unknown costs are still eligible.
            if r.avg_cost_for_two is not None and float(r.avg_cost_for_two) > max_budget:
                continue
        key = (
            (r.name or "").strip().lower(),
            (r.location_city or "").strip().lower(),
            (r.location_area or "").strip().lower(),
        )
        unique_keys.add(key)
        if r.avg_cost_for_two is not None:
            costs.append(float(r.avg_cost_for_two))

    if not costs:
        return {"suggested_max_budget": None, "sample_size": 0, "eligible_unique_count": len(unique_keys)}

    costs.sort()
    mid = len(costs) // 2
    median = costs[mid] if len(costs) % 2 == 1 else (costs[mid - 1] + costs[mid]) / 2.0
    # Round up to nearest 50 for cleaner UX.
    suggested = int(math.ceil(median / 50.0) * 50)
    return {"suggested_max_budget": suggested, "sample_size": len(costs), "eligible_unique_count": len(unique_keys)}


@router.post(
    "/recommendations",
    response_model=List[RecommendationResponse],
    summary="Get personalized restaurant recommendations",
)
def get_recommendations(
    payload: RecommendationRequest,
    restaurants: List[Restaurant] = Depends(get_restaurants),
    llm_client: LLMClient | None = Depends(get_llm_client),
    cache: TTLCache = Depends(get_recommendation_cache),
) -> List[RecommendationResponse]:
    started = time.perf_counter()
    prefs = UserPreferences(
        location_city=payload.location_city.strip().title(),
        location_area=payload.location_area.strip().title() if payload.location_area else None,
        max_budget=payload.max_budget,
        budget_bucket=payload.budget_bucket.value,
        cuisines=[c.strip().title() for c in payload.cuisines],
        min_rating=payload.min_rating,
        extras=[e.strip().lower() for e in payload.extras],
    )

    # Phase 7 logging: avoid raw notes, only high-level summary.
    request_summary = {
        "location_city": prefs.location_city,
        "min_rating": prefs.min_rating,
        "max_budget": prefs.max_budget,
        "cuisines": prefs.cuisines[:5],
    }
    print(f"[obs] recommendations.request {json.dumps(request_summary)}")

    # Phase 8 cache key based on normalized preference fields.
    cache_key = hashlib.sha256(
        json.dumps(
            {
                "location_city": prefs.location_city,
                "location_area": prefs.location_area,
                "max_budget": prefs.max_budget,
                "budget_bucket": prefs.budget_bucket,
                "cuisines": sorted(prefs.cuisines),
                "min_rating": prefs.min_rating,
                "extras": sorted(prefs.extras),
            },
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()
    cached = cache.get(cache_key)
    if cached is not None:
        metrics.inc("recommendations.cache_hit")
        metrics.observe_ms("recommendations.latency_ms", (time.perf_counter() - started) * 1000)
        return cached

    metrics.inc("recommendations.cache_miss")
    candidates = filter_candidates(restaurants, prefs)
    metrics.observe_ms("recommendations.candidate_count", len(candidates))

    recs = recommend(
        prefs,
        restaurants=restaurants,
        llm_client=llm_client,
        cfg=RecommendConfig(top_k=50),
    )

    response = [
        RecommendationResponse(
            restaurant_name=r.restaurant.name,
            cuisines=r.restaurant.cuisines,
            rating=r.restaurant.rating,
            estimated_cost_for_two=r.restaurant.avg_cost_for_two,
            location_city=r.restaurant.location_city,
            location_area=r.restaurant.location_area,
            explanation=r.explanation,
            rank=r.rank,
        )
        for r in recs
    ]
    cache.set(cache_key, response)

    top_ids = [r.restaurant.restaurant_id for r in recs[:5]]
    metrics.inc("recommendations.requests_total")
    if not response:
        metrics.inc("recommendations.no_results")
    metrics.observe_ms("recommendations.latency_ms", (time.perf_counter() - started) * 1000)
    print(f"[obs] recommendations.outcome success={True} top_ids={top_ids}")
    return response


@router.get("/metrics", summary="Basic in-process metrics snapshot")
def get_metrics() -> dict:
    return metrics.snapshot()


@router.post("/feedback", summary="Capture recommendation feedback")
def post_feedback(payload: RecommendationFeedbackRequest) -> dict:
    row_id = insert_feedback(
        {
            "location_city": payload.location_city.strip().title(),
            "cuisines_json": json.dumps(payload.cuisines),
            "min_rating": payload.min_rating,
            "max_budget": payload.max_budget,
            "top_restaurant_names_json": json.dumps(payload.top_restaurant_names[:10]),
            "label": payload.label.value,
        }
    )
    metrics.inc(f"feedback.{payload.label.value}")
    return {"status": "ok", "id": row_id}


@router.get("/feedback", summary="Fetch recent feedback records")
def get_feedback(limit: int = 50) -> dict:
    limit = max(1, min(limit, 500))
    rows = fetch_feedback(limit=limit)
    return {"rows": rows, "count": len(rows)}

