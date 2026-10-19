from django.db import models


class Photo(models.Model):
    """Fotostudiyada olingan surat (3-hafta)."""

    title = models.CharField("Nomi", max_length=200)
    photographer = models.CharField("Fotograf", max_length=100)
    date = models.DateField("Suratga olingan sana")

    class Meta:
        verbose_name = "Surat"
        verbose_name_plural = "Suratlar"
        ordering = ['-date', '-id']
