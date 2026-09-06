from django.db import models

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

    class Meta:
        ordering = ['-deployed_at']
