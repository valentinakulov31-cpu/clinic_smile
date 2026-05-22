from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema
from rest_framework import generics

from .api_utils import ActiveQuerysetMixin
from .models import Service, ServiceCategory, ServicePageBlock, ServicePageBlockItem
from .service_serializers import ServiceCategorySerializer, ServiceDetailSerializer, ServiceListSerializer


@extend_schema(tags=["content"], summary="Список категорий услуг")
class ServiceCategoryListView(ActiveQuerysetMixin, generics.ListAPIView):
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer


@extend_schema(tags=["content"], summary="Список услуг")
class ServiceListView(ActiveQuerysetMixin, generics.ListAPIView):
    queryset = Service.objects.select_related("category").prefetch_related("branches")
    serializer_class = ServiceListSerializer


@extend_schema(tags=["content"], summary="Детальная услуга")
class ServiceDetailView(generics.RetrieveAPIView):
    queryset = (
        Service.objects.filter(is_active=True)
        .select_related("category")
        .prefetch_related(
            "branches",
            "images",
            Prefetch(
                "blocks",
                queryset=ServicePageBlock.objects.filter(is_active=True).prefetch_related(
                    Prefetch("items", queryset=ServicePageBlockItem.objects.filter(is_active=True))
                ),
            ),
        )
    )
    serializer_class = ServiceDetailSerializer
    lookup_field = "slug"
