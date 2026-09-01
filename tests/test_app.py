import unittest

from app.app import app


class TestCanaryApplication(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_home_endpoint(self):
        response = self.client.get("/")

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.get_json()

        self.assertEqual(
            data["status"],
            "success",
        )

    def test_health_endpoint(self):
        response = self.client.get("/health")

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.get_json()["status"],
            "healthy",
        )

    def test_readiness_endpoint(self):
        response = self.client.get("/ready")

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response.get_json()["status"],
            "ready",
        )

    def test_metrics_endpoint(self):
        response = self.client.get("/metrics")

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertIn(
            b"canary_http_requests_total",
            response.data,
        )


if __name__ == "__main__":
    unittest.main()
