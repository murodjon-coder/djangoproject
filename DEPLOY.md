# Loyihani internetga joylash (deploy)

Loyiha internetga chiqishga tayyor. Maxfiy sozlamalar `.env` faylida, static fayllarni WhiteNoise beradi,
`python manage.py check --deploy` xatosiz o'tadi. Quyidagi ikki bepul variantdan birini tanlang.

| | **PythonAnywhere** (tavsiya) | **Render** |
|---|---|---|
| Narxi | bepul (karta shart emas) | bepul (karta shart emas) |
| Manzil | `https://<login>.pythonanywhere.com` | `https://photostudio-xxxx.onrender.com` |
| Ma'lumotlar bazasi (SQLite) va yuklangan rasmlar | **saqlanib qoladi** | har qayta deploy'da **o'chadi** (`seed_demo` qayta yaratadi) |
| Uxlab qolish | yo'q (3 oyda bir marta "Extend" tugmasini bosish kerak) | 15 daqiqa ishlatilmasa uxlaydi, birinchi ochilish ~1 daqiqa |
| Qiyinligi | 15–20 daqiqa, qo'lda sozlanadi | 5 daqiqa, deyarli avtomatik |

> **Shart:** ikkala variant ham kodni **GitHub**'dan oladi. Avval loyihani GitHub'ga push qiling
> ([`hisobot/week14.md`](hisobot/week14.md) dagi buyruqlar).

---

## 1-variant: PythonAnywhere (tavsiya etiladi)

### 1. Akkaunt
<https://www.pythonanywhere.com/registration/register/beginner/> — bepul **Beginner** akkaunt oching.
Login (masalan `murodjon`) saytingiz manzili bo'ladi: `https://murodjon.pythonanywhere.com`.

### 2. Kodni yuklab olish va o'rnatish
**Dashboard → Consoles → Bash** ni oching va ketma-ket bajaring (`<github-login>` ni o'zingiznikiga almashtiring):

```bash
git clone https://github.com/<github-login>/photostudio.git
cd photostudio

python3.13 -m venv ~/venv-photostudio
source ~/venv-photostudio/bin/activate
pip install -r requirements.txt
```

### 3. `.env` — maxfiy sozlamalar

```bash
cp .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(50))"    # chiqqan kalitni nusxalang
nano .env
```

`.env` ichida (`murodjon` o'rniga o'z PythonAnywhere loginingiz):

```
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<yuqorida chiqqan uzun kalit>
DJANGO_ALLOWED_HOSTS=murodjon.pythonanywhere.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://murodjon.pythonanywhere.com
DJANGO_SERVE_MEDIA=False
DJANGO_SSL_REDIRECT=False
```

Saqlash: `Ctrl+O`, `Enter`, chiqish: `Ctrl+X`.

### 4. Ma'lumotlar bazasi va static fayllar

```bash
python manage.py migrate
python manage.py collectstatic --no-input
python manage.py createsuperuser          # admin akkaunti
python manage.py seed_demo                # demo mijozlar, fotosessiyalar, AI suratlar, teglar
```

### 5. Web ilovani yaratish
**Web → Add a new web app → Next → Manual configuration → Python 3.13 → Next.**

Ochilgan sahifada:

1. **Virtualenv:** `/home/murodjon/venv-photostudio`
2. **Code → WSGI configuration file** havolasini bosing, ichidagini **to'liq o'chirib**, quyidagini yozing va saqlang:

   ```python
   import os
   import sys

   path = '/home/murodjon/photostudio'
   if path not in sys.path:
       sys.path.insert(0, path)

   os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```

3. **Static files** bo'limida ikkita qator qo'shing:

   | URL | Directory |
   |---|---|
   | `/static/` | `/home/murodjon/photostudio/staticfiles` |
   | `/media/` | `/home/murodjon/photostudio/media` |

4. **Security → Force HTTPS** ni yoqing.
5. Yuqoridagi yashil **Reload** tugmasini bosing.

Tayyor: <https://murodjon.pythonanywhere.com> 🎉

### Yangilash (kodni o'zgartirgandan keyin)
Kompyuterda `git push`, keyin PythonAnywhere Bash konsolida:

```bash
cd ~/photostudio && source ~/venv-photostudio/bin/activate
git pull
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --no-input
```

So'ng **Web → Reload**.

### Xato bo'lsa
**Web → Log files → Error log** ni oching — eng pastdagi qator xatoni ko'rsatadi.

| Belgi | Sabab va yechim |
|---|---|
| `DisallowedHost` / 400 Bad Request | `.env` dagi `DJANGO_ALLOWED_HOSTS` loginingizga mos emas |
| `ImproperlyConfigured: ... DJANGO_SECRET_KEY` | `.env` da kalit yozilmagan |
| Sayt CSS'siz, oq | `collectstatic` bajarilmagan yoki `/static/` xaritasi noto'g'ri |
| Hamma sahifa 500, log'da `Missing staticfiles manifest entry` | `collectstatic` `.env` siz (DEBUG=True) ishga tushirilgan — `.env` ni tekshirib, qayta `collectstatic` |
| Rasmlar chiqmaydi | `/media/` xaritasi qo'shilmagan |
| Formani yuborganda 403 CSRF | `DJANGO_CSRF_TRUSTED_ORIGINS` da `https://` bilan to'liq manzil yo'q |

---

## 2-variant: Render (avtomatik)

1. <https://render.com> da GitHub orqali ro'yxatdan o'ting.
2. **New → Blueprint** → `photostudio` repozitoriyasini tanlang.
   Render loyihadagi [`render.yaml`](render.yaml) faylini o'qiydi va hammasini o'zi sozlaydi: Python 3.13,
   [`build.sh`](build.sh) (kutubxonalar, `collectstatic`, `migrate`, `seed_demo`), `gunicorn` server,
   tasodifiy `DJANGO_SECRET_KEY`.
3. So'ralganda `DJANGO_SUPERUSER_PASSWORD` uchun admin parolini kiriting → **Apply**.
4. 3–5 daqiqadan so'ng sayt `https://photostudio-xxxx.onrender.com` manzilida ochiladi.

> ⚠️ Render'ning bepul tarifida disk vaqtinchalik: har yangi deploy'da baza va yuklangan rasmlar o'chadi,
> `seed_demo` demo ma'lumotlarni qayta yaratadi. Taqdimot uchun yetarli; doimiy ishlatish uchun PythonAnywhere'ni tanlang.

---

## Kompyuterda "server rejimi"ni sinash

```bash
export DJANGO_DEBUG=False DJANGO_SECRET_KEY=test-uchun-uzun-kalit-12345678901234567890 \
       DJANGO_SERVE_MEDIA=True DJANGO_SSL_REDIRECT=False
python manage.py collectstatic --no-input --clear     # DEBUG=False da — manifest (staticfiles.json) yaratiladi
gunicorn config.wsgi:application --bind 127.0.0.1:8001
```

Brauzerda <http://127.0.0.1:8001/>. Login bu rejimda ishlamaydi: xavfsiz cookie'lar faqat HTTPS orqali yuboriladi, bu to'g'ri xatti-harakat.
Tugagach terminalda `unset DJANGO_DEBUG DJANGO_SECRET_KEY DJANGO_SERVE_MEDIA DJANGO_SSL_REDIRECT`.

> ⚠️ `collectstatic` ni albatta `DJANGO_DEBUG=False` bilan ishga tushiring. Aks holda `staticfiles.json`
> yaratilmaydi va sayt **500** xato beradi. Serverda bu `.env` orqali avtomatik bo'ladi.

Sinov natijasi: [`hisobot/terminal/deploy_sinov.txt`](hisobot/terminal/deploy_sinov.txt)

## Nima qilindi (texnik)

| Fayl | O'zgarish |
|---|---|
| [`config/env.py`](config/env.py) | `.env` faylni o'qiydigan kichik yordamchi (qo'shimcha kutubxonasiz) |
| [`config/settings.py`](config/settings.py) | `DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` — `.env` dan; `DEBUG=False` da: WhiteNoise, siqilgan static fayllar, HTTPS cookie'lar, HSTS, SMTP email |
| [`config/urls.py`](config/urls.py) | `DJANGO_SERVE_MEDIA=True` bo'lsa media fayllarni Django beradi |
| [`.env.example`](.env.example) | `.env` namunasi |
| [`requirements.txt`](requirements.txt) | `whitenoise`, `gunicorn` qo'shildi |
| [`render.yaml`](render.yaml), [`build.sh`](build.sh) | Render uchun avtomatik sozlama |
