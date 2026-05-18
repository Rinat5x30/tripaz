from .models import Notification
from apps.chat.models import ChatMessage


def notifications_processor(request):
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
        unread_messages = ChatMessage.objects.filter(receiver=request.user, is_read=False).count()
        return {
            'unread_notifications': unread_count,
            'recent_notifications': notifications,
            'unread_messages': unread_messages,
        }
    return {'unread_notifications': 0, 'recent_notifications': [], 'unread_messages': 0}
