from django.test import TestCase, Client
from django.urls import reverse
from test_cases.models import Project, TestPlan, TestCase as TC
from defects.models import Defect

class DashboardViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.project = Project.objects.create(
            project_number='DASH001',
            name='Projekt dashboardu',
            status='IN_PROGRESS'
        )
        self.test_plan = TestPlan.objects.create(
            project=self.project,
            name='Plan testowy'
        )
        self.test_case = TC.objects.create(
            test_plan=self.test_plan,
            test_id='TC001',
            name='Test dashboardu',
            steps='Kroki',
            expected_result='Rezultat',
            status='PASS'
        )

    def test_dashboard_view(self):
        # sprawdza czy strona główna dashboardu zwraca kod 200
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_contains_project(self):
        # sprawdza czy na dashboardzie widoczny jest projekt
        response = self.client.get(reverse('dashboard:index'))
        self.assertContains(response, 'Projekt dashboardu')