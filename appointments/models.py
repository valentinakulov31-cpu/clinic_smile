from django.core.exceptions import ValidationError
from django.db import models

from clinic.models import Branch, Service, Specialist, Vacancy, validate_document


class RequestStatus(models.TextChoices):
    NEW = "new", "Новая"
    IN_PROGRESS = "in_progress", "В работе"
    DONE = "done", "Обработана"
    CANCELED = "canceled", "Отменена"


class RequestType(models.TextChoices):
    CONSULTATION = "consultation", "Бесплатная консультация"
    APPOINTMENT = "appointment", "Запись на прием"
    CALLBACK = "callback", "Обратный звонок"
    VACANCY = "vacancy", "Отклик на вакансию"


class LeadRequest(models.Model):
    request_type = models.CharField("Тип заявки", max_length=32, choices=RequestType.choices)
    name = models.CharField("Имя", max_length=255)
    phone = models.CharField("Телефон", max_length=64)
    email = models.EmailField("Email", blank=True)
    comment = models.TextField("Комментарий", blank=True)
    service = models.ForeignKey(Service, verbose_name="Услуга", on_delete=models.SET_NULL, blank=True, null=True)
    specialist = models.ForeignKey(Specialist, verbose_name="Специалист", on_delete=models.SET_NULL, blank=True, null=True)
    branch = models.ForeignKey(Branch, verbose_name="Филиал", on_delete=models.SET_NULL, blank=True, null=True)
    vacancy = models.ForeignKey(Vacancy, verbose_name="Вакансия", on_delete=models.SET_NULL, blank=True, null=True)
    attachment = models.FileField("Файл", upload_to="requests/", blank=True, null=True, validators=[validate_document])
    source = models.CharField("Источник формы", max_length=255, blank=True)
    status = models.CharField("Статус", max_length=32, choices=RequestStatus.choices, default=RequestStatus.NEW)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ("-created_at",)

    def clean(self):
        if self.request_type == RequestType.VACANCY and not self.vacancy_id:
            raise ValidationError("Для отклика нужно выбрать вакансию.")

    def __str__(self):
        return f"{self.get_request_type_display()} от {self.name}"
