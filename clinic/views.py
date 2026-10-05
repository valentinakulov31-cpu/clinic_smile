from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.response import Response

from .models import (
    AboutPage,
    Advantage,
    Branch,
    ContactInfo,
    Document,
    DocumentCategory,
    GalleryImage,
    HomePage,
    Offer,
    PatientsPage,
    PriceCategory,
    PriceItem,
    Review,
    Service,
    ServiceCategory,
    ServiceImage,
    ServicePageBlock,
    ServicePageBlockCard,
    SiteSettings,
    SocialLink,
    Specialist,
    SpecialistCategory,
    StaticPage,
    Vacancy,
)
from .serializers import (
    AboutPageSerializer,
    AdvantageSerializer,
    BranchSerializer,
    ContactInfoSerializer,
    DocumentCategoryWithDocumentsSerializer,
    DocumentSerializer,
    GalleryImageSerializer,
    HomePageSerializer,
    OfferSerializer,
    PatientsPageSerializer,
    PriceCategorySerializer,
    ReviewSerializer,
    ServiceCategorySerializer,
    ServiceDetailSerializer,
    ServiceListSerializer,
    SiteSettingsSerializer,
    SocialLinkSerializer,
    SpecialistCategoryWithSpecialistsSerializer,
    SpecialistDetailSerializer,
    SpecialistListSerializer,
    StaticPageSerializer,
    VacancyDetailSerializer,
    VacancyListSerializer,
)


class ActiveFilteredQuerysetMixin:
    branch_query_param = "branch"
    category_query_param = "category"

    def get_base_queryset(self):
        return super().get_queryset()

    def get_queryset(self):
        queryset = self.get_base_queryset().filter(is_active=True)
        branch = self.request.query_params.get(self.branch_query_param)
        category = self.request.query_params.get(self.category_query_param)

        if branch and hasattr(queryset.model, "branches"):
            queryset = queryset.filter(branches__id=branch)
        if category and hasattr(queryset.model, "category_id"):
            queryset = queryset.filter(category__slug=category)

        return queryset.distinct()


class ActiveListAPIView(ActiveFilteredQuerysetMixin, generics.ListAPIView):
    # Контентные справочники небольшие, фронту удобнее получать их без пагинации.
    pagination_class = None


class ActiveSlugDetailAPIView(generics.RetrieveAPIView):
    lookup_field = "slug"

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class SingletonPageAPIView(generics.GenericAPIView):
    queryset = None

    def get_object(self):
        return self.get_queryset().first()

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        if not obj:
            return Response(None)
        return Response(self.get_serializer(obj).data)


@extend_schema(tags=["content"], summary="Список филиалов")
class BranchListView(ActiveListAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer


@extend_schema(tags=["content"], summary="Список категорий услуг")
class ServiceCategoryListView(ActiveListAPIView):
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer


@extend_schema(tags=["content"], summary="Список услуг")
class ServiceListView(ActiveListAPIView):
    queryset = Service.objects.select_related("category").prefetch_related("branches")
    serializer_class = ServiceListSerializer


@extend_schema(tags=["content"], summary="Детальная услуга")
class ServiceDetailView(ActiveSlugDetailAPIView):
    queryset = Service.objects.select_related("category").prefetch_related(
        "branches",
        Prefetch("images", queryset=ServiceImage.objects.filter(is_active=True)),
        Prefetch(
            "page_blocks",
            queryset=ServicePageBlock.objects.filter(is_active=True).prefetch_related(
                Prefetch("cards", queryset=ServicePageBlockCard.objects.filter(is_active=True))
            ),
        ),
    )
    serializer_class = ServiceDetailSerializer


@extend_schema(tags=["content"], summary="Прайс, сгруппированный по категориям")
class PriceCategoryListView(generics.ListAPIView):
    serializer_class = PriceCategorySerializer
    pagination_class = None

    def get_queryset(self):
        branch = self.request.query_params.get("branch")
        items = PriceItem.objects.filter(is_active=True)
        if branch:
            items = items.filter(branch_id=branch)
        return (
            PriceCategory.objects.filter(is_active=True, items__in=items)
            .prefetch_related(Prefetch("items", queryset=items))
            .distinct()
        )


@extend_schema(tags=["content"], summary="Список специальных предложений")
class OfferListView(ActiveListAPIView):
    queryset = Offer.objects.prefetch_related("branches")
    serializer_class = OfferSerializer


@extend_schema(tags=["content"], summary="Список специалистов")
class SpecialistListView(ActiveListAPIView):
    queryset = Specialist.objects.prefetch_related("services", "branches")
    serializer_class = SpecialistListSerializer


@extend_schema(tags=["content"], summary="Специалисты, сгруппированные по категориям (Врачи, Младший персонал, Администрация)")
class SpecialistCategoryListView(generics.ListAPIView):
    serializer_class = SpecialistCategoryWithSpecialistsSerializer
    pagination_class = None

    def get_queryset(self):
        specialists = Specialist.objects.filter(is_active=True)
        return (
            SpecialistCategory.objects.filter(is_active=True, specialists__in=specialists)
            .prefetch_related(Prefetch("specialists", queryset=specialists))
            .distinct()
        )


@extend_schema(tags=["content"], summary="Детальный специалист")
class SpecialistDetailView(ActiveSlugDetailAPIView):
    queryset = Specialist.objects.prefetch_related("services", "branches", "documents")
    serializer_class = SpecialistDetailSerializer


@extend_schema(tags=["content"], summary="Страница пациентам")
class PatientsPageView(SingletonPageAPIView):
    queryset = PatientsPage.objects.prefetch_related("offers")
    serializer_class = PatientsPageSerializer


@extend_schema(tags=["content"], summary="Страница о клинике")
class AboutPageView(SingletonPageAPIView):
    queryset = AboutPage.objects.prefetch_related("gallery")
    serializer_class = AboutPageSerializer


@extend_schema(tags=["content"], summary="Галерея")
class GalleryListView(ActiveListAPIView):
    queryset = GalleryImage.objects.all()
    serializer_class = GalleryImageSerializer


@extend_schema(tags=["content"], summary="Список вакансий")
class VacancyListView(ActiveListAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacancyListSerializer


@extend_schema(tags=["content"], summary="Детальная вакансия")
class VacancyDetailView(ActiveSlugDetailAPIView):
    queryset = Vacancy.objects.all()
    serializer_class = VacancyDetailSerializer


@extend_schema(tags=["content"], summary="Контакты и реквизиты")
class ContactInfoView(SingletonPageAPIView):
    queryset = ContactInfo.objects.all()
    serializer_class = ContactInfoSerializer


@extend_schema(tags=["content"], summary="Список документов")
class DocumentListView(ActiveListAPIView):
    queryset = Document.objects.select_related("category")
    serializer_class = DocumentSerializer


@extend_schema(tags=["content"], summary="Документы, сгруппированные по категориям")
class DocumentCategoryListView(generics.ListAPIView):
    serializer_class = DocumentCategoryWithDocumentsSerializer
    pagination_class = None

    def get_queryset(self):
        documents = Document.objects.filter(is_active=True)
        return (
            DocumentCategory.objects.filter(is_active=True, documents__in=documents)
            .prefetch_related(Prefetch("documents", queryset=documents))
            .distinct()
        )


@extend_schema(tags=["content"], summary="Список отзывов")
class ReviewListView(ActiveListAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


@extend_schema(tags=["content"], summary="Главная страница")
class HomePageView(SingletonPageAPIView):
    queryset = HomePage.objects.all()
    serializer_class = HomePageSerializer


@extend_schema(tags=["content"], summary="Список преимуществ")
class AdvantageListView(ActiveListAPIView):
    queryset = Advantage.objects.all()
    serializer_class = AdvantageSerializer


@extend_schema(tags=["content"], summary="Список соцсетей")
class SocialLinkListView(ActiveListAPIView):
    queryset = SocialLink.objects.all()
    serializer_class = SocialLinkSerializer


@extend_schema(tags=["content"], summary="Настройки сайта (шапка, футер, CTA)")
class SiteSettingsView(SingletonPageAPIView):
    queryset = SiteSettings.objects.all()
    serializer_class = SiteSettingsSerializer


@extend_schema(tags=["content"], summary="Статичные страницы (заголовки, SEO, тексты)")
class StaticPageListView(generics.ListAPIView):
    queryset = StaticPage.objects.all()
    serializer_class = StaticPageSerializer
    pagination_class = None


@extend_schema(tags=["content"], summary="Статичная страница по ключу")
class StaticPageDetailView(generics.RetrieveAPIView):
    queryset = StaticPage.objects.all()
    serializer_class = StaticPageSerializer
    lookup_field = "key"
