from django.contrib import admin
from .models import Project, TestPlan, TestCase

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['project_number', 'name', 'status', 'deadline', 'created_at']
    list_filter = ['status']
    search_fields = ['project_number', 'name']

@admin.register(TestPlan)
class TestPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'created_at']
    search_fields = ['name']

@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ['test_id', 'name', 'test_plan', 'priority', 'status']
    list_filter = ['status', 'priority']
    search_fields = ['test_id', 'name']