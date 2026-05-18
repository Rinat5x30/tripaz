from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from .models import Review
from .forms import ReviewForm
from apps.bookings.models import Booking
from apps.guides.models import GuideProfile
from apps.core.models import Notification


@login_required
def create_review(request, booking_pk):
    booking = get_object_or_404(Booking, pk=booking_pk, tourist=request.user, status='completed')

    if hasattr(booking, 'review'):
        messages.info(request, 'You already reviewed this booking.')
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.tourist = request.user
            review.guide = booking.guide
            review.save()

            # Update guide rating
            guide = booking.guide
            avg = Review.objects.filter(guide=guide, is_visible=True).aggregate(avg=Avg('rating'))['avg'] or 0
            guide.rating = round(avg, 2)
            guide.total_reviews = Review.objects.filter(guide=guide, is_visible=True).count()
            guide.save()

            Notification.objects.create(
                user=guide.user,
                notification_type='review',
                title='New Review',
                message=f'{request.user.get_full_name()} left you a {review.rating}-star review.',
                link=f'/guides/{guide.pk}/'
            )

            messages.success(request, 'Thank you for your review!')
            return redirect('accounts:dashboard')
    else:
        form = ReviewForm()

    return render(request, 'reviews/review_form.html', {'form': form, 'booking': booking})
