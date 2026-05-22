from rest_framework import serializers

from .models import Document, DocumentCategory


class DocumentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentCategory
        fields = ("id", "title", "slug", "sort_order")


class DocumentSerializer(serializers.ModelSerializer):
    category = DocumentCategorySerializer(read_only=True)

    class Meta:
        model = Document
        fields = ("id", "category", "title", "description", "file", "published_at", "sort_order")
