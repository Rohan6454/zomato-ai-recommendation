import unittest

from fastapi.testclient import TestClient

from app.api.dependencies import get_llm_client, get_restaurants
from app.data_ingestion.schema import Restaurant
from app.main import create_app


class Phase5APITests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = TestClient(self.app)

        sample_restaurants = [
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
                name="Pasta Hub",
                location_city="Delhi",
                location_area="Saket",
                address=None,
                cuisines=["Italian"],
                avg_cost_for_two=1200.0,
                rating=4.5,
                votes=230,
                is_delivery=True,
                budget_bucket="medium",
                tags=[],
            ),
            Restaurant(
                restaurant_id="3",
                name="Pasta Hub Premium",
                location_city="Delhi",
                location_area="Saket",
                address=None,
                cuisines=["Italian"],
                avg_cost_for_two=1800.0,
                rating=4.6,
                votes=180,
                is_delivery=True,
                budget_bucket="high",
                tags=[],
            ),
        ]

        self.app.dependency_overrides[get_restaurants] = lambda: sample_restaurants
        self.app.dependency_overrides[get_llm_client] = lambda: None

    def tearDown(self):
        self.app.dependency_overrides = {}

    def test_health(self):
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "ok")

    def test_recommendations_happy_path(self):
        payload = {
            "location_city": "delhi",
            "max_budget": 1300,
            "cuisines": ["italian"],
            "min_rating": 4.0,
        }
        resp = self.client.post("/recommendations", json=payload)
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(isinstance(body, list))
        self.assertGreaterEqual(len(body), 1)
        self.assertEqual(body[0]["restaurant_name"], "Pasta Hub")
        self.assertLessEqual(body[0]["estimated_cost_for_two"], 1300)

    def test_localities_unique_sorted(self):
        resp = self.client.get("/localities")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body, ["Delhi"])

    def test_recommendations_invalid_min_rating(self):
        payload = {
            "location_city": "Delhi",
            "max_budget": 1000,
            "cuisines": ["Italian"],
            "min_rating": 7.0,
        }
        resp = self.client.post("/recommendations", json=payload)
        self.assertEqual(resp.status_code, 422)


if __name__ == "__main__":
    unittest.main()

