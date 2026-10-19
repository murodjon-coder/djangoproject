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
| `Tag` | `name`, `slug` | — |
| `Client` (mijoz) | `full_name`, `phone`, `email`, `created_at`, `user` | `user` → **User** (One-to-One, shaxsiy kabinet) |
| `Session` (fotosessiya) | `client`, `photographer`, `scheduled_at`, `duration_minutes`, `location`, `price`, `status`, `notes` | `client` → **Client** (ForeignKey, bitta mijozda ko'p sessiya) |
| `BookingRequest` (bron so'rovi) | `full_name`, `phone`, `email`, `category`, `preferred_at`, `message`, `user`, `status`, `answer`, `session` | `session` ↔ **Session** (One-to-One, tasdiqlanganda) |
| `Photo` (surat) | `title`, `photographer`, `date`, `category`, `image`, `session`, `tags` | `category` → **Category**, `session` → **Session** (ForeignKey), `tags` ↔ **Tag** (Many-to-Many) |

```
User 1 ──── 1 Client 1 ──── * Session 1 ──── * Photo * ──── 1 Category
                                                  * ──── * Tag
```

### Sahifalar

| Manzil | Sahifa | Kim ko'ra oladi |
|---|---|---|
| `/` | Bosh sahifa (statistika, so'nggi suratlar, video) | hamma |
| `/about/` | Men haqimda (shaxsiy surat, video, JDU logotipi) | hamma |
| `/cabinet/` | Mijozning shaxsiy kabineti — faqat o'z fotosessiyalari va suratlari | mijoz |
| `/photos/` | Galereya — function-based view (+ qidiruv `?q=`, filtr `?category=`, `?tag=`, sahifalash) | xodim |
| `/photos/cbv/` | Galereya — ListView | xodim |
| `/photos/add/`, `/photos/<id>/edit/` | Surat qo'shish / tahrirlash (rasm, teglar) | xodim |
| `/photos/<id>/` | Surat haqida batafsil | xodim; mijoz — faqat o'z surati |
| `/photos/<id>/delete/` | Suratni o'chirish | admin |
| `/clients/...` | Mijozlar CRUD + `/clients/<id>/account/` — kabinet yaratish | xodim (o'chirish — admin) |
| `/sessions/...` | Fotosessiyalar CRUD, holat bo'yicha saralash | xodim (o'chirish — admin) |
| `/dashboard/` | Statistika paneli | xodim |
| `/book/` | Fotosessiyaga onlayn yozilish | hamma |
| `/bookings/`, `/bookings/<id>/` | Bron so'rovlari: ko'rib chiqish, tasdiqlash (mijoz + sessiya yaratiladi), rad etish | xodim |
| `/accounts/register/`, `/accounts/login/`, `/accounts/logout/` | Ro'yxatdan o'tish, kirish, chiqish | hamma |
| `/api/photostudio/`, `/api/photostudio/<id>/` | REST API (DRF) | xodim |
| `/admin/` | Django admin panel | admin |

### Foydalanuvchi rollari

1. **Mehmon** (login qilmagan) — bosh sahifa, "Men haqimda", onlayn bron; ro'yxatdan o'tishi mumkin.
2. **Mijoz** (oddiy ro'yxatdan o'tgan foydalanuvchi) — faqat o'z kabineti: fotosessiyalari va suratlari, yuklab olish.
3. **Xodim** (`Xodimlar` guruhi) — galereya, mijozlar, fotosessiyalar, bronlar, statistika, API: ko'rish, qo'shish, tahrirlash.
4. **Administrator** (`is_staff`) — xodim qila oladigan hamma narsa + o'chirish + admin panel.

> 14-haftada 3 ta rol bor edi (mehmon, xodim, administrator). Mijoz kabineti qo'shilgach, mijoz va xodim rollari ajratildi —
> batafsil: [`hisobot/qoshimcha.md`](hisobot/qoshimcha.md).

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
python manage.py seed_demo        # ixtiyoriy: demo mijozlar, fotosessiyalar, suratlar, teglar va 'aziza' mijoz kabineti

# 4) Server
python manage.py runserver
```

Brauzerda: <http://127.0.0.1:8000/>

### Internetga joylash

`.env.example` → `.env`, keyin [**DEPLOY.md**](DEPLOY.md) dagi qadamlar (PythonAnywhere yoki Render).

## 3. Testlar

```bash
pytest
```

`pytest.ini` loyiha ildizida joylashgan va `DJANGO_SETTINGS_MODULE = config.settings` ni ko'rsatadi.
Testlar `photostudio/tests/` papkasida (74 ta): modellar, view'lar, formalar, API, middleware, rollar, qidiruv, teglar, kabinet, statistika va onlayn bron.

## 4. API (Django REST Framework)

```bash
# API faqat xodimlar uchun — brauzerda admin/xodim bilan kirib oching:
http://127.0.0.1:8000/api/photostudio/       # ro'yxat
http://127.0.0.1:8000/api/photostudio/1/     # bitta surat
```

## 5. Loyiha tuzilmasi

```
photostudio/                  ← loyiha ildizi (manage.py shu yerda)
├── config/                   ← loyiha sozlamalari (settings.py, urls.py, wsgi.py, asgi.py)
├── photostudio/              ← ilova (app)
│   ├── models.py             ← Category, Tag, Client, Session, Photo
│   ├── views.py              ← FBV va CBV'lar
│   ├── forms.py              ← PhotoForm, ClientForm, SessionForm
│   ├── urls.py               ← ilova URL'lari (app_name = 'photostudio')
│   ├── admin.py              ← admin panel sozlamalari
│   ├── roles.py              ← rollar: is_employee, employee_required, mixin'lar
│   ├── context_processors.py ← is_employee, client_profile — har bir template'da
│   ├── backends.py           ← login katta-kichik harfga sezgir emas
│   ├── middleware.py         ← RequestTimingMiddleware
│   ├── serializers.py        ← PhotoSerializer
│   ├── api.py                ← PhotoViewSet
│   ├── management/commands/seed_demo.py
│   ├── demo_photos/          ← AI bilan yaratilgan demo suratlar (seed_demo ishlatadi)
│   ├── migrations/
│   ├── templates/photostudio/
│   └── tests/
├── templates/                ← base.html, registration/, 403.html, 404.html
├── static/                   ← css/, images/, video/
├── media/                    ← yuklangan rasmlar (git'ga kirmaydi)
├── hisobot/                  ← haftalik hisobotlar va skrinshotlar
├── DEPLOY.md               ← internetga joylash qo'llanmasi
├── .env.example            ← maxfiy sozlamalar namunasi (.env git'ga kirmaydi)
├── render.yaml, build.sh   ← Render uchun
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
