from django.db import migrations

def create_initial_tiers(apps, schema_editor):
    Tier = apps.get_model('savings', 'Tier')
    
    tiers_data = [
        {
            'name': 'Bronze Saver',
            'description': 'Start your savings journey with our entry-level tier. Perfect for testing the waters.',
            'deposit_amount': 100.00,
            'payout_percentage': 10.00,
        },
        {
            'name': 'Silver Saver',
            'description': 'Mid-level tier with balanced returns. Great for consistent savers.',
            'deposit_amount': 250.00,
            'payout_percentage': 15.00,
        },
        {
            'name': 'Gold Saver',
            'description': 'Premium tier with highest returns. For serious savers looking for maximum benefits.',
            'deposit_amount': 500.00,
            'payout_percentage': 20.00,
        },
    ]
    
    for tier_data in tiers_data:
        Tier.objects.create(**tier_data)

def remove_initial_tiers(apps, schema_editor):
    Tier = apps.get_model('savings', 'Tier')
    Tier.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('savings', '0001_initial'),  # Replace with your actual initial migration name
    ]

    operations = [
        migrations.RunPython(create_initial_tiers, remove_initial_tiers),
    ] 