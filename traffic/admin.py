from datetime import datetime, time, timedelta
from io import BytesIO
from urllib.parse import urlencode

from django import forms
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDate
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html

from appointments.models import LeadRequest
from .models import CampaignLink, Visit
from .sources import CHANNELS, CHANNEL_LABELS, channel_expression


def duration(seconds):
    seconds = int(seconds or 0)
    return f"{seconds // 60} мин {seconds % 60:02d} с"


class PeriodForm(forms.Form):
    start = forms.DateField(label="С", widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"))
    end = forms.DateField(label="По", widget=forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"))
    link = forms.ModelChoiceField(label="Ссылка", queryset=CampaignLink.objects.all(), required=False, empty_label="Все источники")
    channel = forms.ChoiceField(label="Источник", choices=(("", "Все источники"), *CHANNELS), required=False)
    visitor = forms.RegexField(regex=r"^[a-f0-9]{64}$", required=False, widget=forms.HiddenInput,
                              error_messages={"invalid": "Некорректный номер посетителя."})

    def clean(self):
        data = super().clean()
        if data.get("start") and data.get("end"):
            days = (data["end"] - data["start"]).days
            if not 0 <= days <= 365:
                raise forms.ValidationError("Выберите период от 1 до 366 дней.")
        return data


@admin.register(CampaignLink)
class CampaignLinkAdmin(admin.ModelAdmin):
    list_display = ("name", "short_link", "destination", "utm_campaign", "is_active", "link_actions")
    list_filter = ("is_active", "utm_source", "utm_medium")
    search_fields = ("name", "slug", "utm_campaign")
    readonly_fields = ("short_link", "link_actions", "created_at")
    prepopulated_fields = {"slug": ("name",)}
    fields = ("name", "slug", "destination", "is_active", "utm_source", "utm_medium", "utm_campaign",
              "utm_content", "utm_term", "short_link", "link_actions", "created_at")

    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields + (("slug",) if obj else ())

    def get_prepopulated_fields(self, request, obj=None):
        return {} if obj else self.prepopulated_fields

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.display(description="Ссылка для баннера")
    def short_link(self, obj):
        return format_html('<a href="{}" target="_blank" rel="noopener">{}</a>', obj.public_url, obj.public_url) if obj.pk else "—"

    @admin.display(description="QR и статистика")
    def link_actions(self, obj):
        if not obj.pk:
            return "—"
        return format_html('<a href="{}">QR PNG</a> · <a href="{}">QR SVG</a> · <a href="{}?link={}">Статистика</a>',
                           reverse("admin:traffic_campaignlink_qr", args=[obj.pk, "png"]),
                           reverse("admin:traffic_campaignlink_qr", args=[obj.pk, "svg"]),
                           reverse("admin:traffic_visit_changelist"), obj.pk)

    def get_urls(self):
        return [path("<int:pk>/qr/<str:kind>/", self.admin_site.admin_view(self.qr), name="traffic_campaignlink_qr")] + super().get_urls()

    def qr(self, request, pk, kind):
        import qrcode
        import qrcode.image.svg
        link = get_object_or_404(CampaignLink, pk=pk)
        if not self.has_view_permission(request, link):
            raise PermissionDenied
        if kind not in ("png", "svg"):
            return HttpResponse(status=404)
        code = qrcode.QRCode(box_size=16, border=4, error_correction=qrcode.constants.ERROR_CORRECT_M)
        code.add_data(link.public_url)
        code.make(fit=True)
        factory = qrcode.image.svg.SvgPathImage if kind == "svg" else None
        image = code.make_image(image_factory=factory)
        output = BytesIO()
        image.save(output)
        response = HttpResponse(output.getvalue(), content_type="image/svg+xml" if kind == "svg" else "image/png")
        response["Content-Disposition"] = f'attachment; filename="qr-{link.slug}.{kind}"'
        return response


@admin.register(Visit)
class StatisticsAdmin(admin.ModelAdmin):
    def get_urls(self):
        return [
            path("sessions/", self.admin_site.admin_view(self.sessions), name="traffic_visit_sessions"),
            path("sessions/<uuid:pk>/", self.admin_site.admin_view(self.session_detail), name="traffic_visit_session_detail"),
        ] + super().get_urls()

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def filtered_visits(self, request):
        today = timezone.localdate()
        params = request.GET.copy()
        params.setdefault("start", (today - timedelta(days=29)).isoformat())
        params.setdefault("end", today.isoformat())
        form = PeriodForm(params)
        visits = Visit.objects.none()
        if form.is_valid():
            start = timezone.make_aware(datetime.combine(form.cleaned_data["start"], time.min))
            end = timezone.make_aware(datetime.combine(form.cleaned_data["end"] + timedelta(days=1), time.min))
            visits = Visit.objects.filter(started_at__gte=start, started_at__lt=end)
            if form.cleaned_data["link"]:
                visits = visits.filter(link=form.cleaned_data["link"])
            if form.cleaned_data["visitor"]:
                visits = visits.filter(visitor_key=form.cleaned_data["visitor"])
        visits = visits.annotate(channel=channel_expression())
        if form.is_valid() and form.cleaned_data["channel"]:
            visits = visits.filter(channel=form.cleaned_data["channel"])
        return form, visits

    def report_context(self, request, title):
        return {
            **self.admin_site.each_context(request), "opts": self.model._meta, "title": title,
            "summary_url": reverse("admin:traffic_visit_changelist"),
            "sessions_url": reverse("admin:traffic_visit_sessions"),
            "links_url": reverse("admin:traffic_campaignlink_changelist"),
            "add_url": reverse("admin:traffic_campaignlink_add"),
            "can_add_link": request.user.has_perm("traffic.add_campaignlink"),
        }

    def filter_query(self, form):
        return urlencode({key: form.data.get(key) for key in form.fields if form.data.get(key)})

    def changelist_view(self, request, extra_context=None):
        if not self.has_view_permission(request):
            raise PermissionDenied
        form, visits = self.filtered_visits(request)
        totals = visits.aggregate(visits=Count("id"), visitors=Count("visitor_key", distinct=True),
                                   pages=Sum("page_count"), seconds=Sum("active_seconds"))
        leads = LeadRequest.objects.filter(visit__in=visits).exclude(status="canceled")
        totals["leads"] = leads.count()
        totals["pages"] = totals["pages"] or 0
        totals["duration"] = duration((totals["seconds"] or 0) / (totals["visits"] or 1))
        groups = ["link_id", "link__name", "utm_source", "utm_medium", "utm_campaign", "referrer_host"]
        sources = list(visits.values(*groups, "channel").annotate(visits=Count("id"), visitors=Count("visitor_key", distinct=True),
                       seconds=Sum("active_seconds")).order_by("-visits")[:100])
        lead_counts = {
            tuple(row["visit__" + field] for field in groups): row["total"]
            for row in leads.values(*["visit__" + field for field in groups]).annotate(total=Count("id"))
        }
        for row in sources:
            row["label"] = row["link__name"] or row["utm_source"] or row["referrer_host"] or "Прямой / неизвестный"
            row["duration"] = duration(row["seconds"] / row["visits"])
            row["leads"] = lead_counts.get(tuple(row[field] for field in groups), 0)
            row["channel_label"] = CHANNEL_LABELS[row["channel"]]
        daily = list(visits.annotate(day=TruncDate("started_at")).values("day").annotate(visits=Count("id"),
                     visitors=Count("visitor_key", distinct=True)).order_by("-day"))
        context = {
            **self.report_context(request, "Статистика сайта"),
            "form": form, "totals": totals, "sources": sources, "daily": daily,
            "filter_query": self.filter_query(form),
        }
        return TemplateResponse(request, "admin/traffic/statistics.html", context)

    def sessions(self, request):
        if not self.has_view_permission(request):
            raise PermissionDenied
        form, visits = self.filtered_visits(request)
        visits = visits.select_related("link").annotate(
            lead_count=Count("leads", filter=~Q(leads__status="canceled")),
        ).order_by("-started_at", "-pk")
        page = Paginator(visits, 50).get_page(request.GET.get("page"))
        for visit in page:
            visit.duration = duration(visit.active_seconds)
            visit.channel_label = CHANNEL_LABELS[visit.channel]
        visitor_key = form.cleaned_data.get("visitor") if form.is_valid() else ""
        context = {
            **self.report_context(request, "Журнал посещений"),
            "form": form, "page": page, "filter_query": self.filter_query(form),
            "visitor_label": visitor_key[:12] if visitor_key else "",
        }
        return TemplateResponse(request, "admin/traffic/sessions.html", context)

    def session_detail(self, request, pk):
        if not self.has_view_permission(request):
            raise PermissionDenied
        visit = get_object_or_404(Visit.objects.select_related("link").annotate(channel=channel_expression()), pk=pk)
        pages = visit.pages.order_by("started_at", "pk")
        page = Paginator(pages, 100).get_page(request.GET.get("page"))
        for item in page:
            item.duration = duration(item.active_seconds)
        leads = None
        if request.user.has_perm("appointments.view_leadrequest") or request.user.has_perm("appointments.change_leadrequest"):
            leads = visit.leads.exclude(status="canceled").only("id", "status").order_by("id")
        today = timezone.localdate()
        visitor_query = urlencode({"visitor": visit.visitor_key, "start": (today - timedelta(days=179)).isoformat(), "end": today.isoformat()})
        context = {
            **self.report_context(request, "Посещение " + timezone.localtime(visit.started_at).strftime("%d.%m.%Y %H:%M")),
            "visit": visit, "page": page, "leads": leads, "channel_label": CHANNEL_LABELS[visit.channel],
            "active_duration": duration(visit.active_seconds), "visitor_query": visitor_query,
        }
        return TemplateResponse(request, "admin/traffic/session_detail.html", context)
