from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path, re_path
from django.views.static import serve
from rest_framework.routers import DefaultRouter

from photostudio.api import PhotoViewSet

# 12-hafta: router /api/photostudio/ va /api/photostudio/<id>/ manzillarini avtomatik yaratadi
router = DefaultRouter()
router.register('photostudio', PhotoViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    # 8-hafta: Django'ning tayyor LoginView/LogoutView klasslari
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('', include('photostudio.urls')),
]

# 11-hafta: DEBUG rejimida yuklangan fayllarni (MEDIA) Django'ning o'zi beradi
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
elif settings.SERVE_MEDIA:
    # Kichik serverlar uchun (masalan, Render): media fayllarni DEBUG=False da ham Django beradi
    urlpatterns += [re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT})]
