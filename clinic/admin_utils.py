from django.contrib import admin
from django.db import models
from django_ckeditor_5.widgets import CKEditor5Widget


RICH_TEXT_FIELDS = {
    "description",
    "short_description",
    "text",
    "responsibilities",
    "requirements",
    "conditions",
    "body",
}


class RichTextAdminMixin:
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if isinstance(db_field, models.TextField) and db_field.name in RICH_TEXT_FIELDS:
            kwargs["widget"] = CKEditor5Widget(config_name="default")
        return super().formfield_for_dbfield(db_field, request, **kwargs)


class TabbedAdminMixin:
    class Media:
        css = {"all": ("admin/css/admin-tabs.css",)}
        js = ("admin/js/admin-tabs.js",)


class ActiveOrderedAdmin(RichTextAdminMixin, admin.ModelAdmin):
    list_display = ("__str__", "is_active", "sort_order", "updated_at")
    list_editable = ("is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("name", "title")
