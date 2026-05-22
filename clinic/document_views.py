from drf_spectacular.utils import extend_schema
from rest_framework import generics

from .api_utils import ActiveQuerysetMixin
from .document_serializers import DocumentSerializer
from .models import Document


@extend_schema(tags=["content"], summary="Список документов")
class DocumentListView(ActiveQuerysetMixin, generics.ListAPIView):
    queryset = Document.objects.select_related("category")
    serializer_class = DocumentSerializer
