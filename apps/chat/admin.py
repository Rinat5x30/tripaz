from django.contrib import admin
from .models import ChatMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'content_preview', 'is_read', 'created_at']
    list_filter = ['is_read']
    search_fields = ['sender__username', 'receiver__username']

    def content_preview(self, obj):
        return obj.content[:60]
    content_preview.short_description = 'Message'
