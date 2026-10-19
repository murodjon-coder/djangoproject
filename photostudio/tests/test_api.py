import pytest


@pytest.mark.django_db
def test_api_royxat(client, photo):
    response = client.get('/api/photostudio/')
    assert response.status_code == 200
    assert response.json()[0]['title'] == 'Studiyadagi portret'
    assert response.json()[0]['category_name'] == 'Portret'


@pytest.mark.django_db
def test_api_bitta_obyekt(client, photo):
    response = client.get(f'/api/photostudio/{photo.id}/')
    assert response.status_code == 200
    assert response.json()['photographer'] == 'Murodjon'


@pytest.mark.django_db
def test_api_login_qilmasdan_qoshib_bolmaydi(client):
    response = client.post('/api/photostudio/', {'title': 'Test'})
    assert response.status_code == 403
