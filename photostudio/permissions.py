from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import BasePermission

from .roles import is_employee


class IsEmployee(BasePermission):
    """API faqat fotostudiya xodimlari va administratorlar uchun.

    Suratlarda mijozlarning shaxsiy fotosessiyalari bor — ularni begona odam ko'rmasligi kerak.
    """

    message = "Bu API faqat fotostudiya xodimlari uchun."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            # DRF'ning inglizcha "Authentication credentials were not provided" o'rniga
            raise NotAuthenticated("Bu API faqat fotostudiya xodimlari uchun. Avval xodim akkaunti bilan tizimga kiring.")
        return is_employee(request.user)
