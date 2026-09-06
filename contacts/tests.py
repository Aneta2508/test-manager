from django.test import TestCase, Client
from django.urls import reverse
from .models import Contact
from .forms import ContactForm

class ContactModelTest(TestCase):

    def setUp(self):
        self.contact = Contact.objects.create(
            full_name='Anna Kowalska',
            email='anna@test.pl',
            role='TESTER'
        )

    def test_contact_str(self):
        # sprawdza czy metoda __str__ zwraca poprawny tekst
        self.assertEqual(str(self.contact), 'Anna Kowalska — Tester')

    def test_contact_role(self):
        # sprawdza czy rola została zapisana poprawnie
        self.assertEqual(self.contact.role, 'TESTER')

    def test_contact_email_unique(self):
        # sprawdza czy nie można dodać dwóch kontaktów z tym samym emailem
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Contact.objects.create(
                full_name='Jan Nowak',
                email='anna@test.pl',
                role='DEVELOPER'
            )


class ContactFormTest(TestCase):

    def test_valid_form(self):
        # sprawdza czy formularz z poprawnymi danymi jest ważny i przejdzie
        form = ContactForm(data={
            'full_name': 'Anna Kowalska',
            'email': 'anna@test.pl',
            'role': 'TESTER'
        })
        self.assertTrue(form.is_valid())

    def test_invalid_email(self):
        # sprawdza czy formularz odrzuca niepoprawny email
        form = ContactForm(data={
            'full_name': 'Anna Kowalska',
            'email': 'niepoprawny-email',
            'role': 'TESTER'
        })
        self.assertFalse(form.is_valid())

    def test_missing_full_name(self):
        # sprawdza czy formularz odrzuca brak imienia i nazwiska
        form = ContactForm(data={
            'email': 'anna@test.pl',
            'role': 'TESTER'
        })
        self.assertFalse(form.is_valid())


class ContactViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.contact = Contact.objects.create(
            full_name='Anna Kowalska',
            email='anna@test.pl',
            role='TESTER'
        )

    def test_contact_list_view(self):
        # sprawdza czy lista kontaktów zwraca kod 200, strona działa poprawnie
        response = self.client.get(reverse('contacts:contact_list'))
        self.assertEqual(response.status_code, 200)

    def test_contact_list_contains_name(self):
        # sprawdza czy na liście kontaktów jest imię i nazwisko
        response = self.client.get(reverse('contacts:contact_list'))
        self.assertContains(response, 'Anna Kowalska')

    def test_contact_add_get(self):
        # sprawdza czy formularz dodawania kontaktu się otwiera
        response = self.client.get(reverse('contacts:contact_add'))
        self.assertEqual(response.status_code, 200)

    def test_contact_add_post(self):
        # sprawdza czy można dodać kontakt przez formularz
        response = self.client.post(reverse('contacts:contact_add'), {
            'full_name': 'Jan Nowak',
            'email': 'jan@test.pl',
            'role': 'DEVELOPER'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Contact.objects.filter(email='jan@test.pl').exists())