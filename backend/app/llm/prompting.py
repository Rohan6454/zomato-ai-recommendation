from __future__ import annotations

from typing import List

from ..core.models import UserPreferences
from ..data_ingestion.schema import Restaurant


def build_prompt(
    prefs: UserPreferences,
    candidates: List[Restaurant],
    *,
    top_k: int = 8,
) -> str:
    """
    Build a compact prompt for LLM re-ranking + explanations.

    We keep it provider-agnostic and return a single string prompt as specified in Phase 4.
    """
    top_k = max(1, min(top_k, 10))

    prefs_lines = [
        f"- City: {prefs.location_city}",
        f"- Area: {prefs.location_area or 'Any'}",
        f"- Budget: {prefs.budget_bucket}",
        f"- Cuisines: {', '.join(prefs.cuisines) if prefs.cuisines else 'Any'}",
        f"- Minimum rating: {prefs.min_rating:g}",
        f"- Extras: {', '.join(prefs.extras) if prefs.extras else 'None'}",
    ]

    # Candidate list: keep it dense to control tokens.
    header = "ID | Name | City | Area | Cuisines | Rating | CostForTwo | CostBucket | Tags"
    rows: List[str] = [header]
    for r in candidates:
        rows.append(
            " | ".join(
                [
                    str(r.restaurant_id),
                    r.name,
                    r.location_city,
                    r.location_area or "",
                    ",".join(r.cuisines[:4]),
                    "" if r.rating is None else f"{r.rating:.1f}",
                    "" if r.avg_cost_for_two is None else f"{r.avg_cost_for_two:.0f}",
                    r.budget_bucket or "",
                    ",".join((r.tags or [])[:6]),
                ]
            )
        )

    instructions = f"""
You are an expert restaurant recommendation assistant.

Given:
1) The user's preferences
2) A list of candidate restaurants (structured data)

Your tasks:
- Select and rank the top {top_k} restaurants that best match the user's preferences.
- For each ranked restaurant, provide a short explanation (1–3 sentences) of why it fits.
- If some preferences cannot be fully satisfied, prefer the closest matches and mention the trade-off briefly.

Return ONLY a JSON array inside a markdown ```json code fence``` in the following format:

[
  {{"id": "<restaurant_id>", "rank": 1, "short_explanation": "<text>"}},
  ...
]
"""

    return "\n".join(
        [
            "USER_PREFERENCES:",
            *prefs_lines,
            "",
            "CANDIDATES:",
            *rows,
            "",
            instructions.strip(),
        ]
    )

