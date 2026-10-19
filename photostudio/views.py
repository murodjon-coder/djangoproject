import datetime
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Avg, Count, DecimalField, Prefetch, Q, Sum, Value
from django.db.models.functions import Coalesce, TruncMonth
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import (
    BookingApproveForm,
    BookingRejectForm,
    BookingRequestForm,
    ClientForm,
    PhotoForm,
    SessionForm,
)
from .models import BookingRequest, Category, Client, Photo, Session, Tag
from .roles import (
    EmployeeRequiredMixin,
    StaffRequiredMixin,
    employee_required,
    get_client_profile,
    is_employee,
    staff_required,
)

PHOTOS_PER_PAGE = 12
# Sum() bo'sh to'plamda None qaytaradi — Coalesce uni 0 ga almashtiradi
ZERO = Value(Decimal('0'), output_field=DecimalField(max_digits=14, decimal_places=0))


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
    # Mijozlarning ismi va telefoni — maxfiy ma'lumot, faqat xodimlarga ko'rsatiladi
    if is_employee(request.user):
        context['upcoming_sessions'] = upcoming.select_related('client').order_by('scheduled_at')[:4]
    return render(request, 'photostudio/home.html', context)


def about(request):
    """10-hafta: static fayllar — shaxsiy surat, video va JDU logotipi."""
    return render(request, 'photostudio/about.html')


@login_required
def after_login(request):
    """Kirgandan keyin rolga qarab yo'naltirish: xodim — bosh sahifa, mijoz — shaxsiy kabinet."""
    if is_employee(request.user):
        return redirect('photostudio:home')
    return redirect('photostudio:cabinet')


# ---------------------------------------------------------------- Suratlar (Photo)

def filter_photos(request, queryset):
    """Galereya uchun qidiruv (?q=), kategoriya (?category=) va teg (?tag=) filtrlari."""
    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(title__icontains=q)
            | Q(photographer__icontains=q)
            | Q(category__name__icontains=q)
            | Q(tags__name__icontains=q)
        ).distinct()
    category = request.GET.get('category', '')
    if category.isdigit():
        queryset = queryset.filter(category_id=category)
    tag = request.GET.get('tag', '')
    if tag:
        queryset = queryset.filter(tags__slug=tag)
    return queryset


def gallery_filters(request):
    """Filtr paneli uchun kategoriyalar, teglar va joriy tanlov."""
    return {
        'categories': Category.objects.annotate(photo_count=Count('photos')).filter(photo_count__gt=0),
        'tags': Tag.objects.annotate(photo_count=Count('photos')).filter(photo_count__gt=0),
        'current_q': request.GET.get('q', '').strip(),
        'current_category': request.GET.get('category', ''),
        'current_tag': request.GET.get('tag', ''),
    }


def gallery_queryset():
    # 7-hafta: select_related — ForeignKey (kategoriya) JOIN bilan bitta so'rovda;
    # prefetch_related — Many-to-Many (teglar) bitta qo'shimcha so'rovda
    return Photo.objects.select_related('category').prefetch_related('tags')


@login_required
@employee_required
def photo_list(request):
    """4-hafta: function-based view — barcha suratlar ro'yxati (+ qidiruv, filtr, sahifalash)."""
    photos = filter_photos(request, gallery_queryset())
    page_obj = Paginator(photos, PHOTOS_PER_PAGE).get_page(request.GET.get('page'))
    return render(request, 'photostudio/photo_list.html', {
        'photos': page_obj,
        'page_obj': page_obj,
        'view_type': 'Function-based view',
        **gallery_filters(request),
    })


class PhotoListView(EmployeeRequiredMixin, ListView):
    """4-hafta: xuddi shu ro'yxat, lekin class-based view (ListView) bilan."""

    template_name = 'photostudio/photo_list.html'
    context_object_name = 'photos'
    paginate_by = PHOTOS_PER_PAGE
    extra_context = {'view_type': 'Class-based view (ListView)'}

    def get_queryset(self):
        return filter_photos(self.request, gallery_queryset())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(gallery_filters(self.request))
        return context


@login_required
def photo_detail(request, id):
    """5-hafta: bitta suratni ko'rsatuvchi view (dinamik URL: photos/<int:id>/)."""
    photo = get_object_or_404(
        Photo.objects.select_related('category', 'session__client').prefetch_related('tags'), id=id,
    )
    if not is_employee(request.user):
        # Mijoz faqat o'z fotosessiyasidagi suratni ko'ra oladi
        profile = get_client_profile(request.user)
        if not (profile and photo.session and photo.session.client_id == profile.pk):
            raise PermissionDenied
    return render(request, 'photostudio/photo_detail.html', {'photo': photo})


@login_required
@employee_required
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
@employee_required
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

class ClientListView(EmployeeRequiredMixin, ListView):
    queryset = Client.objects.select_related('user').annotate(session_count=Count('sessions'))
    context_object_name = 'clients'


class ClientDetailView(EmployeeRequiredMixin, DetailView):
    queryset = Client.objects.select_related('user')
    context_object_name = 'client'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sessions = self.object.sessions.annotate(photo_count=Count('photos'))
        context['sessions'] = sessions
        context['photo_total'] = sum(s.photo_count for s in sessions)
        context['paid_total'] = sum(s.price for s in sessions if s.status == Session.Status.DONE)
        return context


class ClientCreateView(EmployeeRequiredMixin, SuccessMessageMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'photostudio/form.html'
    success_message = "“%(full_name)s” mijoz sifatida qo'shildi."
    extra_context = {'page_title': "Yangi mijoz", 'cancel_url': reverse_lazy('photostudio:client_list')}


class ClientUpdateView(EmployeeRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'photostudio/form.html'
    success_message = "“%(full_name)s” ma'lumotlari yangilandi."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"Tahrirlash: {self.object}"
        context['cancel_url'] = self.object.get_absolute_url()
        return context


class ClientDeleteView(StaffRequiredMixin, DeleteView):
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


@login_required
@employee_required
def client_account_create(request, pk):
    """Mijoz uchun shaxsiy kabinet akkaunti yaratish (One-to-One: Client.user)."""
    client = get_object_or_404(Client, pk=pk)
    if client.user:
        messages.info(request, f"Bu mijozning kabineti allaqachon bor: {client.user.username}.")
        return redirect(client)
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            client.user = form.save()
            client.save(update_fields=['user'])
            messages.success(
                request,
                f"Kabinet yaratildi. Login: {client.user.username} — login va parolni mijozga bering.",
            )
            return redirect(client)
    else:
        form = UserCreationForm()
    return render(request, 'photostudio/form.html', {
        'form': form,
        'page_title': f"Kabinet yaratish: {client.full_name}",
        'page_intro': "Mijoz shu login va parol bilan kirib, faqat o'z fotosessiyalari va suratlarini ko'radi.",
        'cancel_url': client.get_absolute_url(),
    })


# ---------------------------------------------------------------- Fotosessiyalar (Session)

class SessionListView(EmployeeRequiredMixin, ListView):
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


class SessionDetailView(EmployeeRequiredMixin, DetailView):
    queryset = Session.objects.select_related('client')
    context_object_name = 'photo_session'
    template_name = 'photostudio/session_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['photos'] = self.object.photos.select_related('category')
        return context


class SessionCreateView(EmployeeRequiredMixin, SuccessMessageMixin, CreateView):
    model = Session
    form_class = SessionForm
    template_name = 'photostudio/form.html'
    success_message = "Fotosessiya rejalashtirildi."
    extra_context = {'page_title': "Yangi fotosessiya", 'cancel_url': reverse_lazy('photostudio:session_list')}

    def get_initial(self):
        return {'client': self.request.GET.get('client')}


class SessionUpdateView(EmployeeRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Session
    form_class = SessionForm
    template_name = 'photostudio/form.html'
    success_message = "Fotosessiya yangilandi."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f"Tahrirlash: {self.object}"
        context['cancel_url'] = self.object.get_absolute_url()
        return context


class SessionDeleteView(StaffRequiredMixin, DeleteView):
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


# ---------------------------------------------------------------- Mijoz kabineti

@login_required
def cabinet(request):
    """Mijozning shaxsiy kabineti: faqat o'z fotosessiyalari va suratlari."""
    client = get_client_profile(request.user)
    context = {
        'client': client,
        'bookings': BookingRequest.objects.filter(user=request.user).select_related('category')[:10],
    }
    if client:
        photos_qs = Photo.objects.select_related('category').prefetch_related('tags')
        sessions = list(
            client.sessions.prefetch_related(Prefetch('photos', queryset=photos_qs)).order_by('-scheduled_at')
        )
        now = timezone.now()
        context.update({
            'sessions': sessions,
            'upcoming': sorted(
                (s for s in sessions if s.status == Session.Status.PLANNED and s.scheduled_at >= now),
                key=lambda s: s.scheduled_at,
            ),
            'photo_count': sum(len(s.photos.all()) for s in sessions),
            'done_count': sum(1 for s in sessions if s.status == Session.Status.DONE),
        })
    return render(request, 'photostudio/cabinet.html', context)


# ---------------------------------------------------------------- Statistika (dashboard)

def last_months(count, today):
    """Joriy oy bilan birga oxirgi `count` oyning birinchi kunlari (eskisidan yangisiga)."""
    year, month = today.year, today.month
    months = []
    for _ in range(count):
        months.append(datetime.date(year, month, 1))
        month -= 1
        if month == 0:
            year, month = year - 1, 12
    return list(reversed(months))


def money_short(value):
    """Grafik yozuvlari uchun qisqa summa: 2 500 000 → "2,5 mln", 800 000 → "800 ming"."""
    value = int(value or 0)
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}".rstrip('0').rstrip('.').replace('.', ',') + " mln"
    if value >= 1_000:
        return f"{round(value / 1_000)} ming"
    return str(value)


def with_percent(rows, key):
    """Har bir qatorga eng katta qiymatga nisbatan foiz (`pct`) qo'shadi — gorizontal ustunlar uchun."""
    top = max((row[key] or 0 for row in rows), default=0)
    for row in rows:
        row['pct'] = round((row[key] or 0) * 100 / top) if top else 0
    return rows


@login_required
@employee_required
def dashboard(request):
    """Statistika paneli: daromad, fotograflar, kategoriyalar, holatlar (ORM aggregatsiyasi)."""
    done = Session.objects.filter(status=Session.Status.DONE)
    today = timezone.localdate()
    months = last_months(6, today)

    # Oylik daromad: TruncMonth + Sum — bitta GROUP BY so'rov
    monthly = (
        done.filter(scheduled_at__date__gte=months[0])
        .annotate(month=TruncMonth('scheduled_at'))
        .values('month')
        .annotate(total=Sum('price'), sessions=Count('id'))
    )
    by_month = {(row['month'].year, row['month'].month): row for row in monthly}
    revenue_by_month = with_percent([
        {
            'month': m,
            'total': by_month.get((m.year, m.month), {}).get('total') or 0,
            'sessions': by_month.get((m.year, m.month), {}).get('sessions') or 0,
            'is_current': (m.year, m.month) == (today.year, today.month),
        }
        for m in months
    ], 'total')
    for row in revenue_by_month:
        row['short'] = money_short(row['total'])

    totals = done.aggregate(revenue=Coalesce(Sum('price'), ZERO), average=Avg('price'), count=Count('id'))
    all_sessions = Session.objects.count()
    cancelled = Session.objects.filter(status=Session.Status.CANCELLED).count()
    this_month = by_month.get((today.year, today.month), {})

    # Fotograflar reytingi: sessiyalar va suratlar alohida guruhlanadi (JOIN qiymatlarni ko'paytirib yubormasligi uchun)
    photo_counts = dict(Photo.objects.values_list('photographer').annotate(n=Count('id')))
    photographers = with_percent([
        {**row, 'photos': photo_counts.get(row['photographer'], 0)}
        for row in Session.objects.values('photographer').annotate(
            sessions=Count('id'),
            revenue=Coalesce(Sum('price', filter=Q(status=Session.Status.DONE)), ZERO),
        ).order_by('-revenue', 'photographer')
    ], 'revenue')

    categories = with_percent(list(
        Category.objects.annotate(count=Count('photos')).filter(count__gt=0).order_by('-count').values('name', 'count')
    ), 'count')

    status_labels = dict(Session.Status.choices)
    statuses = with_percent([
        {'status': row['status'], 'label': status_labels[row['status']], 'count': row['count']}
        for row in Session.objects.values('status').annotate(count=Count('id')).order_by('-count')
    ], 'count')

    top_clients = (
        Client.objects.annotate(
            revenue=Coalesce(Sum('sessions__price', filter=Q(sessions__status=Session.Status.DONE)), ZERO),
            session_count=Count('sessions'),
        ).filter(revenue__gt=0).order_by('-revenue')[:5]
    )

    return render(request, 'photostudio/dashboard.html', {
        'revenue_by_month': revenue_by_month,
        'revenue_total': totals['revenue'],
        'revenue_this_month': this_month.get('total') or 0,
        'sessions_this_month': this_month.get('sessions') or 0,
        'average_price': round(totals['average'] or 0),
        'done_count': totals['count'],
        'cancel_rate': round(cancelled * 100 / all_sessions) if all_sessions else 0,
        'photographers': photographers,
        'categories': categories,
        'statuses': statuses,
        'top_clients': top_clients,
        'popular_tags': Tag.objects.annotate(count=Count('photos')).filter(count__gt=0).order_by('-count')[:10],
    })


# ---------------------------------------------------------------- Onlayn bron

def phone_digits(phone):
    return ''.join(ch for ch in phone if ch.isdigit())


def find_client_by_phone(phone):
    """Telefon raqam bo'yicha mavjud mijozni topish (probel va belgilarga qaramay)."""
    digits = phone_digits(phone)
    return next((c for c in Client.objects.all() if phone_digits(c.phone) == digits), None)


def booking_create(request):
    """Hamma uchun: fotosessiyaga onlayn yozilish formasi."""
    profile = get_client_profile(request.user)
    if request.method == 'POST':
        form = BookingRequestForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            if request.user.is_authenticated:
                booking.user = request.user
            booking.save()
            messages.success(
                request,
                "So'rovingiz qabul qilindi! Administrator tez orada siz bilan bog'lanadi.",
            )
            return redirect('photostudio:cabinet' if request.user.is_authenticated else 'photostudio:home')
    else:
        initial = {}
        if profile:
            initial = {'full_name': profile.full_name, 'phone': profile.phone, 'email': profile.email}
        form = BookingRequestForm(initial=initial)
    return render(request, 'photostudio/booking_form.html', {'form': form})


class BookingListView(EmployeeRequiredMixin, ListView):
    context_object_name = 'bookings'
    template_name = 'photostudio/booking_list.html'

    def get_queryset(self):
        queryset = BookingRequest.objects.select_related('category', 'session')
        status = self.request.GET.get('status', BookingRequest.Status.NEW)
        if status in BookingRequest.Status.values:
            queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuses'] = BookingRequest.Status.choices
        context['current_status'] = self.request.GET.get('status', BookingRequest.Status.NEW)
        context['counts'] = dict(
            BookingRequest.objects.values_list('status').annotate(n=Count('id')).order_by()
        )
        return context


@login_required
@employee_required
def booking_detail(request, pk):
    booking = get_object_or_404(BookingRequest.objects.select_related('category', 'session', 'user'), pk=pk)
    approve_form = BookingApproveForm(initial={'scheduled_at': booking.preferred_at})
    reject_form = BookingRejectForm()
    if request.method == 'POST' and booking.status == BookingRequest.Status.NEW:
        if 'approve' in request.POST:
            approve_form = BookingApproveForm(request.POST)
            if approve_form.is_valid():
                session = approve_booking(booking, approve_form.cleaned_data)
                messages.success(request, f"So'rov tasdiqlandi va fotosessiya yaratildi: {session}.")
                return redirect(session)
        elif 'reject' in request.POST:
            reject_form = BookingRejectForm(request.POST)
            if reject_form.is_valid():
                booking.status = BookingRequest.Status.REJECTED
                booking.answer = reject_form.cleaned_data['answer']
                booking.save(update_fields=['status', 'answer'])
                messages.info(request, f"“{booking.full_name}” so'rovi rad etildi.")
                return redirect('photostudio:booking_list')
    return render(request, 'photostudio/booking_detail.html', {
        'booking': booking,
        'existing_client': find_client_by_phone(booking.phone),
        'approve_form': approve_form,
        'reject_form': reject_form,
    })


@transaction.atomic
def approve_booking(booking, data):
    """So'rovni tasdiqlash: mijozni topadi yoki yaratadi, kabinetni bog'laydi, fotosessiya yaratadi."""
    client = find_client_by_phone(booking.phone)
    if client is None:
        client = Client.objects.create(full_name=booking.full_name, phone=booking.phone, email=booking.email)
    # So'rovni mijozning o'zi akkauntidan yuborgan bo'lsa — kabinetini avtomatik bog'laymiz
    if booking.user and client.user is None and get_client_profile(booking.user) is None:
        client.user = booking.user
        client.save(update_fields=['user'])
    notes = f"Onlayn bron #{booking.pk}."
    if booking.category:
        notes += f" Turi: {booking.category.name}."
    if booking.message:
        notes += f" Mijoz izohi: {booking.message}"
    session = Session.objects.create(
        client=client,
        photographer=data['photographer'],
        scheduled_at=data['scheduled_at'],
        duration_minutes=data['duration_minutes'],
        location=data['location'],
        price=data['price'],
        notes=notes,
    )
    booking.status = BookingRequest.Status.APPROVED
    booking.answer = data['answer']
    booking.session = session
    booking.save(update_fields=['status', 'answer', 'session'])
    return session


# ---------------------------------------------------------------- Ro'yxatdan o'tish

def register(request):
    """8-hafta: UserCreationForm yordamida ro'yxatdan o'tish."""
    if request.user.is_authenticated:
        return redirect('photostudio:after_login')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='photostudio.backends.CaseInsensitiveModelBackend')
            messages.success(request, f"Xush kelibsiz, {user.username}! Siz ro'yxatdan o'tdingiz.")
            return redirect('photostudio:cabinet')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
