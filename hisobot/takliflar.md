# Loyihani rivojlantirish bo'yicha takliflar

> ✅ **Bajarildi:** qidiruv + filtr + sahifalash, teglar (Many-to-Many), mijoz kabineti (One-to-One), statistika paneli — [qoshimcha.md](qoshimcha.md).

Har bir taklifda: **nima qo'shiladi**, **foydasi**, **qaysi Django mavzusini mustahkamlaydi**, **qiyinligi** (⭐ — oson, ⭐⭐⭐ — qiyin) va taxminiy vaqt.
Istalganini tanlang — men qo'shib beraman.

---

## 🏆 Eng tavsiya etiladigan 5 ta (taqdimotda eng ko'p taassurot qoldiradi)

| # | Taklif | Nima uchun aynan shu | Qiyinlik | Vaqt |
|---|---|---|---|---|
| 1 | **Galereyada qidiruv va kategoriya filtri** | Eng ko'p ishlatiladigan funksiya; `filter()`, `Q` obyektlari, GET parametrlari — 5-6-hafta mavzulari | ⭐ | 1 soat |
| 2 | **Mijoz shaxsiy kabineti** — mijoz login qilib, faqat o'z fotosessiyalari va suratlarini ko'radi, yuklab oladi | Haqiqiy fotostudiyada eng kerakli narsa; **One-to-One** (`Client.user`) va rollar — 7- va 8-hafta | ⭐⭐ | 3 soat |
| 3 | **Statistika paneli (dashboard)** — oylik daromad grafigi, eng faol fotograf, kategoriya bo'yicha suratlar | `annotate`, `Sum`, `Count`, `TruncMonth` — ORM'ni chuqur ko'rsatadi | ⭐⭐ | 2–3 soat |
| 4 | **Onlayn bron so'rovi** — mehmon saytdan "Fotosessiyaga yozilish" formasini to'ldiradi, admin tasdiqlaydi | Saytni "ichki tizim"dan "real biznes"ga aylantiradi; yangi model + forma + holatlar | ⭐⭐ | 2–3 soat |
| 5 | **Internetga joylash (deploy)** — PythonAnywhere yoki Render, `DEBUG=False`, `.env` | O'qituvchi va do'stlar telefonidan ochib ko'ra oladi; `SECRET_KEY` ni koddan chiqarish | ⭐⭐ | 2 soat |

---

## 📸 Galereya va suratlar

| Taklif | Tavsif | Mavzu | Qiyinlik |
|---|---|---|---|
| Sahifalash (pagination) | Galereyada 12 tadan surat, "Keyingi sahifa" | `Paginator`, `ListView.paginate_by` | ⭐ |
| Teglar (Tag) | Bir suratga bir nechta teg: "oq fon", "tashqi", "kechqurun" | **Many-to-Many** — 7-haftadagi uchinchi bog'lanish turini amalda ko'rsatadi | ⭐ |
| Bir nechta rasmni birdan yuklash | Fotosessiya sahifasidan 20 ta rasmni bir yo'la yuklash | `request.FILES.getlist()`, multiple file input | ⭐⭐ |
| Avtomatik kichik rasm (thumbnail) | Yuklanganda Pillow bilan 600px nusxa yaratish — galereya tezlashadi | `save()` ni qayta yozish yoki **signals** | ⭐⭐ |
| EXIF ma'lumotlari | Kamera modeli, diafragma, ISO, ekspozitsiyani rasmdan o'qib ko'rsatish | Pillow, model maydonlari | ⭐⭐ |
| Lightbox | Suratni bosganda to'liq ekranda ochish, ← → bilan varaqlash | Kichik JavaScript, static fayllar | ⭐ |
| "Yoqdi" (like) va eng mashhur suratlar | Foydalanuvchi suratni belgilaydi | M2M (`User` ↔ `Photo`), `annotate(Count)` | ⭐⭐ |

## 👥 Mijozlar va fotosessiyalar

| Taklif | Tavsif | Mavzu | Qiyinlik |
|---|---|---|---|
| Fotograf modeli | Hozir `photographer` — oddiy matn. Alohida `Photographer` modeli (rasm, telefon, tajriba) va profil sahifasi | ForeignKey + **data migration** (`RunPython`) — eski matnni yangi modelga ko'chirish | ⭐⭐ |
| Xizmat paketlari | "Portret — 60 daqiqa — 500 000", "To'y — 4 soat — 3 000 000"; sessiyada paket tanlansa narx avtomatik | Yangi model, forma `initial`/`clean` | ⭐ |
| Kalendar ko'rinishi | Oylik kalendar, har kunda fotosessiyalar; band vaqtlar ko'rinadi | Python `calendar`, sana filtrlari | ⭐⭐ |
| Vaqt to'qnashuvini tekshirish | Bir fotograf bir vaqtda ikki sessiyaga yozilmasligi | `SessionForm.clean()` da so'rov | ⭐ |
| To'lov holati | "To'langan / qisman / to'lanmagan", avans summasi | Model maydoni, choices, statistika | ⭐ |
| Mijoz sharhlari | Sessiyadan keyin 1–5 yulduz va izoh | Yangi model, OneToOne (`Review.session`) | ⭐ |
| Excel/CSV eksport | Mijozlar yoki oylik hisobotni yuklab olish | `HttpResponse` + `csv` moduli | ⭐ |

## 🔔 Xabarnomalar

| Taklif | Tavsif | Mavzu | Qiyinlik |
|---|---|---|---|
| Email eslatma | Fotosessiyadan 1 kun oldin mijozga xat (hozircha konsolga chiqadi) | `send_mail`, management command, Django 6 **tasks** | ⭐⭐ |
| Telegram bot xabari | Yangi bron so'rovi kelsa adminning Telegramiga xabar | `requests`, Bot API, `.env` da token | ⭐⭐ |

## 🔌 API

| Taklif | Tavsif | Mavzu | Qiyinlik |
|---|---|---|---|
| Client va Session uchun API | `/api/clients/`, `/api/sessions/` (faqat login qilganlarga) | ViewSet, permissions | ⭐ |
| API'da filtr va qidiruv | `/api/photostudio/?category=2&search=portret` | `django-filter`, `SearchFilter` | ⭐ |
| Token autentifikatsiya | Mobil ilova uchun token bilan kirish | `TokenAuthentication` | ⭐⭐ |
| Swagger hujjatlari | `/api/docs/` — barcha endpointlar chiroyli ro'yxatda | `drf-spectacular` | ⭐ |

## 🎨 Interfeys

| Taklif | Tavsif | Qiyinlik |
|---|---|---|
| Yorug' / qorong'i mavzu tugmasi | Foydalanuvchi tanlovi `localStorage` da saqlanadi | ⭐ |
| Ko'p tillilik (o'zbek / rus / ingliz) | `gettext`, `LocaleMiddleware`, til tanlash menyusi — middleware mavzusiga ham bog'lanadi | ⭐⭐ |
| Shriftlarni loyiha ichiga olish | Hozir Google Fonts internetdan yuklanadi; darsda internet bo'lmasa ham bir xil ko'rinishi uchun | ⭐ |

## 🛠 Sifat va texnik

| Taklif | Tavsif | Qiyinlik |
|---|---|---|
| `SECRET_KEY` va `DEBUG` ni `.env` ga chiqarish | GitHub'da maxfiy kalit ochiq turmasligi uchun (hozir `settings.py` da) | ⭐ |
| Test qamrovi (coverage) | `pytest --cov` — kodning necha foizi test qilingani | ⭐ |
| GitHub Actions | Har push'da testlar avtomatik ishlaydi, GitHub'da yashil ✔ belgisi | ⭐⭐ |
| django-debug-toolbar | `select_related` ta'sirini (SQL so'rovlar sonini) brauzerda jonli ko'rsatish — 7-hafta taqdimoti uchun zo'r | ⭐ |
| PostgreSQL | SQLite o'rniga haqiqiy server bazasi (deploy bilan birga) | ⭐⭐ |

---

## Mening tavsiyam — tartib bilan

1. **Qidiruv + filtr + pagination** — tez, darhol foydali.
2. **Teglar (Many-to-Many)** — 7-hafta nazariyasidagi uchala bog'lanish turi ham loyihada bo'ladi.
3. **Mijoz kabineti (One-to-One)** — loyihaga real ma'no beradi.
4. **Dashboard** — taqdimotda eng ko'zga tashlanadigan sahifa.
5. **`.env` + deploy** — loyiha internetda, havola bilan ko'rsatish mumkin.

Qaysilarini qo'shishni xohlasangiz, raqamini yozing.
