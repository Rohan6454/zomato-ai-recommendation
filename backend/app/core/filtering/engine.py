from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence, Tuple

from ...data_ingestion.schema import Restaurant
from ..models import UserPreferences


@dataclass(frozen=True)
class FilteringConfig:
    """
    Controls candidate selection size and scoring weights.
    """

    max_candidates_for_llm: int = 50
    alpha_rating: float = 1.0
    beta_votes: float = 0.15
    cost_penalty_weight: float = 0.0005
    min_rating_step_down: float = 0.5


def _norm(s: Optional[str]) -> str:
    return (s or "").strip().lower()


def _cuisine_match_count(restaurant: Restaurant, requested_cuisines: Sequence[str]) -> int:
    if not requested_cuisines:
        return 0
    r_cuisines = {_norm(c) for c in restaurant.cuisines}
    return sum(1 for c in requested_cuisines if _norm(c) in r_cuisines)


def _has_all_extras(restaurant: Restaurant, extras: Sequence[str]) -> bool:
    if not extras:
        return True
    r_tags = {_norm(t) for t in (restaurant.tags or [])}
    return all(_norm(e) in r_tags for e in extras)


def _score_candidate(r: Restaurant, prefs: UserPreferences, cfg: FilteringConfig) -> float:
    rating = r.rating if r.rating is not None else 0.0
    votes = r.votes if r.votes is not None else 0
    cost = r.avg_cost_for_two if r.avg_cost_for_two is not None else 0.0

    base = rating * cfg.alpha_rating + math.log(votes + 1) * cfg.beta_votes

    # Penalize higher costs when user has a strict max budget, or old low/medium bucket.
    if prefs.max_budget is not None or prefs.budget_bucket in {"low", "medium"}:
        base -= cost * cfg.cost_penalty_weight

    # Encourage matching more of the requested cuisines.
    base += 0.2 * _cuisine_match_count(r, prefs.cuisines)

    # Soft preference for extras: down-rank if missing (not a hard filter).
    if prefs.extras and not _has_all_extras(r, prefs.extras):
        base -= 0.5

    return base


def _apply_hard_filters(
    restaurants: Iterable[Restaurant],
    prefs: UserPreferences,
    *,
    include_area: bool,
    include_extras_as_hard: bool,
) -> List[Restaurant]:
    city = _norm(prefs.location_city)
    area = _norm(prefs.location_area) if include_area else ""
    budget = _norm(prefs.budget_bucket)
    max_budget = prefs.max_budget
    requested_cuisines = [c for c in prefs.cuisines if _norm(c)]
    min_rating = prefs.min_rating or 0.0

    out: List[Restaurant] = []
    for r in restaurants:
        if _norm(r.location_city) != city:
            continue
        if area:
            if _norm(r.location_area) != area:
                continue

        if budget and budget != "any":
            if _norm(r.budget_bucket) != budget:
                continue
        if max_budget is not None:
            # Respect budget when cost is known; keep unknown costs to avoid empty results.
            if r.avg_cost_for_two is not None and r.avg_cost_for_two > max_budget:
                continue

        if requested_cuisines:
            if _cuisine_match_count(r, requested_cuisines) <= 0:
                continue

        if r.rating is None or r.rating < min_rating:
            continue

        if include_extras_as_hard and prefs.extras:
            if not _has_all_extras(r, prefs.extras):
                continue

        out.append(r)
    return out


def _relax_preferences(prefs: UserPreferences, *, cfg: FilteringConfig) -> List[Tuple[str, UserPreferences]]:
    """
    Generate a sequence of relaxed preference variants.

    Order is aligned with the architecture doc:
    - drop extras
    - lower min_rating
    - expand beyond location_area to entire city
    """
    variants: List[Tuple[str, UserPreferences]] = []

    # 1) Drop extras (keep area, rating).
    if prefs.extras:
        variants.append(
            (
                "drop_extras",
                UserPreferences(
                    location_city=prefs.location_city,
                    location_area=prefs.location_area,
                    max_budget=prefs.max_budget,
                    budget_bucket=prefs.budget_bucket,
                    cuisines=list(prefs.cuisines),
                    min_rating=prefs.min_rating,
                    extras=[],
                ),
            )
        )

    # 2) Lower min_rating progressively (keep extras/area as provided).
    if prefs.min_rating and prefs.min_rating > 0:
        r = prefs.min_rating
        while r > 0:
            r = max(0.0, r - cfg.min_rating_step_down)
            variants.append(
                (
                    f"lower_min_rating_to_{r:g}",
                    UserPreferences(
                        location_city=prefs.location_city,
                        location_area=prefs.location_area,
                        max_budget=prefs.max_budget,
                        budget_bucket=prefs.budget_bucket,
                        cuisines=list(prefs.cuisines),
                        min_rating=r,
                        extras=list(prefs.extras),
                    ),
                )
            )

    # 3) Drop area constraint (expand to whole city).
    if prefs.location_area:
        variants.append(
            (
                "drop_area",
                UserPreferences(
                    location_city=prefs.location_city,
                    location_area=None,
                    max_budget=prefs.max_budget,
                    budget_bucket=prefs.budget_bucket,
                    cuisines=list(prefs.cuisines),
                    min_rating=prefs.min_rating,
                    extras=list(prefs.extras),
                ),
            )
        )

    return variants


def filter_candidates(
    restaurants: Sequence[Restaurant],
    prefs: UserPreferences,
    *,
    cfg: FilteringConfig = FilteringConfig(),
) -> List[Restaurant]:
    """
    Deterministically filter and pre-rank restaurants for LLM input.

    Returns:
    - A list of candidates sorted by descending heuristic score.
    - Length is capped at `cfg.max_candidates_for_llm`.
    """
    # First attempt: apply all hard filters, but treat extras as soft (Phase 2 tags are minimal).
    candidates = _apply_hard_filters(
        restaurants,
        prefs,
        include_area=True,
        include_extras_as_hard=False,
    )

    if not candidates:
        # Try progressive relaxation as described in the phase doc.
        for _reason, relaxed in _relax_preferences(prefs, cfg=cfg):
            candidates = _apply_hard_filters(
                restaurants,
                relaxed,
                include_area=True,
                include_extras_as_hard=False,
            )
            if candidates:
                prefs = relaxed  # use relaxed prefs for scoring decisions
                break

        # If still empty, finally drop area (city-only) if it exists and wasn't already tried.
        if not candidates and prefs.location_area:
            candidates = _apply_hard_filters(
                restaurants,
                UserPreferences(
                    location_city=prefs.location_city,
                    location_area=None,
                    budget_bucket=prefs.budget_bucket,
                    cuisines=list(prefs.cuisines),
                    min_rating=prefs.min_rating,
                    extras=list(prefs.extras),
                ),
                include_area=False,
                include_extras_as_hard=False,
            )

    scored = sorted(
        candidates,
        key=lambda r: _score_candidate(r, prefs, cfg),
        reverse=True,
    )

    # Cap to keep prompt sizes controlled.
    return scored[: cfg.max_candidates_for_llm]

