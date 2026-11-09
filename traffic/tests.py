from datetime import timedelta
import uuid

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from appointments.models import LeadRequest
from .models import CampaignLink, PageView, Visit
from .sources import channel_expression


@override_settings(PUBLIC_SITE_URL="https://ulybnis24.ru", ALLOWED_HOSTS=["ulybnis24.ru"],
                   EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class TrafficTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = Client(enforce_csrf_checks=True, HTTP_HOST="ulybnis24.ru", HTTP_ORIGIN="https://ulybnis24.ru",
                             HTTP_USER_AGENT="Mozilla/5.0 TestBrowser")
        self.link = CampaignLink.objects.create(name="Баннер у клиники", slug="banner1", utm_campaign="outdoor")

    def event(self, data, **extra):
        return self.client.post(reverse("traffic-event"), data, content_type="application/json", **extra)

    def page(self, **data):
        return self.event({"event": "page", "page_id": str(uuid.uuid4()), "path": "/", **data})

    def staff(self):
        return get_user_model().objects.create_superuser("traffic-test", password="test-only-password")

    def test_redirect_utm_and_no_cache(self):
        response = self.client.get("/r/banner1")
        self.assertEqual(response.status_code, 302)
        self.assertIn("cl=banner1", response.url)
        self.assertIn("utm_source=banner", response.url)
        self.assertEqual(response["Cache-Control"], "no-store")
        self.assertEqual(Visit.objects.count(), 0)
        self.link.is_active = False
        self.link.save()
        self.assertEqual(self.client.get("/r/banner1").status_code, 404)

    def test_destinations_cannot_redirect_outside_site_or_to_admin(self):
        for url in ("https://evil.example", "//evil.example", "/\\evil.example", "/%2fexample.com", "/admin/", "/api/", "/r/test", "/%0aHeader"):
            with self.subTest(url=url), self.assertRaises(ValidationError):
                self.link.destination = url
                self.link.full_clean()
        self.link.destination = "/services?category=3#prices"
        self.link.full_clean()

    def test_session_attribution_and_page_idempotency(self):
        page_id = str(uuid.uuid4())
        data = {"cl": "banner1", "path": "/?private=secret", "page_id": page_id, "referrer": "https://search.example/path?secret=yes"}
        self.assertEqual(self.page(**data).status_code, 200)
        self.assertEqual(self.page(**data).status_code, 200)
        self.page(path="/contacts")
        visit = Visit.objects.get()
        self.assertEqual(visit.page_count, 2)
        self.assertEqual(visit.landing_path, "/")
        self.assertEqual(visit.referrer_host, "search.example")
        self.assertEqual(visit.utm_source, "banner")
        self.assertEqual(visit.link, self.link)
        self.assertEqual(PageView.objects.count(), 2)
        self.assertEqual(len(visit.visitor_key), 64)

    def test_heartbeat_monotonic_capped_and_signed(self):
        token = self.page().json()["token"]
        page = PageView.objects.get()
        PageView.objects.filter(pk=page.pk).update(started_at=timezone.now() - timedelta(seconds=30))
        for seconds in (10, 10, 5, 100000):
            self.assertEqual(self.event({"event": "heartbeat", "token": token, "active_seconds": seconds}).status_code, 204)
        visit = Visit.objects.get()
        self.assertEqual(visit.active_seconds, 30)
        self.assertEqual(self.event({"event": "heartbeat", "token": "invalid", "active_seconds": 30}).status_code, 400)

    def test_source_change_and_expired_visit(self):
        self.page(utm_source="advert", utm_campaign="one")
        self.page(utm_source="advert", utm_campaign="two")
        self.assertEqual(Visit.objects.count(), 2)
        Visit.objects.update(last_seen=timezone.now() - timedelta(minutes=31))
        self.page(path="/contacts")
        self.assertEqual(Visit.objects.count(), 3)
        self.assertEqual(Visit.objects.values("visitor_key").distinct().count(), 1)

    def test_ignored_requests_and_origin(self):
        for extra in ({"HTTP_DNT": "1"}, {"HTTP_SEC_GPC": "1"}, {"HTTP_USER_AGENT": "Googlebot"}):
            response = self.event({"event": "page", "page_id": str(uuid.uuid4()), "path": "/"}, **extra)
            self.assertEqual(response.status_code, 204)
        self.assertEqual(self.event({}, HTTP_ORIGIN="https://evil.example").status_code, 403)
        self.client.force_login(self.staff())
        self.assertEqual(self.page().status_code, 204)
        self.assertFalse(Visit.objects.exists())

    def test_lead_gets_attribution_and_legacy_forms_work(self):
        self.page(cl="banner1")
        response = self.client.post(reverse("appointment-request"), {"name": "Test", "phone": "+70000000000"}, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(LeadRequest.objects.get().visit.link, self.link)
        self.client.cookies.clear()
        response = self.client.post(reverse("callback-request"), {"name": "Test", "phone": "+70000000000"}, content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertIsNone(LeadRequest.objects.get(pk=response.json()["id"]).visit_id)

    def test_admin_stats_and_qr_permissions(self):
        url = reverse("admin:traffic_visit_changelist")
        self.assertEqual(self.client.get(url).status_code, 302)
        self.page(cl="banner1")
        self.page(path="/contacts")
        visit = Visit.objects.get()
        for status in ("new", "new", "canceled"):
            LeadRequest.objects.create(name="Test", phone="0", request_type="callback", visit=visit, status=status)
        Visit.objects.update(active_seconds=40)
        self.client.force_login(self.staff())
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data["totals"]["visits"], 1)
        self.assertEqual(response.context_data["totals"]["leads"], 2)
        self.assertEqual(response.context_data["totals"]["duration"], "0 мин 40 с")
        self.assertEqual(response.context_data["sources"][0]["leads"], 2)
        self.assertEqual(response.context_data["sources"][0]["duration"], "0 мин 40 с")
        for kind in ("png", "svg"):
            response = self.client.get(reverse("admin:traffic_campaignlink_qr", args=[self.link.pk, kind]))
            self.assertEqual(response.status_code, 200)
            self.assertGreater(len(response.content), 300)
        self.assertEqual(self.client.get(url + "?start=wrong").status_code, 200)

    def test_invalid_events_and_page_collision(self):
        for data in ([], {"event": "wrong"}, {"event": "page", "path": "//evil.example"}, {"event": "heartbeat", "active_seconds": "5"}):
            self.assertEqual(self.event(data).status_code, 400)
        page_id = str(uuid.uuid4())
        self.page(page_id=page_id)
        self.client.cookies.clear()
        self.assertEqual(self.page(page_id=page_id).status_code, 409)

    def test_staff_without_stats_permission_is_forbidden(self):
        user = get_user_model().objects.create_user("limited", password="test-only", is_staff=True)
        self.client.force_login(user)
        self.assertEqual(self.client.get(reverse("admin:traffic_visit_changelist")).status_code, 403)
        self.assertEqual(self.client.get(reverse("admin:traffic_campaignlink_qr", args=[self.link.pk, "png"])).status_code, 403)


class VisitJournalTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser("journal-test", password="test-only-password")
        self.client.force_login(self.user)
        self.url = reverse("admin:traffic_visit_sessions")

    def visit(self, **values):
        now = timezone.now()
        data = {"visitor_key": "a" * 64, "started_at": now, "last_seen": now, "landing_path": "/"}
        data.update(values)
        return Visit.objects.create(**data)

    def test_channels_match_hosts_and_campaign_precedence(self):
        cases = [
            ({"referrer_host": "yandex.ru"}, "search"),
            ({"referrer_host": "www.google.com"}, "search"),
            ({"referrer_host": "WWW.YANDEX.RU"}, "search"),
            ({"referrer_host": "yandex.ru.evil.example"}, "referral"),
            ({"referrer_host": "notgoogle.com"}, "referral"),
            ({"referrer_host": "yandex.ru", "utm_medium": "CPC"}, "paid"),
            ({"referrer_host": "google.com", "utm_medium": "qr"}, "qr"),
            ({"referrer_host": "vk.com"}, "social"),
            ({"referrer_host": "mail.ru"}, "referral"),
            ({"referrer_host": "go.mail.ru"}, "search"),
            ({"utm_medium": "email"}, "email"),
            ({"utm_medium": "organic"}, "search"),
            ({"utm_source": "partner", "referrer_host": "google.com"}, "tagged"),
            ({"referrer_host": "example.com"}, "referral"),
            ({}, "direct"),
        ]
        for values, expected in cases:
            with self.subTest(values=values):
                visit = self.visit(**values)
                actual = Visit.objects.annotate(channel=channel_expression()).get(pk=visit.pk).channel
                self.assertEqual(actual, expected)

    def test_journal_filters_and_counts(self):
        search_visit = self.visit(referrer_host="yandex.ru", page_count=2, active_seconds=95)
        self.visit(utm_medium="qr", visitor_key="b" * 64)
        self.visit(referrer_host="google.com", started_at=timezone.now() - timedelta(days=40))
        for status in ("new", "new", "canceled"):
            LeadRequest.objects.create(name="Test", phone="0", request_type="callback", visit=search_visit, status=status)
        response = self.client.get(self.url, {"channel": "search"})
        self.assertEqual(response.status_code, 200)
        page = response.context_data["page"]
        self.assertEqual(page.paginator.count, 1)
        self.assertEqual(page[0].lead_count, 2)
        self.assertEqual(page[0].duration, "1 мин 35 с")
        self.assertContains(response, "yandex.ru")
        self.assertContains(response, "Поиск")
        summary = self.client.get(reverse("admin:traffic_visit_changelist"), {"channel": "search"})
        self.assertEqual(summary.context_data["totals"]["visits"], 1)
        self.assertEqual(summary.context_data["sources"][0]["channel_label"], "Поиск")
        self.assertEqual(summary.context_data["sources"][0]["leads"], 2)

    def test_link_and_visitor_filters(self):
        link = CampaignLink.objects.create(name="Test", slug="test", utm_campaign="test")
        selected = self.visit(link=link)
        self.visit(visitor_key="b" * 64, link=link)
        self.visit(visitor_key="c" * 64)
        response = self.client.get(self.url, {"visitor": selected.visitor_key, "link": link.pk})
        self.assertEqual(response.context_data["page"].paginator.count, 1)
        self.assertEqual(response.context_data["visitor_label"], "a" * 12)

    def test_invalid_filters_do_not_expose_unfiltered_data(self):
        self.visit()
        for params in ({"channel": "bad"}, {"visitor": "bad"}, {"start": "bad"}, {"link": "-1"}):
            with self.subTest(params=params):
                response = self.client.get(self.url, params)
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context_data["form"].errors)
                self.assertEqual(response.context_data["page"].paginator.count, 0)

    def test_journal_pagination_preserves_filters(self):
        now = timezone.now()
        Visit.objects.bulk_create([
            Visit(visitor_key="a" * 64, started_at=now - timedelta(seconds=i), last_seen=now,
                  landing_path="/", referrer_host="yandex.ru") for i in range(51)
        ])
        response = self.client.get(self.url, {"channel": "search"})
        self.assertEqual(len(response.context_data["page"]), 50)
        self.assertContains(response, "channel=search")
        second = self.client.get(self.url, {"channel": "search", "page": 2})
        self.assertEqual(len(second.context_data["page"]), 1)
        self.assertEqual(self.client.get(self.url, {"page": "invalid"}).status_code, 200)

    def test_detail_pages_are_ordered_and_show_times(self):
        visit = self.visit(page_count=2, active_seconds=100, referrer_host="google.com", utm_term="campaign-label")
        now = timezone.now()
        PageView.objects.create(id=uuid.uuid4(), visit=visit, path="/contacts", started_at=now, active_seconds=40)
        PageView.objects.create(id=uuid.uuid4(), visit=visit, path="/", started_at=now - timedelta(seconds=90), active_seconds=60)
        lead = LeadRequest.objects.create(name="Private name", phone="0", request_type="callback", visit=visit)
        response = self.client.get(reverse("admin:traffic_visit_session_detail", args=[visit.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual([page.path for page in response.context_data["page"]], ["/", "/contacts"])
        self.assertContains(response, "1 мин 00 с")
        self.assertContains(response, "0 мин 40 с")
        self.assertContains(response, "1 мин 40 с")
        self.assertContains(response, "Метка (utm_term)")
        self.assertContains(response, reverse("admin:appointments_leadrequest_change", args=[lead.pk]))
        self.assertNotContains(response, "Private name")
        self.assertContains(response, "Все посещения этого браузера")

    def test_permissions_and_missing_visit(self):
        from django.contrib.auth.models import Permission
        visit = self.visit()
        detail = reverse("admin:traffic_visit_session_detail", args=[visit.pk])
        self.client.logout()
        for url in (self.url, detail):
            self.assertEqual(self.client.get(url).status_code, 302)
        limited = get_user_model().objects.create_user("journal-limited", is_staff=True)
        self.client.force_login(limited)
        for url in (self.url, detail):
            self.assertEqual(self.client.get(url).status_code, 403)
        limited.user_permissions.add(Permission.objects.get(content_type__app_label="traffic", codename="view_visit"))
        response = self.client.get(detail)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context_data["leads"])
        self.assertNotContains(response, 'id="leads-title"')
        self.assertEqual(self.client.get(reverse("admin:traffic_visit_session_detail", args=[uuid.uuid4()])).status_code, 404)

    def test_untrusted_metadata_is_escaped(self):
        visit = self.visit(utm_source='<script>alert("x")</script>')
        PageView.objects.create(id=uuid.uuid4(), visit=visit, path='/<img src=x onerror="alert(1)">', started_at=timezone.now())
        response = self.client.get(reverse("admin:traffic_visit_session_detail", args=[visit.pk]))
        self.assertNotContains(response, '<script>alert("x")</script>')
        self.assertNotContains(response, '<img src=x')
        self.assertContains(response, "&lt;script&gt;")
