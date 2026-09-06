from django.shortcuts import render, get_object_or_404
from .models import Build

def build_list(request):
    builds = Build.objects.all()
    builds_success = builds.filter(status='SUCCESS').count()
    builds_failed = builds.filter(status='FAILED').count()
    return render(request, 'builds/build_list.html', {
        'builds': builds,
        'builds_success': builds_success,
        'builds_failed': builds_failed,
    })

def build_detail(request, pk):
    build = get_object_or_404(Build, pk=pk)
    return render(request, 'builds/build_detail.html', {'build': build})