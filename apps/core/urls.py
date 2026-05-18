from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('support/', views.support_ticket_create, name='support'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/verify/<int:guide_pk>/', views.admin_verify_guide, name='admin_verify_guide'),
    path('admin-panel/users/', views.admin_users, name='admin_users'),
    path('admin-panel/tickets/', views.admin_tickets, name='admin_tickets'),
]
