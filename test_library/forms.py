from django import forms
from .models import LibraryTestCase

class LibraryTestCaseForm(forms.ModelForm):
    class Meta:
        model = LibraryTestCase
        fields = ['test_id', 'name', 'description', 'preconditions', 'steps', 'expected_result', 'priority']
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
                'placeholder': 'np. Użytkownik zostaje zalogowany'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
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
        }