from __future__ import annotations

import math
import re
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .schema import BudgetBucket


_WHITESPACE_RE = re.compile(r"\s+")


def normalize_str(value: Any) -> Optional[str]:
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    s = _WHITESPACE_RE.sub(" ", s)
    return s


def normalize_city(value: Any) -> Optional[str]:
    s = normalize_str(value)
    if s is None:
        return None
    # Title-case is a reasonable default for cities; keep acronyms intact.
    return s.title()


def normalize_area(value: Any) -> Optional[str]:
    s = normalize_str(value)
    if s is None:
        return None
    return s.title()


def normalize_cuisines(value: Any) -> List[str]:
    """
    Normalize cuisines into a list of strings.

    Accepts:
    - already-a-list
    - comma-separated string
    - None / empty
    """
    if value is None:
        return []

    if isinstance(value, list):
        items = value
    else:
        items = str(value).split(",")

    out: List[str] = []
    for item in items:
        s = normalize_str(item)
        if not s:
            continue
        out.append(s.title())

    # de-duplicate while preserving order
    seen = set()
    deduped: List[str] = []
    for c in out:
        key = c.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(c)
    return deduped


def normalize_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(f) or math.isinf(f):
        return None
    return f


def normalize_cost(value: Any) -> Optional[float]:
    """
    Normalize cost fields that may contain currency symbols/commas, e.g.:
    - "800"
    - "1,200"
    - "₹1,500 for two"
    """
    f = normalize_float(value)
    if f is not None:
        return f
    if value is None:
        return None
    s = str(value).strip().lower()
    m = re.search(r"(\d[\d,]*(?:\.\d+)?)", s)
    if not m:
        return None
    try:
        return float(m.group(1).replace(",", ""))
    except ValueError:
        return None


def normalize_int(value: Any) -> Optional[int]:
    if value is None:
        return None
    try:
        i = int(float(value))
    except (TypeError, ValueError):
        return None
    return i


def normalize_rating(value: Any) -> Optional[float]:
    r = normalize_float(value)
    if r is None and value is not None:
        s = str(value).strip().lower()
        # Handle common dataset formats like "4.1/5", "3.9 / 5", "NEW", "-"
        m = re.search(r"(\d+(?:\.\d+)?)", s)
        if m:
            try:
                r = float(m.group(1))
            except ValueError:
                r = None
    if r is None:
        return None
    # clamp to [0, 5]
    if r < 0:
        r = 0.0
    if r > 5:
        r = 5.0
    return r


def normalize_bool(value: Any) -> Optional[bool]:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    s = str(value).strip().lower()
    if s in {"true", "t", "1", "yes", "y"}:
        return True
    if s in {"false", "f", "0", "no", "n"}:
        return False
    return None


def derive_budget_bucket(
    avg_cost_for_two: Optional[float],
    *,
    low_max: float,
    medium_max: float,
) -> Optional[BudgetBucket]:
    if avg_cost_for_two is None:
        return None
    if avg_cost_for_two <= low_max:
        return "low"
    if avg_cost_for_two <= medium_max:
        return "medium"
    return "high"


def budget_thresholds_from_costs(
    costs: Iterable[float],
    *,
    low_quantile: float = 0.33,
    medium_quantile: float = 0.66,
) -> Tuple[float, float]:
    """
    Compute budget thresholds from cost distribution.

    Returns:
    - low_max
    - medium_max
    """
    values = sorted([c for c in costs if c is not None and c >= 0])
    if not values:
        # fallback defaults if dataset doesn't contain costs
        return 500.0, 1500.0

    def q(p: float) -> float:
        idx = int(round((len(values) - 1) * p))
        idx = max(0, min(len(values) - 1, idx))
        return float(values[idx])

    low_max = q(low_quantile)
    medium_max = max(low_max, q(medium_quantile))
    return low_max, medium_max


def extract_tags(record: Dict[str, Any]) -> List[str]:
    """
    Best-effort tag extraction.

    The dataset may not explicitly provide tags like "family-friendly".
    This function can be extended later (Phase 2 keeps it conservative).
    """
    tags: List[str] = []
    # Placeholder for future rules; keep empty for now.
    return tags

