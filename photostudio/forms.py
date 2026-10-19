from django import forms
from django.utils import timezone

from .models import Photo


class PhotoForm(forms.ModelForm):
    """6-hafta: Photo modeli maydonlariga mos forma."""

    class Meta:
        model = Photo
        fields = ['title', 'photographer', 'date', 'category', 'image']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'image': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 11-hafta: yangi surat qo'shishda rasm majburiy, tahrirlashda esa eski rasm qolishi mumkin
        self.fields['image'].required = not self.instance.image

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
