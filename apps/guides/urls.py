from django.urls import path
from . import views

app_name = 'guides'

urlpatterns = [
    path('', views.guide_catalog, name='catalog'),
    path('tours/', views.tour_catalog, name='tour_catalog'),
    path('<int:pk>/', views.guide_profile, name='profile'),
    path('register/', views.guide_register, name='register'),
    path('dashboard/', views.guide_dashboard, name='dashboard'),
    path('profile/edit/', views.guide_profile_edit, name='profile_edit'),
    path('tours/create/', views.tour_create, name='tour_create'),
    path('tours/<int:pk>/', views.tour_detail, name='tour_detail'),
    path('tours/<int:pk>/edit/', views.tour_edit, name='tour_edit'),
    path('tours/<int:pk>/photos/upload/', views.upload_tour_photos, name='upload_tour_photos'),
    path('tours/<int:pk>/images/<int:image_pk>/delete/', views.delete_tour_image, name='delete_tour_image'),
    path('tours/<int:pk>/delete/', views.tour_delete, name='tour_delete'),
    path('<int:guide_pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('photos/upload/', views.upload_guide_photos, name='upload_photos'),
    path('photos/<int:photo_pk>/delete/', views.delete_guide_photo, name='delete_photo'),
    path('availability/', views.manage_availability, name='availability'),
    path('bookings/<int:booking_pk>/handle/', views.handle_booking_request, name='handle_booking'),
]
