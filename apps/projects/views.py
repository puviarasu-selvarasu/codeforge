# apps/projects/views.py
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from apps.projects.models import Project
from apps.projects.generator import generate_plan
from apps.projects.builder import build_project
from django.conf import settings
from pathlib import Path
import json
import logging

import shutil

logger = logging.getLogger(__name__)

@csrf_exempt
def generate_project(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    data = json.loads(request.body)
    prompt = data.get('prompt', '').strip()
    if not prompt:
        return JsonResponse({'error': 'Prompt required'}, status=400)
    
    # Generate plan
    plan = generate_plan(prompt)
    # Create project record
    project_name = plan.get('project_name', 'project')
    framework = plan.get('framework', '')
    # Ensure unique name
    base_name = project_name
    counter = 1
    while Project.objects.filter(name=project_name).exists():
        project_name = f"{base_name}_{counter}"
        counter += 1
    root_path = settings.PROJECTS_ROOT / project_name
    project = Project.objects.create(
        name=project_name,
        framework=framework,
        root_path=str(root_path),
        status='generating'
    )
    # Save plan to project folder
    root_path.mkdir(parents=True, exist_ok=True)
    plan_path = root_path / 'codeforge_plan.json'
    with open(plan_path, 'w') as f:
        json.dump(plan, f, indent=2)
    # Build
    success, message = build_project(project)
    project.status = 'success' if success else 'failed'
    project.save()
    return JsonResponse({
        'project_id': project.id,
        'name': project.name,
        'status': project.status,
        'message': message,
        'root_path': str(root_path)
    })

def list_projects(request):
    projects = Project.objects.all().values('id', 'name', 'framework', 'status', 'created_at')
    return JsonResponse(list(projects), safe=False)

@csrf_exempt
def approve_project(request):
    """User approves the draft project and triggers the build."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    data = json.loads(request.body)
    project_id = data.get('project_id')
    if not project_id:
        return JsonResponse({'error': 'project_id required'}, status=400)

    project = get_object_or_404(Project, id=project_id)

    if project.status != 'draft':
        return JsonResponse({'error': 'Project is not in draft state'}, status=400)

    # Start building
    project.status = 'building'
    project.save()

    success, msg = build_project(project)
    project.status = 'success' if success else 'failed'
    project.save()

    return JsonResponse({
        'success': success,
        'project_id': project.id,
        'name': project.name,
        'status': project.status,
        'message': msg
    })

@csrf_exempt
def delete_project(request, project_id):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'DELETE required'}, status=400)

    project = get_object_or_404(Project, id=project_id)
    root_path = Path(project.root_path)

    # Delete folder from disk (if exists)
    if root_path.exists():
        shutil.rmtree(root_path)

    # Delete from DB
    project.delete()

    return JsonResponse({'success': True})