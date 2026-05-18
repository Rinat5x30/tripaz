from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, TouristProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_banned', 'date_joined']
    list_filter = ['role', 'is_banned', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    fieldsets = UserAdmin.fieldsets + (
        ('TripAZ', {'fields': ('role', 'phone', 'avatar', 'is_banned')}),
    )
    actions = ['ban_users', 'unban_users']

    def ban_users(self, request, queryset):
        queryset.update(is_banned=True)
        self.message_user(request, f'{queryset.count()} users banned.')
    ban_users.short_description = 'Ban selected users'

    def unban_users(self, request, queryset):
        queryset.update(is_banned=False)
        self.message_user(request, f'{queryset.count()} users unbanned.')
    unban_users.short_description = 'Unban selected users'


@admin.register(TouristProfile)
class TouristProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'country', 'updated_at']
    search_fields = ['user__username', 'user__email', 'country']
