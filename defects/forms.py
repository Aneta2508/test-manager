from django import forms
from .models import Defect

class DefectForm(forms.ModelForm):
    class Meta:
        model = Defect
        fields = ['name', 'description', 'severity', 'status']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'np. Błąd logowania przy złym haśle'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Szczegółowy opis defektu...'
            }),
            'severity': forms.Select(attrs={
                'class': 'form-select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'name': 'Nazwa defektu',
            'description': 'Opis',
            'severity': 'Waga',
            'status': 'Status',
        }