from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Client, Photo, Session


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


class SessionInline(admin.TabularInline):
    model = Session
    extra = 0
    fields = ('scheduled_at', 'photographer', 'price', 'status')


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'phone', 'email', 'created_at')
    search_fields = ('full_name', 'phone', 'email')
    inlines = [SessionInline]


class PhotoInline(admin.TabularInline):
    model = Photo
    extra = 0
    fields = ('title', 'photographer', 'date', 'category', 'image')


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'photographer', 'scheduled_at', 'price', 'status')
    list_select_related = ('client',)
    list_filter = ('status', 'scheduled_at')
    search_fields = ('client__full_name', 'photographer', 'location')
    date_hierarchy = 'scheduled_at'
    inlines = [PhotoInline]


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('id', 'thumbnail', '__str__', 'category', 'session', 'date')
    list_display_links = ('id', 'thumbnail', '__str__')
    list_select_related = ('category', 'session__client')
    search_fields = ('title', 'photographer')
    list_filter = ('category', 'date')

    @admin.display(description="Rasm")
    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:48px;border-radius:6px;">', obj.image.url)
        return "—"
