import os
import django
from datetime import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RollVision.settings')
django.setup()

from dashboard.models import LecturePeriod

# Add lecture periods with breaks
periods = [
    {'period_number': 1, 'start_time': time(9, 0), 'end_time': time(10, 0), 'name': 'Period 1'},
    {'period_number': 2, 'start_time': time(10, 0), 'end_time': time(11, 0), 'name': 'Period 2'},
    # 10 min break (11:00 - 11:10)
    {'period_number': 3, 'start_time': time(11, 10), 'end_time': time(12, 10), 'name': 'Period 3'},
    {'period_number': 4, 'start_time': time(12, 10), 'end_time': time(13, 10), 'name': 'Period 4'},
    # 50 min lunch break (1:10 PM - 2:00 PM)
    {'period_number': 5, 'start_time': time(14, 0), 'end_time': time(15, 0), 'name': 'Period 5'},
    {'period_number': 6, 'start_time': time(15, 0), 'end_time': time(16, 0), 'name': 'Period 6'},
]

for period_data in periods:
    period, created = LecturePeriod.objects.get_or_create(
        period_number=period_data['period_number'],
        defaults={
            'name': period_data['name'],
            'start_time': period_data['start_time'],
            'end_time': period_data['end_time']
        }
    )
    if created:
        print(f"✅ Created: {period.name} ({period.start_time.strftime('%I:%M %p')} - {period.end_time.strftime('%I:%M %p')})")
    else:
        print(f"ℹ️  Already exists: {period.name} ({period.start_time.strftime('%I:%M %p')} - {period.end_time.strftime('%I:%M %p')})")

print("\n📋 All lecture periods:")
for p in LecturePeriod.objects.all().order_by('period_number'):
    print(f"  - {p.name}: {p.start_time.strftime('%I:%M %p')} - {p.end_time.strftime('%I:%M %p')}")
