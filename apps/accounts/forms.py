from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, TouristProfile


class TouristRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    country = forms.CharField(max_length=100, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.role = User.ROLE_TOURIST
        if commit:
            user.save()
            TouristProfile.objects.create(
                user=user,
                country=self.cleaned_data.get('country', '')
            )
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Username or email', 'autofocus': True})
    )
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


class TouristProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    phone = forms.CharField(max_length=20, required=False)
    avatar = forms.ImageField(required=False)

    class Meta:
        model = TouristProfile
        fields = ['country', 'bio']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['phone'].initial = user.phone

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
