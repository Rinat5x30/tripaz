from django import forms
from .models import GuideProfile, Tour, TourImage, VerificationDocument
from apps.accounts.models import User


class GuideRegisterForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    phone = forms.CharField(max_length=20)
    passport = forms.FileField(label='Passport Copy', required=False)
    license_doc = forms.FileField(label='Guide License / Certificate', required=False)
    photo = forms.ImageField(label='Professional Photo', required=False)
    languages = forms.MultipleChoiceField(
        choices=GuideProfile.LANGUAGE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label='Languages Spoken',
    )

    class Meta:
        model = GuideProfile
        fields = ['bio', 'tagline', 'city', 'experience_years', 'license_number', 'has_certificate']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['phone'].initial = getattr(user, 'phone', '')

    def clean_languages(self):
        langs = self.cleaned_data.get('languages', [])
        if not langs:
            raise forms.ValidationError('Please select at least one language.')
        return ','.join(langs)


class GuideProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    phone = forms.CharField(max_length=20, required=False)
    avatar = forms.ImageField(required=False)

    class Meta:
        model = GuideProfile
        fields = ['bio', 'tagline', 'city', 'languages', 'experience_years', 'has_certificate', 'cover_image']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['phone'].initial = user.phone
        lang_choices = GuideProfile.LANGUAGE_CHOICES
        self.fields['languages'] = forms.MultipleChoiceField(
            choices=lang_choices,
            widget=forms.CheckboxSelectMultiple,
            initial=self.instance.get_languages_list() if self.instance.pk else ['english'],
        )

    def clean_languages(self):
        langs = self.cleaned_data.get('languages', [])
        if not langs:
            raise forms.ValidationError('Select at least one language.')
        return ','.join(langs)

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            self.user.phone = self.cleaned_data.get('phone', '')
            if self.cleaned_data.get('avatar'):
                self.user.avatar = self.cleaned_data['avatar']
            if commit:
                self.user.save()
                profile.save()
        return profile


class TourForm(forms.ModelForm):
    class Meta:
        model = Tour
        fields = ['title', 'category', 'description', 'duration_hours', 'max_people',
                  'price_per_person', 'location', 'meeting_point', 'itinerary',
                  'included', 'not_included', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'itinerary': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Step 1: Meet at main entrance\nStep 2: Walk through the Old City\nStep 3: ...'}),
            'included': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Professional guide\nEntrance tickets\nBottled water'}),
            'not_included': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Meals\nPersonal expenses\nTransport'}),
        }


class TourImageForm(forms.ModelForm):
    class Meta:
        model = TourImage
        fields = ['image', 'caption']


class GuideSearchForm(forms.Form):
    q = forms.CharField(required=False, label='Search')
    city = forms.ChoiceField(
        required=False,
        choices=[('', 'Any City')] + GuideProfile.CITY_CHOICES
    )
    language = forms.ChoiceField(
        required=False,
        choices=[('', 'Any Language')] + GuideProfile.LANGUAGE_CHOICES
    )
    min_rating = forms.DecimalField(required=False, min_value=0, max_value=5, label='Min Rating')
