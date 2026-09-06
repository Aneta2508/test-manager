from django.contrib import admin
from .models import Build

@admin.register(Build)
class BuildAdmin(admin.ModelAdmin):
    list_display = ['build_number', 'commit_id', 'status', 'deployed_at']
    list_filter = ['status']
    search_fields = ['build_number', 'commit_id']
