import datetime

from django import forms
from django.utils import timezone

from .models import BookingRequest, Client, Photo, Session, Tag


class ImageInput(forms.ClearableFileInput):
    """Rasm maydoni — o'zbekcha yozuvlar bilan (standart tarjimada "Clear" → "Aniq" bo'lib qolgan)."""

    initial_text = "Hozirgi rasm"
    input_text = "Yangisini tanlash"
    clear_checkbox_label = "Rasmni o'chirish"


class PhotoForm(forms.ModelForm):
    """6-hafta: Photo modeli maydonlariga mos forma (11-haftada rasm, keyin teglar qo'shilgan)."""

    new_tags = forms.CharField(
        label="Yangi teglar",
        required=False,
        help_text="Ro'yxatda yo'q teglarni vergul bilan yozing: masalan, <em>oq fon, kechqurun</em>",
        widget=forms.TextInput(attrs={'placeholder': 'oq fon, kechqurun'}),
    )

    class Meta:
        model = Photo
        fields = ['title', 'photographer', 'date', 'category', 'tags', 'new_tags', 'session', 'image']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'tags': forms.CheckboxSelectMultiple(attrs={'class': 'chip-check'}),
            'image': ImageInput(attrs={'accept': 'image/*'}),
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

    def clean_new_tags(self):
        names = [name.strip() for name in self.cleaned_data['new_tags'].split(',')]
        names = [name for name in names if name]
        too_long = [name for name in names if len(name) > 50]
        if too_long:
            raise forms.ValidationError("Teg nomi 50 belgidan oshmasligi kerak.")
        return names

    def save(self, commit=True):
        photo = super().save(commit=commit)
        if commit:
            # Many-to-Many: yangi teglarni yaratib (yoki borini topib) suratga qo'shamiz
            for name in self.cleaned_data['new_tags']:
                tag = Tag.objects.filter(name__iexact=name).first() or Tag.objects.create(name=name)
                photo.tags.add(tag)
        return photo


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


class BookingRequestForm(forms.ModelForm):
    """Onlayn bron: mehmon yoki mijoz fotosessiyaga yoziladi."""

    class Meta:
        model = BookingRequest
        fields = ['full_name', 'phone', 'email', 'category', 'preferred_at', 'message']
        widgets = {
            'phone': forms.TextInput(attrs={'placeholder': '+998 90 123 45 67'}),
            'preferred_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'message': forms.Textarea(attrs={'rows': 3, 'placeholder': "Masalan: 3 kishilik oila, oq fon, 1 soat"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = "— Farqi yo'q / bilmayman —"

    def clean_preferred_at(self):
        preferred_at = self.cleaned_data['preferred_at']
        if preferred_at < timezone.now() + datetime.timedelta(hours=2):
            raise forms.ValidationError("Kamida 2 soat keyingi vaqtni tanlang.")
        if preferred_at > timezone.now() + datetime.timedelta(days=365):
            raise forms.ValidationError("Bir yildan uzoq muddatga bron qilib bo'lmaydi.")
        return preferred_at


class BookingApproveForm(forms.Form):
    """Xodim so'rovni tasdiqlaganda fotosessiya ma'lumotlarini kiritadi."""

    photographer = forms.CharField(label="Fotograf", max_length=100)
    scheduled_at = forms.DateTimeField(
        label="Sana va vaqt",
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
    )
    duration_minutes = forms.IntegerField(label="Davomiyligi (daqiqa)", min_value=15, initial=60)
    location = forms.CharField(label="Joy", max_length=150, initial="Asosiy studiya")
    price = forms.DecimalField(label="Narxi (so'm)", min_value=0, max_digits=12, decimal_places=0)
    answer = forms.CharField(
        label="Mijozga xabar",
        required=False,
        widget=forms.Textarea(attrs={'rows': 2}),
        initial="Fotosessiyangiz tasdiqlandi. Sizni kutamiz!",
    )

    def clean_scheduled_at(self):
        scheduled_at = self.cleaned_data['scheduled_at']
        if scheduled_at < timezone.now():
            raise forms.ValidationError("O'tib ketgan vaqtga fotosessiya qo'yib bo'lmaydi.")
        return scheduled_at


class BookingRejectForm(forms.Form):
    answer = forms.CharField(
        label="Rad etish sababi",
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': "Masalan: bu vaqt band, iltimos boshqa kunni tanlang"}),
    )
