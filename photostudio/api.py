from rest_framework import viewsets

from .models import Photo
from .serializers import PhotoSerializer


class PhotoViewSet(viewsets.ModelViewSet):
    """12-hafta: Photo uchun to'liq CRUD API (list, retrieve, create, update, delete)."""

    queryset = Photo.objects.select_related('category')
    serializer_class = PhotoSerializer
