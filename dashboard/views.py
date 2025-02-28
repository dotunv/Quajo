from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from savings.models import QueueMember, SavingsQueue, Tier
from .models import Transaction, Notification
from django.db import models

# Create your views here.
@login_required
def home(request):
    # Get user's active queues
    active_memberships = QueueMember.objects.filter(
        user=request.user,
        payment_status='confirmed',
        queue__status='active'
    ).select_related('queue', 'queue__tier')

    # Get recent transactions
    recent_transactions = Transaction.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]

    # Get unread notifications
    notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by('-created_at')[:5]

    # Calculate statistics
    total_invested = Transaction.objects.filter(
        user=request.user,
        transaction_type='deposit'
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_earned = Transaction.objects.filter(
        user=request.user,
        transaction_type='payout'
    ).aggregate(total=Sum('amount'))['total'] or 0

    active_queue_count = active_memberships.count()

    # Get queue completion progress
    queues_progress = []
    for membership in active_memberships:
        queue = membership.queue
        progress = {
            'queue': queue,
            'tier': queue.tier,
            'total_members': queue.total_members,
            'percentage': (queue.total_members / 12) * 100,
            'position': membership.position
        }
        queues_progress.append(progress)

    # Fix: Change the annotation syntax
    available_tiers = Tier.objects.annotate(
        active_queues=Count(
            'savingsqueue',
            filter=models.Q(savingsqueue__status='active')
        )
    ).filter(active_queues__gt=0)[:3]

    context = {
        'active_memberships': active_memberships,
        'recent_transactions': recent_transactions,
        'notifications': notifications,
        'total_invested': total_invested,
        'total_earned': total_earned,
        'active_queue_count': active_queue_count,
        'queues_progress': queues_progress,
        'available_tiers': available_tiers,
    }
    return render(request, 'dashboard/home.html', context)

@login_required
def transactions(request):
    transactions = Transaction.objects.filter(
        user=request.user
    ).order_by('-created_at')

    # Group transactions by month
    grouped_transactions = {}
    for transaction in transactions:
        month_key = transaction.created_at.strftime('%B %Y')
        if month_key not in grouped_transactions:
            grouped_transactions[month_key] = []
        grouped_transactions[month_key].append(transaction)

    context = {
        'grouped_transactions': grouped_transactions,
    }
    return render(request, 'dashboard/transactions.html', context)

@login_required
def notifications(request):
    # Mark all notifications as read
    Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(is_read=True)

    # Get all notifications
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')

    context = {
        'notifications': notifications,
    }
    return render(request, 'dashboard/notifications.html', context)