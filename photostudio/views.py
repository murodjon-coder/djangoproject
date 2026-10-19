from functools import wraps

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import ClientForm, PhotoForm, SessionForm
from .models import Client, Photo, Session


def staff_required(view_func):
    """O'chirish faqat administratorga (is_staff) ruxsat etiladi, boshqalarga 403."""

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


class StaffRequiredMixin(UserPassesTestMixin):
    """O'chirish faqat administratorga (is_staff) ruxsat etiladi (14-hafta: foydalanuvchi rollari)."""

    def test_func(self):
        return self.request.user.is_staff


# ---------------------------------------------------------------- Bosh sahifa

def home(request):
    """14-hafta: hamma ko'ra oladigan bosh sahifa."""
    upcoming = Session.objects.filter(status=Session.Status.PLANNED, scheduled_at__gte=timezone.now())
    context = {
        'latest_photos': Photo.objects.select_related('category').exclude(image='')[:6],
        'photo_count': Photo.objects.count(),
        'client_count': Client.objects.count(),
        'upcoming_count': upcoming.count(),
    }
    # Mijozlarning ismi va telefoni — maxfiy ma'lumot, faqat tizimga kirganlarga ko'rsatiladi
    if request.user.is_authenticated:
        context['upcoming_sessions'] = upcoming.select_related('client').order_by('scheduled_at')[:4]
    return render(request, 'photostudio/home.html', context)


def about(request):
    """10-hafta: static fayllar — shaxsiy surat, video va JDU logotipi."""
    return render(request, 'photostudio/about.html')


# ---------------------------------------------------------------- Suratlar (Photo)

@login_required
def photo_list(request):
    """4-hafta: function-based view — barcha suratlar ro'yxati."""
    # 7-hafta: select_related — kategoriya nomini JOIN orqali bitta so'rovda olamiz
    photos = Photo.objects.select_related('category')
    return render(request, 'photostudio/photo_list.html', {
        'photos': photos,
        'view_type': 'Function-based view',
    })


class PhotoListView(LoginRequiredMixin, ListView):
    """4-hafta: xuddi shu ro'yxat, lekin class-based view (ListView) bilan."""

    queryset = Photo.objects.select_related('category')
    template_name = 'photostudio/photo_list.html'
    context_object_name = 'photos'
    extra_context = {'view_type': 'Class-based view (ListView)'}


@login_required
def photo_detail(request, id):
    """5-hafta: bitta suratni ko'rsatuvchi view (dinamik URL: photos/<int:id>/)."""
    photo = get_object_or_404(Photo.objects.select_related('category', 'session__client'), id=id)
    return render(request, 'photostudio/photo_detail.html', {'photo': photo})


@login_required
def photo_create(request):
    """6-hafta: GET — bo'sh formani ko'rsatadi, POST — ma'lumotni tekshirib saqlaydi."""
    if request.method == 'POST':
        # 11-hafta: fayllar request.FILES orqali keladi
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save()
            messages.success(request, f"“{photo.title}” surati qo'shildi.")
            return redirect('photostudio:photo_detail', id=photo.id)
    else:
        form = PhotoForm(initial={'session': request.GET.get('session')})
    return render(request, 'photostudio/form.html', {
        'form': form,
        'page_title': "Yangi surat qo'shish",
        'cancel_url': reverse_lazy('photostudio:photo_list'),
    })


@login_required
def photo_update(request, id):
    """14-hafta: mavjud suratni tahrirlash (CRUD — Update)."""
    photo = get_object_or_404(Photo, id=id)
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES, instance=photo)
        if form.is_valid():
            form.save()
            messages.success(request, f"“{photo.title}” surati yangilandi.")
            return redirect('photostudio:photo_detail', id=photo.id)
    else:
        form = PhotoForm(instance=photo)
    return render(request, 'photostudio/form.html', {
        'form': form,
        'page_title': f"Tahrirlash: {photo.title}",
        'cancel_url': photo.get_absolute_url(),
    })


@login_required
@staff_required
def photo_delete(request, id):
    """14-hafta: suratni o'chirish (faqat administrator)."""
    photo = get_object_or_404(Photo, id=id)
    if request.method == 'POST':
        photo.image.delete(save=False)
        photo.delete()
        messages.success(request, f"“{photo.title}” surati o'chirildi.")
        return redirect('photostudio:photo_list')
    return render(request, 'photostudio/confirm_delete.html', {
        'object': photo,
        'cancel_url': photo.get_absolute_url(),
    })


# ---------------------------------------------------------------- Mijozlar (Client)

class ClientListView(LoginRequiredMixin, ListView):
    queryset = Client.objects.annotate(session_count=Count('sessions'))
    context_object_name = 'clients'


class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    context_object_name = 'client'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sessions = self.object.sessions.annotate(photo_count=Count('photos'))
        context['sessions'] = sessions
        context['photo_total'] = sum(s.photo_count for s in sessions)
        context['paid_total'] = sum(s.price for s in sessions if s.status == Session.Status.DONE)
        return context


class ClientCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'photostudio/form.html'
    success_message = "“%(full_name)s” mijoz sifatida qo'shildi."
    extra_context = {'page_title': "Yangi mijoz", 'cancel_url': reverse_lazy('photostudio:client_list')}


class ClientUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'photostudio/form.html'
    success_message = "“%(full_name)s” ma'lumotlari yangilandi."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"Tahrirlash: {self.object}"
        context['cancel_url'] = self.object.get_absolute_url()
        return context


class ClientDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Client
    template_name = 'photostudio/confirm_delete.html'
    success_url = reverse_lazy('photostudio:client_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = self.object.get_absolute_url()
        context['warning'] = "Mijoz bilan birga uning barcha fotosessiyalari ham o'chiriladi."
        return context

    def form_valid(self, form):
        messages.success(self.request, f"“{self.object}” mijozi o'chirildi.")
        return super().form_valid(form)


# ---------------------------------------------------------------- Fotosessiyalar (Session)

class SessionListView(LoginRequiredMixin, ListView):
    context_object_name = 'photo_sessions'
    template_name = 'photostudio/session_list.html'

    def get_queryset(self):
        queryset = Session.objects.select_related('client').annotate(photo_count=Count('photos'))
        status = self.request.GET.get('status')
        if status in Session.Status.values:
            queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuses'] = Session.Status.choices
        context['current_status'] = self.request.GET.get('status', '')
        return context


class SessionDetailView(LoginRequiredMixin, DetailView):
    queryset = Session.objects.select_related('client')
    context_object_name = 'photo_session'
    template_name = 'photostudio/session_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['photos'] = self.object.photos.select_related('category')
        return context


class SessionCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Session
    form_class = SessionForm
    template_name = 'photostudio/form.html'
    success_message = "Fotosessiya rejalashtirildi."
    extra_context = {'page_title': "Yangi fotosessiya", 'cancel_url': reverse_lazy('photostudio:session_list')}

    def get_initial(self):
        return {'client': self.request.GET.get('client')}


class SessionUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Session
    form_class = SessionForm
    template_name = 'photostudio/form.html'
    success_message = "Fotosessiya yangilandi."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"Tahrirlash: {self.object}"
        context['cancel_url'] = self.object.get_absolute_url()
        return context


class SessionDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Session
    template_name = 'photostudio/confirm_delete.html'
    success_url = reverse_lazy('photostudio:session_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cancel_url'] = self.object.get_absolute_url()
        context['warning'] = "Suratlar o'chirilmaydi, faqat fotosessiyaga bog'lanishi olib tashlanadi."
        return context

    def form_valid(self, form):
        messages.success(self.request, f"“{self.object}” fotosessiyasi o'chirildi.")
        return super().form_valid(form)


# ---------------------------------------------------------------- Ro'yxatdan o'tish

def register(request):
    """8-hafta: UserCreationForm yordamida ro'yxatdan o'tish."""
    if request.user.is_authenticated:
        return redirect('photostudio:photo_list')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Xush kelibsiz, {user.username}! Siz ro'yxatdan o'tdingiz.")
            return redirect('photostudio:photo_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
