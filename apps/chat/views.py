from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q, Max
from .models import ChatMessage
from apps.accounts.models import User


@login_required
def inbox(request):
    user = request.user

    # Get all unique conversation partners
    partners_sent = ChatMessage.objects.filter(sender=user).values_list('receiver', flat=True).distinct()
    partners_recv = ChatMessage.objects.filter(receiver=user).values_list('sender', flat=True).distinct()
    partner_ids = set(list(partners_sent) + list(partners_recv))
    partners = User.objects.filter(id__in=partner_ids)

    conversations = []
    for partner in partners:
        last_msg = ChatMessage.objects.filter(
            Q(sender=user, receiver=partner) | Q(sender=partner, receiver=user)
        ).order_by('-created_at').first()
        unread_count = ChatMessage.objects.filter(sender=partner, receiver=user, is_read=False).count()
        conversations.append({
            'partner': partner,
            'last_message': last_msg,
            'unread': unread_count,
        })

    conversations.sort(key=lambda x: x['last_message'].created_at if x['last_message'] else None, reverse=True)

    return render(request, 'chat/inbox.html', {'conversations': conversations})


@login_required
def conversation(request, partner_id):
    partner = get_object_or_404(User, pk=partner_id)
    user = request.user

    if partner == user:
        from django.contrib import messages as django_messages
        django_messages.error(request, "You can't message yourself.")
        return redirect('chat:inbox')

    messages_qs = ChatMessage.objects.filter(
        Q(sender=user, receiver=partner) | Q(sender=partner, receiver=user)
    ).order_by('created_at')

    # Mark as read
    messages_qs.filter(sender=partner, is_read=False).update(is_read=True)

    return render(request, 'chat/conversation.html', {
        'partner': partner,
        'messages': messages_qs,
        'user': user,
    })


@login_required
@require_POST
def send_message(request, partner_id):
    partner = get_object_or_404(User, pk=partner_id)

    if partner == request.user:
        return JsonResponse({'error': 'Cannot message yourself'}, status=400)

    content = request.POST.get('content', '').strip()

    if not content:
        return JsonResponse({'error': 'Empty message'}, status=400)

    msg = ChatMessage.objects.create(
        sender=request.user,
        receiver=partner,
        content=content,
    )

    from apps.core.models import Notification
    Notification.objects.create(
        user=partner,
        notification_type='message',
        title=f'New message from {request.user.get_full_name() or request.user.username}',
        message=content[:100],
        link=f'/chat/{request.user.pk}/',  # link to conversation with sender
    )

    return JsonResponse({
        'id': msg.pk,
        'content': msg.content,
        'created_at': msg.created_at.strftime('%H:%M'),
        'sender_id': request.user.pk,
    })


@login_required
def poll_messages(request, partner_id):
    """AJAX polling: returns new messages since a given message ID."""
    partner = get_object_or_404(User, pk=partner_id)
    since_id = int(request.GET.get('since', 0))

    new_messages = ChatMessage.objects.filter(
        Q(sender=request.user, receiver=partner) | Q(sender=partner, receiver=request.user),
        pk__gt=since_id
    ).order_by('created_at')

    new_messages.filter(sender=partner, is_read=False).update(is_read=True)

    data = [{
        'id': m.pk,
        'content': m.content,
        'sender_id': m.sender_id,
        'created_at': m.created_at.strftime('%H:%M'),
        'is_own': m.sender == request.user,
    } for m in new_messages]

    return JsonResponse({'messages': data})


@login_required
def start_chat(request, user_id):
    """Redirect to conversation, starting a new one if needed."""
    return redirect('chat:conversation', partner_id=user_id)
