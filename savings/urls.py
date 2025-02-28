from django.urls import path

from savings import views

app_name = 'savings'

urlpatterns = [
    path('tiers/', views.tier_list, name='tier_list'),
    path('join/<int:tier_id>/', views.join_tier, name='join_tier'),
    path('payment/confirm/<uuid:queue_id>/', views.confirm_payment, name='confirm_payment'),
    path('queue/<uuid:queue_id>/', views.queue_detail, name='queue_detail'),
    path('queues/', views.my_queues, name='my_queues'),
    path('global-queue/', views.global_queue, name='global_queue'),
]
