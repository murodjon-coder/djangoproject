from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

UserModel = get_user_model()


class CaseInsensitiveModelBackend(ModelBackend):
    """Login (username) katta-kichik harfga va chetdagi probellarga qaramaydi: "Murodjon" == "murodjon".

    Parol esa avvalgidek aniq (katta-kichik harfga sezgir) tekshiriladi.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return None
        username = username.strip()
        users = UserModel._default_manager.filter(**{f'{UserModel.USERNAME_FIELD}__iexact': username})
        # Agar bir xil harflardan iborat bir nechta login bo'lsa, aynan mos kelganini tanlaymiz
        user = users.filter(**{UserModel.USERNAME_FIELD: username}).first() or users.first()
        if user is None:
            # Vaqt bo'yicha hujumlarga qarshi: foydalanuvchi bo'lmasa ham parol xeshlanadi
            UserModel().set_password(password)
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
