from django import forms
from django.utils import timezone

from .models import Photo


class PhotoForm(forms.ModelForm):
    """6-hafta: Photo modeli maydonlariga mos forma."""

    class Meta:
        model = Photo
        fields = ['title', 'photographer', 'date', 'category']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def clean_title(self):
        title = self.cleaned_data['title'].strip()
        if len(title) < 3:
            raise forms.ValidationError("Nomi kamida 3 ta belgidan iborat bo'lishi kerak.")
        return title

    def clean_date(self):
        date = self.cleaned_data['date']
        if date > timezone.localdate():
            raise forms.ValidationError("Suratga olingan sana kelajakda bo'lishi mumkin emas.")
        return date
