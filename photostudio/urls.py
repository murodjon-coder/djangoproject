from django.urls import path

from . import views

app_name = 'photostudio'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('after-login/', views.after_login, name='after_login'),
    path('cabinet/', views.cabinet, name='cabinet'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Suratlar (4–6, 11, 14-haftalar)
    path('photos/', views.photo_list, name='photo_list'),
    path('photos/cbv/', views.PhotoListView.as_view(), name='photo_list_cbv'),
    path('photos/add/', views.photo_create, name='photo_create'),
    path('photos/<int:id>/', views.photo_detail, name='photo_detail'),
    path('photos/<int:id>/edit/', views.photo_update, name='photo_update'),
    path('photos/<int:id>/delete/', views.photo_delete, name='photo_delete'),

    # Mijozlar (14-hafta)
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/add/', views.ClientCreateView.as_view(), name='client_create'),
    path('clients/<int:pk>/', views.ClientDetailView.as_view(), name='client_detail'),
    path('clients/<int:pk>/edit/', views.ClientUpdateView.as_view(), name='client_update'),
    path('clients/<int:pk>/delete/', views.ClientDeleteView.as_view(), name='client_delete'),
    path('clients/<int:pk>/account/', views.client_account_create, name='client_account_create'),

    # Fotosessiyalar (14-hafta)
    path('sessions/', views.SessionListView.as_view(), name='session_list'),
    path('sessions/add/', views.SessionCreateView.as_view(), name='session_create'),
    path('sessions/<int:pk>/', views.SessionDetailView.as_view(), name='session_detail'),
    path('sessions/<int:pk>/edit/', views.SessionUpdateView.as_view(), name='session_update'),
    path('sessions/<int:pk>/delete/', views.SessionDeleteView.as_view(), name='session_delete'),

    # Onlayn bron
    path('book/', views.booking_create, name='booking_create'),
    path('bookings/', views.BookingListView.as_view(), name='booking_list'),
    path('bookings/<int:pk>/', views.booking_detail, name='booking_detail'),

    # 8-hafta: ro'yxatdan o'tish
    path('accounts/register/', views.register, name='register'),
]
