from django.test import TestCase, Client
from django.urls import reverse
from contacts.models import Contact
from test_cases.models import Project, TestPlan, TestCase as TC
from .models import Defect

class DefectModelTest(TestCase):

    def setUp(self):
        self.project = Project.objects.create(
            project_number='DEF001',
            name='Projekt defektów',
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
            steps='Kroki testowe',
            expected_result='Rezultat',
            status='FAIL'
        )
        self.defect = Defect.objects.create(
            test_case=self.test_case,
            name='Błąd logowania',
            description='Aplikacja nie pozwala się zalogować',
            severity='CRITICAL',
            status='NEW'
        )

    def test_defect_str(self):
        # sprawdza czy __str__ zwraca poprawny tekst
        self.assertEqual(str(self.defect), 'Błąd logowania — CRITICAL')

    def test_defect_default_status(self):
        # sprawdza czy domyślny status defektu to NEW
        self.assertEqual(self.defect.status, 'NEW')

    def test_defect_severity(self):
        # sprawdza czy waga defektu została zapisana poprawnie
        self.assertEqual(self.defect.severity, 'CRITICAL')


class DefectViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.project = Project.objects.create(
            project_number='DEF001',
            name='Projekt defektów',
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
            steps='Kroki testowe',
            expected_result='Rezultat',
            status='FAIL'
        )
        self.defect = Defect.objects.create(
            test_case=self.test_case,
            name='Błąd logowania',
            description='Opis błędu',
            severity='MAJOR',
            status='NEW'
        )

    def test_defect_list_view(self):
        # sprawdza czy lista defektów zwraca kod 200
        response = self.client.get(reverse('defects:defect_list'))
        self.assertEqual(response.status_code, 200)

    def test_defect_detail_view(self):
        # sprawdza czy szczegóły defektu zwracają kod 200
        response = self.client.get(
            reverse('defects:defect_detail', args=[self.defect.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_defect_not_found(self):
        # sprawdza czy nieistniejący defekt zwraca 404
        response = self.client.get(
            reverse('defects:defect_detail', args=[9999])
        )
        self.assertEqual(response.status_code, 404)