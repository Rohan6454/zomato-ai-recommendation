import unittest

from app.core.models import UserPreferences
from app.data_ingestion.schema import Restaurant
from app.llm.client import MockLLMClient
from app.recommendation.engine import recommend


class RecommendationEnginePhase4Tests(unittest.TestCase):
    def setUp(self):
        self.restaurants = [
            Restaurant(
                restaurant_id="1",
                name="Budget Bites",
                location_city="Delhi",
                location_area="Connaught Place",
                address=None,
                cuisines=["Indian"],
                avg_cost_for_two=400.0,
                rating=4.2,
                votes=120,
                is_delivery=True,
                budget_bucket="low",
                tags=[],
            ),
            Restaurant(
                restaurant_id="2",
                name="Fancy Feast",
                location_city="Delhi",
                location_area="Connaught Place",
                address=None,
                cuisines=["Italian"],
                avg_cost_for_two=2200.0,
                rating=4.6,
                votes=500,
                is_delivery=False,
                budget_bucket="high",
                tags=[],
            ),
        ]

    def test_recommend_with_mock_llm(self):
        prefs = UserPreferences(location_city="Delhi", cuisines=["Italian"], min_rating=4.0)
        llm = MockLLMClient(
            """```json
[
  {"id": "2", "rank": 1, "short_explanation": "Best match for Italian with high rating."}
]
```"""
        )
        out = recommend(prefs, restaurants=self.restaurants, llm_client=llm)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].restaurant.restaurant_id, "2")
        self.assertEqual(out[0].rank, 1)
        self.assertIn("Italian", out[0].explanation)

    def test_recommend_falls_back_when_llm_output_invalid(self):
        prefs = UserPreferences(location_city="Delhi", cuisines=["Italian"], min_rating=4.0)
        llm = MockLLMClient("not json at all")
        out = recommend(prefs, restaurants=self.restaurants, llm_client=llm)
        self.assertTrue(len(out) >= 1)
        self.assertEqual(out[0].rank, 1)


if __name__ == "__main__":
    unittest.main()

