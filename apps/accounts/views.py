from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from .forms import TouristRegisterForm, LoginForm, TouristProfileForm
from .models import User, TouristProfile
from apps.bookings.models import Booking, Payment
from apps.guides.models import FavoriteGuide


def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    next_url = request.GET.get('next') or request.POST.get('next') or '/'
    if request.method == 'POST':
        form = TouristRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to TripAZ, {user.first_name}! Start exploring guides.')
            return redirect(next_url)
    else:
        form = TouristRegisterForm()
    return render(request, 'accounts/register.html', {'form': form, 'next': next_url})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_banned:
                messages.error(request, 'Your account has been suspended. Contact support.')
                return redirect('accounts:login')
            login(request, user)
            next_url = request.GET.get('next', '/')
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect(next_url)
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('core:home')


@login_required
def tourist_dashboard(request):
    user = request.user
    bookings = Booking.objects.filter(tourist=user).select_related('guide__user', 'tour').order_by('-created_at')
    favorites = FavoriteGuide.objects.filter(tourist=user).select_related('guide__user')

    stats = {
        'total_bookings': bookings.count(),
        'completed': bookings.filter(status='completed').count(),
        'upcoming': bookings.filter(status='confirmed').count(),
        'pending': bookings.filter(status='pending').count(),
        'total_spent': Payment.objects.filter(
            booking__tourist=user, status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0,
    }

    context = {
        'bookings': bookings[:10],
        'favorites': favorites[:6],
        'stats': stats,
    }
    return render(request, 'accounts/tourist_dashboard.html', context)


@login_required
def favorites_view(request):
    favorites = FavoriteGuide.objects.filter(
        tourist=request.user
    ).select_related('guide__user', 'guide')
    return render(request, 'accounts/favorites.html', {'favorites': favorites})


@login_required
def profile_edit(request):
    user = request.user
    profile, _ = TouristProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = TouristProfileForm(request.POST, request.FILES, instance=profile, user=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:dashboard')
    else:
        form = TouristProfileForm(instance=profile, user=user)

    return render(request, 'accounts/profile_edit.html', {'form': form})
