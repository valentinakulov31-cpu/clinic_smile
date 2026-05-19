from django.urls import path

from . import views


urlpatterns = [
    path("consultation/", views.ConsultationRequestCreateView.as_view(), name="consultation-request"),
    path("appointment/", views.AppointmentRequestCreateView.as_view(), name="appointment-request"),
    path("callback/", views.CallbackRequestCreateView.as_view(), name="callback-request"),
    path("vacancy/", views.VacancyRequestCreateView.as_view(), name="vacancy-request"),
]
