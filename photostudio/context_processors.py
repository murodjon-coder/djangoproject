from .models import BookingRequest
from .roles import get_client_profile, is_employee


def roles(request):
    """Har bir template'da rolga qarab menyu va tugmalarni ko'rsatish uchun."""
    employee = is_employee(request.user)
    return {
        'is_employee': employee,
        'client_profile': get_client_profile(request.user),
        # Xodimlar menyusida yangi bron so'rovlari soni (belgi)
        'new_booking_count': BookingRequest.objects.filter(status=BookingRequest.Status.NEW).count() if employee else 0,
    }
