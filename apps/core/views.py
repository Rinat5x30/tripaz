from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta
from apps.guides.models import GuideProfile, Tour
from apps.bookings.models import Booking, Payment
from apps.accounts.models import User
from apps.reviews.models import Review
from apps.core.models import Notification, SupportTicket
from .models import Notification


def home(request):
    featured_guides = GuideProfile.objects.filter(
        verification_status='approved', is_featured=True
    ).select_related('user')[:6]

    if featured_guides.count() < 4:
        extra = GuideProfile.objects.filter(
            verification_status='approved'
        ).select_related('user').order_by('-rating')[:6]
        featured_guides = extra

    recent_reviews = Review.objects.filter(is_visible=True).select_related(
        'tourist', 'guide__user'
    ).order_by('-created_at')[:6]

    stats = {
        'guides': GuideProfile.objects.filter(verification_status='approved').count(),
        'bookings': Booking.objects.filter(status__in=['confirmed', 'completed']).count(),
        'tourists': User.objects.filter(role='tourist').count(),
        'cities': 9,
    }

    categories = [
        {'name': 'City Tours', 'icon': '🏛️', 'slug': 'city_tour'},
        {'name': 'Historical', 'icon': '🕌', 'slug': 'historical'},
        {'name': 'Nature', 'icon': '🏔️', 'slug': 'nature'},
        {'name': 'Food & Wine', 'icon': '🍷', 'slug': 'food'},
        {'name': 'Photography', 'icon': '📷', 'slug': 'photography'},
        {'name': 'Day Trips', 'icon': '🚌', 'slug': 'day_trip'},
    ]

    return render(request, 'core/home.html', {
        'featured_guides': featured_guides,
        'recent_reviews': recent_reviews,
        'stats': stats,
        'categories': categories,
    })


def about(request):
    return render(request, 'core/about.html')


def contacts(request):
    if request.method == 'POST':
        # Store as support ticket so messages don't get lost
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message = request.POST.get('message', '').strip()
        if name and email and message:
            from apps.core.models import SupportTicket
            ticket_user = request.user if request.user.is_authenticated else None
            if ticket_user:
                SupportTicket.objects.create(
                    user=ticket_user,
                    category='other',
                    subject=f'Contact form: {name}',
                    description=f'From: {name} <{email}>\n\n{message}',
                )
            messages.success(request, "Thank you! We'll get back to you within 24 hours.")
            return redirect('core:contacts')
        messages.error(request, 'Please fill in all fields.')
    return render(request, 'core/contacts.html')


@login_required
def notifications_view(request):
    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')
    notifs.filter(is_read=False).update(is_read=True)
    return render(request, 'core/notifications.html', {'notifications': notifs})


@login_required
def support_ticket_create(request):
    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        description = request.POST.get('description', '').strip()
        category = request.POST.get('category', 'other')

        if subject and description:
            SupportTicket.objects.create(
                user=request.user,
                subject=subject,
                description=description,
                category=category,
            )
            messages.success(request, 'Support ticket submitted. We\'ll respond within 24 hours.')
            return redirect('core:home')
        else:
            messages.error(request, 'Please fill in all fields.')

    from apps.core.models import SupportTicket as ST
    categories = ST.CATEGORY_CHOICES
    return render(request, 'core/support.html', {'categories': categories})


# ─── Admin Panel Views ────────────────────────────────────────────────────────

@login_required
def admin_dashboard(request):
    if not (request.user.is_staff or request.user.role in ['admin', 'support']):
        messages.error(request, 'Access denied.')
        return redirect('core:home')

    now = timezone.now()
    month_start = now.replace(day=1)

    stats = {
        'total_users': User.objects.count(),
        'total_guides': GuideProfile.objects.filter(verification_status='approved').count(),
        'pending_guides': GuideProfile.objects.filter(verification_status='pending').count(),
        'total_bookings': Booking.objects.count(),
        'monthly_bookings': Booking.objects.filter(created_at__gte=month_start).count(),
        'gmv': Payment.objects.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0,
        'monthly_gmv': Payment.objects.filter(status='completed', created_at__gte=month_start).aggregate(
            total=Sum('amount'))['total'] or 0,
        'open_tickets': SupportTicket.objects.filter(status='open').count(),
        'avg_rating': Review.objects.aggregate(avg=Avg('rating'))['avg'] or 0,
    }

    top_guides = GuideProfile.objects.filter(verification_status='approved').annotate(
        booking_count=Count('bookings')
    ).order_by('-booking_count')[:5]

    recent_bookings = Booking.objects.select_related(
        'tourist', 'guide__user'
    ).order_by('-created_at')[:10]

    pending_guides = GuideProfile.objects.filter(
        verification_status='pending'
    ).select_related('user').order_by('-created_at')[:10]

    context = {
        'stats': stats,
        'top_guides': top_guides,
        'recent_bookings': recent_bookings,
        'pending_guides': pending_guides,
    }
    return render(request, 'admin_panel/dashboard.html', context)


@login_required
def admin_verify_guide(request, guide_pk):
    if not (request.user.is_staff or request.user.role in ['admin', 'support']):
        return redirect('core:home')

    guide = get_object_or_404(GuideProfile, pk=guide_pk)

    if request.method == 'POST':
        action = request.POST.get('action')
        reason = request.POST.get('reason', '')

        if action == 'approve':
            guide.verification_status = 'approved'
            guide.rejection_reason = ''
            guide.save()
            guide.user.role = User.ROLE_GUIDE
            guide.user.save()
            Notification.objects.create(
                user=guide.user,
                notification_type='verification',
                title='Application Approved! 🎉',
                message='Your guide application has been approved. Welcome to TripAZ!',
            )
            messages.success(request, f'{guide.user.get_full_name()} approved.')
        elif action == 'reject':
            guide.verification_status = 'rejected'
            guide.rejection_reason = reason
            guide.save()
            guide.user.role = User.ROLE_TOURIST
            guide.user.save()
            Notification.objects.create(
                user=guide.user,
                notification_type='verification',
                title='Application Update',
                message=f'Your guide application was not approved. Reason: {reason}',
            )
            messages.info(request, f'{guide.user.get_full_name()} rejected.')

        return redirect('core:admin_dashboard')

    return render(request, 'admin_panel/guide_verify.html', {'guide': guide})


@login_required
def admin_users(request):
    if not request.user.is_staff:
        return redirect('core:home')
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'admin_panel/users.html', {'users': users})


@login_required
def admin_tickets(request):
    if not (request.user.is_staff or request.user.role in ['admin', 'support']):
        return redirect('core:home')

    tickets = SupportTicket.objects.select_related('user').order_by('-created_at')

    if request.method == 'POST':
        ticket_id = request.POST.get('ticket_id')
        status = request.POST.get('status')
        note = request.POST.get('resolution_note', '')
        ticket = get_object_or_404(SupportTicket, pk=ticket_id)
        ticket.status = status
        ticket.resolution_note = note
        ticket.assigned_to = request.user
        ticket.save()
        messages.success(request, 'Ticket updated.')

    return render(request, 'admin_panel/tickets.html', {'tickets': tickets})
