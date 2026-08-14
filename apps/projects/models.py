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
    frontend = models.CharField(max_length=50, blank=True, default='none')   # <-- NEW
    description = models.TextField(blank=True)
    root_path = models.CharField(max_length=500)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    plan_summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.status})"

class ProjectMessage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10)  # 'user' or 'assistant'
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project.name} - {self.role} - {self.created_at}"