from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView

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
