from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('profile/', views.profile_update, name='profile'),
    path('password/', views.password_change, name='password'),
]
