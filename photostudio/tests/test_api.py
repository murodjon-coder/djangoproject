"""12-hafta: DRF API. Mijoz kabineti qo'shilgach API faqat xodimlarga ochiq."""
import pytest
from django.test import Client as BrowserClient


@pytest.mark.django_db
def test_api_royxat(logged_client, photo):
    response = logged_client.get('/api/photostudio/')
    assert response.status_code == 200
    assert response.json()[0]['title'] == 'Studiyadagi portret'
    assert response.json()[0]['category_name'] == 'Portret'


@pytest.mark.django_db
def test_api_bitta_obyekt(logged_client, photo):
    response = logged_client.get(f'/api/photostudio/{photo.id}/')
    assert response.status_code == 200
    assert response.json()['photographer'] == 'Murodjon'


@pytest.mark.django_db
def test_xodim_api_orqali_surat_qoshadi(logged_client, category):
    response = logged_client.post('/api/photostudio/', {
        'title': 'API orqali', 'photographer': 'Murodjon', 'date': '2026-10-01', 'category': category.id,
    })
    assert response.status_code == 201
    assert response.json()['category_name'] == 'Portret'


@pytest.mark.django_db
@pytest.mark.parametrize('url', ['/api/', '/api/photostudio/', '/api/photostudio/1/'])
def test_api_mehmon_uchun_yopiq(client, photo, url):
    response = client.get(url)
    assert response.status_code == 403
    assert 'xodimlari uchun' in response.json()['detail']


@pytest.mark.django_db
def test_api_mijoz_uchun_yopiq(customer, photo):
    browser = BrowserClient()
    browser.force_login(customer)
    assert browser.get('/api/photostudio/').status_code == 403
    assert browser.post('/api/photostudio/', {'title': 'Test'}).status_code == 403


@pytest.mark.django_db
def test_menyuda_api_faqat_xodimga(client, logged_client):
    assert 'href="/api/"' in logged_client.get('/').content.decode()
    assert 'href="/api/"' not in BrowserClient().get('/').content.decode()
