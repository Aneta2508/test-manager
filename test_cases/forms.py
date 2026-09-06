from django import forms
from .models import Project, TestPlan, TestCase
from contacts.models import Contact

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['project_number', 'name', 'description', 'deadline', 'status', 'contacts']
        widgets = {
            'project_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'np. MO00123'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'np. Testy sklepu internetowego'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Opis projektu...'
            }),
            'deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'contacts': forms.CheckboxSelectMultiple(),
        }
        labels = {
            'project_number': 'Numer projektu',
            'name': 'Nazwa projektu',
            'description': 'Opis',
            'deadline': 'Termin',
            'status': 'Status',
            'contacts': 'Przypisane kontakty',
        }


class TestPlanForm(forms.ModelForm):
    class Meta:
        model = TestPlan
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'np. Testy logowania'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Opis planu testów...'
            }),
        }
        labels = {
            'name': 'Nazwa planu',
            'description': 'Opis',
        }


class TestCaseForm(forms.ModelForm):
    class Meta:
        model = TestCase
        fields = [
            'test_id', 'name', 'description', 'preconditions',
            'steps', 'expected_result', 'priority', 'status',
            'comment', 'executed_at', 'environment', 'screenshot'
        ]
        widgets = {
            'test_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'np. TC001'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'np. Logowanie poprawnym hasłem'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Opis przypadku testowego...'
            }),
            'preconditions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'np. Użytkownik musi być zarejestrowany'
            }),
            'steps': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': '1. Wejdź na stronę logowania\n2. Wpisz email\n3. Wpisz hasło\n4. Kliknij Zaloguj'
            }),
            'expected_result': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'np. Użytkownik zostaje zalogowany i przekierowany na dashboard'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Dodatkowy komentarz...'
            }),
            'executed_at': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'environment': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'np. Windows 11, Chrome 120'
            }),
            'screenshot': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'test_id': 'ID przypadku testowego',
            'name': 'Nazwa',
            'description': 'Opis',
            'preconditions': 'Warunki wstępne',
            'steps': 'Kroki testowe',
            'expected_result': 'Oczekiwany rezultat',
            'priority': 'Priorytet',
            'status': 'Status',
            'comment': 'Komentarz',
            'executed_at': 'Data wykonania',
            'environment': 'Środowisko/Software',
            'screenshot': 'Zrzut ekranu',
        }