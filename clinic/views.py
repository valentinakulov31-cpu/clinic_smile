from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.response import Response

from .models import (
    AboutPage,
    Branch,
    ContactInfo,
    Document,
    GalleryImage,
    Offer,
    PatientsPage,
    PriceCategory,
    PriceGroup,
    PriceItem,
    Review,
    Service,
    ServiceCategory,
    ServicePageBlock,
    ServicePageBlockItem,
    Specialist,
    Vacancy,
)
from .serializers import (
    AboutPageSerializer,
    BranchSerializer,
    ContactInfoSerializer,
    DocumentSerializer,
    GalleryImageSerializer,
    OfferSerializer,
    PatientsPageSerializer,
    PriceCategorySerializer,
    ReviewSerializer,
    ServiceCategorySerializer,
    ServiceDetailSerializer,
    ServiceListSerializer,
    SpecialistDetailSerializer,
    SpecialistListSerializer,
    VacancyDetailSerializer,
    VacancyListSerializer,
)


class ActiveQuerysetMixin:
    def get_queryset(self):
        queryset = super().get_queryset().filter(is_active=True)
        branch = self.request.query_params.get("branch")
        category = self.request.query_params.get("category")

        if branch and hasattr(queryset.model, "branches"):
            queryset = queryset.filter(branches__id=branch)
        if category and hasattr(queryset.model, "category_id"):
            queryset = queryset.filter(category__slug=category)

        return queryset.distinct()


@extend_schema(tags=["content"], summary="Список филиалов")
class BranchListView(ActiveQuerysetMixin, generics.ListAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer


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


@extend_schema(tags=["content"], summary="Список специальных предложений")
class OfferListView(ActiveQuerysetMixin, generics.ListAPIView):
    queryset = Offer.objects.prefetch_related("branches")
    serializer_class = OfferSerializer


@extend_schema(tags=["content"], summary="Детальное специальное предложение")
class OfferDetailView(generics.RetrieveAPIView):
    queryset = Offer.objects.filter(is_active=True).prefetch_related("branches")
    serializer_class = OfferSerializer
    lookup_field = "slug"


@extend_schema(tags=["content"], summary="Список специалистов")
class SpecialistListView(ActiveQuerysetMixin, generics.ListAPIView):
    queryset = Specialist.objects.prefetch_related("services", "branches")
    serializer_class = SpecialistListSerializer


@extend_schema(tags=["content"], summary="Детальный специалист")
class SpecialistDetailView(generics.RetrieveAPIView):
    queryset = Specialist.objects.filter(is_active=True).prefetch_related("services", "branches", "documents")
    serializer_class = SpecialistDetailSerializer
    lookup_field = "slug"


@extend_schema(tags=["content"], summary="Страница пациентам")
class PatientsPageView(generics.GenericAPIView):
    serializer_class = PatientsPageSerializer

    def get(self, request):
        page = PatientsPage.objects.prefetch_related("offers").first()
        if not page:
            return Response(None)
        return Response(self.get_serializer(page).data)


@extend_schema(tags=["content"], summary="Страница о клинике")
class AboutPageView(generics.GenericAPIView):
    serializer_class = AboutPageSerializer

    def get(self, request):
        page = AboutPage.objects.prefetch_related("gallery").first()
        if not page:
            return Response(None)
        return Response(self.get_serializer(page).data)


@extend_schema(tags=["content"], summary="Галерея")
class GalleryListView(ActiveQuerysetMixin, generics.ListAPIView):
    queryset = GalleryImage.objects.all()
    serializer_class = GalleryImageSerializer


@extend_schema(tags=["content"], summary="Список вакансий")
class VacancyListView(ActiveQuerysetMixin, generics.ListAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacancyListSerializer


@extend_schema(tags=["content"], summary="Детальная вакансия")
class VacancyDetailView(generics.RetrieveAPIView):
    queryset = Vacancy.objects.filter(is_active=True)
    serializer_class = VacancyDetailSerializer
    lookup_field = "slug"


@extend_schema(tags=["content"], summary="Контакты и реквизиты")
class ContactInfoView(generics.GenericAPIView):
    serializer_class = ContactInfoSerializer

    def get(self, request):
        contacts = ContactInfo.objects.first()
        if not contacts:
            return Response(None)
        return Response(self.get_serializer(contacts).data)


@extend_schema(tags=["content"], summary="Список документов")
class DocumentListView(ActiveQuerysetMixin, generics.ListAPIView):
    queryset = Document.objects.select_related("category")
    serializer_class = DocumentSerializer


@extend_schema(tags=["content"], summary="Список отзывов")
class ReviewListView(ActiveQuerysetMixin, generics.ListAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
