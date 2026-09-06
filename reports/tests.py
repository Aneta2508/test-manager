from django.test import TestCase, Client
from django.urls import reverse
from test_cases.models import Project, TestPlan, TestCase as TC

class ReportViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.project = Project.objects.create(
            project_number='REP001',
            name='Projekt raportów',
            status='IN_PROGRESS'
        )
        self.test_plan = TestPlan.objects.create(
            project=self.project,
            name='Plan testowy'
        )
        self.test_case = TC.objects.create(
            test_plan=self.test_plan,
            test_id='TC001',
            name='Test raportu',
            steps='Kroki testowe',
            expected_result='Rezultat',
            status='PASS'
        )

    def test_report_list_view(self):
        # sprawdza czy strona z listą raportów zwraca kod 200
        response = self.client.get(reverse('reports:report_list'))
        self.assertEqual(response.status_code, 200)

    def test_report_list_contains_project(self):
        # sprawdza czy na liście raportów widoczny jest projekt
        response = self.client.get(reverse('reports:report_list'))
        self.assertContains(response, 'REP001')

    def test_generate_report_returns_pdf(self):
        # sprawdza czy generowanie raportu zwraca plik PDF
        response = self.client.get(
            reverse('reports:generate_report', args=[self.project.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')