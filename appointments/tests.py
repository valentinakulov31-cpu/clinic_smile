from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from clinic.models import Branch, Service, ServiceCategory, Specialist, Vacancy

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
