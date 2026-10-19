from django import forms
from django.utils import timezone

from .models import Client, Photo, Session


class PhotoForm(forms.ModelForm):
    """6-hafta: Photo modeli maydonlariga mos forma (11-haftada rasm qo'shilgan)."""

    class Meta:
        model = Photo
        fields = ['title', 'photographer', 'date', 'category', 'session', 'image']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'image': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 11-hafta: yangi surat qo'shishda rasm majburiy, tahrirlashda esa eski rasm qolishi mumkin
        self.fields['image'].required = not self.instance.image
        self.fields['session'].queryset = Session.objects.select_related('client')
        self.fields['category'].empty_label = "— Kategoriyani tanlang —"
        self.fields['session'].empty_label = "— Fotosessiyasiz —"

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


class ClientForm(forms.ModelForm):
    """14-hafta: mijoz qo'shish va tahrirlash formasi."""

    class Meta:
        model = Client
        fields = ['full_name', 'phone', 'email']
        widgets = {
            'phone': forms.TextInput(attrs={'placeholder': '+998 90 123 45 67'}),
        }


class SessionForm(forms.ModelForm):
    """14-hafta: fotosessiya qo'shish va tahrirlash formasi."""

    class Meta:
        model = Session
        fields = ['client', 'photographer', 'scheduled_at', 'duration_minutes', 'location', 'price', 'status', 'notes']
        widgets = {
            'scheduled_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].empty_label = "— Mijozni tanlang —"

    def clean(self):
        cleaned = super().clean()
        scheduled_at = cleaned.get('scheduled_at')
        status = cleaned.get('status')
        if scheduled_at and status == Session.Status.PLANNED and scheduled_at < timezone.now():
            self.add_error('scheduled_at', "Rejalashtirilgan fotosessiya vaqti o'tib ketgan bo'lmasligi kerak.")
        return cleaned
