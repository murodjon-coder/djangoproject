import datetime

import pytest

from photostudio.models import Category, Photo


@pytest.mark.django_db
def test_photo_yaratish():
    """13-hafta, 4-topshiriq: obyekt yaratib, maydonini assert bilan tekshiramiz."""
    photo = Photo.objects.create(
        title='Kelin-kuyov portreti',
        photographer='Murodjon',
        date=datetime.date(2026, 9, 12),
    )
    assert photo.title == 'Kelin-kuyov portreti'
    assert photo.photographer == 'Murodjon'
    assert Photo.objects.count() == 1


@pytest.mark.django_db
def test_photo_str_metodi(photo):
    assert str(photo) == 'Studiyadagi portret (Murodjon)'


@pytest.mark.django_db
def test_kategoriya_bilan_bog_lanish(photo, category):
    assert photo.category == category
    assert list(category.photos.all()) == [photo]


@pytest.mark.django_db
def test_kategoriya_ochirilsa_surat_qoladi(photo, category):
    category.delete()
    photo.refresh_from_db()
    assert photo.category is None


@pytest.mark.django_db
def test_category_str():
    assert str(Category.objects.create(name="To'y")) == "To'y"
