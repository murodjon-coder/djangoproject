from django.urls import path

from . import views

app_name = 'photostudio'

urlpatterns = [
    path('photos/', views.photo_list, name='photo_list'),
    path('photos/cbv/', views.PhotoListView.as_view(), name='photo_list_cbv'),
    path('photos/add/', views.photo_create, name='photo_create'),
    path('photos/<int:id>/', views.photo_detail, name='photo_detail'),
    path('accounts/register/', views.register, name='register'),
]
