from django.db import models
from django.conf import settings
import uuid


class Booking(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    booking_ref = models.CharField(max_length=20, unique=True, editable=False)
    tourist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    guide = models.ForeignKey('guides.GuideProfile', on_delete=models.CASCADE, related_name='bookings')
    tour = models.ForeignKey('guides.Tour', on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    booking_date = models.DateField()
    booking_time = models.TimeField(default='09:00')
    people_count = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    special_requests = models.TextField(blank=True)
    guide_message = models.TextField(blank=True, help_text='Message from guide on accept/reject')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tourist']),
            models.Index(fields=['guide']),
            models.Index(fields=['status']),
        ]

    def save(self, *args, **kwargs):
        if not self.booking_ref:
            self.booking_ref = 'TZ' + uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Booking {self.booking_ref} - {self.tourist.username}'

    @property
    def can_review(self):
        return self.status == self.STATUS_COMPLETED


class Payment(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    STATUS_REFUNDED = 'refunded'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_REFUNDED, 'Refunded'),
    ]

    TYPE_PREPAY = 'prepay'
    TYPE_FINAL = 'final'
    TYPE_CHOICES = [
        (TYPE_PREPAY, '50% Prepayment'),
        (TYPE_FINAL, '50% Final Payment'),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    payment_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=TYPE_PREPAY)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    mock_transaction_id = models.CharField(max_length=100, blank=True)
    card_last4 = models.CharField(max_length=4, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Payment for {self.booking.booking_ref} - {self.status}'


class Withdrawal(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PROCESSED = 'processed'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PROCESSED, 'Processed'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    METHOD_BANK = 'bank'
    METHOD_M10 = 'm10'
    METHOD_KAPITAL = 'kapital'

    METHOD_CHOICES = [
        (METHOD_BANK, 'Bank Transfer'),
        (METHOD_M10, 'M10 Wallet'),
        (METHOD_KAPITAL, 'Kapital Bank'),
    ]

    guide = models.ForeignKey('guides.GuideProfile', on_delete=models.CASCADE, related_name='withdrawals')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default=METHOD_BANK)
    account_details = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Withdrawal {self.amount} AZN by {self.guide}'
