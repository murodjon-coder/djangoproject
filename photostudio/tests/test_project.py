"""14-hafta: kichik loyiha — Client, Session, CRUD va foydalanuvchi rollari testlari."""
import datetime

import pytest
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone

from photostudio.models import Client, Photo, Session


@pytest.mark.django_db
def test_bosh_sahifa_hamma_uchun_ochiq(client):
    response = client.get(reverse('photostudio:home'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_session_mijozga_boglangan(photo_session, studio_client):
    assert photo_session.client == studio_client
    assert list(studio_client.sessions.all()) == [photo_session]
    assert photo_session.status == Session.Status.PLANNED
    assert str(photo_session).startswith('Aziza Rahimova — ')


@pytest.mark.django_db
def test_mijoz_ochirilsa_sessiyalari_ham_ochadi(photo_session, studio_client):
    studio_client.delete()
    assert Session.objects.count() == 0


@pytest.mark.django_db
def test_mijoz_qoshish(logged_client):
    response = logged_client.post(reverse('photostudio:client_create'), {
        'full_name': 'Jasur Hamidov', 'phone': '+998 91 234 56 78', 'email': '',
    })
    client_obj = Client.objects.get(full_name='Jasur Hamidov')
    assert response.status_code == 302
    assert response.url == client_obj.get_absolute_url()


@pytest.mark.django_db
def test_notogri_telefon_raqam(logged_client):
    response = logged_client.post(reverse('photostudio:client_create'), {
        'full_name': 'Jasur Hamidov', 'phone': '12ab',
    })
    assert response.status_code == 200
    assert 'phone' in response.context['form'].errors


@pytest.mark.django_db
def test_otgan_vaqtga_sessiya_rejalashtirib_bolmaydi(logged_client, studio_client):
    response = logged_client.post(reverse('photostudio:session_create'), {
        'client': studio_client.pk,
        'photographer': 'Murodjon',
        'scheduled_at': (timezone.localtime() - datetime.timedelta(days=1)).strftime('%Y-%m-%dT%H:%M'),
        'duration_minutes': 60,
        'location': 'Asosiy studiya',
        'price': 500000,
        'status': Session.Status.PLANNED,
    })
    assert response.status_code == 200
    assert 'scheduled_at' in response.context['form'].errors


@pytest.mark.django_db
def test_sessiyalarni_holat_boyicha_saralash(logged_client, photo_session, studio_client):
    Session.objects.create(
        client=studio_client, photographer='Dilnoza', price=100,
        scheduled_at=timezone.now(), status=Session.Status.DONE,
    )
    response = logged_client.get(reverse('photostudio:session_list') + '?status=planned')
    assert list(response.context['photo_sessions']) == [photo_session]


@pytest.mark.django_db
def test_suratni_tahrirlash(logged_client, photo, image_file):
    url = reverse('photostudio:photo_update', args=[photo.id])
    data = {'title': 'Yangi nom', 'photographer': photo.photographer, 'date': photo.date.isoformat()}

    # Rasmsiz suratni tahrirlashda rasm yuklash talab qilinadi
    response = logged_client.post(url, data)
    assert 'image' in response.context['form'].errors

    response = logged_client.post(url, {**data, 'image': image_file})
    photo.refresh_from_db()
    assert response.status_code == 302
    assert photo.title == 'Yangi nom'

    # Rasm bor bo'lsa, faqat nomini o'zgartirish yetarli — eski rasm saqlanib qoladi
    old_image = photo.image.name
    response = logged_client.post(url, {**data, 'title': 'Yana yangi nom'})
    photo.refresh_from_db()
    assert response.status_code == 302
    assert photo.image.name == old_image


@pytest.mark.django_db
def test_oddiy_foydalanuvchi_ochira_olmaydi(logged_client, photo, photo_session, studio_client):
    assert logged_client.post(reverse('photostudio:photo_delete', args=[photo.id])).status_code == 403
    assert logged_client.post(reverse('photostudio:session_delete', args=[photo_session.pk])).status_code == 403
    assert logged_client.post(reverse('photostudio:client_delete', args=[studio_client.pk])).status_code == 403
    assert Photo.objects.count() == 1


@pytest.mark.django_db
def test_admin_ochira_oladi(staff_client, photo):
    response = staff_client.post(reverse('photostudio:photo_delete', args=[photo.id]))
    assert response.status_code == 302
    assert Photo.objects.count() == 0


@pytest.mark.django_db
def test_seed_demo_buyrugi_takrorlanmaydi():
    call_command('seed_demo')
    call_command('seed_demo')
    assert Client.objects.count() == 4
    assert Session.objects.count() == 14
    assert Photo.objects.count() == 11
    assert all(photo.image for photo in Photo.objects.all())
    assert all(photo.tags.exists() for photo in Photo.objects.all())
    assert Client.objects.get(full_name='Aziza Rahimova').user.username == 'aziza'
