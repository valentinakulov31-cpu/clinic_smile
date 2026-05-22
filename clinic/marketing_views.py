from drf_spectacular.utils import extend_schema
from rest_framework import generics

from .api_utils import ActiveQuerysetMixin
from .marketing_serializers import OfferSerializer, ReviewSerializer
from .models import Offer, Review


@extend_schema(tags=["content"], summary="Список специальных предложений")
class OfferListView(ActiveQuerysetMixin, generics.ListAPIView):
    queryset = Offer.objects.prefetch_related("branches")
    serializer_class = OfferSerializer


@extend_schema(tags=["content"], summary="Детальное специальное предложение")
class OfferDetailView(generics.RetrieveAPIView):
    queryset = Offer.objects.filter(is_active=True).prefetch_related("branches")
    serializer_class = OfferSerializer
    lookup_field = "slug"


@extend_schema(tags=["content"], summary="Список отзывов")
class ReviewListView(ActiveQuerysetMixin, generics.ListAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
