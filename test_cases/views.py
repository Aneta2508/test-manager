from django.shortcuts import render, get_object_or_404, redirect
from .models import Project, TestPlan, TestCase
from .forms import ProjectForm, TestPlanForm, TestCaseForm

# ===== PROJEKTY =====

def project_list(request):
    projects = Project.objects.all()
    return render(request, 'test_cases/project_list.html', {'projects': projects})

def project_add(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('test_cases:project_list')
    else:
        form = ProjectForm()
    return render(request, 'test_cases/project_form.html', {'form': form, 'title': 'Dodaj projekt'})

def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    test_plans = project.test_plans.all()
    return render(request, 'test_cases/project_detail.html', {
        'project': project,
        'test_plans': test_plans,
    })

def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('test_cases:project_detail', pk=pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'test_cases/project_form.html', {'form': form, 'title': 'Edytuj projekt'})

def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project.delete()
        return redirect('test_cases:project_list')
    return render(request, 'test_cases/project_confirm_delete.html', {'project': project})

# ===== PLANY TESTÓW =====

def test_plan_add(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk)
    if request.method == 'POST':
        form = TestPlanForm(request.POST)
        if form.is_valid():
            test_plan = form.save(commit=False)
            test_plan.project = project
            test_plan.save()
            return redirect('test_cases:project_detail', pk=project_pk)
    else:
        form = TestPlanForm()
    return render(request, 'test_cases/test_plan_form.html', {
        'form': form,
        'title': 'Dodaj plan testów',
        'project': project
    })

def test_plan_edit(request, pk):
    test_plan = get_object_or_404(TestPlan, pk=pk)
    if request.method == 'POST':
        form = TestPlanForm(request.POST, instance=test_plan)
        if form.is_valid():
            form.save()
            return redirect('test_cases:project_detail', pk=test_plan.project.pk)
    else:
        form = TestPlanForm(instance=test_plan)
    return render(request, 'test_cases/test_plan_form.html', {
        'form': form,
        'title': 'Edytuj plan testów',
        'project': test_plan.project
    })

def test_plan_delete(request, pk):
    test_plan = get_object_or_404(TestPlan, pk=pk)
    project_pk = test_plan.project.pk
    if request.method == 'POST':
        test_plan.delete()
        return redirect('test_cases:project_detail', pk=project_pk)
    return render(request, 'test_cases/test_plan_confirm_delete.html', {'test_plan': test_plan})

# ===== PRZYPADKI TESTOWE =====

def test_case_add(request, plan_pk):
    test_plan = get_object_or_404(TestPlan, pk=plan_pk)
    if request.method == 'POST':
        form = TestCaseForm(request.POST, request.FILES)
        if form.is_valid():
            test_case = form.save(commit=False)
            test_case.test_plan = test_plan
            test_case.save()
            return redirect('test_cases:project_detail', pk=test_plan.project.pk)
    else:
        form = TestCaseForm()
    return render(request, 'test_cases/test_case_form.html', {
        'form': form,
        'title': 'Dodaj przypadek testowy',
        'test_plan': test_plan
    })

def test_case_detail(request, pk):
    test_case = get_object_or_404(TestCase, pk=pk)
    return render(request, 'test_cases/test_case_detail.html', {'test_case': test_case})

def test_case_edit(request, pk):
    test_case = get_object_or_404(TestCase, pk=pk)
    if request.method == 'POST':
        form = TestCaseForm(request.POST, request.FILES, instance=test_case)
        if form.is_valid():
            form.save()
            return redirect('test_cases:test_case_detail', pk=pk)
    else:
        form = TestCaseForm(instance=test_case)
    return render(request, 'test_cases/test_case_form.html', {
        'form': form,
        'title': 'Edytuj przypadek testowy',
        'test_plan': test_case.test_plan
    })

def test_case_delete(request, pk):
    test_case = get_object_or_404(TestCase, pk=pk)
    project_pk = test_case.test_plan.project.pk
    if request.method == 'POST':
        test_case.delete()
        return redirect('test_cases:project_detail', pk=project_pk)
    return render(request, 'test_cases/test_case_confirm_delete.html', {'test_case': test_case})
