from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema
from rest_framework import generics

from .api_utils import ActiveQuerysetMixin
from .models import PriceCategory, PriceGroup, PriceItem
from .price_serializers import PriceCategorySerializer


@extend_schema(tags=["content"], summary="Прайс, сгруппированный по категориям")
class PriceCategoryListView(ActiveQuerysetMixin, generics.ListAPIView):
    serializer_class = PriceCategorySerializer

    def get_queryset(self):
        branch = self.request.query_params.get("branch")
        items = PriceItem.objects.filter(is_active=True)
        if branch:
            items = items.filter(branch_id=branch)
        groups = PriceGroup.objects.filter(is_active=True, items__in=items).prefetch_related(
            Prefetch("items", queryset=items)
        )
        return (
            PriceCategory.objects.filter(is_active=True, items__in=items)
            .prefetch_related(
                Prefetch("groups", queryset=groups),
                Prefetch("items", queryset=items.filter(group__isnull=True)),
            )
            .distinct()
        )
