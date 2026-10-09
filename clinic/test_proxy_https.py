from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings

from .models import SiteSettings


@override_settings(
    ALLOWED_HOSTS=["ulybnis24.ru", "www.ulybnis24.ru"],
    SECURE_PROXY_SSL_HEADER=("HTTP_X_FORWARDED_PROTO", "https"),
    SESSION_COOKIE_SECURE=True,
    CSRF_COOKIE_SECURE=True,
)
class ProxyHttpsTests(TestCase):
    def setUp(self):
        self.client = Client(
            enforce_csrf_checks=True,
            HTTP_HOST="ulybnis24.ru",
            HTTP_X_FORWARDED_PROTO="https",
        )

    def test_domain_api_and_unknown_host(self):
        SiteSettings.objects.create()
        self.assertEqual(self.client.get("/api/settings/").status_code, 200)
        self.assertEqual(
            self.client.get("/api/settings/", HTTP_HOST="untrusted.example").status_code,
            400,
        )

    def test_admin_login_behind_https_proxy(self):
        get_user_model().objects.create_superuser("proxy-test", password="test-only-password")
        response = self.client.get("/admin/login/")
        self.assertTrue(response.wsgi_request.is_secure())
        self.assertTrue(response.cookies["csrftoken"]["secure"])
        response = self.client.post("/admin/login/", {
            "username": "proxy-test",
            "password": "test-only-password",
            "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value,
            "next": "/admin/",
        }, HTTP_ORIGIN="https://ulybnis24.ru")
        self.assertRedirects(response, "/admin/")
        self.assertTrue(response.cookies["sessionid"]["secure"])

    def test_https_proxy_does_not_bypass_origin_check(self):
        self.client.get("/admin/login/")
        response = self.client.post("/admin/login/", {
            "username": "proxy-test",
            "password": "test-only-password",
            "csrfmiddlewaretoken": self.client.cookies["csrftoken"].value,
        }, HTTP_ORIGIN="https://untrusted.example")
        self.assertEqual(response.status_code, 403)
