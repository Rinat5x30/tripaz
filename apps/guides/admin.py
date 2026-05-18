from django.contrib import admin
from django.utils.html import format_html
from .models import GuideProfile, Tour, TourImage, VerificationDocument, FavoriteGuide, GuideAvailability
from apps.core.models import Notification


@admin.register(GuideProfile)
class GuideProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'city', 'verification_status', 'rating', 'total_reviews', 'is_featured', 'created_at']
    list_filter = ['verification_status', 'city', 'is_featured']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name', 'license_number']
    readonly_fields = ['rating', 'total_reviews', 'created_at', 'updated_at']
    actions = ['approve_guides', 'reject_guides', 'feature_guides']

    def approve_guides(self, request, queryset):
        for guide in queryset.filter(verification_status='pending'):
            guide.verification_status = 'approved'
            guide.save()
            Notification.objects.create(
                user=guide.user,
                notification_type='verification',
                title='Application Approved!',
                message='Congratulations! Your guide application has been approved. You can now receive bookings.',
            )
        self.message_user(request, f'{queryset.count()} guides approved.')
    approve_guides.short_description = 'Approve selected guides'

    def reject_guides(self, request, queryset):
        queryset.update(verification_status='rejected')
        self.message_user(request, f'{queryset.count()} guides rejected.')
    reject_guides.short_description = 'Reject selected guides'

    def feature_guides(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f'{queryset.count()} guides featured.')
    feature_guides.short_description = 'Mark as featured'


@admin.register(VerificationDocument)
class VerificationDocumentAdmin(admin.ModelAdmin):
    list_display = ['guide', 'doc_type', 'uploaded_at', 'view_file']
    list_filter = ['doc_type']

    def view_file(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank">View</a>', obj.file.url)
        return '-'
    view_file.short_description = 'File'


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ['title', 'guide', 'price_per_person', 'duration_hours', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title', 'guide__user__username']


@admin.register(TourImage)
class TourImageAdmin(admin.ModelAdmin):
    list_display = ['tour', 'caption', 'order']
