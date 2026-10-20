# 14-hafta — Kichik loyiha yaratish

**Holat:** ✅ bajarildi (GitHub'ga push qilish bundan mustasno, pastga qarang) · **Commit:** `9294fa8` (`week14-kichik-loyiha` branch'ida) → `main` ga merge: `ef328b2`

Variant 19: **Fotostudiya boshqaruvi — Photo, Client, Session**.

---

## Nazariy qism

### 1-topshiriq — Git branch

Branch — loyihaning alohida "nusxa yo'li": asosiy koddagi (`main`) ishlaydigan versiyani buzmasdan yangi funksiya ustida ishlash imkonini beradi.
Ish tayyor va tekshirilgan bo'lgach, branch `main` ga **merge** qilinadi. Bir necha dasturchi esa bir vaqtda turli branch'larda bir-biriga xalaqit bermay ishlay oladi.
Men 14-hafta ishini `week14-kichik-loyiha` branch'ida qildim va keyin `main` ga birlashtirdim.

### 2-topshiriq — `.gitignore`

`.gitignore` — git kuzatmasligi va GitHub'ga yuklamasligi kerak bo'lgan fayllar ro'yxati.
U bo'lmasa, quyidagilar ham yuklanib ketadi: `venv/` (yuzlab MB kutubxona), `__pycache__/` (keraksiz fayllar), `db.sqlite3` (foydalanuvchilar va parol xeshlari, mijozlarning telefon raqamlari), `media/` (yuklangan rasmlar), `.env` (maxfiy kalitlar).
Natijada repozitoriy og'irlashadi, maxfiy ma'lumot oshkor bo'ladi va boshqalar bilan ishlaganda keraksiz konfliktlar chiqadi.

---

## Amaliy qism

### 3-topshiriq — Reja va Git

**Reja** — [`README.md`](../README.md) ning "1. Reja" bo'limida: modellar jadvali, sahifalar va URL'lar, foydalanuvchi rollari.

**Foydalanuvchi rollari:**

| Rol | Nima qila oladi |
|---|---|
| Mehmon | bosh sahifa, "Men haqimda", API'ni o'qish, ro'yxatdan o'tish |
| Xodim (ro'yxatdan o'tgan) | suratlar, mijozlar, fotosessiyalarni ko'rish / qo'shish / tahrirlash |
| Administrator (`is_staff`) | + o'chirish va admin panel |

> Keyinchalik mijoz kabineti qo'shilgach, **Mijoz** roli alohida ajratildi — [qoshimcha.md](qoshimcha.md#rollar-yangilangan).

**Git:**

```bash
git init -b main
# .gitignore yaratildi (Python, venv, db.sqlite3, media/, staticfiles/, .pytest_cache/, .env, .DS_Store)
git add -A
git commit -m "Week 1: Django loyihasi yaratildi (django-admin startproject)"
...                                  # har bir hafta — alohida commit
git switch -c week14-kichik-loyiha   # 14-hafta — alohida branch
git commit -m "Week 14: ..."
git switch main
git merge --no-ff week14-kichik-loyiha
```

[`.gitignore`](../.gitignore) — loyiha ildizida.

Commit tarixi (`git log --oneline --graph`):

```
*   ef328b2 Merge branch 'week14-kichik-loyiha': fotostudiya boshqaruv tizimi
|\
| * 9294fa8 Week 14: Client va Session modellari, to'liq CRUD, foydalanuvchi rollari, seed_demo va README rejasi
|/
* 1b20588 Week 13: pytest + pytest-django — pytest.ini, model/view/API/middleware testlari (17 ta)
* 1dcf208 Week 12: DRF — PhotoSerializer, PhotoViewSet va /api/photostudio/ endpoint
* d0b5371 Week 11: Photo.image (ImageField), multipart forma, request.FILES va MEDIA sozlamalari
* 250cb7c Week 10: static fayllar — STATICFILES_DIRS, CSS, shaxsiy surat, video va JDU logotipi
* 014026d Week 9: RequestTimingMiddleware (request.path + bajarilish vaqti) va MIDDLEWARE izohlari
* 22166f2 Week 8: ro'yxatdan o'tish (UserCreationForm), LoginView/LogoutView va @login_required
* adf43fe Week 7: Category modeli (ForeignKey), __str__ metodi va select_related
* 1dcfb61 Week 6: PhotoForm (forms.py), photo_create view (GET/POST, is_valid) va xato xabarlari
* 90db2ac Week 5: photo_detail view, <int:id> dinamik URL va {% url %} havolalari
* d0501e6 Week 4: photo_list (FBV), PhotoListView (ListView) va ro'yxat template'i
* d84e81f Week 3: Photo modeli (title, photographer, date), migratsiya va admin
* 4776b76 Week 2: photostudio ilovasi yaratildi va INSTALLED_APPS ga ulandi
* 2109946 Week 1: Django loyihasi yaratildi (django-admin startproject)
```

> ⚠️ **SIZ BAJARISHINGIZ KERAK — GitHub'ga push.** Buni sizning GitHub akkauntingizsiz qilib bo'lmaydi:
> 1. <https://github.com/new> da yangi repozitoriy yarating (masalan `photostudio`). README, .gitignore **qo'shmang** — ular loyihada bor.
> 2. Terminalda:
>    ```bash
>    cd ~/Django/photostudio
>    git remote add origin https://github.com/<github-login>/photostudio.git
>    git push -u origin main
>    git push origin week14-kichik-loyiha
>    ```
> 3. Parol so'ralsa, GitHub paroli emas, **Personal Access Token** kiriting (GitHub → Settings → Developer settings → Tokens).

### 4-topshiriq — Asosiy funksionallikni birlashtirish

**Yangi modellar** — [`photostudio/models.py`](../photostudio/models.py):

```
Client 1 ──── * Session 1 ──── * Photo * ──── 1 Category
```

- `Client` (`:47`) — `full_name`, `phone` (RegexValidator bilan), `email`, `created_at`
- `Session` (`:81`) — `client` (FK), `photographer`, `scheduled_at`, `duration_minutes`, `location`, `price`, `status` (TextChoices: Rejalashtirilgan / Bajarilgan / Bekor qilingan), `notes`
- `Photo.session` (`:138`) — surat qaysi fotosessiyada olingani

Migratsiya: [`0004_client_session_photo_session.py`](../photostudio/migrations/0004_client_session_photo_session.py)

**To'liq CRUD:**

| | Ro'yxat | Detail | Qo'shish | Tahrirlash | O'chirish |
|---|---|---|---|---|---|
| Surat | `photo_list` (FBV), `PhotoListView` | `photo_detail` | `photo_create` | `photo_update` | `photo_delete` (admin) |
| Mijoz | `ClientListView` | `ClientDetailView` | `ClientCreateView` | `ClientUpdateView` | `ClientDeleteView` (admin) |
| Fotosessiya | `SessionListView` (+ holat bo'yicha saralash) | `SessionDetailView` | `SessionCreateView` | `SessionUpdateView` | `SessionDeleteView` (admin) |

- View'lar: [`photostudio/views.py`](../photostudio/views.py); URL'lar: [`photostudio/urls.py`](../photostudio/urls.py)
- Formalar: `PhotoForm`, `ClientForm`, `SessionForm` — [`photostudio/forms.py`](../photostudio/forms.py). `SessionForm.clean()` o'tib ketgan vaqtga "rejalashtirilgan" sessiya qo'yishga yo'l qo'ymaydi.
- Template'lar: umumiy `form.html` va `confirm_delete.html`; `home.html`, `client_*.html`, `session_*.html`, `403.html`, `404.html`.
- Admin: barcha 4 model, `Client` ichida sessiyalar (inline), `Session` ichida suratlar (inline) — [`photostudio/admin.py`](../photostudio/admin.py).
- Demo ma'lumot: `python manage.py seed_demo` — [`management/commands/seed_demo.py`](../photostudio/management/commands/seed_demo.py).

### 5-topshiriq — Autentifikatsiya

8-haftada qilingan ro'yxatdan o'tish / login / logout to'liq ishlaydi. `@login_required` va `LoginRequiredMixin` bilan barcha surat, mijoz va fotosessiya sahifalari himoyalangan.
Qo'shimcha: o'chirish faqat administratorga ruxsat (`staff_required` dekoratori, `StaffRequiredMixin`). Oddiy foydalanuvchi o'chirish tugmasini ko'rmaydi, URL'ni qo'lda ochsa **403**.

---

## Darsda qanday ko'rsatish

1. Chiqib turgan holda bosh sahifa `/` (mehmon ko'rinishi).
2. `admin` bilan kiring → "Mijozlar" → "+ Mijoz qo'shish" (avval noto'g'ri telefon bilan — xato) → saqlang.
3. Mijoz sahifasida "+ Fotosessiya" → sessiya yarating → sessiya sahifasida "+ Surat qo'shish" → rasm yuklang.
4. Suratni "Tahrirlash", keyin "O'chirish" (tasdiqlash sahifasi).
5. "Fotosessiyalar" → "Rejalashtirilgan" bo'yicha saralash.
6. Chiqib, `murodjon` bilan kiring → o'chirish tugmasi yo'q; `/photos/1/delete/` → 403.
7. Terminalda `git log --oneline --graph` va GitHub sahifasini ko'rsating.

## Natija

| | |
|---|---|
| ![](screenshots/week14_bosh_sahifa_mehmon.png) | ![](screenshots/week14_bosh_sahifa_login.png) |
| ![](screenshots/week14_mijozlar_royxati.png) | ![](screenshots/week14_mijoz_detail.png) |
| ![](screenshots/week14_mijoz_forma_xato.png) | ![](screenshots/week14_mijoz_qoshildi.png) |
| ![](screenshots/week14_fotosessiya_forma.png) | ![](screenshots/week14_fotosessiya_detail.png) |
| ![](screenshots/week14_fotosessiyalar_royxati.png) | ![](screenshots/week14_fotosessiyalar_saralash.png) |
| ![](screenshots/week14_surat_detail_sessiya_bilan.png) | ![](screenshots/week14_surat_tahrirlash.png) |
| ![](screenshots/week14_ochirish_tasdiqlash.png) | ![](screenshots/week14_ochirildi.png) |
| ![](screenshots/week14_oddiy_user_ochirish_tugmasi_yoq.png) | ![](screenshots/week14_oddiy_user_403.png) |
