from django.db import models
from django.conf import settings

class Build(models.Model):

    STATUS_CHOICES = [
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('IN_PROGRESS', 'In Progress'),
    ]

    build_number = models.IntegerField(unique=True)
    commit_id = models.CharField(max_length=100)
    deployed_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IN_PROGRESS')
    description = models.TextField(blank=True)

    def __str__(self):
        return f"Build #{self.build_number} — {self.status}"

    @property
    def commit_url(self):
        return f"{settings.REPO_URL}/commit/{self.commit_id}"

    class Meta:
        ordering = ['-deployed_at']
