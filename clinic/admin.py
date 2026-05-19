from django.contrib import admin

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


class ActiveOrderedAdmin(admin.ModelAdmin):
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
class ServiceCategoryAdmin(ActiveOrderedAdmin):
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Service)
class ServiceAdmin(ActiveOrderedAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name", "category", "is_active", "sort_order")
    list_filter = ("category", "is_active")
    search_fields = ("name", "short_description", "description")
    filter_horizontal = ("branches",)
    inlines = (ServiceImageInline,)


@admin.register(PriceCategory)
class PriceCategoryAdmin(ActiveOrderedAdmin):
    prepopulated_fields = {"slug": ("name",)}


@admin.register(PriceItem)
class PriceItemAdmin(ActiveOrderedAdmin):
    list_display = ("title", "category", "price", "is_from_price", "is_active", "sort_order")
    list_filter = ("category", "is_active", "is_from_price")
    search_fields = ("title", "comment")


@admin.register(Offer)
class OfferAdmin(ActiveOrderedAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "price", "ends_at", "is_active", "sort_order")
    list_filter = ("is_active", "starts_at", "ends_at")
    search_fields = ("title", "short_description", "description")
    filter_horizontal = ("branches",)


@admin.register(Specialist)
class SpecialistAdmin(ActiveOrderedAdmin):
    prepopulated_fields = {"slug": ("full_name",)}
    list_display = ("full_name", "position", "is_active", "sort_order")
    search_fields = ("full_name", "position", "specializations")
    filter_horizontal = ("services", "branches")
    inlines = (SpecialistDocumentInline,)


@admin.register(PaymentMethod)
class PaymentMethodAdmin(ActiveOrderedAdmin):
    search_fields = ("title",)


@admin.register(PatientsPage)
class PatientsPageAdmin(admin.ModelAdmin):
    filter_horizontal = ("offers",)


class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 1


@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    inlines = (GalleryImageInline,)


@admin.register(GalleryImage)
class GalleryImageAdmin(ActiveOrderedAdmin):
    search_fields = ("caption",)


@admin.register(Vacancy)
class VacancyAdmin(ActiveOrderedAdmin):
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "short_description", "description")


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    search_fields = ("address", "email")


@admin.register(Requisites)
class RequisitesAdmin(admin.ModelAdmin):
    search_fields = ("company_name", "inn", "ogrn")


@admin.register(DocumentCategory)
class DocumentCategoryAdmin(ActiveOrderedAdmin):
    prepopulated_fields = {"slug": ("title",)}


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
