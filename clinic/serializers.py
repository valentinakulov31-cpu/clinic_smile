from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

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
    ServiceCategory,
    ServiceImage,
    ServicePageBlock,
    ServicePageBlockCard,
    SiteSettings,
    SocialLink,
    Specialist,
    SpecialistCategory,
    SpecialistDocument,
    StaticPage,
    Vacancy,
)


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = "__all__"


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = "__all__"


class ServiceImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceImage
        fields = ("id", "image", "caption", "sort_order")


class ServicePageBlockCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicePageBlockCard
        fields = ("id", "title", "subtitle", "description", "price_text", "image", "sort_order")


class ServicePageBlockSerializer(serializers.ModelSerializer):
    cards = ServicePageBlockCardSerializer(many=True, read_only=True)

    class Meta:
        model = ServicePageBlock
        fields = ("id", "block_type", "title", "description", "image", "cards", "sort_order")


class ServiceListSerializer(serializers.ModelSerializer):
    category = ServiceCategorySerializer(read_only=True)

    class Meta:
        model = Service
        fields = (
            "id",
            "name",
            "slug",
            "category",
            "short_description",
            "icon",
            "card_image",
            "sort_order",
            "seo_title",
            "seo_description",
        )


class ServiceDetailSerializer(ServiceListSerializer):
    images = ServiceImageSerializer(many=True, read_only=True)
    page_blocks = ServicePageBlockSerializer(many=True, read_only=True)
    hero_badges = serializers.SerializerMethodField()

    class Meta(ServiceListSerializer.Meta):
        fields = (
            "id",
            "slug",
            "preview_logo",
            "card_image",
            "name",
            "short_description",
            "description",
            "hero_badges",
            "page_blocks",
            "images",
            "branches",
            "seo_title",
            "seo_description",
            "og_title",
            "og_description",
            "og_image",
        )

    @extend_schema_field(serializers.ListField(child=serializers.CharField(allow_blank=True)))
    def get_hero_badges(self, obj):
        return [obj.hero_badge_1, obj.hero_badge_2, obj.hero_badge_3]


class PriceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceItem
        fields = ("id", "title", "price", "is_from_price", "comment", "service", "branch", "sort_order")


class PriceCategorySerializer(serializers.ModelSerializer):
    items = PriceItemSerializer(many=True, read_only=True)

    class Meta:
        model = PriceCategory
        fields = ("id", "name", "slug", "sort_order", "items")


class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = "__all__"


class SpecialistDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialistDocument
        fields = ("id", "title", "file", "sort_order")


class SpecialistCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialistCategory
        fields = ("id", "name", "slug", "sort_order")


class SpecialistListSerializer(serializers.ModelSerializer):
    category = SpecialistCategorySerializer(read_only=True)

    class Meta:
        model = Specialist
        fields = (
            "id",
            "category",
            "full_name",
            "slug",
            "photo",
            "position",
            "specializations",
            "short_description",
            "experience",
            "sort_order",
        )


class SpecialistCategoryWithSpecialistsSerializer(SpecialistCategorySerializer):
    specialists = serializers.SerializerMethodField()

    class Meta(SpecialistCategorySerializer.Meta):
        fields = SpecialistCategorySerializer.Meta.fields + ("specialists",)

    @extend_schema_field(SpecialistListSerializer(many=True))
    def get_specialists(self, obj):
        specialists = [specialist for specialist in obj.specialists.all() if specialist.is_active]
        return SpecialistListSerializer(specialists, many=True, context=self.context).data


class SpecialistDetailSerializer(SpecialistListSerializer):
    documents = SpecialistDocumentSerializer(many=True, read_only=True)

    class Meta(SpecialistListSerializer.Meta):
        fields = SpecialistListSerializer.Meta.fields + (
            "description",
            "education",
            "services",
            "branches",
            "documents",
            "seo_title",
            "seo_description",
            "og_title",
            "og_description",
            "og_image",
        )


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ("id", "title", "icon", "description", "sort_order")


class PatientsPageSerializer(serializers.ModelSerializer):
    payment_methods = serializers.SerializerMethodField()
    offers = OfferSerializer(many=True, read_only=True)

    class Meta:
        model = PatientsPage
        fields = ("id", "title", "text", "image", "offers", "payment_methods", "seo_title", "seo_description")

    @extend_schema_field(PaymentMethodSerializer(many=True))
    def get_payment_methods(self, _obj):
        return PaymentMethodSerializer(PaymentMethod.objects.filter(is_active=True), many=True, context=self.context).data


class GalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryImage
        fields = ("id", "image", "caption", "sort_order")


class AboutPageSerializer(serializers.ModelSerializer):
    gallery = GalleryImageSerializer(many=True, read_only=True)

    class Meta:
        model = AboutPage
        fields = ("id", "title", "text", "image", "gallery", "seo_title", "seo_description")


class VacancyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacancy
        fields = ("id", "title", "slug", "short_description", "image", "sort_order")


class VacancyDetailSerializer(VacancyListSerializer):
    class Meta(VacancyListSerializer.Meta):
        fields = VacancyListSerializer.Meta.fields + (
            "responsibilities",
            "requirements",
            "conditions",
            "description",
            "seo_title",
            "seo_description",
        )


class RequisitesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requisites
        fields = "__all__"


class ContactInfoSerializer(serializers.ModelSerializer):
    requisites = serializers.SerializerMethodField()

    class Meta:
        model = ContactInfo
        fields = "__all__"

    @extend_schema_field(RequisitesSerializer(allow_null=True))
    def get_requisites(self, _obj):
        requisites = Requisites.objects.first()
        if not requisites:
            return None
        return RequisitesSerializer(requisites, context=self.context).data


class DocumentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentCategory
        fields = ("id", "title", "slug", "sort_order")


class DocumentSerializer(serializers.ModelSerializer):
    category = DocumentCategorySerializer(read_only=True)

    class Meta:
        model = Document
        fields = ("id", "title", "description", "file", "published_at", "category", "sort_order")


class DocumentCategoryWithDocumentsSerializer(DocumentCategorySerializer):
    documents = serializers.SerializerMethodField()

    class Meta(DocumentCategorySerializer.Meta):
        fields = DocumentCategorySerializer.Meta.fields + ("documents",)

    @extend_schema_field(DocumentSerializer(many=True))
    def get_documents(self, obj):
        documents = [document for document in obj.documents.all() if document.is_active]
        return DocumentSerializer(documents, many=True, context=self.context).data


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ("id", "author_name", "text", "rating", "source", "source_url", "reviewed_at", "sort_order")


class AdvantageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advantage
        fields = ("id", "title", "text", "icon", "sort_order")


class SocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialLink
        fields = ("id", "title", "url", "icon", "sort_order")


class HomePageSerializer(serializers.ModelSerializer):
    advantages = serializers.SerializerMethodField()

    class Meta:
        model = HomePage
        fields = (
            "id",
            "hero_title",
            "hero_subtitle",
            "hero_button_text",
            "hero_secondary_button_text",
            "hero_image",
            "about_title",
            "about_text",
            "about_image",
            "advantages",
            "seo_title",
            "seo_description",
        )

    @extend_schema_field(AdvantageSerializer(many=True))
    def get_advantages(self, _obj):
        return AdvantageSerializer(Advantage.objects.filter(is_active=True), many=True, context=self.context).data


class SiteSettingsSerializer(serializers.ModelSerializer):
    social_links = serializers.SerializerMethodField()

    class Meta:
        model = SiteSettings
        fields = (
            "id",
            "site_name",
            "logo",
            "copyright_text",
            "disclaimer",
            "cta_title",
            "cta_subtitle",
            "price_full_url",
            "social_links",
        )

    @extend_schema_field(SocialLinkSerializer(many=True))
    def get_social_links(self, _obj):
        return SocialLinkSerializer(SocialLink.objects.filter(is_active=True), many=True, context=self.context).data


class StaticPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaticPage
        fields = ("id", "key", "title", "subtitle", "text", "seo_title", "seo_description")
