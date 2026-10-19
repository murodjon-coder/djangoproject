from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Photo


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'thumbnail', '__str__', 'category', 'date')
    list_display_links = ('id', 'thumbnail', '__str__')
    list_select_related = ('category',)
    search_fields = ('title', 'photographer')
    list_filter = ('category', 'date')

    @admin.display(description="Rasm")
    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:48px;border-radius:6px;">', obj.image.url)
        return "—"
