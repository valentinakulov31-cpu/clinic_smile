from smtplib import SMTPException
from unittest.mock import patch

from django.core import mail
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from clinic.models import Branch, Service, ServiceCategory, SiteSettings, Specialist, Vacancy

from .models import LeadRequest, RequestType


class LeadRequestApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.category = ServiceCategory.objects.create(name="Ортопедия")
        cls.service = Service.objects.create(category=cls.category, name="Протезирование")
        cls.specialist = Specialist.objects.create(full_name="Иван Иванов")
        cls.branch = Branch.objects.create(name="Центр", address="Адрес")
        cls.vacancy = Vacancy.objects.create(title="Администратор")

    def setUp(self):
        cache.clear()

    def test_consultation_request_is_created(self):
        response = self.client.post(
            reverse("consultation-request"),
            {
                "name": "Иван",
                "phone": "+79990000000",
                "email": "ivan@example.com",
                "comment": "Хочу записаться",
                "service": self.service.id,
                "specialist": self.specialist.id,
                "branch": self.branch.id,
                "source": "hero-form",
                "website": "",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(LeadRequest.objects.count(), 1)
        self.assertEqual(LeadRequest.objects.first().request_type, RequestType.CONSULTATION)

    def test_rate_limit_blocks_repeated_requests(self):
        payload = {
            "name": "Иван",
            "phone": "+79990000000",
            "website": "",
        }
        first = self.client.post(reverse("callback-request"), payload, format="json")
        second = self.client.post(reverse("callback-request"), payload, format="json")
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 429)

    def test_vacancy_request_requires_vacancy(self):
        response = self.client.post(
            reverse("vacancy-request"),
            {
                "name": "Иван",
                "phone": "+79990000000",
                "website": "",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("vacancy", response.data)

    def test_honeypot_field_rejects_spam(self):
        response = self.client.post(
            reverse("appointment-request"),
            {
                "name": "Спамер",
                "phone": "+79990000000",
                "website": "https://spam.example",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("website", response.data)

    def test_vacancy_request_saves_selected_vacancy(self):
        response = self.client.post(
            reverse("vacancy-request"),
            {
                "name": "Кандидат",
                "phone": "+79990000000",
                "vacancy": self.vacancy.id,
                "website": "",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(LeadRequest.objects.first().vacancy_id, self.vacancy.id)


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend", DEFAULT_FROM_EMAIL="noreply@example.com")
class LeadNotificationTests(TestCase):
    def setUp(self):
        cache.clear()
        self.site_settings = SiteSettings.objects.create(
            request_notification_emails=["reception@example.com", "manager@example.com"]
        )

    def submit(self):
        return self.client.post(reverse("callback-request"), {"name": "Test", "phone": "+79990000000"})

    def test_notification_reaches_all_configured_recipients(self):
        response = self.submit()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.to, self.site_settings.request_notification_emails)
        self.assertEqual(message.from_email, "noreply@example.com")
        self.assertIn("+79990000000", message.body)
        self.assertIn(reverse("admin:appointments_leadrequest_change", args=[response.json()["id"]]), message.body)

    def test_empty_list_keeps_request_without_sending_email(self):
        self.site_settings.request_notification_emails = []
        self.site_settings.save()
        self.assertEqual(self.submit().status_code, 201)
        self.assertEqual(LeadRequest.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 0)

    def test_smtp_failure_does_not_lose_request(self):
        with patch("appointments.views.send_mail", side_effect=SMTPException("SMTP unavailable")):
            with self.assertLogs("appointments.views", level="ERROR"):
                response = self.submit()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(LeadRequest.objects.count(), 1)
