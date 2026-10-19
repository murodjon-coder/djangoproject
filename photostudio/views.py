from django.shortcuts import render
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
