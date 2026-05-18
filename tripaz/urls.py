from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('guides/', include('apps.guides.urls')),
    path('bookings/', include('apps.bookings.urls')),
    path('chat/', include('apps.chat.urls')),
    path('reviews/', include('apps.reviews.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = 'TripAZ Administration'
admin.site.site_title = 'TripAZ Admin'
admin.site.index_title = 'Welcome to TripAZ Admin Panel'
