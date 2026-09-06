from django.db import models
from contacts.models import Contact


class Project(models.Model):
    STATUS_CHOICES = [
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('ON_HOLD', 'On Hold'),
    ]

    project_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IN_PROGRESS')
    contacts = models.ManyToManyField(Contact, blank=True, related_name='projects')

    def __str__(self):
        return f"{self.project_number} — {self.name}"

    def get_progress(self):
        total = TestCase.objects.filter(test_plan__project=self).count()
        if total == 0:
            return 0
        passed = TestCase.objects.filter(test_plan__project=self, status='PASS').count()
        return round((passed / total) * 100)

    class Meta:
        ordering = ['-created_at']


class TestPlan(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='test_plans')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — {self.project.project_number}"

    class Meta:
        ordering = ['created_at']


class TestCase(models.Model):
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    ]

    STATUS_CHOICES = [
        ('NOT_STARTED', 'Not Started'),
        ('ONGOING', 'Ongoing'),
        ('PASS', 'Pass'),
        ('FAIL', 'Fail'),
        ('BLOCKED', 'Blocked'),
    ]

    test_plan = models.ForeignKey(TestPlan, on_delete=models.CASCADE, related_name='test_cases')
    test_id = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    preconditions = models.TextField(blank=True)
    steps = models.TextField()
    expected_result = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    comment = models.TextField(blank=True)
    executed_at = models.DateField(null=True, blank=True)
    environment = models.CharField(max_length=200, blank=True)
    screenshot = models.ImageField(upload_to='screenshots/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.test_id} — {self.name}"

    class Meta:
        ordering = ['test_id']

