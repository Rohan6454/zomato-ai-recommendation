from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import mean
from typing import List

from app.api.dependencies import get_restaurants
from app.core.models import UserPreferences
from app.recommendation.engine import recommend


@dataclass
class Scenario:
    name: str
    prefs: UserPreferences


def _scenarios() -> List[Scenario]:
    return [
        Scenario(
            name="budget-friendly-banashankari-north-indian",
            prefs=UserPreferences(location_city="Banashankari", max_budget=500, cuisines=["North Indian"], min_rating=3.5),
        ),
        Scenario(
            name="family-style-btm-indian",
            prefs=UserPreferences(location_city="Btm", max_budget=800, cuisines=["Indian"], min_rating=4.0),
        ),
        Scenario(
            name="italian-jp-nagar-mid-budget",
            prefs=UserPreferences(location_city="Jp Nagar", max_budget=1200, cuisines=["Italian"], min_rating=3.5),
        ),
    ]


def _output_dir() -> Path:
    path = Path(__file__).resolve().parents[1] / "evaluation" / "reports"
    path.mkdir(parents=True, exist_ok=True)
    return path


def main() -> int:
    restaurants = get_restaurants()
    scenarios = _scenarios()
    out = []
    for sc in scenarios:
        recs = recommend(sc.prefs, restaurants=restaurants, llm_client=None)
        ratings = [r.restaurant.rating for r in recs if r.restaurant.rating is not None]
        costs = [r.restaurant.avg_cost_for_two for r in recs if r.restaurant.avg_cost_for_two is not None]
        out.append(
            {
                "scenario": sc.name,
                "preferences": asdict(sc.prefs),
                "count": len(recs),
                "avg_rating": mean(ratings) if ratings else None,
                "avg_cost_for_two": mean(costs) if costs else None,
                "top": [
                    {
                        "rank": r.rank,
                        "name": r.restaurant.name,
                        "rating": r.restaurant.rating,
                        "cost_for_two": r.restaurant.avg_cost_for_two,
                        "cuisines": r.restaurant.cuisines,
                        "explanation": r.explanation,
                    }
                    for r in recs[:5]
                ],
            }
        )

    out_dir = _output_dir()
    json_path = out_dir / "scenario_results.json"
    md_path = out_dir / "scenario_summary.md"
    json_path.write_text(json.dumps(out, indent=2), encoding="utf-8")

    lines = ["## Evaluation Summary", ""]
    for item in out:
        lines.append(f"### {item['scenario']}")
        lines.append(f"- recommendations: {item['count']}")
        lines.append(f"- avg_rating: {item['avg_rating']}")
        lines.append(f"- avg_cost_for_two: {item['avg_cost_for_two']}")
        for t in item["top"][:3]:
            lines.append(f"- #{t['rank']} {t['name']} (rating={t['rating']}, cost={t['cost_for_two']})")
        lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"status": "ok", "json": str(json_path), "summary": str(md_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

