from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome_view, name='welcome'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('home/', views.home, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('help/', views.help_view, name='help'),
    path('report/', views.report_view, name='report'),
    path('tickets/', views.ticket_list, name='tickets'),
    path('activity/', views.activity_list, name='activity'),
    path('announcements/', views.announcement_list, name='announcements'),
    path('announcements/<int:pk>/update/', views.announcement_update, name='announcement_update'),
    path('announcements/<int:pk>/edit/', views.announcement_edit, name='announcement_edit'),
    path('tickets/<int:pk>/update/', views.ticket_update, name='ticket_update'),
]
