from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

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
    PriceGroup,
    PriceItem,
    Requisites,
    Review,
    Service,
    ServiceCategory,
    ServiceImage,
    ServicePageBlock,
    ServicePageBlockItem,
    Specialist,
    SpecialistDocument,
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


class ServicePageBlockItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServicePageBlockItem
        fields = (
            "id",
            "title",
            "subtitle",
            "description",
            "image",
            "price",
            "label",
            "url",
            "metadata",
            "sort_order",
        )


class ServicePageBlockSerializer(serializers.ModelSerializer):
    items = ServicePageBlockItemSerializer(many=True, read_only=True)

    class Meta:
        model = ServicePageBlock
        fields = (
            "id",
            "block_type",
            "title",
            "subtitle",
            "body",
            "image",
            "button_label",
            "button_url",
            "items",
            "sort_order",
        )


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
            "card_image",
            "sort_order",
            "seo_title",
            "seo_description",
        )


class ServiceDetailSerializer(ServiceListSerializer):
    images = ServiceImageSerializer(many=True, read_only=True)
    blocks = ServicePageBlockSerializer(many=True, read_only=True)

    class Meta(ServiceListSerializer.Meta):
        fields = ServiceListSerializer.Meta.fields + (
            "description",
            "images",
            "blocks",
            "branches",
            "og_title",
            "og_description",
            "og_image",
        )


class PriceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceItem
        fields = ("id", "title", "price", "is_from_price", "comment", "service", "branch", "sort_order")


class PriceGroupSerializer(serializers.ModelSerializer):
    items = PriceItemSerializer(many=True, read_only=True)

    class Meta:
        model = PriceGroup
        fields = ("id", "title", "sort_order", "items")


class PriceCategorySerializer(serializers.ModelSerializer):
    items = PriceItemSerializer(many=True, read_only=True)
    groups = PriceGroupSerializer(many=True, read_only=True)

    class Meta:
        model = PriceCategory
        fields = ("id", "name", "slug", "sort_order", "groups", "items")


class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = "__all__"


class SpecialistDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialistDocument
        fields = ("id", "title", "file", "sort_order")


class SpecialistListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialist
        fields = (
            "id",
            "full_name",
            "slug",
            "photo",
            "position",
            "specializations",
            "short_description",
            "experience",
            "sort_order",
        )


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
        fields = ("id", "category", "title", "description", "file", "published_at", "sort_order")


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = (
            "id",
            "author_name",
            "text",
            "rating",
            "source",
            "source_url",
            "reviewed_at",
            "specialist",
            "service",
            "sort_order",
        )
