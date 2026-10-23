from django.urls import path

from . import views

app_name = 'chat'

urlpatterns = [
    # Canonical chat URL is the site root (/); /chat/ is only an alias.
    path('', views.chat_page, name='page'),
    path('open/', views.chat_open, name='open'),
    path('new/', views.chat_new, name='new'),
    path('send/', views.chat_send, name='send'),
    path('leave/', views.chat_leave, name='leave'),
    path('history/', views.chat_history, name='history'),
    # Old links select the conversation then bounce to the root URL.
    path('<slug:token>/', views.chat_open_link, name='session'),
    path('<slug:token>/delete/', views.chat_delete, name='session_delete'),
]
