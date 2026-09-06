from django.test import TestCase, Client
from django.urls import reverse
from .models import LibraryTestCase
from test_cases.models import Project, TestPlan, TestCase as TC

class LibraryTestCaseModelTest(TestCase):

    def setUp(self):
        self.library_case = LibraryTestCase.objects.create(
            test_id='LIB001',
            name='Test logowania z biblioteki',
            description='Opis testu',
            preconditions='Użytkownik musi być zarejestrowany',
            steps='1. Wejdź na stronę\n2. Wpisz dane\n3. Kliknij Zaloguj',
            expected_result='Użytkownik zostaje zalogowany',
            priority='HIGH'
        )

    def test_library_case_str(self):
        # sprawdza czy __str__ zwraca poprawny tekst
        self.assertEqual(str(self.library_case), 'LIB001 — Test logowania z biblioteki')

    def test_library_case_priority(self):
        # sprawdza czy priorytet został zapisany poprawnie
        self.assertEqual(self.library_case.priority, 'HIGH')

    def test_library_case_unique_test_id(self):
        # sprawdza czy nie można dodać dwóch testów z tym samym ID
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            LibraryTestCase.objects.create(
                test_id='LIB001',
                name='Inny test',
                steps='Kroki',
                expected_result='Rezultat'
            )


class LibraryViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.library_case = LibraryTestCase.objects.create(
            test_id='LIB001',
            name='Test logowania z biblioteki',
            steps='1. Wejdź na stronę',
            expected_result='Użytkownik zalogowany',
            priority='MEDIUM'
        )
        self.project = Project.objects.create(
            project_number='LIB001',
            name='Projekt biblioteki',
            status='IN_PROGRESS'
        )
        self.test_plan = TestPlan.objects.create(
            project=self.project,
            name='Plan testowy'
        )

    def test_library_list_view(self):
        # sprawdza czy lista biblioteki zwraca kod 200
        response = self.client.get(reverse('test_library:library_list'))
        self.assertEqual(response.status_code, 200)

    def test_library_detail_view(self):
        # sprawdza czy szczegóły testu z biblioteki zwracają kod 200
        response = self.client.get(
            reverse('test_library:library_detail', args=[self.library_case.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_library_copy_to_plan(self):
        # sprawdza czy test z biblioteki kopiuje się poprawnie do planu testów
        response = self.client.get(
            reverse('test_library:library_copy_to_plan',
                args=[self.library_case.pk, self.test_plan.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            TC.objects.filter(
                test_plan=self.test_plan,
                test_id='LIB001'
            ).exists()
        )