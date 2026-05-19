from django.contrib import admin

from .models import LeadRequest


@admin.register(LeadRequest)
class LeadRequestAdmin(admin.ModelAdmin):
    list_display = ("request_type", "name", "phone", "status", "created_at")
    list_filter = ("request_type", "status", "created_at")
    search_fields = ("name", "phone", "email", "comment")
    readonly_fields = ("created_at", "updated_at")
