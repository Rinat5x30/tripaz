from django.contrib import admin
from .models import Notification, SupportTicket


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read']
    search_fields = ['user__username', 'title']


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'subject', 'category', 'status', 'assigned_to', 'created_at']
    list_filter = ['status', 'category']
    search_fields = ['user__username', 'subject']
    actions = ['resolve_tickets']

    def resolve_tickets(self, request, queryset):
        queryset.update(status='resolved', assigned_to=request.user)
    resolve_tickets.short_description = 'Mark selected as resolved'
