import unittest

from fastapi.testclient import TestClient

from app.api.dependencies import get_llm_client, get_restaurants
from app.data_ingestion.schema import Restaurant
from app.main import create_app


class ObservabilityPhase7Tests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = TestClient(self.app)
        sample_restaurants = [
            Restaurant(
                restaurant_id="1",
                name="Budget Bites",
                location_city="Delhi",
                location_area=None,
                address=None,
                cuisines=["Indian"],
                avg_cost_for_two=400.0,
                rating=4.2,
                votes=120,
                is_delivery=True,
                budget_bucket="low",
                tags=[],
            )
        ]
        self.app.dependency_overrides[get_restaurants] = lambda: sample_restaurants
        self.app.dependency_overrides[get_llm_client] = lambda: None

    def tearDown(self):
        self.app.dependency_overrides = {}

    def test_metrics_endpoint(self):
        _ = self.client.get("/health")
        resp = self.client.get("/metrics")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn("counters", body)
        self.assertIn("timings_ms_avg", body)

    def test_feedback_roundtrip(self):
        payload = {
            "location_city": "Delhi",
            "cuisines": ["Indian"],
            "min_rating": 4.0,
            "max_budget": 500,
            "top_restaurant_names": ["Budget Bites"],
            "label": "helpful",
        }
        r1 = self.client.post("/feedback", json=payload)
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r1.json()["status"], "ok")

        r2 = self.client.get("/feedback?limit=5")
        self.assertEqual(r2.status_code, 200)
        self.assertIn("rows", r2.json())
        self.assertGreaterEqual(r2.json()["count"], 1)


if __name__ == "__main__":
    unittest.main()

