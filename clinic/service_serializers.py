from rest_framework import serializers

from .models import Service, ServiceCategory, ServiceImage, ServicePageBlock, ServicePageBlockItem


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
