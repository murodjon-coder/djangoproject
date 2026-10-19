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
