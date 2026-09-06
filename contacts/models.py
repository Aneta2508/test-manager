from django.db import models


class Contact(models.Model):
    ROLE_CHOICES = [
        ('TESTER', 'Tester'),
        ('QA_LEAD', 'QA Lead'),
        ('MANAGER', 'Kierownik projektu'),
        ('DEVELOPER', 'Developer'),
    ]

    full_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.full_name} — {self.get_role_display()}"

    class Meta:
        ordering = ['full_name']

