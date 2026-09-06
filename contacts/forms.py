from django import forms
from .models import Contact

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['full_name', 'email', 'role']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'np. Monika Kowalska'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'np. monika@firma.pl'
            }),
            'role': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'full_name': 'Imię i nazwisko',
            'email': 'Email',
            'role': 'Rola',
        }