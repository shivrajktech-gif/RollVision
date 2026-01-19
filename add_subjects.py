import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RollVision.settings')
django.setup()

from dashboard.models import Subject, Department

# Get CS department
cs_dept = Department.objects.get(code='CS')

# Add engineering subjects
subjects = [
    {'name': 'Natural Language Processing', 'code': 'NLP', 'credits': 4, 'semester': 7},
    {'name': 'High Performance Computing', 'code': 'HPC', 'credits': 4, 'semester': 7},
    {'name': 'Business Intelligence', 'code': 'BI', 'credits': 3, 'semester': 6},
    {'name': 'Deep Learning', 'code': 'DL', 'credits': 4, 'semester': 8},
]

for subj_data in subjects:
    subj, created = Subject.objects.get_or_create(
        code=subj_data['code'],
        defaults={
            'name': subj_data['name'],
            'credits': subj_data['credits'],
            'semester': subj_data['semester'],
            'department': cs_dept
        }
    )
    if created:
        print(f"✅ Created: {subj.code} - {subj.name}")
    else:
        print(f"ℹ️  Already exists: {subj.code} - {subj.name}")

print("\n📋 All subjects in database:")
for s in Subject.objects.all().order_by('code'):
    print(f"  - {s.code}: {s.name} ({s.credits} credits)")
