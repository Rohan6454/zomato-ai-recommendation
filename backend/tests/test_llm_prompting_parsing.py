import unittest

from app.core.models import UserPreferences
from app.data_ingestion.schema import Restaurant
from app.llm.parsing import parse_ranked_recommendations
from app.llm.prompting import build_prompt


class PromptingParsingTests(unittest.TestCase):
    def setUp(self):
        self.candidates = [
            Restaurant(
                restaurant_id="10",
                name="Pasta Place",
                location_city="Delhi",
                location_area="Saket",
                address=None,
                cuisines=["Italian"],
                avg_cost_for_two=1200.0,
                rating=4.4,
                votes=200,
                is_delivery=True,
                budget_bucket="medium",
                tags=[],
            ),
            Restaurant(
                restaurant_id="11",
                name="Wok World",
                location_city="Delhi",
                location_area="Saket",
                address=None,
                cuisines=["Chinese"],
                avg_cost_for_two=900.0,
                rating=4.1,
                votes=140,
                is_delivery=True,
                budget_bucket="medium",
                tags=[],
            ),
        ]

    def test_build_prompt_contains_preferences_and_candidates(self):
        prefs = UserPreferences(location_city="Delhi", cuisines=["Italian"], min_rating=4.0, budget_bucket="medium")
        prompt = build_prompt(prefs, self.candidates, top_k=2)
        self.assertIn("USER_PREFERENCES:", prompt)
        self.assertIn("CANDIDATES:", prompt)
        self.assertIn("Pasta Place", prompt)
        self.assertIn("Wok World", prompt)
        self.assertIn("top 2", prompt.lower())

    def test_parse_ranked_recommendations_from_json_fence(self):
        llm_text = """Here you go:
```json
[
  {"id": "11", "rank": 1, "short_explanation": "Great Chinese option."},
  {"id": "10", "rank": 2, "short_explanation": "Strong Italian choice."}
]
```
"""
        ranked = parse_ranked_recommendations(llm_text, candidates=self.candidates)
        self.assertEqual([r.restaurant_id for r in ranked], ["11", "10"])
        self.assertEqual([r.rank for r in ranked], [1, 2])


if __name__ == "__main__":
    unittest.main()

