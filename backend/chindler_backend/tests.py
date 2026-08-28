from django.test import TestCase
from django.urls import reverse


class HealthCheckTests(TestCase):
    def test_root_redirects_to_admin(self):
        response = self.client.get("/")

        self.assertRedirects(response, "/admin/", fetch_redirect_response=False)

    def test_health_check_reports_service_ready(self):
        response = self.client.get(reverse("health-check"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {"status": "ok", "service": "chindler-backend"}
        )

    def test_database_health_check_reports_active_database(self):
        response = self.client.get(reverse("database-health-check"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertIn(response.json()["database"], {"sqlite", "postgresql"})
