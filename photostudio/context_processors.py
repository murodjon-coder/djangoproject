from .roles import get_client_profile, is_employee


def roles(request):
    """Har bir template'da rolga qarab menyu va tugmalarni ko'rsatish uchun."""
    return {
        'is_employee': is_employee(request.user),
        'client_profile': get_client_profile(request.user),
    }
