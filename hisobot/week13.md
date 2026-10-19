# 13-hafta — Django'da testlash

**Holat:** ✅ bajarildi · **Commit:** `1b20588` (17 ta test), 14-haftada yana 11 ta qo'shildi → **jami 69 ta test, hammasi passed**

---

## Nazariy qism

### 1-topshiriq — Nima uchun test yozamiz

1. **Xatoni erta topish.** Kodni o'zgartirganda eski funksiya buzilsa, test darhol aytadi. Masalan, 14-haftada tahrirlash testi rasm majburiyligini eslatib qo'ydi.
2. **Qo'rqmasdan o'zgartirish.** Testlar bor bo'lsa, kodni qayta yozish (refactoring) yoki yangi funksiya qo'shish xavfsiz bo'ladi.
3. **Hujjat vazifasi.** Testlar kod qanday ishlashi kerakligini ko'rsatib turadi, masalan "oddiy foydalanuvchi o'chira olmaydi".

### 2-topshiriq — `@pytest.mark.django_db` va `assert`

`@pytest.mark.django_db` testga ma'lumotlar bazasidan foydalanishga ruxsat beradi. pytest-django test uchun alohida vaqtinchalik baza yaratadi va har bir testdan keyin uni tozalaydi, shuning uchun haqiqiy `db.sqlite3` ga tegilmaydi. Bu belgisiz bazaga murojaat qilgan test xato beradi.
`assert` — shart rost ekanini tekshiradi: `assert photo.title == 'Kelin-kuyov portreti'`. Shart yolg'on bo'lsa, test **FAILED** bo'ladi va pytest nima kutilgani va nima chiqqanini ko'rsatadi.

---

## Amaliy qism

### 3-topshiriq — pytest sozlash

```bash
pip install pytest pytest-django
```

[`pytest.ini`](../pytest.ini) (loyiha ildizida, `manage.py` yonida):

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = test_*.py
testpaths = photostudio/tests
addopts = -v
```

`startapp` yaratgan `photostudio/tests.py` o'chirildi, uning o'rniga `photostudio/tests/` papkasi (paket) yaratildi.
Umumiy fixture'lar (`user`, `logged_client`, `photo`, `image_file`...) — [`tests/conftest.py`](../photostudio/tests/conftest.py).

### 4-topshiriq — Model testi

[`photostudio/tests/test_models.py`](../photostudio/tests/test_models.py):

```python
@pytest.mark.django_db
def test_photo_yaratish():
    photo = Photo.objects.create(
        title='Kelin-kuyov portreti',
        photographer='Murodjon',
        date=datetime.date(2026, 9, 12),
    )
    assert photo.title == 'Kelin-kuyov portreti'
    assert photo.photographer == 'Murodjon'
    assert Photo.objects.count() == 1
```

### 5-topshiriq — View testi va ishga tushirish

[`photostudio/tests/test_views.py`](../photostudio/tests/test_views.py):

```python
@pytest.mark.django_db
def test_royxat_sahifasi_200(logged_client, photo):
    response = logged_client.get(reverse('photostudio:photo_list'))
    assert response.status_code == 200
    assert 'Studiyadagi portret' in response.content.decode()
```

`logged_client` — pytest-django'ning `client` fixture'i, `force_login` bilan tizimga kiritilgan. Ro'yxat sahifasi `@login_required` bo'lgani uchun shunday qilingan.
Login'siz holat alohida test qilingan: `test_login_qilmagan_foydalanuvchi_loginga_yonaltiriladi` → 302.

**Test fayllari:**

| Fayl | Nimani tekshiradi |
|---|---|
| `test_models.py` | obyekt yaratish, `__str__`, ForeignKey, `SET_NULL` |
| `test_views.py` | ro'yxat (FBV/CBV), detail, 404, rasm yuklash, forma xatolari, ro'yxatdan o'tish |
| `test_api.py` | `/api/photostudio/` ro'yxat, bitta obyekt, login'siz POST → 403 |
| `test_middleware.py` | middleware konsolga yozishi |
| `test_project.py` | 14-hafta: mijoz/fotosessiya, CRUD, rollar (403), `seed_demo` |

---

## Darsda qanday ko'rsatish

```bash
pytest
```

## Natija

To'liq chiqish: [`terminal/week13_pytest.txt`](terminal/week13_pytest.txt)

```
platform darwin -- Python 3.14.8, pytest-9.1.1, pluggy-1.7.0
django: version: 6.1.2, settings: config.settings (from ini)
configfile: pytest.ini
plugins: django-4.14.0
collected 69 items

photostudio/tests/test_api.py::test_api_royxat PASSED
photostudio/tests/test_api.py::test_api_bitta_obyekt PASSED
photostudio/tests/test_api.py::test_api_login_qilmasdan_qoshib_bolmaydi PASSED
photostudio/tests/test_middleware.py::test_middleware_konsolga_yozadi PASSED
photostudio/tests/test_models.py::test_photo_yaratish PASSED
photostudio/tests/test_models.py::test_photo_str_metodi PASSED
...
photostudio/tests/test_views.py::test_royxat_sahifasi_200 PASSED
...
============================== 69 passed ==============================
```
