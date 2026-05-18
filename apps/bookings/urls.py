from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('book/<int:guide_pk>/', views.booking_create, name='create'),
    path('<int:pk>/payment/', views.payment_view, name='payment'),
    path('<int:pk>/confirmation/', views.booking_confirmation, name='confirmation'),
    path('<int:pk>/', views.booking_detail, name='detail'),
    path('<int:pk>/cancel/', views.booking_cancel, name='cancel'),
    path('<int:pk>/complete/', views.booking_complete, name='complete'),
    path('withdrawal/', views.withdrawal_request, name='withdrawal'),
]
