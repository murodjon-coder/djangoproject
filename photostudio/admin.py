from django.contrib import admin

from .models import Category, Photo


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__', 'category', 'date')
    list_select_related = ('category',)
    search_fields = ('title', 'photographer')
    list_filter = ('category', 'date')
