from rest_framework import serializers

from .models import Offer, Review


class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = "__all__"


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
