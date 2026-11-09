import re
import posixpath
import uuid
from urllib.parse import parse_qsl, unquote, urlencode, urlsplit, urlunsplit

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse


UTM_FIELDS = ("utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term")


def validate_destination(value):
    decoded = value
    for _ in range(3):
        decoded = unquote(decoded)
    try:
        parts = urlsplit(decoded)
    except ValueError as exc:
        raise ValidationError("Некорректный адрес страницы.") from exc
    if (not decoded.startswith("/") or decoded.startswith("//") or parts.netloc or parts.scheme
            or "\\" in decoded or re.search(r"[\x00-\x20\x7f]", decoded)
            or posixpath.normpath(parts.path).split("/")[1].lower() in {"admin", "api", "r", "static", "media"}):
        raise ValidationError("Укажите страницу сайта, например / или /services. Внешние адреса запрещены.")


class CampaignLink(models.Model):
    name = models.CharField("Название", max_length=160)
    slug = models.SlugField("Короткий адрес", max_length=64, unique=True)
    destination = models.CharField("Страница перехода", max_length=500, default="/", validators=[validate_destination])
    utm_source = models.CharField("Источник (utm_source)", max_length=120, default="banner")
    utm_medium = models.CharField("Канал (utm_medium)", max_length=120, default="qr")
    utm_campaign = models.CharField("Кампания (utm_campaign)", max_length=120)
    utm_content = models.CharField("Вариант (utm_content)", max_length=120, blank=True)
    utm_term = models.CharField("Метка (utm_term)", max_length=120, blank=True)
    is_active = models.BooleanField("Активна", default=True)
    created_at = models.DateTimeField("Создана", auto_now_add=True)

    class Meta:
        verbose_name = "Рекламная ссылка"
        verbose_name_plural = "Рекламные ссылки"
        ordering = ("-created_at",)

    def __str__(self):
        return self.name

    @property
    def public_url(self):
        return settings.PUBLIC_SITE_URL + reverse("campaign-redirect", args=[self.slug])

    def target_url(self):
        parts = urlsplit(self.destination)
        query = {key: value for key, value in parse_qsl(parts.query) if key not in (*UTM_FIELDS, "cl")}
        query.update({key: getattr(self, key) for key in UTM_FIELDS if getattr(self, key)})
        query["cl"] = self.slug
        return urlunsplit(("", "", parts.path, urlencode(query), parts.fragment))


class Visit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    visitor_key = models.CharField(max_length=64, db_index=True)
    link = models.ForeignKey(CampaignLink, on_delete=models.SET_NULL, null=True, blank=True)
    started_at = models.DateTimeField(db_index=True)
    last_seen = models.DateTimeField(db_index=True)
    landing_path = models.CharField(max_length=500)
    referrer_host = models.CharField(max_length=253, blank=True)
    utm_source = models.CharField(max_length=120, blank=True)
    utm_medium = models.CharField(max_length=120, blank=True)
    utm_campaign = models.CharField(max_length=120, blank=True)
    utm_content = models.CharField(max_length=120, blank=True)
    utm_term = models.CharField(max_length=120, blank=True)
    page_count = models.PositiveIntegerField(default=0)
    active_seconds = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Статистика"
        verbose_name_plural = "Статистика"


class PageView(models.Model):
    id = models.UUIDField(primary_key=True, editable=False)
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, related_name="pages")
    path = models.CharField(max_length=500)
    started_at = models.DateTimeField()
    active_seconds = models.PositiveIntegerField(default=0)
