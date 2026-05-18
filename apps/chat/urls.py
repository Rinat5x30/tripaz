from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('<int:partner_id>/', views.conversation, name='conversation'),
    path('<int:partner_id>/send/', views.send_message, name='send'),
    path('<int:partner_id>/poll/', views.poll_messages, name='poll'),
    path('start/<int:user_id>/', views.start_chat, name='start'),
]
