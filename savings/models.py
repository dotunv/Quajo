import uuid

from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Tier(models.Model):
    name = models.CharField(max_length=50)
    deposit_amount = models.DecimalField(decimal_places=2, max_digits=10)
    payout_percentage = models.DecimalField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - ${self.deposit_amount}"

    @property
    def payout_amount(self):
        """Calculate payout money based on tier deposit and percentage"""
        return self.deposit_amount * 12 * (self.payout_percentage / 100)


class SavingsQueue(models.Model):
    STATUS_CHOICES = (
        ('pending', 'pending'),
        ('active', 'Active'),
        ('completed', 'Completed')
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_queues')
    tier = models.ForeignKey(Tier, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Queue {self.id} - {self.get_status_display()}"

    @property
    def total_members(self):
        return self.queue_members.count()

    @property
    def is_full(self):
        return self.total_members >= 12

    @property
    def total_amount(self):
        return self.tier.deposit_amount * self.total_members

    @property
    def payout_amount(self):
        return self.tier.payout_amount


class QueueMember(models.Model):
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('paid_out', 'Paid Out'),
    )

    queue = models.ForeignKey(SavingsQueue, on_delete=models.CASCADE, related_name='queue_members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='queue_memberships')
    position = models.PositiveIntegerField()
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='pending')
    payment_proof = models.ImageField(upload_to='payment_proofs/', blank=True, null=True)
    payment_tx_id = models.CharField(max_length=100, blank=True, null=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    payout_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('queue', 'position')
        ordering = ['position']

    def __str__(self):
        return f"{self.user.username} - Position {self.position}"
