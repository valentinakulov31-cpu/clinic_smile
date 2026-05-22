from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.response import Response

from .api_utils import ActiveQuerysetMixin
from .models import AboutPage, Branch, ContactInfo, GalleryImage, PatientsPage
from .page_serializers import AboutPageSerializer, ContactInfoSerializer, GalleryImageSerializer, PatientsPageSerializer
from .serializers_common import BranchSerializer


@extend_schema(tags=["content"], summary="Список филиалов")
class BranchListView(ActiveQuerysetMixin, generics.ListAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer


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


@extend_schema(tags=["content"], summary="Контакты и реквизиты")
class ContactInfoView(generics.GenericAPIView):
    serializer_class = ContactInfoSerializer

    def get(self, request):
        contacts = ContactInfo.objects.first()
        if not contacts:
            return Response(None)
        return Response(self.get_serializer(contacts).data)
