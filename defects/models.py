from django.db import models
from test_cases.models import TestCase

class Defect(models.Model):

    SEVERITY_CHOICES = [
        ('CRITICAL', 'Critical'),
        ('MAJOR', 'Major'),
        ('MEDIUM', 'Medium'),
        ('MINOR', 'Minor'),
    ]

    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]

    test_case = models.ForeignKey(TestCase, on_delete=models.CASCADE, related_name='defects')
    name = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    reported_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — {self.severity}"

    class Meta:
        ordering = ['-reported_at']