import datetime

import pytest
from django.urls import reverse

from photostudio.models import Photo


@pytest.mark.django_db
def test_royxat_sahifasi_200(logged_client, photo):
    """13-hafta, 5-topshiriq: ro'yxat view'i 200 qaytaradi va suratni ko'rsatadi."""
    response = logged_client.get(reverse('photostudio:photo_list'))
    assert response.status_code == 200
    assert 'Studiyadagi portret' in response.content.decode()


@pytest.mark.django_db
def test_cbv_royxat_sahifasi_200(logged_client, photo):
    response = logged_client.get(reverse('photostudio:photo_list_cbv'))
    assert response.status_code == 200
    assert list(response.context['photos']) == [photo]


@pytest.mark.django_db
def test_login_qilmagan_foydalanuvchi_loginga_yonaltiriladi(client):
    url = reverse('photostudio:photo_list')
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == f"{reverse('login')}?next={url}"


@pytest.mark.django_db
def test_detail_sahifa(logged_client, photo):
    response = logged_client.get(reverse('photostudio:photo_detail', args=[photo.id]))
    assert response.status_code == 200
    assert response.context['photo'] == photo


@pytest.mark.django_db
def test_detail_mavjud_bolmagan_id_404(logged_client):
    response = logged_client.get(reverse('photostudio:photo_detail', args=[999]))
    assert response.status_code == 404


@pytest.mark.django_db
def test_rasm_yuklab_surat_qoshish(logged_client, category, image_file):
    response = logged_client.post(reverse('photostudio:photo_create'), {
        'title': 'Yangi surat',
        'photographer': 'Murodjon',
        'date': '2026-10-01',
        'category': category.id,
        'image': image_file,
    })
    photo = Photo.objects.get(title='Yangi surat')
    assert response.status_code == 302
    assert response.url == reverse('photostudio:photo_detail', args=[photo.id])
    assert photo.image.name.startswith('photos/')


@pytest.mark.django_db
def test_notogri_forma_xato_qaytaradi(logged_client):
    response = logged_client.post(reverse('photostudio:photo_create'), {
        'title': 'ab',
        'photographer': 'Murodjon',
        'date': (datetime.date.today() + datetime.timedelta(days=30)).isoformat(),
    })
    assert response.status_code == 200
    errors = response.context['form'].errors
    assert 'title' in errors
    assert 'date' in errors
    assert 'image' in errors
    assert Photo.objects.count() == 0


@pytest.mark.django_db
def test_royxatdan_otish(client, django_user_model):
    response = client.post(reverse('photostudio:register'), {
        'username': 'yangi_user',
        'password1': 'Fotostudiya2026',
        'password2': 'Fotostudiya2026',
    })
    assert response.status_code == 302
    assert django_user_model.objects.filter(username='yangi_user').exists()
