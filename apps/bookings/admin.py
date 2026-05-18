from django.contrib import admin
from .models import Booking, Payment, Withdrawal


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_ref', 'tourist', 'guide', 'booking_date', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'booking_date']
    search_fields = ['booking_ref', 'tourist__username', 'guide__user__username']
    readonly_fields = ['booking_ref', 'created_at', 'updated_at']
    date_hierarchy = 'booking_date'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['booking', 'amount', 'status', 'mock_transaction_id', 'created_at']
    list_filter = ['status']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ['guide', 'amount', 'method', 'status', 'created_at']
    list_filter = ['status', 'method']
    actions = ['process_withdrawals']

    def process_withdrawals(self, request, queryset):
        queryset.filter(status='pending').update(status='processed')
        self.message_user(request, f'Withdrawals processed.')
    process_withdrawals.short_description = 'Mark as processed'
