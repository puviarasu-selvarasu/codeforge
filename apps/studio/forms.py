from django import forms
from apps.projects.models import Project

BACKEND_CHOICES = [
    ('django', 'Django'),
    ('flask', 'Flask'),
    ('laravel', 'Laravel'),
    ('springboot', 'Spring Boot'),
    ('node_express', 'Node.js (Express)'),
]

FRONTEND_CHOICES = [
    ('none', 'None'),
    ('react', 'React'),
    ('vue', 'Vue'),
    ('blade', 'Blade (Laravel)'),
    ('django_templates', 'Django Templates'),
]

class ProjectCreateForm(forms.ModelForm):
    backend = forms.ChoiceField(choices=BACKEND_CHOICES, label='Backend Stack')
    frontend = forms.ChoiceField(choices=FRONTEND_CHOICES, label='Frontend Stack', required=False)

    class Meta:
        model = Project
        fields = ['name', 'description']  # we'll add backend/frontend as extra fields

    def save(self, commit=True):
        project = super().save(commit=False)
        project.framework = self.cleaned_data['backend']
        # We'll store frontend choice in a new field or as part of framework?
        # For simplicity, we can store it in a new field called 'frontend' – we'll add it to Project model.
        # We'll add a 'frontend' CharField to Project model.
        if commit:
            project.save()
        return project