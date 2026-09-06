from django.test import TestCase, Client
from django.urls import reverse
from .models import Build

class BuildModelTest(TestCase):

    def setUp(self):
        self.build = Build.objects.create(
            build_number=1,
            commit_id='abc123',
            status='SUCCESS',
            description='Pierwszy build testowy'
        )

    def test_build_str(self):
        # sprawdza czy __str__ zwraca poprawny tekst
        self.assertEqual(str(self.build), 'Build #1 — SUCCESS')

    def test_build_default_status(self):
        # sprawdza czy domyślny status nowego builda to IN_PROGRESS
        build = Build.objects.create(
            build_number=2,
            commit_id='def456'
        )
        self.assertEqual(build.status, 'IN_PROGRESS')

    def test_build_unique_number(self):
        # sprawdza czy nie można dodać dwóch buildów z tym samym numerem

        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Build.objects.create(
                build_number=1,
                commit_id='xyz789'
            )


class BuildViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.build = Build.objects.create(
            build_number=1,
            commit_id='abc123',
            status='SUCCESS'
        )

    def test_build_list_view(self):
        # sprawdza czy lista buildów zwraca kod 200
        response = self.client.get(reverse('builds:build_list'))
        self.assertEqual(response.status_code, 200)

    def test_build_detail_view(self):
        # sprawdza czy szczegóły builda zwracają kod 200
        response = self.client.get(
            reverse('builds:build_detail', args=[self.build.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_build_not_found(self):
        # sprawdza czy nieistniejący build zwraca 404
        response = self.client.get(
            reverse('builds:build_detail', args=[9999])
        )
        self.assertEqual(response.status_code, 404)