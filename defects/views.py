from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail
from django.conf import settings
from .models import Defect
from .forms import DefectForm
from test_cases.models import TestCase

def defect_list(request):
    defects = Defect.objects.all()
    return render(request, 'defects/defect_list.html', {'defects': defects})

def defect_detail(request, pk):
    defect = get_object_or_404(Defect, pk=pk)
    return render(request, 'defects/defect_detail.html', {'defect': defect})

def defect_add(request, test_case_pk):
    test_case = get_object_or_404(TestCase, pk=test_case_pk)
    if request.method == 'POST':
        form = DefectForm(request.POST)
        if form.is_valid():
            defect = form.save(commit=False)
            defect.test_case = test_case
            defect.save()
            send_defect_notification(defect)
            return redirect('test_cases:test_case_detail', pk=test_case_pk)
    else:
        form = DefectForm()
    return render(request, 'defects/defect_form.html', {
        'form': form,
        'title': 'Zgłoś defekt',
        'test_case': test_case
    })

def defect_edit(request, pk):
    defect = get_object_or_404(Defect, pk=pk)
    if request.method == 'POST':
        form = DefectForm(request.POST, instance=defect)
        if form.is_valid():
            form.save()
            return redirect('defects:defect_detail', pk=pk)
    else:
        form = DefectForm(instance=defect)
    return render(request, 'defects/defect_form.html', {
        'form': form,
        'title': 'Edytuj defekt',
        'test_case': defect.test_case
    })

def defect_delete(request, pk):
    defect = get_object_or_404(Defect, pk=pk)
    test_case_pk = defect.test_case.pk
    if request.method == 'POST':
        defect.delete()
        return redirect('test_cases:test_case_detail', pk=test_case_pk)
    return render(request, 'defects/defect_confirm_delete.html', {'defect': defect})

def send_defect_notification(defect):
    project = defect.test_case.test_plan.project
    contacts = project.contacts.all()

    tester_emails = [c.email for c in contacts if c.role == 'TESTER']
    qa_lead_emails = [c.email for c in contacts if c.role == 'QA_LEAD']
    manager_emails = [c.email for c in contacts if c.role == 'MANAGER']
    developer_emails = [c.email for c in contacts if c.role == 'DEVELOPER']

    if defect.severity == 'CRITICAL':
        recipients = tester_emails + qa_lead_emails + manager_emails + developer_emails
        subject = f'🚨 CRITICAL: {defect.name} — blokada wdrożenia!'
    elif defect.severity == 'MAJOR':
        recipients = tester_emails + qa_lead_emails + manager_emails
        subject = f'⚠️ MAJOR: {defect.name}'
    elif defect.severity == 'MEDIUM':
        recipients = tester_emails + qa_lead_emails
        subject = f'📋 MEDIUM: {defect.name}'
    else:
        recipients = tester_emails
        subject = f'📝 MINOR: {defect.name}'

    if not recipients:
        return

    message = f"""
Zgłoszono nowy defekt w projekcie {project.project_number} — {project.name}

Defekt: {defect.name}
Waga: {defect.severity}
Status: {defect.status}
Przypadek testowy: {defect.test_case.test_id} — {defect.test_case.name}

Opis:
{defect.description}
    """

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
        fail_silently=True,
    )