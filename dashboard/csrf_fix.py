"""
Temporary CSRF exempt view for admin login
"""
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.sites import AdminSite

# Override admin site to make login CSRF exempt temporarily
class CSRFExemptAdminSite(AdminSite):
    @csrf_exempt
    def login(self, request, extra_context=None):
        return super().login(request, extra_context)

# Replace default admin site
from django.contrib import admin
admin.site.__class__ = CSRFExemptAdminSite
