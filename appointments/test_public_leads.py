from django.contrib.auth import get_user_model
from django.core import mail
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from clinic.models import SiteSettings, Vacancy
from .models import LeadRequest


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    ALLOWED_HOSTS=["ulybnis24.ru"],
    SECURE_PROXY_SSL_HEADER=("HTTP_X_FORWARDED_PROTO", "https"),
)
class PublicLeadSessionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = get_user_model().objects.create_superuser(
            username="lead-session-test", password="test-only-password",
        )
        cls.vacancy = Vacancy.objects.create(title="Reception")
        SiteSettings.objects.create(request_notification_emails=["reception@example.com"])

    def setUp(self):
        cache.clear()
        self.client = Client(
            enforce_csrf_checks=True,
            HTTP_HOST="ulybnis24.ru",
            HTTP_X_FORWARDED_PROTO="https",
            HTTP_ORIGIN="https://ulybnis24.ru",
        )

    def submit_all_forms(self):
        for endpoint in ("callback-request", "appointment-request", "consultation-request", "vacancy-request"):
            with self.subTest(endpoint=endpoint):
                data = {"name": "Public form test", "phone": "+79990000000", "consent": True}
                if endpoint == "vacancy-request":
                    data["vacancy"] = self.vacancy.pk
                response = self.client.post(reverse(endpoint), data, content_type="application/json")
                self.assertEqual(response.status_code, 201, response.content)
                self.assertTrue(LeadRequest.objects.filter(pk=response.json()["id"]).exists())
        self.assertEqual(LeadRequest.objects.count(), 4)
        self.assertEqual(len(mail.outbox), 4)

    def test_visitor_can_submit_without_csrf_token(self):
        self.submit_all_forms()

    def test_admin_session_does_not_break_public_forms(self):
        self.client.force_login(self.staff)
        self.client.get("/admin/")
        self.assertIn("sessionid", self.client.cookies)
        self.assertIn("csrftoken", self.client.cookies)
        self.submit_all_forms()

    def test_admin_session_still_validates_data_and_blocks_repeated_submissions(self):
        self.client.force_login(self.staff)
        url = reverse("callback-request")
        invalid = self.client.post(url, {}, content_type="application/json")
        self.assertEqual(invalid.status_code, 400)
        self.assertIn("phone", invalid.json())
        data = {"name": "Public form test", "phone": "+79990000000"}
        first = self.client.post(url, data, content_type="application/json")
        second = self.client.post(url, data, content_type="application/json")
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 429)
        self.assertEqual(LeadRequest.objects.count(), 1)

    def test_admin_changes_still_require_csrf_token(self):
        self.client.force_login(self.staff)
        url = reverse("admin:appointments_leadrequest_add")
        self.assertEqual(self.client.get(url).status_code, 200)
        response = self.client.post(url, {"name": "Must not save", "phone": "+79990000000"})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(LeadRequest.objects.exists())
