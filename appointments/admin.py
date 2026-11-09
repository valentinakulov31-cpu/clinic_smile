from django.contrib import admin

from .models import LeadRequest


@admin.register(LeadRequest)
class LeadRequestAdmin(admin.ModelAdmin):
    list_display = ("request_type", "name", "phone", "status", "created_at")
    list_filter = ("request_type", "status", "created_at")
    search_fields = ("name", "phone", "email", "comment")
    readonly_fields = ("created_at", "updated_at", "campaign_source")

    @admin.display(description="Рекламный источник")
    def campaign_source(self, obj):
        if not obj.visit_id:
            return "—"
        visit = obj.visit
        return " / ".join(filter(None, [str(visit.link) if visit.link_id else "", visit.utm_source,
                                        visit.utm_medium, visit.utm_campaign, visit.referrer_host])) or "Прямой переход"
