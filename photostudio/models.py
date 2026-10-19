from django.db import models


class Category(models.Model):
    """Surat turi: portret, to'y, oilaviy va h.k. (7-hafta)."""

    name = models.CharField("Nomi", max_length=100, unique=True)

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
        ordering = ['name']

    def __str__(self):
        return self.name


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

    class Meta:
        verbose_name = "Surat"
        verbose_name_plural = "Suratlar"
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.title} ({self.photographer})"
