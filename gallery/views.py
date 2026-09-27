from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import Painting, ArtistProfile
from .forms import ContactForm


def home(request):
    featured = Painting.objects.filter(is_featured=True)[:4]

    if not featured:
        featured = Painting.objects.all()[:4]

    artist = ArtistProfile.objects.first()

    return render(request, 'gallery/home.html', {
        'featured': featured,
        'artist': artist,
    })


def gallery_list(request):
    category = request.GET.get('category', 'all')
    query = request.GET.get('q', '')

    paintings = Painting.objects.all()

    # Filter by category
    if category != 'all':
        paintings = paintings.filter(category=category)

    # Filter by search query
    if query:
        paintings = paintings.filter(title__icontains=query)

    artist = ArtistProfile.objects.first()

    return render(request, 'gallery/gallery.html', {
        'paintings': paintings,
        'current_category': category,
        'query': query,
        'categories': Painting.CATEGORY_CHOICES,
        'artist': artist,
    })


def painting_detail(request, pk):
    painting = get_object_or_404(Painting, pk=pk)
    artist = ArtistProfile.objects.first()

    if request.method == 'POST':
        form = ContactForm(request.POST)

        if form.is_valid():
            msg = form.save(commit=False)
            msg.related_painting = painting
            msg.save()

            messages.success(
                request,
                'Ujumbe wako umetumwa. Tutawasiliana nawe hivi karibuni!'
            )

            return redirect('painting_detail', pk=pk)
    else:
        form = ContactForm()

    return render(request, 'gallery/painting_detail.html', {
        'painting': painting,
        'artist': artist,
        'form': form,
    })


def about(request):
    artist = ArtistProfile.objects.first()

    return render(request, 'gallery/about.html', {
        'artist': artist,
    })


def contact(request):
    artist = ArtistProfile.objects.first()

    if request.method == 'POST':
        form = ContactForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Ujumbe wako umetumwa. Tutawasiliana nawe hivi karibuni!'
            )

            return redirect('contact')
    else:
        form = ContactForm()

    return render(request, 'gallery/contact.html', {
        'form': form,
        'artist': artist,
    })

from django.http import HttpResponseRedirect

def set_language(request):
    lang = request.GET.get('lang', 'en')
    if lang in ['en', 'es', 'fr']:
        request.session['language'] = lang
    next_url = request.GET.get('next', '/')
    return HttpResponseRedirect(next_url)
