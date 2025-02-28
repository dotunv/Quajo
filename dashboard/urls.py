from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('notifications/', views.notifications, name='notifications'),
    path('transactions/', views.transactions, name='transactions'),
]