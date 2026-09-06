from django.test import TestCase, Client
from django.urls import reverse
from .models import Project, TestPlan, TestCase as TC

class ProjectModelTest(TestCase):

    def setUp(self):
        self.project = Project.objects.create(
            project_number='TEST001',
            name='Projekt testowy',
            description='Opis testowy',
            status='IN_PROGRESS'
        )
        self.test_plan = TestPlan.objects.create(
            project=self.project,
            name='Plan testowy'
        )

    def test_project_str(self):
        # sprawdza czy metoda __str__ zwraca poprawny tekst
        self.assertEqual(str(self.project), 'TEST001 — Projekt testowy')

    def test_project_progress_empty(self):
        # sprawdza czy postęp wynosi 0 gdy nie ma przypadków testowych
        self.assertEqual(self.project.get_progress(), 0)

    def test_project_progress_all_pass(self):
        # sprawdza czy postęp wynosi 100% gdy wszystkie testy PASS
        TC.objects.create(
            test_plan=self.test_plan,
            test_id='TC001',
            name='Test 1',
            steps='Kroki',
            expected_result='Rezultat',
            status='PASS'
        )
        TC.objects.create(
            test_plan=self.test_plan,
            test_id='TC002',
            name='Test 2',
            steps='Kroki',
            expected_result='Rezultat',
            status='PASS'
        )
        self.assertEqual(self.project.get_progress(), 100)

    def test_project_progress_half_pass(self):
        # sprawdza czy postęp wynosi 50% gdy połowa testów PASS
        TC.objects.create(
            test_plan=self.test_plan,
            test_id='TC001',
            name='Test 1',
            steps='Kroki',
            expected_result='Rezultat',
            status='PASS'
        )
        TC.objects.create(
            test_plan=self.test_plan,
            test_id='TC002',
            name='Test 2',
            steps='Kroki',
            expected_result='Rezultat',
            status='FAIL'
        )
        self.assertEqual(self.project.get_progress(), 50)

    def test_project_default_status(self):
        # sprawdza czy domyślny status projektu to IN_PROGRESS
        self.assertEqual(self.project.status, 'IN_PROGRESS')


class ProjectViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.project = Project.objects.create(
            project_number='TEST001',
            name='Projekt testowy',
            status='IN_PROGRESS'
        )

    def test_project_list_view(self):
        # sprawdza czy lista projektów zwraca kod 200 (strona działa)
        response = self.client.get(reverse('test_cases:project_list'))
        self.assertEqual(response.status_code, 200)

    def test_project_detail_view(self):
        # sprawdza czy szczegóły projektu zwracają kod 200
        response = self.client.get(
            reverse('test_cases:project_detail', args=[self.project.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_project_detail_contains_name(self):
        # sprawdza czy na stronie szczegółów projektu jest jego nazwa
        response = self.client.get(
            reverse('test_cases:project_detail', args=[self.project.pk])
        )
        self.assertContains(response, 'Projekt testowy')

    def test_project_not_found(self):
        # sprawdza czy wejście na nieistniejący projekt zwraca 404
        response = self.client.get(
            reverse('test_cases:project_detail', args=[9999])
        )
        self.assertEqual(response.status_code, 404)


class TestCaseModelTest(TestCase):

    def setUp(self):
        self.project = Project.objects.create(
            project_number='TEST001',
            name='Projekt testowy',
            status='IN_PROGRESS'
        )
        self.test_plan = TestPlan.objects.create(
            project=self.project,
            name='Plan testowy'
        )
        self.test_case = TC.objects.create(
            test_plan=self.test_plan,
            test_id='TC001',
            name='Test logowania',
            steps='1. Wejdź na stronę\n2. Wpisz dane',
            expected_result='Użytkownik zalogowany',
            priority='HIGH',
            status='NOT_STARTED'
        )

    def test_test_case_str(self):
        # sprawdza czy metoda __str__ zwraca poprawny tekst
        self.assertEqual(str(self.test_case), 'TC001 — Test logowania')

    def test_test_case_default_status(self):
        # sprawdza czy domyślny status to NOT_STARTED
        self.assertEqual(self.test_case.status, 'NOT_STARTED')

    def test_test_case_priority(self):
        # sprawdza czy priorytet został zapisany poprawnie
        self.assertEqual(self.test_case.priority, 'HIGH')