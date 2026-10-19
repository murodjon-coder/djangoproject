"""Onlayn bron: so'rov yuborish, xodim tasdiqlashi/rad etishi, mijoz kabineti bilan bog'lanish."""
import datetime

import pytest
from django.test import Client as BrowserClient
from django.urls import reverse
from django.utils import timezone

from photostudio.models import BookingRequest, Client, Session


def future(days=3, hour=15):
    when = timezone.localtime() + datetime.timedelta(days=days)
    return when.replace(hour=hour, minute=0, second=0, microsecond=0)


def booking_data(**overrides):
    data = {
        'full_name': 'Kamola Saidova',
        'phone': '+998 94 111 22 33',
        'email': 'kamola@example.com',
        'preferred_at': future().strftime('%Y-%m-%dT%H:%M'),
        'message': 'Oq fon, 1 soat',
    }
    data.update(overrides)
    return data


def approve_data(**overrides):
    data = {
        'approve': '1',
        'photographer': 'Murodjon',
        'scheduled_at': future().strftime('%Y-%m-%dT%H:%M'),
        'duration_minutes': 60,
        'location': 'Asosiy studiya',
        'price': 700000,
        'answer': 'Kutamiz!',
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
def test_mehmon_bron_sorovi_yuboradi(client):
    response = client.post(reverse('photostudio:booking_create'), booking_data())
    booking = BookingRequest.objects.get()
    assert response.status_code == 302
    assert booking.status == BookingRequest.Status.NEW
    assert booking.user is None


@pytest.mark.django_db
def test_otgan_vaqtga_bron_qilib_bolmaydi(client):
    yesterday = (timezone.localtime() - datetime.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')
    response = client.post(reverse('photostudio:booking_create'), booking_data(preferred_at=yesterday, phone='12ab'))
    errors = response.context['form'].errors
    assert 'preferred_at' in errors
    assert 'phone' in errors
    assert BookingRequest.objects.count() == 0


@pytest.mark.django_db
def test_mijoz_formasi_profildan_toldiriladi(customer_client, studio_client):
    response = customer_client.get(reverse('photostudio:booking_create'))
    assert response.context['form'].initial['phone'] == studio_client.phone


def browser_for(user):
    """Har bir foydalanuvchi uchun alohida brauzer (alohida session)."""
    browser = BrowserClient()
    if user is not None:
        browser.force_login(user)
    return browser


@pytest.mark.django_db
def test_tasdiqlash_yangi_mijoz_va_sessiya_yaratadi(logged_client, django_user_model):
    account = django_user_model.objects.create_user('kamola', password='Parol-12345')
    client = browser_for(account)
    client.post(reverse('photostudio:booking_create'), booking_data())
    booking = BookingRequest.objects.get()
    assert booking.user == account

    response = logged_client.post(reverse('photostudio:booking_detail', args=[booking.pk]), approve_data())
    booking.refresh_from_db()
    new_client = Client.objects.get(phone='+998 94 111 22 33')
    assert response.status_code == 302
    assert booking.status == BookingRequest.Status.APPROVED
    assert booking.session.client == new_client
    assert booking.session.status == Session.Status.PLANNED
    # So'rov akkauntdan yuborilgani uchun kabinet avtomatik bog'landi
    assert new_client.user == account
    assert 'Kutamiz!' in client.get(reverse('photostudio:cabinet')).content.decode()


@pytest.mark.django_db
def test_tasdiqlash_mavjud_mijozni_telefon_boyicha_topadi(logged_client, studio_client):
    booking = BookingRequest.objects.create(
        full_name='Aziza', phone='+998901234567', preferred_at=future(),
    )
    logged_client.post(reverse('photostudio:booking_detail', args=[booking.pk]), approve_data())
    booking.refresh_from_db()
    assert Client.objects.count() == 1
    assert booking.session.client == studio_client


@pytest.mark.django_db
def test_rad_etish(logged_client):
    booking = BookingRequest.objects.create(full_name='X', phone='+998 90 000 00 00', preferred_at=future())
    logged_client.post(reverse('photostudio:booking_detail', args=[booking.pk]), {'reject': '1', 'answer': 'Bu vaqt band'})
    booking.refresh_from_db()
    assert booking.status == BookingRequest.Status.REJECTED
    assert booking.answer == 'Bu vaqt band'
    assert Session.objects.count() == 0


@pytest.mark.django_db
def test_bron_royxati_faqat_xodimlarga(user, customer):
    url = reverse('photostudio:booking_list')
    assert browser_for(None).get(url).status_code == 302
    assert browser_for(customer).get(url).status_code == 403
    assert browser_for(user).get(url).status_code == 200


@pytest.mark.django_db
def test_menyuda_yangi_bronlar_soni(logged_client):
    BookingRequest.objects.create(full_name='X', phone='+998 90 000 00 00', preferred_at=future())
    response = logged_client.get(reverse('photostudio:home'))
    assert response.context['new_booking_count'] == 1
    assert 'nav-badge' in response.content.decode()
