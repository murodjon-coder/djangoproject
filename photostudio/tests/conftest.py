import datetime
import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image

from photostudio.models import Category, Photo


@pytest.fixture(autouse=True)
def media_tmp(settings, tmp_path):
    """Testlarda yuklangan fayllar haqiqiy media/ papkani ifloslamasligi uchun."""
    settings.MEDIA_ROOT = tmp_path / 'media'


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(username='testuser', password='Parol-12345')


@pytest.fixture
def logged_client(client, user):
    client.force_login(user)
    return client


@pytest.fixture
def category():
    return Category.objects.create(name='Portret')


@pytest.fixture
def photo(category):
    return Photo.objects.create(
        title='Studiyadagi portret',
        photographer='Murodjon',
        date=datetime.date(2026, 10, 1),
        category=category,
    )


@pytest.fixture
def image_file():
    """Xotirada yaratilgan kichik PNG rasm (yuklashni sinash uchun)."""
    buffer = io.BytesIO()
    Image.new('RGB', (10, 10), 'orange').save(buffer, format='PNG')
    return SimpleUploadedFile('test.png', buffer.getvalue(), content_type='image/png')


@pytest.fixture
def staff_client(client, django_user_model):
    admin = django_user_model.objects.create_user(username='admin_test', password='Parol-12345', is_staff=True)
    client.force_login(admin)
    return client


@pytest.fixture
def studio_client():
    from photostudio.models import Client
    return Client.objects.create(full_name='Aziza Rahimova', phone='+998 90 123 45 67')


@pytest.fixture
def photo_session(studio_client):
    from django.utils import timezone

    from photostudio.models import Session
    return Session.objects.create(
        client=studio_client,
        photographer='Murodjon',
        scheduled_at=timezone.now() + datetime.timedelta(days=3),
        price=500000,
    )
