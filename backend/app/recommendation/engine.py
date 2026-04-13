from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence

from ..core.filtering.engine import FilteringConfig, filter_candidates
from ..core.models import UserPreferences
from ..data_ingestion.schema import Restaurant
from ..llm.client import LLMClient
from ..llm.parsing import LLMResponseParseError, map_ranked_items_to_restaurants, parse_ranked_recommendations
from ..llm.prompting import build_prompt


@dataclass(frozen=True)
class Recommendation:
    restaurant: Restaurant
    rank: int
    explanation: str


@dataclass(frozen=True)
class RecommendConfig:
    top_k: int = 8
    llm_model: str = "default"
    temperature: float = 0.2
    max_tokens: int = 600
    filtering: FilteringConfig = FilteringConfig()


def _dedupe_restaurants(restaurants: Sequence[Restaurant]) -> List[Restaurant]:
    """
    Remove duplicate entries that represent the same restaurant in the same locality.
    """
    seen = set()
    out: List[Restaurant] = []
    for r in restaurants:
        key = (
            (r.name or "").strip().lower(),
            (r.location_city or "").strip().lower(),
            (r.location_area or "").strip().lower(),
        )
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


def _build_personalized_explanation(restaurant: Restaurant, prefs: UserPreferences) -> str:
    matched_cuisines = []
    pref_c = {c.strip().lower() for c in prefs.cuisines}
    for c in restaurant.cuisines:
        if c.strip().lower() in pref_c:
            matched_cuisines.append(c)

    cuisine_part = ""
    if matched_cuisines:
        cuisine_part = f"It is popular for {', '.join(matched_cuisines[:2])} cuisine."
    elif restaurant.cuisines:
        cuisine_part = f"It is known for {', '.join(restaurant.cuisines[:2])} cuisine."
    else:
        cuisine_part = "It matches your selected locality and rating preference."

    if restaurant.votes is None:
        votes_part = "Review volume is limited, so treat this as an exploratory option."
    elif restaurant.votes >= 1000:
        votes_part = f"It has {restaurant.votes} votes, you can be sure that you'll enjoy this restaurant #Zomato's Choice."
    elif restaurant.votes >= 300:
        votes_part = f"It has {restaurant.votes} votes, have a great meal!!"
    else:
        votes_part = f"It has {restaurant.votes} votes, have a great meal!!"

    return f"{cuisine_part} {votes_part}"


def _fill_with_fallback_candidates(
    mapped: List[dict],
    candidates: Sequence[Restaurant],
    prefs: UserPreferences,
    *,
    top_k: int,
) -> List[Recommendation]:
    """
    Ensure we return a stable number of results even when LLM output is short.
    """
    out: List[Recommendation] = []
    used_keys = set()

    for m in mapped:
        r = m["restaurant"]
        key = (
            (r.name or "").strip().lower(),
            (r.location_city or "").strip().lower(),
            (r.location_area or "").strip().lower(),
        )
        used_keys.add(key)
        out.append(Recommendation(restaurant=r, rank=int(m["rank"]), explanation=str(m["explanation"])))
        if len(out) >= top_k:
            return out

    next_rank = len(out) + 1
    for r in candidates:
        key = (
            (r.name or "").strip().lower(),
            (r.location_city or "").strip().lower(),
            (r.location_area or "").strip().lower(),
        )
        if key in used_keys:
            continue
        out.append(Recommendation(restaurant=r, rank=next_rank, explanation=_build_personalized_explanation(r, prefs)))
        next_rank += 1
        if len(out) >= top_k:
            break

    return out


def recommend(
    prefs: UserPreferences,
    *,
    restaurants: Sequence[Restaurant],
    llm_client: Optional[LLMClient],
    cfg: RecommendConfig = RecommendConfig(),
) -> List[Recommendation]:
    """
    Orchestrate:
    - Phase 3 filtering + heuristic ranking
    - Phase 4 LLM re-ranking + explanation generation

    If LLM is unavailable or parsing fails, fall back to heuristic-only candidates.
    """
    candidates = filter_candidates(list(restaurants), prefs, cfg=cfg.filtering)
    candidates = _dedupe_restaurants(candidates)
    if not candidates:
        return []

    # If no LLM client is provided, return heuristic-only results.
    if llm_client is None:
        return [
            Recommendation(
                restaurant=r,
                rank=i + 1,
                explanation=_build_personalized_explanation(r, prefs),
            )
            for i, r in enumerate(candidates[: cfg.top_k])
        ]

    prompt = build_prompt(prefs, candidates, top_k=cfg.top_k)
    raw = llm_client.generate(
        prompt,
        model=cfg.llm_model,
        temperature=cfg.temperature,
        max_tokens=cfg.max_tokens,
    )

    try:
        ranked_items = parse_ranked_recommendations(raw, candidates=candidates)
        mapped = map_ranked_items_to_restaurants(ranked_items, candidates=candidates)
        # Ensure we only return up to top_k; if LLM returns fewer rows, backfill heuristically.
        mapped = mapped[: cfg.top_k]
        return _fill_with_fallback_candidates(mapped, candidates, prefs, top_k=cfg.top_k)
    except LLMResponseParseError:
        # Fall back to heuristic-only results if the LLM output isn't parseable/valid.
        return [
            Recommendation(
                restaurant=r,
                rank=i + 1,
                explanation=_build_personalized_explanation(r, prefs),
            )
            for i, r in enumerate(candidates[: cfg.top_k])
        ]

