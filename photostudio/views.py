from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from .forms import PhotoForm
from .models import Photo


def photo_list(request):
    """4-hafta: function-based view — barcha suratlar ro'yxati."""
    photos = Photo.objects.all()
    return render(request, 'photostudio/photo_list.html', {
        'photos': photos,
        'view_type': 'Function-based view',
    })


class PhotoListView(ListView):
    """4-hafta: xuddi shu ro'yxat, lekin class-based view (ListView) bilan."""

    model = Photo
    template_name = 'photostudio/photo_list.html'
    context_object_name = 'photos'
    extra_context = {'view_type': 'Class-based view (ListView)'}


def photo_detail(request, id):
    """5-hafta: bitta suratni ko'rsatuvchi view (dinamik URL: photos/<int:id>/)."""
    photo = get_object_or_404(Photo, id=id)
    return render(request, 'photostudio/photo_detail.html', {'photo': photo})


def photo_create(request):
    """6-hafta: GET — bo'sh formani ko'rsatadi, POST — ma'lumotni tekshirib saqlaydi."""
    if request.method == 'POST':
        form = PhotoForm(request.POST)
        if form.is_valid():
            photo = form.save()
            messages.success(request, f"“{photo.title}” surati qo'shildi.")
            return redirect('photostudio:photo_detail', id=photo.id)
    else:
        form = PhotoForm()
    return render(request, 'photostudio/photo_form.html', {'form': form})
