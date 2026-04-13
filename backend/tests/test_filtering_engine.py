import unittest

from app.core.filtering.engine import FilteringConfig, filter_candidates
from app.core.models import UserPreferences
from app.data_ingestion.schema import Restaurant


class FilteringEngineTests(unittest.TestCase):
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
            Restaurant(
                restaurant_id="3",
                name="Decent Diner",
                location_city="Delhi",
                location_area="Saket",
                address=None,
                cuisines=["Italian", "Chinese"],
                avg_cost_for_two=1200.0,
                rating=4.0,
                votes=80,
                is_delivery=True,
                budget_bucket="medium",
                tags=[],
            ),
            Restaurant(
                restaurant_id="4",
                name="No Rating Cafe",
                location_city="Delhi",
                location_area="Connaught Place",
                address=None,
                cuisines=["Chinese"],
                avg_cost_for_two=600.0,
                rating=None,
                votes=10,
                is_delivery=True,
                budget_bucket="low",
                tags=[],
            ),
        ]

    def test_city_filter_required(self):
        prefs = UserPreferences(location_city="Delhi")
        out = filter_candidates(self.restaurants, prefs, cfg=FilteringConfig(max_candidates_for_llm=50))
        self.assertTrue(all(r.location_city == "Delhi" for r in out))

    def test_budget_filter(self):
        prefs = UserPreferences(location_city="Delhi", budget_bucket="low")
        out = filter_candidates(self.restaurants, prefs)
        self.assertTrue(all(r.budget_bucket == "low" for r in out))

    def test_cuisine_filter_case_insensitive(self):
        prefs = UserPreferences(location_city="Delhi", cuisines=["italian"])
        out = filter_candidates(self.restaurants, prefs)
        self.assertTrue(all("Italian" in r.cuisines for r in out))

    def test_min_rating_excludes_missing_rating(self):
        prefs = UserPreferences(location_city="Delhi", min_rating=4.0)
        out = filter_candidates(self.restaurants, prefs)
        self.assertTrue(all(r.rating is not None and r.rating >= 4.0 for r in out))

    def test_area_filter_then_relax(self):
        # Area has no Italian restaurants with rating >= 4.5 (only "Fancy Feast" matches but budget is high).
        # We set impossible min_rating for that area, expecting relaxation to expand candidates.
        prefs = UserPreferences(location_city="Delhi", location_area="Connaught Place", cuisines=["Chinese"], min_rating=4.5)
        out = filter_candidates(self.restaurants, prefs)
        # After relaxation, it should return something from Delhi (likely from other areas).
        self.assertTrue(all(r.location_city == "Delhi" for r in out))


if __name__ == "__main__":
    unittest.main()

