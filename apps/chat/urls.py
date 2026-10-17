from django.urls import path

from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_page, name='page'),
    path('new/', views.chat_new, name='new'),
    path('send/', views.chat_send, name='send'),
    path('<int:pk>/', views.chat_page, name='session'),
    path('<int:pk>/delete/', views.chat_delete, name='session_delete'),
]
