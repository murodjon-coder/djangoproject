# Fotostudiya boshqaruv tizimi

**Introduction to Django** kursi bo'yicha yakuniy loyiha.
Variant: **19 — fotostudiya (`photostudio`)**. Muallif: Murodjon.

Fotostudiya xodimlari uchun veb-tizim: suratlar (portfolio), mijozlar va fotosessiyalarni
bir joyda boshqarish, rasm yuklash, REST API va testlar.

---

## 1. Reja (14-hafta, 3-topshiriq)

### Modellar

| Model | Maydonlar | Bog'lanish |
|---|---|---|
| `Category` | `name` | — |
| `Client` (mijoz) | `full_name`, `phone`, `email`, `created_at` | — |
| `Session` (fotosessiya) | `client`, `photographer`, `scheduled_at`, `duration_minutes`, `location`, `price`, `status`, `notes` | `client` → **Client** (ForeignKey, bitta mijozda ko'p sessiya) |
| `Photo` (surat) | `title`, `photographer`, `date`, `category`, `image`, `session` | `category` → **Category**, `session` → **Session** (ForeignKey) |

```
Client 1 ──── * Session 1 ──── * Photo * ──── 1 Category
```

### Sahifalar

| Manzil | Sahifa | Kim ko'ra oladi |
|---|---|---|
| `/` | Bosh sahifa (statistika, so'nggi suratlar, video) | hamma |
| `/about/` | Men haqimda (shaxsiy surat, video, JDU logotipi) | hamma |
| `/photos/` | Suratlar ro'yxati — function-based view | login qilganlar |
| `/photos/cbv/` | Suratlar ro'yxati — ListView | login qilganlar |
| `/photos/add/` | Surat qo'shish (rasm yuklash bilan) | login qilganlar |
| `/photos/<id>/` | Surat haqida batafsil | login qilganlar |
| `/photos/<id>/edit/` | Suratni tahrirlash | login qilganlar |
| `/photos/<id>/delete/` | Suratni o'chirish | faqat admin |
| `/clients/`, `/clients/add/`, `/clients/<id>/`, `/clients/<id>/edit/`, `/clients/<id>/delete/` | Mijozlar CRUD | login qilganlar (o'chirish — admin) |
| `/sessions/`, `/sessions/add/`, `/sessions/<id>/`, `/sessions/<id>/edit/`, `/sessions/<id>/delete/` | Fotosessiyalar CRUD, holat bo'yicha saralash | login qilganlar (o'chirish — admin) |
| `/accounts/register/`, `/accounts/login/`, `/accounts/logout/` | Ro'yxatdan o'tish, kirish, chiqish | hamma |
| `/api/photostudio/`, `/api/photostudio/<id>/` | REST API (DRF) | o'qish — hamma, yozish — login qilganlar |
| `/admin/` | Django admin panel | admin |

### Foydalanuvchi rollari

1. **Mehmon** (login qilmagan) — bosh sahifa, "Men haqimda", API'ni o'qish; ro'yxatdan o'tishi mumkin.
2. **Xodim** (ro'yxatdan o'tgan foydalanuvchi) — suratlar, mijozlar va fotosessiyalarni ko'rish, qo'shish, tahrirlash.
3. **Administrator** (`is_staff`) — xodim qila oladigan hamma narsa + o'chirish + admin panel.

---

## 2. O'rnatish va ishga tushirish

```bash
# 1) Virtual muhit
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2) Kutubxonalar
pip install -r requirements.txt

# 3) Ma'lumotlar bazasi
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo        # ixtiyoriy: demo mijoz, fotosessiya va suratlar

# 4) Server
python manage.py runserver
```

Brauzerda: <http://127.0.0.1:8000/>

## 3. Testlar

```bash
pytest
```

`pytest.ini` loyiha ildizida joylashgan va `DJANGO_SETTINGS_MODULE = config.settings` ni ko'rsatadi.
Testlar `photostudio/tests/` papkasida: modellar, view'lar, formalar, API, middleware va rollar.

## 4. API (Django REST Framework)

```bash
curl http://127.0.0.1:8000/api/photostudio/       # ro'yxat
curl http://127.0.0.1:8000/api/photostudio/1/     # bitta surat
```

## 5. Loyiha tuzilmasi

```
photostudio/                  ← loyiha ildizi (manage.py shu yerda)
├── config/                   ← loyiha sozlamalari (settings.py, urls.py, wsgi.py, asgi.py)
├── photostudio/              ← ilova (app)
│   ├── models.py             ← Category, Client, Session, Photo
│   ├── views.py              ← FBV va CBV'lar
│   ├── forms.py              ← PhotoForm, ClientForm, SessionForm
│   ├── urls.py               ← ilova URL'lari (app_name = 'photostudio')
│   ├── admin.py              ← admin panel sozlamalari
│   ├── middleware.py         ← RequestTimingMiddleware
│   ├── serializers.py        ← PhotoSerializer
│   ├── api.py                ← PhotoViewSet
│   ├── management/commands/seed_demo.py
│   ├── migrations/
│   ├── templates/photostudio/
│   └── tests/
├── templates/                ← base.html, registration/, 403.html, 404.html
├── static/                   ← css/, images/, video/
├── media/                    ← yuklangan rasmlar (git'ga kirmaydi)
├── hisobot/                  ← haftalik hisobotlar va skrinshotlar
├── pytest.ini
├── requirements.txt
└── .gitignore
```

> **Eslatma:** loyiha `django-admin startproject photostudio` bilan yaratilgan edi. Ilova ham
> `photostudio` deb nomlanishi kerak bo'lgani uchun `startapp photostudio` nom to'qnashuvi xatosini berdi.
> Shu sababli loyiha sozlamalari papkasi `config/` deb qayta nomlandi.

## 6. Haftalik hisobotlar

Har bir hafta bo'yicha nima qilingani, qaysi faylda ekani, nazariy javoblar va skrinshotlar —
[`hisobot/`](hisobot/README.md) papkasida.
