from django.shortcuts import render, get_object_or_404, redirect
from .models import LibraryTestCase
from .forms import LibraryTestCaseForm
from test_cases.models import TestPlan, TestCase

def library_list(request):
    library_cases = LibraryTestCase.objects.all()
    return render(request, 'test_library/library_list.html', {'library_cases': library_cases})

def library_detail(request, pk):
    library_case = get_object_or_404(LibraryTestCase, pk=pk)
    test_plans = TestPlan.objects.all()
    return render(request, 'test_library/library_detail.html', {
        'library_case': library_case,
        'test_plans': test_plans,
    })

def library_add(request):
    if request.method == 'POST':
        form = LibraryTestCaseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('test_library:library_list')
    else:
        form = LibraryTestCaseForm()
    return render(request, 'test_library/library_form.html', {
        'form': form,
        'title': 'Dodaj test do biblioteki'
    })

def library_edit(request, pk):
    library_case = get_object_or_404(LibraryTestCase, pk=pk)
    if request.method == 'POST':
        form = LibraryTestCaseForm(request.POST, instance=library_case)
        if form.is_valid():
            form.save()
            return redirect('test_library:library_detail', pk=pk)
    else:
        form = LibraryTestCaseForm(instance=library_case)
    return render(request, 'test_library/library_form.html', {
        'form': form,
        'title': 'Edytuj test w bibliotece'
    })

def library_delete(request, pk):
    library_case = get_object_or_404(LibraryTestCase, pk=pk)
    if request.method == 'POST':
        library_case.delete()
        return redirect('test_library:library_list')
    return render(request, 'test_library/library_confirm_delete.html', {'library_case': library_case})

def library_copy_to_plan(request, pk, plan_pk):
    library_case = get_object_or_404(LibraryTestCase, pk=pk)
    test_plan = get_object_or_404(TestPlan, pk=plan_pk)

    TestCase.objects.create(
        test_plan=test_plan,
        test_id=library_case.test_id,
        name=library_case.name,
        description=library_case.description,
        preconditions=library_case.preconditions,
        steps=library_case.steps,
        expected_result=library_case.expected_result,
        priority=library_case.priority,
        status='NOT_STARTED',
    )

    return redirect('test_cases:project_detail', pk=test_plan.project.pk)
