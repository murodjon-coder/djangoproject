from rest_framework import serializers

from .models import Photo, Tag


class PhotoSerializer(serializers.ModelSerializer):
    """12-hafta: Photo obyektini JSON ga (va aksincha) o'giradi."""

    category_name = serializers.CharField(source='category.name', read_only=True, default=None)
    tags = serializers.SlugRelatedField(many=True, slug_field='name', queryset=Tag.objects.all(), required=False)

    class Meta:
        model = Photo
        fields = ['id', 'title', 'photographer', 'date', 'category', 'category_name', 'tags', 'image']
