from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['tourist', 'guide', 'rating', 'title', 'is_visible', 'created_at']
    list_filter = ['rating', 'is_visible']
    search_fields = ['tourist__username', 'guide__user__username', 'title']
    actions = ['hide_reviews', 'show_reviews']

    def hide_reviews(self, request, queryset):
        queryset.update(is_visible=False)
    hide_reviews.short_description = 'Hide selected reviews'

    def show_reviews(self, request, queryset):
        queryset.update(is_visible=True)
    show_reviews.short_description = 'Show selected reviews'
