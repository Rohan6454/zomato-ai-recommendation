from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Sequence

from ..data_ingestion.schema import Restaurant


_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)


@dataclass(frozen=True)
class LLMRankedItem:
    restaurant_id: str
    rank: int
    short_explanation: str


class LLMResponseParseError(ValueError):
    pass


def _extract_json_block(text: str) -> str:
    """
    Extract JSON from a markdown code fence if present; otherwise return the raw text.
    """
    m = _JSON_FENCE_RE.search(text)
    if m:
        return m.group(1).strip()
    return text.strip()


def _try_parse_json(s: str) -> Any:
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        # Simple cleanup: remove leading/trailing junk outside the first JSON array/object.
        s2 = s.strip()
        start = min([i for i in [s2.find("["), s2.find("{")] if i != -1], default=-1)
        if start > 0:
            s2 = s2[start:]
        end_arr = s2.rfind("]")
        end_obj = s2.rfind("}")
        end = max(end_arr, end_obj)
        if end != -1:
            s2 = s2[: end + 1]
        try:
            return json.loads(s2)
        except json.JSONDecodeError as e:
            raise LLMResponseParseError("Failed to parse JSON from LLM output.") from e


def parse_ranked_recommendations(
    llm_text: str,
    *,
    candidates: Sequence[Restaurant],
) -> List[LLMRankedItem]:
    """
    Parse LLM response into structured ranked items and validate ids against candidates.
    """
    json_text = _extract_json_block(llm_text)
    try:
        data = _try_parse_json(json_text)
    except json.JSONDecodeError as e:
        raise LLMResponseParseError("Failed to parse JSON from LLM output.") from e

    if not isinstance(data, list):
        raise LLMResponseParseError("Expected a JSON array.")

    allowed_ids = {str(r.restaurant_id) for r in candidates}
    items: List[LLMRankedItem] = []

    for idx, obj in enumerate(data):
        if not isinstance(obj, Mapping):
            raise LLMResponseParseError(f"Item {idx} is not an object.")

        rid = obj.get("id")
        rank = obj.get("rank")
        expl = obj.get("short_explanation")

        if rid is None or rank is None or expl is None:
            raise LLMResponseParseError(f"Item {idx} missing required fields (id, rank, short_explanation).")

        rid_str = str(rid)
        if rid_str not in allowed_ids:
            raise LLMResponseParseError(f"Item {idx} has unknown id '{rid_str}'.")

        try:
            rank_int = int(rank)
        except (TypeError, ValueError):
            raise LLMResponseParseError(f"Item {idx} has invalid rank.")

        expl_str = str(expl).strip()
        if not expl_str:
            raise LLMResponseParseError(f"Item {idx} explanation is empty.")

        items.append(LLMRankedItem(restaurant_id=rid_str, rank=rank_int, short_explanation=expl_str))

    # Sort by rank; keep stable order if ranks collide.
    items.sort(key=lambda x: x.rank)
    return items


def map_ranked_items_to_restaurants(
    ranked: Sequence[LLMRankedItem],
    *,
    candidates: Sequence[Restaurant],
) -> List[Dict[str, Any]]:
    """
    Map ranked items back to full restaurant objects.

    Returns a list of dicts:
      { "restaurant": Restaurant, "rank": int, "explanation": str }
    """
    by_id = {str(r.restaurant_id): r for r in candidates}
    out: List[Dict[str, Any]] = []
    for item in ranked:
        out.append(
            {
                "restaurant": by_id[item.restaurant_id],
                "rank": item.rank,
                "explanation": item.short_explanation,
            }
        )
    return out

