import time


class RequestTimingMiddleware:
    """9-hafta: har bir so'rov manzili va bajarilish vaqtini konsolga chiqaradi."""

    def __init__(self, get_response):
        # Server ishga tushganda bir marta chaqiriladi
        self.get_response = get_response

    def __call__(self, request):
        # 1) View'dan OLDIN: vaqtni belgilab olamiz
        start = time.perf_counter()

        # 2) So'rovni keyingi middleware/view'ga uzatamiz
        response = self.get_response(request)

        # 3) View'dan KEYIN: qancha vaqt ketganini hisoblaymiz
        duration_ms = (time.perf_counter() - start) * 1000
        print(f"[Middleware] {request.method} {request.path} -> {response.status_code} ({duration_ms:.2f} ms)")
        return response
