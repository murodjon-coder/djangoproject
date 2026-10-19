"""Qo'shimcha funksiyalar: qidiruv/filtr/sahifalash, teglar (M2M), mijoz kabineti (O2O), statistika."""
import datetime

import pytest
from django.urls import reverse
from django.utils import timezone

from photostudio.models import Category, Client, Photo, Session, Tag
from photostudio.views import PHOTOS_PER_PAGE, money_short


def make_photo(title, **kwargs):
    kwargs.setdefault('photographer', 'Murodjon')
    kwargs.setdefault('date', datetime.date(2026, 10, 1))
    return Photo.objects.create(title=title, **kwargs)


# ---------------------------------------------------------------- 1. Qidiruv, filtr, sahifalash

@pytest.mark.django_db
def test_qidiruv_nomi_boyicha(logged_client, photo):
    make_photo('Bolalar bayrami')
    response = logged_client.get(reverse('photostudio:photo_list'), {'q': 'bayram'})
    assert [p.title for p in response.context['photos']] == ['Bolalar bayrami']


@pytest.mark.django_db
def test_qidiruv_teg_va_fotograf_boyicha(logged_client):
    tagged = make_photo('Birinchi', photographer='Dilnoza')
    tagged.tags.add(Tag.objects.create(name='oq fon'))
    make_photo('Ikkinchi')
    url = reverse('photostudio:photo_list')
    assert [p.title for p in logged_client.get(url, {'q': 'oq fon'}).context['photos']] == ['Birinchi']
    assert [p.title for p in logged_client.get(url, {'q': 'dilnoza'}).context['photos']] == ['Birinchi']


@pytest.mark.django_db
def test_kategoriya_va_teg_filtri(logged_client, category):
    other = Category.objects.create(name='Tabiat')
    tag = Tag.objects.create(name='kechqurun')
    a = make_photo('A', category=category)
    a.tags.add(tag)
    make_photo('B', category=other)
    url = reverse('photostudio:photo_list_cbv')
    assert [p.title for p in logged_client.get(url, {'category': other.id}).context['photos']] == ['B']
    assert [p.title for p in logged_client.get(url, {'tag': tag.slug}).context['photos']] == ['A']


@pytest.mark.django_db
@pytest.mark.parametrize('url_name', ['photostudio:photo_list', 'photostudio:photo_list_cbv'])
def test_sahifalash(logged_client, url_name):
    for i in range(PHOTOS_PER_PAGE + 3):
        make_photo(f'Surat {i}')
    url = reverse(url_name)
    first = logged_client.get(url)
    second = logged_client.get(url, {'page': 2})
    assert len(first.context['photos']) == PHOTOS_PER_PAGE
    assert len(second.context['photos']) == 3
    assert first.context['page_obj'].paginator.count == PHOTOS_PER_PAGE + 3
    assert '?page=2' in first.content.decode()


# ---------------------------------------------------------------- 2. Teglar (Many-to-Many)

@pytest.mark.django_db
def test_teg_many_to_many(photo):
    tag = Tag.objects.create(name="Oq fon")
    other = make_photo('Boshqa')
    photo.tags.add(tag)
    other.tags.add(tag)
    assert tag.slug == 'oq-fon'
    assert set(tag.photos.all()) == {photo, other}
    assert list(photo.tags.all()) == [tag]


@pytest.mark.django_db
def test_teg_slug_takrorlanmaydi():
    first = Tag.objects.create(name="To'y")
    second = Tag.objects.create(name="Toy")
    assert first.slug == 'toy'
    assert second.slug == 'toy-2'


@pytest.mark.django_db
def test_formada_yangi_teglar_yaratiladi(logged_client, image_file):
    existing = Tag.objects.create(name='studiya')
    response = logged_client.post(reverse('photostudio:photo_create'), {
        'title': 'Teglangan surat',
        'photographer': 'Murodjon',
        'date': '2026-10-01',
        'tags': [existing.pk],
        'new_tags': 'oq fon, Studiya,  kechqurun ',
        'image': image_file,
    })
    photo = Photo.objects.get(title='Teglangan surat')
    assert response.status_code == 302
    assert sorted(t.name for t in photo.tags.all()) == ['kechqurun', 'oq fon', 'studiya']
    assert Tag.objects.count() == 3


@pytest.mark.django_db
def test_galereya_teglarni_prefetch_qiladi(logged_client, django_assert_max_num_queries):
    for i in range(5):
        p = make_photo(f'Surat {i}')
        p.tags.add(Tag.objects.get_or_create(name=f'teg{i}')[0])
    # Suratlar soniga bog'liq bo'lmagan, o'zgarmas sondagi so'rovlar (N+1 yo'q)
    with django_assert_max_num_queries(12):
        logged_client.get(reverse('photostudio:photo_list'))


@pytest.mark.django_db
def test_api_teglarni_qaytaradi(logged_client, photo):
    photo.tags.add(Tag.objects.create(name='portret'))
    assert logged_client.get(f'/api/photostudio/{photo.id}/').json()['tags'] == ['portret']


# ---------------------------------------------------------------- 3. Mijoz kabineti (One-to-One)

@pytest.mark.django_db
def test_mijoz_faqat_oz_suratlarini_koradi(customer_client, studio_client, photo_session):
    own = make_photo('Mening suratim', session=photo_session)
    stranger = Client.objects.create(full_name='Begona', phone='+998 90 000 00 00')
    foreign_session = Session.objects.create(
        client=stranger, photographer='X', price=1, scheduled_at=timezone.now(),
    )
    foreign = make_photo('Begona surat', session=foreign_session)

    response = customer_client.get(reverse('photostudio:cabinet'))
    assert response.status_code == 200
    content = response.content.decode()
    assert 'Mening suratim' in content
    assert 'Begona surat' not in content

    assert customer_client.get(reverse('photostudio:photo_detail', args=[own.id])).status_code == 200
    assert customer_client.get(reverse('photostudio:photo_detail', args=[foreign.id])).status_code == 403


@pytest.mark.django_db
@pytest.mark.parametrize('url_name', [
    'photostudio:photo_list', 'photostudio:photo_list_cbv', 'photostudio:client_list',
    'photostudio:session_list', 'photostudio:dashboard', 'photostudio:photo_create',
])
def test_mijoz_xodim_sahifalariga_kira_olmaydi(customer_client, url_name):
    assert customer_client.get(reverse(url_name)).status_code == 403


@pytest.mark.django_db
def test_bog_lanmagan_foydalanuvchi_kabineti(client, django_user_model):
    client.force_login(django_user_model.objects.create_user('yangi', password='Parol-12345'))
    response = client.get(reverse('photostudio:cabinet'))
    assert response.status_code == 200
    assert response.context['client'] is None
    assert "Kabinet hali bog'lanmagan" in response.content.decode()


@pytest.mark.django_db
def test_kirgandan_keyin_rolga_qarab_yonaltirish(client, user, customer):
    login_url = reverse('login')
    response = client.post(login_url, {'username': 'mijoz', 'password': 'Parol-12345'}, follow=True)
    assert response.redirect_chain[-1][0] == reverse('photostudio:cabinet')
    client.logout()
    response = client.post(login_url, {'username': 'testuser', 'password': 'Parol-12345'}, follow=True)
    assert response.redirect_chain[-1][0] == reverse('photostudio:home')


@pytest.mark.django_db
def test_xodim_mijozga_kabinet_yaratadi(logged_client, studio_client):
    response = logged_client.post(reverse('photostudio:client_account_create', args=[studio_client.pk]), {
        'username': 'aziza',
        'password1': 'Fotostudiya2026',
        'password2': 'Fotostudiya2026',
    })
    studio_client.refresh_from_db()
    assert response.status_code == 302
    assert studio_client.user.username == 'aziza'
    assert studio_client.user.client_profile == studio_client


# ---------------------------------------------------------------- 4. Statistika paneli

@pytest.mark.django_db
def test_statistika_faqat_bajarilgan_sessiyalarni_hisoblaydi(logged_client, studio_client):
    now = timezone.now()
    Session.objects.create(client=studio_client, photographer='A', price=1_000_000, scheduled_at=now, status=Session.Status.DONE)
    Session.objects.create(client=studio_client, photographer='A', price=500_000, scheduled_at=now, status=Session.Status.DONE)
    Session.objects.create(client=studio_client, photographer='B', price=9_000_000, scheduled_at=now, status=Session.Status.CANCELLED)

    response = logged_client.get(reverse('photostudio:dashboard'))
    ctx = response.context
    assert response.status_code == 200
    assert ctx['revenue_total'] == 1_500_000
    assert ctx['revenue_this_month'] == 1_500_000
    assert ctx['average_price'] == 750_000
    assert ctx['cancel_rate'] == 33
    assert len(ctx['revenue_by_month']) == 6
    assert ctx['revenue_by_month'][-1]['total'] == 1_500_000
    assert ctx['revenue_by_month'][-1]['pct'] == 100
    assert ctx['photographers'][0]['photographer'] == 'A'
    assert ctx['top_clients'][0] == studio_client


@pytest.mark.django_db
def test_statistika_mehmon_uchun_yopiq(client):
    assert client.get(reverse('photostudio:dashboard')).status_code == 302


@pytest.mark.parametrize('value, expected', [
    (0, '0'), (850, '850'), (800_000, '800 ming'), (2_500_000, '2,5 mln'), (3_000_000, '3 mln'),
])
def test_qisqa_summa(value, expected):
    assert money_short(value) == expected


@pytest.mark.django_db
def test_mijoz_surat_sahifasida_xodim_havolalari_yoq(customer_client, photo_session):
    own = make_photo('Mening suratim', session=photo_session)
    content = customer_client.get(reverse('photostudio:photo_detail', args=[own.id])).content.decode()
    assert reverse('photostudio:session_detail', args=[photo_session.pk]) not in content
    assert reverse('photostudio:photo_update', args=[own.id]) not in content
