from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_TOURIST = 'tourist'
    ROLE_GUIDE = 'guide'
    ROLE_ADMIN = 'admin'
    ROLE_SUPPORT = 'support'

    ROLE_CHOICES = [
        (ROLE_TOURIST, 'Tourist'),
        (ROLE_GUIDE, 'Guide'),
        (ROLE_ADMIN, 'Admin'),
        (ROLE_SUPPORT, 'Support'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_TOURIST)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_banned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.username} ({self.role})'

    @property
    def is_tourist(self):
        return self.role == self.ROLE_TOURIST

    @property
    def is_guide(self):
        return self.role == self.ROLE_GUIDE

    @property
    def is_support(self):
        return self.role == self.ROLE_SUPPORT


class TouristProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tourist_profile')
    country = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Tourist: {self.user.username}'
