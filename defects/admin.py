from django.contrib import admin
from .models import Defect

@admin.register(Defect)
class DefectAdmin(admin.ModelAdmin):
    list_display = ['name', 'test_case', 'severity', 'status', 'reported_at']
    list_filter = ['severity', 'status']
    search_fields = ['name', 'description']
