# 2-hafta — Django loyiha strukturasi

**Holat:** ✅ bajarildi · **Commit:** `4776b76` (o'zgarishlarni ko'rish: `git show 4776b76 --stat`)

---

## Nazariy qism

### 1-topshiriq — Loyiha fayllari

| Fayl | Vazifasi |
|---|---|
| `manage.py` | Loyihani boshqarish buyruqlari: `runserver`, `migrate`, `startapp`, `createsuperuser` va h.k. |
| `config/__init__.py` | Papkani Python paketiga aylantiradi |
| `config/settings.py` | Barcha sozlamalar: ilovalar, ma'lumotlar bazasi, til, vaqt zonasi, static fayllar |
| `config/urls.py` | Asosiy URL'lar: qaysi manzil qaysi view'ga borishi |
| `config/wsgi.py` / `config/asgi.py` | Loyihani haqiqiy serverga (Gunicorn, Uvicorn) ulash uchun kirish nuqtasi |
| `db.sqlite3` | SQLite ma'lumotlar bazasi fayli |

Ilova (`startapp`) yaratganda qo'shiladigan fayllar: `models.py`, `views.py`, `admin.py`, `apps.py`, `tests.py`, `migrations/`.

### 2-topshiriq — Project va App farqi

**Project** (loyiha) — butun sayt: unda umumiy sozlamalar, asosiy URL'lar va ma'lumotlar bazasi bo'ladi.
**App** (ilova) — loyiha ichidagi bitta vazifani bajaradigan qism, masalan bizda `photostudio` ilovasi suratlar, mijozlar va fotosessiyalar bilan ishlaydi.
Bitta loyihada bir nechta ilova bo'lishi mumkin, bitta ilovani esa boshqa loyihaga ham ko'chirib ishlatsa bo'ladi.

---

## Amaliy qism

### 3-topshiriq — Loyiha fayllarini o'rganish (darsda og'zaki ko'rsatiladi)

| Nima | Qayerda | Nima qiladi (og'zaki tushuntirish) |
|---|---|---|
| `INSTALLED_APPS` | [`config/settings.py:44`](../config/settings.py) | Loyihada qaysi ilovalar ishlashini bildiradi. Django'ning tayyor ilovalari (admin, auth...) va mening `photostudio` ilovam shu yerda |
| `DATABASES` | [`config/settings.py:105`](../config/settings.py) | Qaysi ma'lumotlar bazasi ishlatilishi: bizda SQLite, fayl `db.sqlite3` |
| `TIME_ZONE` | [`config/settings.py:137`](../config/settings.py) | Vaqt zonasi. `'UTC'` dan `'Asia/Tashkent'` ga o'zgartirdim, sana-vaqtlar Toshkent vaqtida ko'rinishi uchun |
| `urlpatterns` | [`config/urls.py:15`](../config/urls.py) | URL manzillar ro'yxati: `admin/`, `api/`, `accounts/...` va ilovaning URL'lari (`include('photostudio.urls')`) |
| ilova `urlpatterns` | [`photostudio/urls.py:7`](../photostudio/urls.py) | Ilovaning o'z URL'lari (`photos/`, `clients/`, ...) |

### 4-topshiriq — Yangi ilova yaratish

Jadval bo'yicha 19-variant: **fotostudiya → `photostudio`**.

```bash
python manage.py startapp photostudio
```

> ⚠️ **Muammo va yechim.** 1-haftada loyiha `django-admin startproject photostudio` bilan yaratilgan edi,
> shuning uchun sozlamalar papkasi ham `photostudio` deb nomlangan edi. `startapp photostudio` quyidagi xatoni berdi:
>
> `CommandError: 'photostudio' conflicts with the name of an existing Python module and cannot be used as an app name.`
>
> Ilova nomi jadvalda aynan `photostudio` bo'lgani uchun, loyihaning sozlamalar papkasini **`config`** deb qayta nomladim
> (bu ko'p loyihalarda ishlatiladigan standart usul). `manage.py`, `asgi.py`, `wsgi.py` va `settings.py` dagi
> `photostudio.settings` / `photostudio.urls` yozuvlari `config...` ga o'zgartirildi.
> To'liq terminal chiqishi: [`terminal/week02_startapp.txt`](terminal/week02_startapp.txt)

### 5-topshiriq — Ilovani loyihaga ulash

[`config/settings.py:44`](../config/settings.py):

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    ...
    'django.contrib.staticfiles',
    ...
    # Mening ilovam (2-hafta)
    'photostudio',
]
```

Ilovaning nomi admin panelda chiroyli ko'rinishi uchun [`photostudio/apps.py`](../photostudio/apps.py) ga `verbose_name = 'Fotostudiya'` qo'shildi.

---

## Darsda qanday ko'rsatish

1. VS Code'da `config/settings.py` ni oching va `INSTALLED_APPS`, `DATABASES`, `TIME_ZONE` qatorlarini ko'rsating (yuqoridagi jadvaldagi tushuntirishlar bilan).
2. `config/urls.py` dagi `urlpatterns` ni ko'rsating.
3. Chap paneldagi `photostudio/` papkasini (ilova) ochib, `startapp` yaratgan fayllarni ko'rsating.
4. `INSTALLED_APPS` dagi `'photostudio'` qatorini ko'rsating.
5. O'qituvchi so'rasa, nima uchun sozlamalar papkasi `config` deb nomlanganini tushuntiring (yuqoridagi "Muammo va yechim").

## Natija

```
$ python manage.py check
System check identified no issues (0 silenced).
```
