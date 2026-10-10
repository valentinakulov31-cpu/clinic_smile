from django.core.cache import cache
from django.test import Client, TestCase, override_settings

from appointments.models import LeadRequest


@override_settings(CORS_ALLOW_ALL_ORIGINS=False, CORS_ALLOWED_ORIGINS=[])
class LocalFrontendCorsTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = Client(enforce_csrf_checks=True)

    def test_local_frontend_can_read_api_on_different_ports(self):
        for origin in (
            "http://localhost:4200",
            "http://localhost:4201",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
            "http://[::1]:8080",
            "https://localhost:4200",
            "http://localhost",
        ):
            with self.subTest(origin=origin):
                response = self.client.get("/api/services/", HTTP_ORIGIN=origin)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response["Access-Control-Allow-Origin"], origin)
                self.assertIn("origin", response["Vary"].lower())
                self.assertNotIn("Access-Control-Allow-Credentials", response)

    def test_json_post_preflight_allows_frontend_headers(self):
        response = self.client.options(
            "/api/requests/callback/",
            HTTP_ORIGIN="http://localhost:4200",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS="content-type, x-csrftoken",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Access-Control-Allow-Origin"], "http://localhost:4200")
        self.assertIn("POST", response["Access-Control-Allow-Methods"])
        self.assertIn("content-type", response["Access-Control-Allow-Headers"])
        self.assertIn("x-csrftoken", response["Access-Control-Allow-Headers"])

    def test_local_frontend_can_submit_anonymous_lead(self):
        response = self.client.post(
            "/api/requests/callback/",
            {"name": "CORS test", "phone": "+79990000000", "website": ""},
            content_type="application/json",
            HTTP_ORIGIN="http://localhost:4200",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response["Access-Control-Allow-Origin"], "http://localhost:4200")
        self.assertEqual(LeadRequest.objects.count(), 1)

    def test_validation_errors_are_readable_without_creating_a_lead(self):
        response = self.client.post(
            "/api/requests/callback/", {}, content_type="application/json",
            HTTP_ORIGIN="http://localhost:4200",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response["Access-Control-Allow-Origin"], "http://localhost:4200")
        self.assertEqual(LeadRequest.objects.count(), 0)

    def test_untrusted_and_lookalike_origins_are_not_allowed(self):
        for origin in (
            "https://untrusted.example",
            "http://localhost.untrusted.example:4200",
            "http://127.0.0.1.untrusted.example:4200",
            "http://untrusted-localhost:4200",
            "null",
        ):
            with self.subTest(origin=origin):
                response = self.client.options(
                    "/api/services/", HTTP_ORIGIN=origin,
                    HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET",
                )
                self.assertNotIn("Access-Control-Allow-Origin", response)

    def test_admin_has_no_cors_and_still_requires_csrf(self):
        response = self.client.get("/admin/login/", HTTP_ORIGIN="http://localhost:4200")
        self.assertNotIn("Access-Control-Allow-Origin", response)
        response = self.client.post("/admin/login/", {
            "username": "test",
            "password": "test",
            "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value,
        }, HTTP_ORIGIN="http://localhost:4200")
        self.assertEqual(response.status_code, 403)
        self.assertNotIn("Access-Control-Allow-Origin", response)
