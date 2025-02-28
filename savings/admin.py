from django.contrib import admin
from .models import Tier, SavingsQueue, QueueMember

@admin.register(Tier)
class TierAdmin(admin.ModelAdmin):
    list_display = ('name', 'deposit_amount', 'payout_percentage', 'created_at')
    search_fields = ('name',)
