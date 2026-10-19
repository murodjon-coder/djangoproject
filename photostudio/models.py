from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Category(models.Model):
    """Surat turi: portret, to'y, oilaviy va h.k. (7-hafta)."""

    name = models.CharField("Nomi", max_length=100, unique=True)

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
        ordering = ['name']

    def __str__(self):
        return self.name


class Client(models.Model):
    """Fotostudiya mijozi (14-hafta)."""

    phone_validator = RegexValidator(
        regex=r'^\+?\d[\d\s-]{6,18}\d$',
        message="Telefon raqam noto'g'ri. Masalan: +998 90 123 45 67",
    )

    full_name = models.CharField("F.I.Sh.", max_length=150)
    phone = models.CharField("Telefon", max_length=20, validators=[phone_validator])
    email = models.EmailField("Email", blank=True)
    created_at = models.DateTimeField("Qo'shilgan vaqt", auto_now_add=True)

    class Meta:
        verbose_name = "Mijoz"
        verbose_name_plural = "Mijozlar"
        ordering = ['full_name']

    def __str__(self):
        return self.full_name

    def get_absolute_url(self):
        return reverse('photostudio:client_detail', args=[self.pk])


class Session(models.Model):
    """Fotosessiya — mijoz bilan belgilangan suratga olish vaqti (14-hafta)."""

    class Status(models.TextChoices):
        PLANNED = 'planned', "Rejalashtirilgan"
        DONE = 'done', "Bajarilgan"
        CANCELLED = 'cancelled', "Bekor qilingan"

    # One-to-Many: bitta mijozning ko'p fotosessiyasi bo'lishi mumkin
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='sessions',
        verbose_name="Mijoz",
    )
    photographer = models.CharField("Fotograf", max_length=100)
    scheduled_at = models.DateTimeField("Sana va vaqt")
    duration_minutes = models.PositiveSmallIntegerField(
        "Davomiyligi (daqiqa)", default=60, validators=[MinValueValidator(15)],
    )
    location = models.CharField("Joy", max_length=150, default="Asosiy studiya")
    price = models.DecimalField(
        "Narxi (so'm)", max_digits=12, decimal_places=0, validators=[MinValueValidator(0)],
    )
    status = models.CharField("Holati", max_length=10, choices=Status.choices, default=Status.PLANNED)
    notes = models.TextField("Izoh", blank=True)

    class Meta:
        verbose_name = "Fotosessiya"
        verbose_name_plural = "Fotosessiyalar"
        ordering = ['-scheduled_at']

    def __str__(self):
        return f"{self.client} — {timezone.localtime(self.scheduled_at):%d.%m.%Y %H:%M}"

    def get_absolute_url(self):
        return reverse('photostudio:session_detail', args=[self.pk])


class Photo(models.Model):
    """Fotostudiyada olingan surat (3-hafta)."""

    title = models.CharField("Nomi", max_length=200)
    photographer = models.CharField("Fotograf", max_length=100)
    date = models.DateField("Suratga olingan sana")
    # 7-hafta: One-to-Many — bitta kategoriyada ko'p surat bo'ladi
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='photos',
        verbose_name="Kategoriya",
    )
    # 11-hafta: rasm fayli media/photos/YYYY/MM/ papkasiga saqlanadi
    image = models.ImageField("Rasm", upload_to='photos/%Y/%m/', blank=True)
    # 14-hafta: surat qaysi fotosessiyada olingani
    session = models.ForeignKey(
        Session,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='photos',
        verbose_name="Fotosessiya",
    )

    class Meta:
        verbose_name = "Surat"
        verbose_name_plural = "Suratlar"
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.title} ({self.photographer})"

    def get_absolute_url(self):
        return reverse('photostudio:photo_detail', args=[self.pk])
