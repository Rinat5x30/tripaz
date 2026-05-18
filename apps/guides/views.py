from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Sum
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import GuideProfile, Tour, TourImage, GuidePhoto, FavoriteGuide, GuideAvailability, VerificationDocument
from .forms import GuideRegisterForm, GuideProfileForm, TourForm, GuideSearchForm
from apps.accounts.models import User
from apps.bookings.models import Booking, Payment
from apps.reviews.models import Review
from apps.core.models import Notification
import json


def tour_catalog(request):
    tours = Tour.objects.filter(
        is_active=True,
        guide__verification_status='approved'
    ).select_related('guide__user').prefetch_related('images')

    q = request.GET.get('q', '').strip()
    category = request.GET.get('category', '')
    city = request.GET.get('city', '')
    max_price = request.GET.get('max_price', '')
    max_duration = request.GET.get('max_duration', '')

    if q:
        tours = tours.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(guide__user__first_name__icontains=q) |
            Q(guide__user__last_name__icontains=q)
        )
    if category:
        tours = tours.filter(category=category)
    if city:
        tours = tours.filter(guide__city=city)
    if max_price:
        try:
            tours = tours.filter(price_per_person__lte=float(max_price))
        except ValueError:
            pass
    if max_duration:
        try:
            tours = tours.filter(duration_hours__lte=float(max_duration))
        except ValueError:
            pass

    sort = request.GET.get('sort', '')
    sort_map = {
        'price_asc': 'price_per_person',
        'price_desc': '-price_per_person',
        'duration': 'duration_hours',
        'newest': '-id',
    }
    tours = tours.order_by(sort_map.get(sort, '-guide__is_featured'))

    return render(request, 'guides/tour_catalog.html', {
        'tours': tours,
        'total': tours.count(),
        'categories': Tour.CATEGORY_CHOICES,
        'q': q,
        'selected_category': category,
        'selected_city': city,
        'max_price': max_price,
        'max_duration': max_duration,
        'sort': sort,
    })


def guide_catalog(request):
    guides = GuideProfile.objects.filter(
        verification_status='approved'
    ).select_related('user')

    form = GuideSearchForm(request.GET)

    if form.is_valid():
        q = form.cleaned_data.get('q')
        city = form.cleaned_data.get('city')
        language = form.cleaned_data.get('language')
        max_price = form.cleaned_data.get('max_price')
        min_rating = form.cleaned_data.get('min_rating')
        category = form.cleaned_data.get('category')

        if q:
            guides = guides.filter(
                Q(user__first_name__icontains=q) |
                Q(user__last_name__icontains=q) |
                Q(bio__icontains=q) |
                Q(tagline__icontains=q)
            )
        if city:
            guides = guides.filter(city=city)
        if language:
            guides = guides.filter(languages__icontains=language)
        if min_rating:
            guides = guides.filter(rating__gte=min_rating)

    sort = request.GET.get('sort', '-is_featured')
    sort_map = {
        'rating': '-rating',
        'newest': '-created_at',
    }
    guides = guides.order_by(sort_map.get(sort, '-is_featured'), '-rating')

    return render(request, 'guides/catalog.html', {
        'guides': guides,
        'form': form,
        'total': guides.count(),
    })


def guide_profile(request, pk):
    guide = get_object_or_404(
        GuideProfile.objects.select_related('user'),
        pk=pk, verification_status='approved'
    )
    tours = guide.tours.filter(is_active=True).prefetch_related('images')
    reviews = guide.reviews.filter(is_visible=True).select_related('tourist')
    review_count = reviews.count()
    completed_tours_count = Booking.objects.filter(guide=guide, status='completed').count()

    availability = list(
        GuideAvailability.objects.filter(guide=guide, is_available=True)
        .values_list('date', flat=True)
    )

    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = FavoriteGuide.objects.filter(tourist=request.user, guide=guide).exists()

    photos = guide.photos.all()
    context = {
        'guide': guide,
        'tours': tours,
        'reviews': reviews[:8],
        'review_count': review_count,
        'completed_tours_count': completed_tours_count,
        'availability_dates': [d.isoformat() for d in availability],
        'is_favorite': is_favorite,
        'photos': photos,
    }
    return render(request, 'guides/profile.html', context)


@login_required
def guide_register(request):
    if hasattr(request.user, 'guide_profile'):
        return redirect('guides:dashboard')

    if request.method == 'POST':
        form = GuideRegisterForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            user = request.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.phone = form.cleaned_data['phone']
            user.save()

            profile = form.save(commit=False)
            profile.user = user
            profile.languages = form.cleaned_data['languages']
            profile.verification_status = 'pending'
            profile.save()

            for doc_type, field in [('passport', 'passport'), ('license', 'license_doc'), ('photo', 'photo')]:
                if form.cleaned_data.get(field):
                    VerificationDocument.objects.create(
                        guide=profile,
                        doc_type=doc_type,
                        file=form.cleaned_data[field]
                    )

            messages.success(request, 'Guide application submitted! Our team will review it within 24 hours.')
            return redirect('guides:dashboard')
    else:
        form = GuideRegisterForm(user=request.user)

    return render(request, 'guides/register.html', {'form': form})


@login_required
def guide_dashboard(request):
    if not hasattr(request.user, 'guide_profile'):
        return redirect('guides:register')

    guide = request.user.guide_profile

    if guide.verification_status != 'approved':
        return render(request, 'guides/application_status.html', {'guide': guide})
    bookings = Booking.objects.filter(guide=guide).select_related('tourist', 'tour').order_by('-created_at')
    reviews = Review.objects.filter(guide=guide, is_visible=True).select_related('tourist')[:5]

    stats = {
        'total_bookings': bookings.count(),
        'pending': bookings.filter(status='pending').count(),
        'confirmed': bookings.filter(status='confirmed').count(),
        'completed': bookings.filter(status='completed').count(),
        'revenue': Payment.objects.filter(
            booking__guide=guide, status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0,
        'rating': guide.rating,
        'total_reviews': guide.total_reviews,
    }

    context = {
        'guide': guide,
        'bookings': bookings[:10],
        'reviews': reviews,
        'stats': stats,
        'tours': guide.tours.all()[:5],
    }
    return render(request, 'guides/dashboard.html', context)


@login_required
def guide_profile_edit(request):
    guide = get_object_or_404(GuideProfile, user=request.user)

    if request.method == 'POST':
        form = GuideProfileForm(request.POST, request.FILES, instance=guide, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('guides:profile_edit')
    else:
        form = GuideProfileForm(instance=guide, user=request.user)

    photos = guide.photos.all()
    return render(request, 'guides/profile_edit.html', {'form': form, 'guide': guide, 'photos': photos})


@login_required
@require_POST
def upload_guide_photos(request):
    guide = get_object_or_404(GuideProfile, user=request.user)
    current_count = guide.photos.count()
    slots = max(0, 8 - current_count)
    for img in list(request.FILES.getlist('gallery_photos'))[:slots]:
        GuidePhoto.objects.create(guide=guide, image=img)
    messages.success(request, 'Photos uploaded.')
    return redirect('guides:profile_edit')


@login_required
@require_POST
def delete_guide_photo(request, photo_pk):
    guide = get_object_or_404(GuideProfile, user=request.user)
    photo = get_object_or_404(GuidePhoto, pk=photo_pk, guide=guide)
    photo.image.delete(save=False)
    photo.delete()
    messages.success(request, 'Photo removed.')
    return redirect('guides:profile_edit')


@login_required
def tour_create(request):
    guide = get_object_or_404(GuideProfile, user=request.user)

    if guide.verification_status != 'approved':
        messages.error(request, 'Your guide application must be approved before you can create tours.')
        return redirect('guides:dashboard')

    if request.method == 'POST':
        form = TourForm(request.POST, request.FILES)
        if form.is_valid():
            tour = form.save(commit=False)
            tour.guide = guide
            tour.save()

            for img in request.FILES.getlist('images'):
                TourImage.objects.create(tour=tour, image=img)

            messages.success(request, 'Tour created successfully!')
            return redirect('guides:tour_edit', pk=tour.pk)
    else:
        form = TourForm()

    return render(request, 'guides/tour_form.html', {'form': form, 'action': 'Create'})


@login_required
def tour_edit(request, pk):
    guide = get_object_or_404(GuideProfile, user=request.user)
    if guide.verification_status != 'approved':
        messages.error(request, 'Your guide application must be approved before you can edit tours.')
        return redirect('guides:dashboard')
    tour = get_object_or_404(Tour, pk=pk, guide=guide)

    if request.method == 'POST':
        form = TourForm(request.POST, instance=tour)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tour updated.')
            return redirect('guides:tour_detail', pk=tour.pk)
    else:
        form = TourForm(instance=tour)

    return render(request, 'guides/tour_form.html', {'form': form, 'tour': tour, 'action': 'Edit'})


@login_required
@require_POST
def upload_tour_photos(request, pk):
    guide = get_object_or_404(GuideProfile, user=request.user)
    tour = get_object_or_404(Tour, pk=pk, guide=guide)
    slots = max(0, 8 - tour.images.count())
    for img in list(request.FILES.getlist('images'))[:slots]:
        TourImage.objects.create(tour=tour, image=img)
    messages.success(request, 'Photos uploaded.')
    return redirect('guides:tour_edit', pk=tour.pk)


@login_required
@require_POST
def delete_tour_image(request, pk, image_pk):
    guide = get_object_or_404(GuideProfile, user=request.user)
    tour = get_object_or_404(Tour, pk=pk, guide=guide)
    image = get_object_or_404(TourImage, pk=image_pk, tour=tour)
    image.image.delete(save=False)
    image.delete()
    messages.success(request, 'Photo removed.')
    return redirect('guides:tour_edit', pk=tour.pk)


@login_required
def tour_delete(request, pk):
    guide = get_object_or_404(GuideProfile, user=request.user)
    if guide.verification_status != 'approved':
        return redirect('guides:dashboard')
    tour = get_object_or_404(Tour, pk=pk, guide=guide)
    if request.method == 'POST':
        tour.delete()
        messages.success(request, 'Tour deleted.')
        return redirect('guides:dashboard')
    return render(request, 'guides/tour_confirm_delete.html', {'tour': tour})


def tour_detail(request, pk):
    tour = get_object_or_404(
        Tour.objects.select_related('guide__user').prefetch_related('images'),
        pk=pk, is_active=True
    )
    guide = tour.guide
    reviews = guide.reviews.filter(is_visible=True).select_related('tourist')[:6]
    other_tours = guide.tours.filter(is_active=True).exclude(pk=pk).prefetch_related('images')[:3]

    context = {
        'tour': tour,
        'guide': guide,
        'reviews': reviews,
        'other_tours': other_tours,
    }
    return render(request, 'guides/tour_detail.html', context)


@login_required
def toggle_favorite(request, guide_pk):
    guide = get_object_or_404(GuideProfile, pk=guide_pk)
    fav, created = FavoriteGuide.objects.get_or_create(tourist=request.user, guide=guide)
    if not created:
        fav.delete()
        return JsonResponse({'status': 'removed'})
    return JsonResponse({'status': 'added'})


@login_required
def manage_availability(request):
    guide = get_object_or_404(GuideProfile, user=request.user)

    if request.method == 'POST':
        data = json.loads(request.body)
        date_str = data.get('date')
        available = data.get('available', True)

        from datetime import date
        obj, created = GuideAvailability.objects.update_or_create(
            guide=guide, date=date_str,
            defaults={'is_available': available}
        )
        return JsonResponse({'status': 'ok', 'date': date_str, 'available': available})

    availability = list(
        GuideAvailability.objects.filter(guide=guide)
        .values('date', 'is_available')
    )
    return JsonResponse({'availability': [
        {'date': a['date'].isoformat(), 'available': a['is_available']} for a in availability
    ]})


@login_required
def handle_booking_request(request, booking_pk):
    guide = get_object_or_404(GuideProfile, user=request.user)
    booking = get_object_or_404(Booking, pk=booking_pk, guide=guide)

    if request.method == 'POST':
        action = request.POST.get('action')
        msg = request.POST.get('message', '')

        if action == 'accept' and booking.status == 'pending':
            booking.status = Booking.STATUS_CONFIRMED
            booking.guide_message = msg
            booking.save()
            Notification.objects.create(
                user=booking.tourist,
                notification_type='booking',
                title='Booking Confirmed!',
                message=f'Your booking with {guide.user.get_full_name()} has been confirmed.',
                link=f'/bookings/{booking.pk}/'
            )
            messages.success(request, 'Booking accepted.')
        elif action == 'reject' and booking.status == 'pending':
            booking.status = Booking.STATUS_REJECTED
            booking.guide_message = msg
            booking.save()
            Notification.objects.create(
                user=booking.tourist,
                notification_type='booking',
                title='Booking Update',
                message=f'Your booking request was not accepted. Reason: {msg}',
                link=f'/bookings/{booking.pk}/'
            )
            messages.info(request, 'Booking rejected.')

    return redirect('guides:dashboard')
