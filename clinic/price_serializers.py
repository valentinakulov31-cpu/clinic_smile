from rest_framework import serializers

from .models import PriceCategory, PriceGroup, PriceItem


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
