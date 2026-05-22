from rest_framework import serializers

from .models import Specialist, SpecialistDocument, Vacancy


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
