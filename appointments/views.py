from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.response import Response

from .models import LeadRequest, RequestType
from .serializers import LeadRequestSerializer


class LeadRequestCreateView(generics.CreateAPIView):
    queryset = LeadRequest.objects.all()
    serializer_class = LeadRequestSerializer
    request_type = None

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request_type"] = self.request_type
        return context

    def create(self, request, *args, **kwargs):
        rate_limit_key = self.get_rate_limit_key()
        if cache.get(rate_limit_key):
            return Response(
                {"detail": "Слишком много заявок. Попробуйте позже."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        response = super().create(request, *args, **kwargs)
        cache.set(rate_limit_key, True, timeout=60)
        return response

    def perform_create(self, serializer):
        lead = serializer.save()
        self.send_notification(lead)

    def get_rate_limit_key(self):
        forwarded = self.request.META.get("HTTP_X_FORWARDED_FOR", "")
        ip = forwarded.split(",")[0].strip() or self.request.META.get("REMOTE_ADDR", "unknown")
        return f"lead-request:{self.request_type}:{ip}"

    def send_notification(self, lead):
        recipient = settings.REQUEST_NOTIFICATION_EMAIL
        if not recipient:
            return

        subject = f"Новая заявка: {lead.get_request_type_display()}"
        lines = [
            f"Тип заявки: {lead.get_request_type_display()}",
            f"Имя: {lead.name}",
            f"Телефон: {lead.phone}",
            f"Email: {lead.email or '-'}",
            f"Комментарий: {lead.comment or '-'}",
            f"Услуга: {lead.service or '-'}",
            f"Специалист: {lead.specialist or '-'}",
            f"Филиал: {lead.branch or '-'}",
            f"Вакансия: {lead.vacancy or '-'}",
            f"Источник: {lead.source or '-'}",
            f"Файл: {lead.attachment.url if lead.attachment else '-'}",
        ]
        send_mail(subject, "\n".join(lines), settings.DEFAULT_FROM_EMAIL, [recipient], fail_silently=True)


@extend_schema(tags=["requests"], summary="Создать заявку на бесплатную консультацию")
class ConsultationRequestCreateView(LeadRequestCreateView):
    request_type = RequestType.CONSULTATION


@extend_schema(tags=["requests"], summary="Создать заявку на запись на прием")
class AppointmentRequestCreateView(LeadRequestCreateView):
    request_type = RequestType.APPOINTMENT


@extend_schema(tags=["requests"], summary="Создать заявку на обратный звонок")
class CallbackRequestCreateView(LeadRequestCreateView):
    request_type = RequestType.CALLBACK


@extend_schema(tags=["requests"], summary="Создать отклик на вакансию")
class VacancyRequestCreateView(LeadRequestCreateView):
    request_type = RequestType.VACANCY
