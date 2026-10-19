"""Foydalanuvchi rollari.

- Mehmon         — tizimga kirmagan.
- Mijoz          — oddiy ro'yxatdan o'tgan foydalanuvchi; faqat o'z kabinetini ko'radi.
- Xodim          — "Xodimlar" guruhidagi foydalanuvchi; galereya, mijozlar, fotosessiyalar, statistika.
- Administrator  — is_staff; xodim qila oladigan hamma narsa + o'chirish va admin panel.
"""
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied

EMPLOYEE_GROUP = 'Xodimlar'


def is_employee(user):
    if not user.is_authenticated:
        return False
    if user.is_staff:
        return True
    # Bir so'rov ichida guruhni qayta-qayta tekshirmaslik uchun natijani saqlab qo'yamiz
    if not hasattr(user, '_is_employee'):
        user._is_employee = user.groups.filter(name=EMPLOYEE_GROUP).exists()
    return user._is_employee


def get_client_profile(user):
    """Foydalanuvchiga bog'langan mijoz profili (One-to-One) yoki None."""
    if not user.is_authenticated:
        return None
    return getattr(user, 'client_profile', None)


def employee_required(view_func):
    """Faqat xodim va administratorlar uchun (mehmon → login sahifasi, mijoz → 403)."""

    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not is_employee(request.user):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


def staff_required(view_func):
    """O'chirish faqat administratorga (is_staff) ruxsat etiladi, boshqalarga 403."""

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


class EmployeeRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return is_employee(self.request.user)


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """O'chirish faqat administratorga (is_staff) ruxsat etiladi (14-hafta: foydalanuvchi rollari)."""

    def test_func(self):
        return self.request.user.is_staff
