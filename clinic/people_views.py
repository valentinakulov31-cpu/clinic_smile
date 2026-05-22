from drf_spectacular.utils import extend_schema
from rest_framework import generics

from .api_utils import ActiveQuerysetMixin
from .models import Specialist, Vacancy
from .people_serializers import (
    SpecialistDetailSerializer,
    SpecialistListSerializer,
    VacancyDetailSerializer,
    VacancyListSerializer,
)


@extend_schema(tags=["content"], summary="Список специалистов")
class SpecialistListView(ActiveQuerysetMixin, generics.ListAPIView):
    queryset = Specialist.objects.prefetch_related("services", "branches")
    serializer_class = SpecialistListSerializer


@extend_schema(tags=["content"], summary="Детальный специалист")
class SpecialistDetailView(generics.RetrieveAPIView):
    queryset = Specialist.objects.filter(is_active=True).prefetch_related("services", "branches", "documents")
    serializer_class = SpecialistDetailSerializer
    lookup_field = "slug"


@extend_schema(tags=["content"], summary="Список вакансий")
class VacancyListView(ActiveQuerysetMixin, generics.ListAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacancyListSerializer


@extend_schema(tags=["content"], summary="Детальная вакансия")
class VacancyDetailView(generics.RetrieveAPIView):
    queryset = Vacancy.objects.filter(is_active=True)
    serializer_class = VacancyDetailSerializer
    lookup_field = "slug"
