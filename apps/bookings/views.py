from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Booking, Payment, Withdrawal
from .forms import BookingForm, MockPaymentForm, WithdrawalForm
from apps.guides.models import GuideProfile
from apps.core.models import Notification
import uuid
import random


@login_required
def booking_create(request, guide_pk):
    guide = get_object_or_404(GuideProfile, pk=guide_pk, verification_status='approved')

    if request.user.is_guide and request.user.guide_profile == guide:
        messages.error(request, "You can't book yourself.")
        return redirect('guides:profile', pk=guide_pk)

    if request.method == 'POST':
        form = BookingForm(guide=guide, data=request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.tourist = request.user
            booking.guide = guide

            if booking.tour:
                booking.total_price = booking.tour.price_per_person * booking.people_count
            else:
                booking.total_price = 0

            booking.save()

            Notification.objects.create(
                user=guide.user,
                notification_type='booking',
                title='New Booking Request',
                message=f'{request.user.get_full_name() or request.user.username} wants to book on {booking.booking_date}.',
                link=f'/guides/dashboard/'
            )

            return redirect('bookings:payment', pk=booking.pk)
    else:
        form = BookingForm(guide=guide)

    return render(request, 'bookings/booking_form.html', {'form': form, 'guide': guide})


@login_required
def payment_view(request, pk):
    booking = get_object_or_404(Booking, pk=pk, tourist=request.user)

    if booking.status != Booking.STATUS_PENDING:
        messages.info(request, 'This booking has already been processed.')
        return redirect('bookings:detail', pk=booking.pk)

    prepay_amount = round(booking.total_price * 50 / 100, 2)
    already_paid = booking.payments.filter(
        payment_type=Payment.TYPE_PREPAY, status=Payment.STATUS_COMPLETED
    ).exists()

    if request.method == 'POST':
        form = MockPaymentForm(request.POST)
        if form.is_valid():
            card_number = form.cleaned_data['card_number'].replace(' ', '')
            transaction_id = 'TXN-' + uuid.uuid4().hex[:12].upper()

            Payment.objects.create(
                booking=booking,
                payment_type=Payment.TYPE_PREPAY,
                amount=prepay_amount,
                status=Payment.STATUS_COMPLETED,
                mock_transaction_id=transaction_id,
                card_last4=card_number[-4:] if len(card_number) >= 4 else '****',
            )

            booking.status = Booking.STATUS_CONFIRMED
            booking.save()

            Notification.objects.create(
                user=booking.guide.user,
                notification_type='booking',
                title='Prepayment Received!',
                message=f'Prepayment of {prepay_amount} AZN (50%) received for booking on {booking.booking_date}.',
                link='/guides/dashboard/'
            )

            messages.success(request, f'Prepayment of {prepay_amount} AZN paid! Remaining {prepay_amount} AZN is due after the tour.')
            return redirect('bookings:confirmation', pk=booking.pk)
    else:
        form = MockPaymentForm(initial={'card_number': '4242 4242 4242 4242'})

    return render(request, 'bookings/payment.html', {
        'booking': booking,
        'form': form,
        'prepay_amount': prepay_amount,
        'already_paid': already_paid,
    })


@login_required
def booking_confirmation(request, pk):
    booking = get_object_or_404(Booking, pk=pk, tourist=request.user)
    return render(request, 'bookings/confirmation.html', {'booking': booking})


@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(
        Booking.objects.select_related('tourist', 'guide__user', 'tour'),
        pk=pk
    )
    if booking.tourist != request.user and booking.guide.user != request.user:
        if not request.user.is_staff:
            messages.error(request, 'Access denied.')
            return redirect('core:home')

    return render(request, 'bookings/detail.html', {'booking': booking})


@login_required
def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk, tourist=request.user)
    if booking.status in [Booking.STATUS_PENDING, Booking.STATUS_CONFIRMED]:
        booking.status = Booking.STATUS_CANCELLED
        booking.save()
        messages.success(request, 'Booking cancelled.')
    return redirect('accounts:dashboard')


@login_required
def booking_complete(request, pk):
    """Guide marks booking as completed."""
    booking = get_object_or_404(Booking, pk=pk, guide__user=request.user)
    if booking.status == Booking.STATUS_CONFIRMED:
        booking.status = Booking.STATUS_COMPLETED
        booking.save()
        Notification.objects.create(
            user=booking.tourist,
            notification_type='booking',
            title='Tour Completed',
            message=f'Your tour on {booking.booking_date} is marked as completed. Please leave a review!',
            link=f'/reviews/create/{booking.pk}/'
        )
        messages.success(request, 'Booking marked as completed.')
    return redirect('guides:dashboard')


@login_required
def withdrawal_request(request):
    guide = get_object_or_404(GuideProfile, user=request.user)
    if request.method == 'POST':
        form = WithdrawalForm(request.POST)
        if form.is_valid():
            w = form.save(commit=False)
            w.guide = guide
            w.save()
            messages.success(request, f'Withdrawal request of {w.amount} AZN submitted. Processing within 3 business days.')
            return redirect('guides:dashboard')
    else:
        form = WithdrawalForm()
    return render(request, 'bookings/withdrawal.html', {'form': form, 'guide': guide})
