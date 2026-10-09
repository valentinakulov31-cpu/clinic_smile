from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .forms import SiteSettingsAdminForm
from .models import SiteSettings


class NotificationSettingsTests(TestCase):
    def test_admin_form_normalizes_and_deduplicates_recipients(self):
        form = SiteSettingsAdminForm(data={
            "request_notification_emails": " reception@example.com \nmanager@example.com\nRECEPTION@example.com\n",
        })
        self.assertTrue(form.is_valid(), form.errors)
        obj = form.save()
        self.assertEqual(obj.request_notification_emails, ["reception@example.com", "manager@example.com"])

    def test_admin_rejects_invalid_address(self):
        form = SiteSettingsAdminForm(data={"request_notification_emails": "ok@example.com\ninvalid"})
        self.assertFalse(form.is_valid())
        self.assertIn("request_notification_emails", form.errors)

    def test_empty_admin_field_disables_notifications(self):
        form = SiteSettingsAdminForm(data={"request_notification_emails": ""})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().request_notification_emails, [])

    def test_model_rejects_invalid_recipient_data(self):
        for value in ["admin@example.com", [123], ["not-an-address"]]:
            with self.subTest(value=value), self.assertRaises(ValidationError):
                SiteSettings(request_notification_emails=value).full_clean()

    def test_public_settings_do_not_expose_recipients(self):
        SiteSettings.objects.create(request_notification_emails=["private@example.com"])
        response = self.client.get(reverse("site-settings"))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("request_notification_emails", response.json())
        self.assertNotContains(response, "private@example.com")
