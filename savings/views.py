from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Tier, SavingsQueue, QueueMember
from .forms import PaymentConfirmationForm
from dashboard.models import Notification, Transaction


@login_required
def tier_list(request):
    tiers = Tier.objects.all()
    return render(request, 'savings/tiers.html', {'tiers': tiers})


@login_required
def join_tier(request, tier_id):
    tier = get_object_or_404(Tier, id=tier_id)

    # Check if user already has a pending queue membership for this tier
    existing_pending = QueueMember.objects.filter(
        user=request.user,
        payment_status='pending',
        queue__tier=tier
    ).exists()

    if existing_pending:
        messages.warning(request, 'You already have a pending queue join for this tier. Please complete your payment.')
        return redirect('savings:my_queues')

    # Look for an available queue or create a new one
    available_queue = SavingsQueue.objects.filter(
        tier=tier,
        status='active'
    ).exclude(
        queue_members__user=request.user
    ).first()

    # If no available queue, create a new one
    if not available_queue or available_queue.total_members >= 12:
        new_queue = SavingsQueue.objects.create(
            creator=request.user,
            tier=tier,
            status='pending'
        )
        position = 1  # Creator is first
        queue = new_queue
    else:
        queue = available_queue
        # Get the next available position
        position = QueueMember.objects.filter(queue=queue).count() + 1

    # Create queue membership
    queue_member = QueueMember.objects.create(
        queue=queue,
        user=request.user,
        position=position
    )

    # If queue is now full, mark as active
    if queue.total_members >= 12:
        queue.status = 'active'
        queue.save()

    # Create notification
    Notification.objects.create(
        user=request.user,
        notification_type='queue_joined',
        message=f'You have joined a {tier.name} tier queue. Please complete your payment.'
    )

    messages.success(request, f'You have joined a {tier.name} tier queue. Please complete your payment.')
    return redirect('savings:confirm_payment', queue_id=queue.id)


@login_required
def confirm_payment(request, queue_id):
    queue = get_object_or_404(SavingsQueue, id=queue_id)
    queue_member = get_object_or_404(QueueMember, queue=queue, user=request.user)

    if queue_member.payment_status != 'pending':
        messages.info(request, 'Your payment has already been processed.')
        return redirect('savings:queue_detail', queue_id=queue.id)

    if request.method == 'POST':
        form = PaymentConfirmationForm(request.POST, request.FILES, instance=queue_member)
        if form.is_valid():
            queue_member = form.save(commit=False)
            queue_member.payment_status = 'confirmed'
            queue_member.save()

            # Create transaction record
            Transaction.objects.create(
                user=request.user,
                transaction_type='deposit',
                amount=queue.tier.deposit_amount,
                description=f'Deposit for {queue.tier.name} tier queue',
                transaction_id=queue_member.payment_tx_id
            )

            # Create notification
            Notification.objects.create(
                user=request.user,
                notification_type='payment_confirmed',
                message=f'Your payment for the {queue.tier.name} tier has been confirmed.'
            )

            # Check if this completes the queue and handle payouts if needed
            if queue.is_full and queue.status == 'pending':
                queue.status = 'active'
                queue.save()

                # Notify the creator that their queue is ready for payout
                Notification.objects.create(
                    user=queue.creator,
                    notification_type='payout_ready',
                    message=f'Your {queue.tier.name} tier queue is now full and ready for payout!'
                )

            messages.success(request, 'Your payment has been confirmed!')
            return redirect('savings:queue_detail', queue_id=queue.id)
    else:
        form = PaymentConfirmationForm(instance=queue_member)

    context = {
        'form': form,
        'queue': queue,
        'queue_member': queue_member,
    }
    return render(request, 'savings/confirm_payment.html', context)


@login_required
def queue_detail(request, queue_id):
    queue = get_object_or_404(SavingsQueue, id=queue_id)
    queue_members = QueueMember.objects.filter(queue=queue).order_by('position')

    # Get the current user's membership in this queue, if any
    try:
        user_membership = QueueMember.objects.get(queue=queue, user=request.user)
    except QueueMember.DoesNotExist:
        user_membership = None

    context = {
        'queue': queue,
        'queue_members': queue_members,
        'user_membership': user_membership,
    }
    return render(request, 'savings/queue_detail.html', context)


@login_required
def my_queues(request):
    # Get all queues the user is a member of
    memberships = QueueMember.objects.filter(user=request.user).select_related('queue')

    # Group by payment status
    pending_payments = [m for m in memberships if m.payment_status == 'pending']
    active_queues = [m for m in memberships if m.payment_status == 'confirmed' and m.queue.status == 'active']
    completed_queues = [m for m in memberships if m.payment_status == 'confirmed' and m.queue.status == 'completed']

    context = {
        'pending_payments': pending_payments,
        'active_queues': active_queues,
        'completed_queues': completed_queues,
    }
    return render(request, 'savings/my_queues.html', context)


@login_required
def global_queue(request):
    # Get all active and pending queues
    queues = SavingsQueue.objects.filter(
        status__in=['active', 'pending']
    ).select_related('tier', 'creator').prefetch_related('queue_members')
    
    # Group queues by tier
    queues_by_tier = {}
    for queue in queues:
        if queue.tier not in queues_by_tier:
            queues_by_tier[queue.tier] = []
        queues_by_tier[queue.tier].append(queue)
    
    context = {
        'queues_by_tier': queues_by_tier,
    }
    return render(request, 'savings/global_queue.html', context)