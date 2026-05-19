from django.conf import settings
from rest_framework import serializers

from .models import LeadRequest, RequestType


class LeadRequestSerializer(serializers.ModelSerializer):
    website = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = LeadRequest
        fields = (
            "id",
            "request_type",
            "name",
            "phone",
            "email",
            "comment",
            "service",
            "specialist",
            "branch",
            "vacancy",
            "attachment",
            "source",
            "website",
            "created_at",
        )
        read_only_fields = ("id", "request_type", "created_at")

    def validate_website(self, value):
        if value:
            raise serializers.ValidationError("Заявка отклонена.")
        return value

    def validate_attachment(self, value):
        if value and value.size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            raise serializers.ValidationError(f"Файл не должен превышать {settings.MAX_UPLOAD_SIZE_MB} МБ.")
        return value

    def validate(self, attrs):
        request_type = self.context["request_type"]
        if request_type == RequestType.VACANCY and not attrs.get("vacancy"):
            raise serializers.ValidationError({"vacancy": "Для отклика нужно выбрать вакансию."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("website", None)
        validated_data["request_type"] = self.context["request_type"]
        return super().create(validated_data)
