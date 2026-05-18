from django import forms
from .models import Booking, Withdrawal
from apps.guides.models import Tour


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['booking_date', 'booking_time', 'people_count', 'tour', 'special_requests']
        widgets = {
            'booking_date': forms.DateInput(attrs={'type': 'date'}),
            'booking_time': forms.TimeInput(attrs={'type': 'time'}),
            'special_requests': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any special requests or notes...'}),
        }

    def __init__(self, guide=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if guide:
            self.fields['tour'].queryset = Tour.objects.filter(guide=guide, is_active=True)
            self.fields['tour'].required = False
            self.fields['tour'].empty_label = '— No specific tour, hourly booking —'


class MockPaymentForm(forms.Form):
    CARD_CHOICES = [
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
        ('amex', 'American Express'),
    ]
    card_type = forms.ChoiceField(choices=CARD_CHOICES, widget=forms.RadioSelect)
    card_number = forms.CharField(
        max_length=19,
        widget=forms.TextInput(attrs={'placeholder': '4242 4242 4242 4242'})
    )
    cardholder_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'John Smith'})
    )
    expiry = forms.CharField(
        max_length=5,
        widget=forms.TextInput(attrs={'placeholder': 'MM/YY'})
    )
    cvv = forms.CharField(
        max_length=4,
        widget=forms.PasswordInput(attrs={'placeholder': '•••'})
    )


class WithdrawalForm(forms.ModelForm):
    class Meta:
        model = Withdrawal
        fields = ['amount', 'method', 'account_details']
        widgets = {
            'account_details': forms.TextInput(attrs={'placeholder': 'Bank account / wallet number'})
        }
