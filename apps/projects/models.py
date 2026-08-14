# apps/projects/models.py
from django.db import models

class Project(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft - Awaiting Approval'),
        ('approved', 'Approved - Ready to Build'),
        ('building', 'Building'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]
    name = models.CharField(max_length=200, unique=True)
    framework = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    root_path = models.CharField(max_length=500)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    plan_summary = models.TextField(blank=True)  # human‑readable summary for approval
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.status})"