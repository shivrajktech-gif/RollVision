import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RollVision.settings')
django.setup()

from dashboard.models import Department

# Add departments
departments = [
    {'name': 'Mechanical Engineering', 'code': 'ME'},
    {'name': 'Information Technology', 'code': 'IT'},
    {'name': 'Electronics and Telecommunication', 'code': 'ENTC'},
    {'name': 'Master of Business Administration', 'code': 'MBA'},
    {'name': 'Master of Computer Applications', 'code': 'MCA'},
]

for dept_data in departments:
    dept, created = Department.objects.get_or_create(
        code=dept_data['code'],
        defaults={'name': dept_data['name']}
    )
    if created:
        print(f"✅ Created: {dept.name} ({dept.code})")
    else:
        print(f"ℹ️  Already exists: {dept.name} ({dept.code})")

print("\n📋 All departments in database:")
for d in Department.objects.all().order_by('code'):
    print(f"  - {d.code}: {d.name}")
