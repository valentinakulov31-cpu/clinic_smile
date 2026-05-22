from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .marketing_serializers import OfferSerializer
from .models import AboutPage, ContactInfo, GalleryImage, PatientsPage, PaymentMethod, Requisites


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
