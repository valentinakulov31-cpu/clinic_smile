from django.contrib import admin

from .forms import BranchAdminForm, ContactInfoAdminForm
from .models import (
    AboutPage,
    Advantage,
    Branch,
    ContactInfo,
    Document,
    DocumentCategory,
    GalleryImage,
    HomePage,
    Offer,
    PatientsPage,
    PaymentMethod,
    PriceCategory,
    PriceItem,
    Requisites,
    Review,
    Service,
    ServicePageBlock,
    ServicePageBlockCard,
    ServiceCategory,
    ServiceImage,
    SiteSettings,
    SocialLink,
    Specialist,
    SpecialistCategory,
    SpecialistDocument,
    StaticPage,
    Vacancy,
)


class TabbedAdminMixin:
    class Media:
        css = {"all": ("admin/css/admin-tabs.css", "admin/css/service-page-blocks-v2.css")}
        js = ("admin/js/admin-tabs.js", "admin/js/service-page-blocks-v2.js")


class SingletonAdminMixin:
    """Для записей, которые должны существовать в одном экземпляре."""

    def has_add_permission(self, request):
        return not self.model.objects.exists()


class ActiveOrderedAdmin(admin.ModelAdmin):
    list_display = ("__str__", "is_active", "sort_order", "updated_at")
    list_editable = ("is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("name", "title")


class ServiceImageInline(admin.TabularInline):
    model = ServiceImage
    extra = 1


class ServicePageBlockInline(admin.StackedInline):
    model = ServicePageBlock
    can_delete = True
    extra = 1
    fields = ("block_type", "title", "description", "image", "is_active", "sort_order")
    show_change_link = True


class ServicePageBlockCardInline(admin.StackedInline):
    model = ServicePageBlockCard
    can_delete = True
    extra = 1
    fields = ("title", "subtitle", "description", "price_text", "image", "is_active", "sort_order")


class SpecialistDocumentInline(admin.TabularInline):
    model = SpecialistDocument
    extra = 1


@admin.register(Branch)
class BranchAdmin(ActiveOrderedAdmin):
    form = BranchAdminForm
    search_fields = ("name", "address", "email")


@admin.register(ServicePageBlock)
class ServicePageBlockAdmin(ActiveOrderedAdmin):
    list_display = ("__str__", "service", "block_type", "is_active", "sort_order")
    list_filter = ("service", "block_type", "is_active")
    search_fields = ("title", "description")
    fields = ("service", "block_type", "title", "description", "image", "is_active", "sort_order")
    inlines = (ServicePageBlockCardInline,)


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(TabbedAdminMixin, ActiveOrderedAdmin):
    fieldsets = (
        ("Основное", {"classes": ("admin-tab",), "fields": ("name", "slug", "description", "icon", "image", "is_active", "sort_order")}),
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
                    "icon",
                    "card_image",
                    "preview_logo",
                    "hero_badge_1",
                    "hero_badge_2",
                    "hero_badge_3",
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
    inlines = (ServiceImageInline, ServicePageBlockInline)


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


@admin.register(SpecialistCategory)
class SpecialistCategoryAdmin(ActiveOrderedAdmin):
    fields = ("name", "slug", "is_active", "sort_order")


@admin.register(Specialist)
class SpecialistAdmin(TabbedAdminMixin, ActiveOrderedAdmin):
    fieldsets = (
        (
            "Основное",
            {
                "classes": ("admin-tab",),
                "fields": (
                    "category",
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
    list_display = ("full_name", "category", "position", "is_active", "sort_order")
    list_filter = ("category", "is_active")
    search_fields = ("full_name", "position", "specializations")
    filter_horizontal = ("services", "branches")
    inlines = (SpecialistDocumentInline,)


@admin.register(PaymentMethod)
class PaymentMethodAdmin(ActiveOrderedAdmin):
    search_fields = ("title",)


@admin.register(PatientsPage)
class PatientsPageAdmin(SingletonAdminMixin, TabbedAdminMixin, admin.ModelAdmin):
    fieldsets = (
        ("Основное", {"classes": ("admin-tab",), "fields": ("title", "text", "image", "offers")}),
        ("SEO", {"classes": ("admin-tab",), "fields": ("seo_title", "seo_description")}),
    )
    filter_horizontal = ("offers",)


class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 1


@admin.register(AboutPage)
class AboutPageAdmin(SingletonAdminMixin, TabbedAdminMixin, admin.ModelAdmin):
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
class ContactInfoAdmin(SingletonAdminMixin, TabbedAdminMixin, admin.ModelAdmin):
    form = ContactInfoAdminForm
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
class RequisitesAdmin(SingletonAdminMixin, admin.ModelAdmin):
    search_fields = ("company_name", "inn", "ogrn")


@admin.register(HomePage)
class HomePageAdmin(SingletonAdminMixin, TabbedAdminMixin, admin.ModelAdmin):
    fieldsets = (
        (
            "Герой",
            {
                "classes": ("admin-tab",),
                "fields": ("hero_title", "hero_subtitle", "hero_button_text", "hero_secondary_button_text", "hero_image"),
            },
        ),
        (
            "О клинике",
            {"classes": ("admin-tab",), "fields": ("about_title", "about_text", "about_image")},
        ),
        ("SEO", {"classes": ("admin-tab",), "fields": ("seo_title", "seo_description")}),
    )


@admin.register(Advantage)
class AdvantageAdmin(ActiveOrderedAdmin):
    search_fields = ("title", "text")


@admin.register(SocialLink)
class SocialLinkAdmin(ActiveOrderedAdmin):
    search_fields = ("title", "url")


@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonAdminMixin, admin.ModelAdmin):
    fields = (
        "site_name",
        "logo",
        "copyright_text",
        "disclaimer",
        "cta_title",
        "cta_subtitle",
        "price_full_url",
    )


@admin.register(StaticPage)
class StaticPageAdmin(TabbedAdminMixin, admin.ModelAdmin):
    list_display = ("__str__", "key")
    fieldsets = (
        ("Основное", {"classes": ("admin-tab",), "fields": ("key", "title", "subtitle", "text")}),
        ("SEO", {"classes": ("admin-tab",), "fields": ("seo_title", "seo_description")}),
    )


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
