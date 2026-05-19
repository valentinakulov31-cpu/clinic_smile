from django.contrib import admin
from django.db import models
from django_ckeditor_5.widgets import CKEditor5Widget

from .models import (
    AboutPage,
    Branch,
    ContactInfo,
    Document,
    DocumentCategory,
    GalleryImage,
    Offer,
    PatientsPage,
    PaymentMethod,
    PriceCategory,
    PriceItem,
    Requisites,
    Review,
    Service,
    ServiceCategory,
    ServiceImage,
    Specialist,
    SpecialistDocument,
    Vacancy,
)


RICH_TEXT_FIELDS = {
    "description",
    "short_description",
    "text",
    "responsibilities",
    "requirements",
    "conditions",
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


class ServiceImageInline(admin.TabularInline):
    model = ServiceImage
    extra = 1


class SpecialistDocumentInline(admin.TabularInline):
    model = SpecialistDocument
    extra = 1


@admin.register(Branch)
class BranchAdmin(ActiveOrderedAdmin):
    search_fields = ("name", "address", "email")


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(TabbedAdminMixin, ActiveOrderedAdmin):
    fieldsets = (
        ("Основное", {"classes": ("admin-tab",), "fields": ("name", "slug", "description", "icon", "is_active", "sort_order")}),
        (
            "SEO",
            {
                "classes": ("admin-tab",),
                "fields": ("seo_title", "seo_description", "og_title", "og_description", "og_image"),
            },
        ),
    )


@admin.register(Service)
class ServiceAdmin(TabbedAdminMixin, ActiveOrderedAdmin):
    fieldsets = (
        (
            "Основное",
            {
                "classes": ("admin-tab",),
                "fields": (
                    "category",
                    "name",
                    "slug",
                    "short_description",
                    "description",
                    "card_image",
                    "branches",
                    "is_active",
                    "sort_order",
                ),
            },
        ),
        (
            "SEO",
            {
                "classes": ("admin-tab",),
                "fields": ("seo_title", "seo_description", "og_title", "og_description", "og_image"),
            },
        ),
    )
    list_display = ("name", "category", "is_active", "sort_order")
    list_filter = ("category", "is_active")
    search_fields = ("name", "short_description", "description")
    filter_horizontal = ("branches",)
    inlines = (ServiceImageInline,)


@admin.register(PriceCategory)
class PriceCategoryAdmin(ActiveOrderedAdmin):
    fields = ("name", "slug", "is_active", "sort_order")


@admin.register(PriceItem)
class PriceItemAdmin(ActiveOrderedAdmin):
    list_display = ("title", "category", "price", "is_from_price", "is_active", "sort_order")
    list_filter = ("category", "is_active", "is_from_price")
    search_fields = ("title", "comment")


@admin.register(Offer)
class OfferAdmin(TabbedAdminMixin, ActiveOrderedAdmin):
    fieldsets = (
        (
            "Основное",
            {
                "classes": ("admin-tab",),
                "fields": (
                    "title",
                    "slug",
                    "short_description",
                    "description",
                    "image",
                    "price",
                    "old_price",
                    "is_from_price",
                    "starts_at",
                    "ends_at",
                    "service",
                    "branches",
                    "is_active",
                    "sort_order",
                ),
            },
        ),
        (
            "SEO",
            {
                "classes": ("admin-tab",),
                "fields": ("seo_title", "seo_description", "og_title", "og_description", "og_image"),
            },
        ),
    )
    list_display = ("title", "price", "ends_at", "is_active", "sort_order")
    list_filter = ("is_active", "starts_at", "ends_at")
    search_fields = ("title", "short_description", "description")
    filter_horizontal = ("branches",)


@admin.register(Specialist)
class SpecialistAdmin(TabbedAdminMixin, ActiveOrderedAdmin):
    fieldsets = (
        (
            "Основное",
            {
                "classes": ("admin-tab",),
                "fields": (
                    "full_name",
                    "slug",
                    "photo",
                    "position",
                    "specializations",
                    "short_description",
                    "description",
                    "experience",
                    "education",
                    "services",
                    "branches",
                    "is_active",
                    "sort_order",
                ),
            },
        ),
        (
            "SEO",
            {
                "classes": ("admin-tab",),
                "fields": ("seo_title", "seo_description", "og_title", "og_description", "og_image"),
            },
        ),
    )
    list_display = ("full_name", "position", "is_active", "sort_order")
    search_fields = ("full_name", "position", "specializations")
    filter_horizontal = ("services", "branches")
    inlines = (SpecialistDocumentInline,)


@admin.register(PaymentMethod)
class PaymentMethodAdmin(ActiveOrderedAdmin):
    search_fields = ("title",)


@admin.register(PatientsPage)
class PatientsPageAdmin(TabbedAdminMixin, RichTextAdminMixin, admin.ModelAdmin):
    fieldsets = (
        ("Основное", {"classes": ("admin-tab",), "fields": ("title", "text", "image", "offers")}),
        ("SEO", {"classes": ("admin-tab",), "fields": ("seo_title", "seo_description")}),
    )
    filter_horizontal = ("offers",)


class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 1


@admin.register(AboutPage)
class AboutPageAdmin(TabbedAdminMixin, RichTextAdminMixin, admin.ModelAdmin):
    fieldsets = (
        ("Основное", {"classes": ("admin-tab",), "fields": ("title", "text", "image")}),
        ("SEO", {"classes": ("admin-tab",), "fields": ("seo_title", "seo_description")}),
    )
    inlines = (GalleryImageInline,)


@admin.register(GalleryImage)
class GalleryImageAdmin(ActiveOrderedAdmin):
    search_fields = ("caption",)


@admin.register(Vacancy)
class VacancyAdmin(TabbedAdminMixin, ActiveOrderedAdmin):
    fieldsets = (
        (
            "Основное",
            {
                "classes": ("admin-tab",),
                "fields": (
                    "title",
                    "slug",
                    "short_description",
                    "image",
                    "responsibilities",
                    "requirements",
                    "conditions",
                    "description",
                    "is_active",
                    "sort_order",
                ),
            },
        ),
        ("SEO", {"classes": ("admin-tab",), "fields": ("seo_title", "seo_description", "og_title", "og_description", "og_image")}),
    )
    search_fields = ("title", "short_description", "description")


@admin.register(ContactInfo)
class ContactInfoAdmin(TabbedAdminMixin, RichTextAdminMixin, admin.ModelAdmin):
    fieldsets = (
        (
            "Основное",
            {
                "classes": ("admin-tab",),
                "fields": ("address", "phones", "email", "work_hours", "latitude", "longitude", "map_url"),
            },
        ),
        ("SEO", {"classes": ("admin-tab",), "fields": ("seo_title", "seo_description")}),
    )
    search_fields = ("address", "email")


@admin.register(Requisites)
class RequisitesAdmin(admin.ModelAdmin):
    search_fields = ("company_name", "inn", "ogrn")


@admin.register(DocumentCategory)
class DocumentCategoryAdmin(ActiveOrderedAdmin):
    fields = ("title", "slug", "is_active", "sort_order")


@admin.register(Document)
class DocumentAdmin(ActiveOrderedAdmin):
    list_display = ("title", "category", "published_at", "is_active", "sort_order")
    list_filter = ("category", "is_active")
    search_fields = ("title", "description")


@admin.register(Review)
class ReviewAdmin(ActiveOrderedAdmin):
    list_display = ("author_name", "rating", "source", "reviewed_at", "is_active", "sort_order")
    list_filter = ("rating", "source", "is_active")
    search_fields = ("author_name", "text", "source")
