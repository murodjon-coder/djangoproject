# 9-hafta — Django Middleware

**Holat:** ✅ bajarildi · **Commit:** `014026d`

---

## Nazariy qism

### 1-topshiriq — Middleware nima

Middleware — har bir so'rov view'ga yetib borishidan **oldin** va javob brauzerga qaytishidan **keyin** ishlaydigan oraliq qatlam.
So'rov `MIDDLEWARE` ro'yxati bo'yicha yuqoridan pastga, javob esa teskari tartibda, pastdan yuqoriga o'tadi (piyozning qatlamlari kabi).
Undan barcha sahifalarga taalluqli umumiy ishlar uchun foydalaniladi: xavfsizlik, session, login, log yozish, vaqtni o'lchash.

### 2-topshiriq — Built-in middleware: `CsrfViewMiddleware`

`CsrfViewMiddleware` saytni **CSRF** (Cross-Site Request Forgery) hujumidan himoya qiladi: boshqa sayt foydalanuvchi nomidan bizning saytga yashirincha POST so'rov yubora olmaydi.
U har bir POST so'rovda formadagi `{% csrf_token %}` qiymatini cookie'dagi token bilan solishtiradi. Mos kelmasa, **403 Forbidden** qaytaradi.
Shuning uchun loyihadagi har bir POST formada `{% csrf_token %}` bor.

---

## Amaliy qism

### 3-topshiriq — MIDDLEWARE ro'yxatini o'rganish

[`config/settings.py:58`](../config/settings.py) — har bir qatorga izoh yozildi:

| Middleware | Vazifasi |
|---|---|
| `SecurityMiddleware` | Xavfsizlik sarlavhalari (HTTPS ga yo'naltirish, HSTS va h.k.) |
| `SessionMiddleware` | `request.session` ni yoqadi, login holati shu yerda saqlanadi |
| `CommonMiddleware` | URL oxiriga `/` qo'shish (APPEND_SLASH) va boshqa umumiy ishlar |
| `CsrfViewMiddleware` | POST formalarni CSRF hujumidan himoya qiladi |
| `AuthenticationMiddleware` | Session asosida `request.user` ni aniqlaydi |
| `MessageMiddleware` | Bir martalik xabarlar (`messages.success(...)`) |
| `XFrameOptionsMiddleware` | Saytni boshqa sayt `<iframe>` ichida ochishini taqiqlaydi (clickjacking) |
| **`RequestTimingMiddleware`** | **Mening middleware'im** — so'rov manzili va vaqtini chiqaradi |

### 4-topshiriq — Custom middleware

[`photostudio/middleware.py`](../photostudio/middleware.py):

```python
import time


class RequestTimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.perf_counter()                      # view'dan OLDIN
        response = self.get_response(request)
        duration_ms = (time.perf_counter() - start) * 1000   # view'dan KEYIN
        print(f"[Middleware] {request.method} {request.path} -> {response.status_code} ({duration_ms:.2f} ms)")
        return response
```

### 5-topshiriq — Middleware'ni ulash

[`config/settings.py:74`](../config/settings.py):

```python
MIDDLEWARE = [
    ...
    # 9-hafta: o'zimning middleware — so'rov manzili va vaqtini konsolga chiqaradi
    'photostudio.middleware.RequestTimingMiddleware',
]
```

Middleware'ning ishlashi avtomatik test bilan ham tekshirilgan: [`tests/test_middleware.py`](../photostudio/tests/test_middleware.py).

---

## Darsda qanday ko'rsatish

1. Terminalda `python manage.py runserver` ishlab tursin.
2. Brauzerda bir nechta sahifani oching: `/`, `/photos/`, `/accounts/login/`, `/admin/`.
3. Terminalga qarang — har bir so'rov uchun `[Middleware] ...` qatori chiqadi.

## Natija — terminal chiqishi

[`terminal/week09_middleware_terminal.txt`](terminal/week09_middleware_terminal.txt):

```
[Middleware] GET /photos/ -> 302 (1.97 ms)
[19/Oct/2026 19:32:35] "GET /photos/ HTTP/1.1" 302 0
[Middleware] GET /accounts/login/ -> 200 (4.52 ms)
[19/Oct/2026 19:32:35] "GET /accounts/login/ HTTP/1.1" 200 1633
[Middleware] GET /photos/1/ -> 302 (0.16 ms)
[19/Oct/2026 19:32:35] "GET /photos/1/ HTTP/1.1" 302 0
[Middleware] GET /accounts/register/ -> 200 (4.84 ms)
[19/Oct/2026 19:32:35] "GET /accounts/register/ HTTP/1.1" 200 2338
[Middleware] GET /admin/login/ -> 200 (6.10 ms)
[19/Oct/2026 19:32:35] "GET /admin/login/ HTTP/1.1" 200 4302
```

`302` — login qilinmagani uchun login sahifasiga yo'naltirildi (8-hafta himoyasi), `200` — sahifa ochildi.
