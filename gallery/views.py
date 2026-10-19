from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.utils.http import url_has_allowed_host_and_scheme
from .models import Painting, ArtistProfile
from .forms import ContactForm, GalleryFilterForm
from .translations import get_text


def _lang(request):
    return request.session.get('language', 'en')


def _contact_form_labels(request):
    return {
        key: get_text(_lang(request), key)
        for key in (
            'name',
            'email',
            'phone',
            'message',
            'optional',
            'inquiry_type',
            'general_inquiry',
            'painting_order',
            'order_details',
            'order_details_help',
            'order_details_required',
        )
    }


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
    labels = {
        key: get_text(_lang(request), key)
        for key in (
            'search_placeholder',
            'filter_category',
            'filter_availability',
            'filter_currency',
            'filter_min_price',
            'filter_max_price',
            'all',
            'available',
            'sold',
            'category_wanyama',
            'category_traditional',
            'category_other',
            'invalid_price',
            'price_range_error',
            'price_currency_required',
            'invalid_filters',
        )
    }
    filter_data = request.GET.copy()
    filter_data.setdefault('category', 'all')
    filter_data.setdefault('availability', 'all')
    filter_data.setdefault('currency', 'all')
    filter_form = GalleryFilterForm(filter_data, labels=labels)
    paintings = Painting.objects.all()

    if filter_form.is_valid():
        filters = filter_form.cleaned_data
        query = filters['q'].strip()
        if query:
            paintings = paintings.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )

        if filters['category'] != 'all':
            paintings = paintings.filter(category=filters['category'])

        if filters['availability'] == 'available':
            paintings = paintings.filter(is_available=True)
        elif filters['availability'] == 'sold':
            paintings = paintings.filter(is_available=False)

        if filters['currency'] != 'all':
            paintings = paintings.filter(currency=filters['currency'])
        if filters['min_price'] is not None:
            paintings = paintings.filter(price__gte=filters['min_price'])
        if filters['max_price'] is not None:
            paintings = paintings.filter(price__lte=filters['max_price'])
    else:
        filter_form.add_error(None, labels['invalid_filters'])
        paintings = paintings.none()

    paginator = Paginator(paintings, 9)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    pagination_params = request.GET.copy()
    pagination_params.pop('page', None)

    artist = ArtistProfile.objects.first()

    return render(request, 'gallery/gallery.html', {
        'page_obj': page_obj,
        'paintings': page_obj.object_list,
        'filter_form': filter_form,
        'filter_query_string': pagination_params.urlencode(),
        'artist': artist,
    })


def painting_detail(request, pk):
    painting = get_object_or_404(Painting, pk=pk)
    artist = ArtistProfile.objects.first()

    if request.method == 'POST':
        form = ContactForm(request.POST, labels=_contact_form_labels(request))
        if form.is_valid():
            msg = form.save(commit=False)
            msg.related_painting = painting
            msg.save()
            messages.success(request, get_text(_lang(request), 'success_message'))
            return redirect('painting_detail', pk=pk)
    else:
        form = ContactForm(labels=_contact_form_labels(request))

    return render(request, 'gallery/painting_detail.html', {
        'painting': painting,
        'artist': artist,
        'form': form,
    })


def about(request):
    artist = ArtistProfile.objects.first()
    return render(request, 'gallery/about.html', {'artist': artist})


def contact(request):
    artist = ArtistProfile.objects.first()

    if request.method == 'POST':
        form = ContactForm(request.POST, labels=_contact_form_labels(request))
        if form.is_valid():
            form.save()
            messages.success(request, get_text(_lang(request), 'success_message'))
            return redirect('contact')
    else:
        inquiry_type = request.GET.get('inquiry_type')
        initial_type = 'order' if inquiry_type == 'order' else 'general'
        form = ContactForm(
            labels=_contact_form_labels(request),
            initial={'inquiry_type': initial_type},
        )

    return render(request, 'gallery/contact.html', {
        'form': form,
        'artist': artist,
    })


def set_language(request):
    lang = request.GET.get('lang', 'en')
    if lang in ['en', 'es', 'fr', 'sw', 'de', 'it', 'zh', 'ar']:
        request.session['language'] = lang
    next_url = request.GET.get('next', '/')
    if not url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = '/'
    return HttpResponseRedirect(next_url)


def custom_404(request, exception):
    return render(request, '404.html', status=404)