# Haftalik hisobotlar — Fotostudiya (19-variant)

Kurs: **Introduction to Django** · O'qituvchi: Erkaboy Qadamboyev · Talaba: Murodjon

Har bir hisobotda: **nazariy javoblar** (2–3 gap), **amaliy qism** (qaysi faylning qaysi qatorida nima qilingani),
**darsda qanday ko'rsatish** (qadamma-qadam) va **natija** (skrinshotlar yoki terminal chiqishi).

| Hafta | Mavzu | Asosiy natija | Commit |
|---|---|---|---|
| 1 | Loyiha yaratish | `django-admin startproject` (siz qilgansiz) | `2109946` |
| [2](week02.md) | Loyiha strukturasi | `photostudio` ilovasi, `config/` sozlamalar | `4776b76` |
| [3](week03.md) | Modellar | `Photo` modeli, migratsiya, admin + 2 yozuv | `d84e81f` |
| [4](week04.md) | Views va Templates | FBV `photo_list` + `PhotoListView` | `d0501e6` |
| [5](week05.md) | URLs va Routing | `photos/<int:id>/`, `{% url %}` | `90db2ac` |
| [6](week06.md) | Formalar | `PhotoForm`, `is_valid()`, xato xabarlari | `1dcfb61` |
| [7](week07.md) | Bog'lanishlar va optimizatsiya | `Category` FK, `__str__`, `select_related` (4→1 so'rov) | `adf43fe` |
| [8](week08.md) | Authentication | ro'yxatdan o'tish, login/logout, `@login_required` | `22166f2` |
| [9](week09.md) | Middleware | `RequestTimingMiddleware` | `014026d` |
| [10](week10.md) | Static fayllar | CSS, surat, video, JDU logotipi | `250cb7c` |
| [11](week11.md) | File Uploads | `ImageField`, `request.FILES`, MEDIA | `d0b5371` |
| [12](week12.md) | DRF | `PhotoSerializer`, `PhotoViewSet`, `/api/photostudio/` | `1dcf208` |
| [13](week13.md) | Testlash | pytest — **74 passed** | `1b20588` |
| [14](week14.md) | Kichik loyiha | Photo + Client + Session, to'liq CRUD, rollar, git branch | `9294fa8`, `ef328b2` |
| [15](week15.md) | Yakuniy loyiha | talablar ro'yxati, taqdimot ssenariysi, savol-javoblar | — |

📌 Kursdan keyin qo'shilgan funksiyalar (qidiruv, teglar, mijoz kabineti, statistika, onlayn bron, deploy, AI suratlar): [**qoshimcha.md**](qoshimcha.md)

📌 Internetga joylash: [**DEPLOY.md**](../DEPLOY.md)

📌 Loyihani rivojlantirish g'oyalari: [**takliflar.md**](takliflar.md)

## ⚠️ Sizda qolgan ishlar

1. **10-hafta:** `static/images/men.jpg` (shaxsiy surat) va `static/images/jdu_logo.png` (JDU logotipi) hozir **vaqtinchalik rasmlar** — o'zingiznikiga almashtiring (nomlari bir xil bo'lsin).
2. **14/15-hafta:** GitHub'da repozitoriy yaratib, `git push` qiling — buyruqlar [`week14.md`](week14.md) da.

## Loyihani ishga tushirish

```bash
cd ~/Django/photostudio
source ../photostudio_venv/bin/activate
python manage.py runserver
```

Brauzer: <http://127.0.0.1:8000/>

| Login | Parol | Roli |
|---|---|---|
| `admin` | `Studio2026!` | administrator (admin panel, o'chirish) |
| `murodjon` | `Fotostudiya2026` | xodim (`Xodimlar` guruhi) — o'chira olmaydi |
| `aziza` | `Mijoz2026` | mijoz — faqat o'z kabineti |

Testlar: `pytest` · Demo ma'lumot: `python manage.py seed_demo`

## Papkalar

- `screenshots/` — barcha skrinshotlar (fayl nomi `weekNN_...png` — qaysi haftaga tegishli ekani)
- `terminal/` — terminal chiqishlari (migratsiya, middleware log, select_related o'lchovi, API, pytest)

> Hisobotlardagi qator raqamlari (`views.py:60` kabi) loyihaning **yakuniy** holatiga tegishli.
> Biror haftadagi holatni ko'rish uchun: `git show <commit> --stat` yoki `git checkout <commit>` (qaytish: `git checkout main`).
