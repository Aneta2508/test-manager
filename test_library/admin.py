from django.contrib import admin
from .models import LibraryTestCase

@admin.register(LibraryTestCase)
class LibraryTestCaseAdmin(admin.ModelAdmin):
    list_display = ['test_id', 'name', 'priority', 'created_at']
    list_filter = ['priority']
    search_fields = ['test_id', 'name']