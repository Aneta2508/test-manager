from django.shortcuts import render
from django.utils import timezone
from test_cases.models import Project, TestCase
from defects.models import Defect

def index(request):
    # Statystyki ogólne
    active_projects = Project.objects.filter(status='IN_PROGRESS').count()
    total_cases = TestCase.objects.count()
    open_defects = Defect.objects.filter(status='NEW').count()

    # Średni postęp wszystkich projektów
    projects = Project.objects.all()
    if projects:
        avg_progress = round(sum(p.get_progress() for p in projects) / projects.count())
    else:
        avg_progress = 0

    # Dane do wykresu kołowego
    passed = TestCase.objects.filter(status='PASS').count()
    failed = TestCase.objects.filter(status='FAIL').count()
    ongoing = TestCase.objects.filter(status='ONGOING').count()
    blocked = TestCase.objects.filter(status='BLOCKED').count()
    not_started = TestCase.objects.filter(status='NOT_STARTED').count()

    # 3 ostatnie projekty
    recent_projects = Project.objects.all()[:3]

    # Projekty z przekroczonym terminem
    overdue_projects = Project.objects.filter(
        deadline__lt=timezone.now().date(),
        status='IN_PROGRESS'
    )

    return render(request, 'dashboard/index.html', {
        'active_projects': active_projects,
        'total_cases': total_cases,
        'open_defects': open_defects,
        'avg_progress': avg_progress,
        'passed': passed,
        'failed': failed,
        'ongoing': ongoing,
        'blocked': blocked,
        'not_started': not_started,
        'recent_projects': recent_projects,
        'overdue_projects': overdue_projects,
    })
