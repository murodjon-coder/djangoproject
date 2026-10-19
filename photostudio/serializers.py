from rest_framework import serializers

from .models import Photo


class PhotoSerializer(serializers.ModelSerializer):
    """12-hafta: Photo obyektini JSON ga (va aksincha) o'giradi."""

    category_name = serializers.CharField(source='category.name', read_only=True, default=None)

    class Meta:
        model = Photo
        fields = ['id', 'title', 'photographer', 'date', 'category', 'category_name', 'image']
