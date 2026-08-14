# apps/studio/views.py
import os
import json
import logging
import re
from pathlib import Path
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib import messages

from apps.projects.models import Project, ProjectMessage
from apps.projects.scaffold import copy_scaffold
from apps.chat.llm_wrapper import LLMWrapper
from apps.knowledge.query import query_knowledge
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

logger = logging.getLogger(__name__)
llm = LLMWrapper()

# ---- Project List ----
def project_list(request):
    projects_list = Project.objects.all().order_by('-created_at')
    paginator = Paginator(projects_list, 10)  # 10 per page
    page = request.GET.get('page')
    try:
        projects = paginator.page(page)
    except PageNotAnInteger:
        projects = paginator.page(1)
    except EmptyPage:
        projects = paginator.page(paginator.num_pages)
    return render(request, 'studio/landing.html', {'projects': projects})

# ---- Project Create ----
def project_create(request):
    from .forms import ProjectCreateForm
    if request.method == 'POST':
        form = ProjectCreateForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.frontend = form.cleaned_data['frontend']
            project.root_path = str(settings.PROJECTS_ROOT / project.name)
            project.status = 'building'
            project.save()

            try:
                copy_scaffold(project)
                project.status = 'ready'
                project.save()
                messages.success(request, f'Project "{project.name}" created successfully!')
            except Exception as e:
                project.delete()
                messages.error(request, f'Failed to create project: {e}')
                return redirect('studio:project_create')

            return redirect('studio:project_detail', project_id=project.id)
    else:
        form = ProjectCreateForm()
    return render(request, 'studio/create.html', {'form': form})

# ---- Project Detail ----
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    return render(request, 'studio/detail.html', {'project': project})

# ---- Project Delete ----
@csrf_exempt
def project_delete(request, project_id):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'DELETE required'}, status=400)
    project = get_object_or_404(Project, id=project_id)
    import shutil
    if os.path.exists(project.root_path):
        shutil.rmtree(project.root_path)
    project.delete()
    return JsonResponse({'success': True})

# ============================================================
# PHASE 4.3 – File Tree, Preview & Contextual Chat
# ============================================================

def file_tree(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    root = Path(project.root_path)
    if not root.exists():
        return JsonResponse({'tree': []})

    def scan_dir(path):
        items = []
        try:
            with os.scandir(path) as it:
                for entry in it:
                    if entry.name.startswith('.'):
                        continue
                    if entry.is_dir():
                        items.append({
                            'name': entry.name,
                            'path': str(entry.path),
                            'is_dir': True,
                            'children': scan_dir(entry.path)
                        })
                    else:
                        items.append({
                            'name': entry.name,
                            'path': str(entry.path),
                            'is_dir': False,
                            'children': []
                        })
        except PermissionError:
            pass
        return items

    tree = scan_dir(root)
    return JsonResponse({'tree': tree})

def file_content(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    file_path = request.GET.get('path')
    if not file_path:
        return JsonResponse({'error': 'path parameter required'}, status=400)

    full_path = Path(file_path).resolve()
    project_root = Path(project.root_path).resolve()
    if not str(full_path).startswith(str(project_root)):
        return JsonResponse({'error': 'Access denied'}, status=403)

    if not full_path.exists() or not full_path.is_file():
        return JsonResponse({'error': 'File not found'}, status=404)

    try:
        content = full_path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        content = 'Binary file (cannot preview)'
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'content': content})

# ---- Chat History Endpoint ----
def chat_history(request, project_id):
    """Return all chat messages for a project."""
    project = get_object_or_404(Project, id=project_id)
    messages = project.messages.all().order_by('created_at')
    data = [
        {'id': msg.id, 'role': msg.role, 'content': msg.content, 'created_at': msg.created_at.isoformat()}
        for msg in messages
    ]
    return JsonResponse(data, safe=False)

# ============================================================
# PHASE 4.4 – Contextual Chat with Persistence & JSON Mutations
# ============================================================

@csrf_exempt
def studio_chat(request, project_id):
    """
    Contextual chat for the Studio.
    - Saves user message to DB.
    - Streams LLM response.
    - Detects JSON blocks and applies file mutations.
    - Saves assistant response to DB.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    project = get_object_or_404(Project, id=project_id)
    data = json.loads(request.body)
    user_message = data.get('message', '').strip()
    if not user_message:
        return JsonResponse({'error': 'Empty message'}, status=400)

    # Save user message
    ProjectMessage.objects.create(
        project=project,
        role='user',
        content=user_message
    )

    # Gather project context
    root = Path(project.root_path)
    file_list = []
    if root.exists():
        for file_path in root.rglob('*'):
            if file_path.is_file() and not file_path.name.startswith('.'):
                rel_path = str(file_path.relative_to(root))
                file_list.append(rel_path)

    context_chunks = query_knowledge(user_message, top_k=3)

    system_prompt = (
        f"You are CodeForge, a senior software engineer and architect. "
        f"You are helping the user build a project named '{project.name}' using {project.framework}."
        f"The current project files are:\n{chr(10).join(file_list[:20])}\n"
        f"IMPORTANT: If the user asks to create, modify, or delete a file, respond with ONLY a JSON block in the following format:\n"
        f"```json\n{{ \"action\": \"create\" or \"modify\" or \"delete\", \"file_path\": \"path/relative/to/project\", \"content\": \"file content\" }}\n```\n"
        f"Do not include any other text. Only provide the JSON block.\n"
        f"For other questions, provide a helpful response."
    )

    def stream_generator():
        full_response = ""
        for chunk in llm.generate_stream(
            user_message,
            context_chunks=context_chunks,
            system_override=system_prompt
        ):
            full_response += chunk
            yield chunk

        # After streaming, parse for JSON mutations
        try:
            # Extract JSON blocks from the response
            json_blocks = re.findall(r'```json\s*(\{.*?\})\s*```', full_response, re.DOTALL)
            for json_str in json_blocks:
                try:
                    mutation = json.loads(json_str)
                    action = mutation.get('action')
                    file_path = mutation.get('file_path')
                    content = mutation.get('content')
                    if action in ['create', 'modify', 'delete'] and file_path:
                        full_path = root / file_path
                        if action == 'delete':
                            if full_path.exists():
                                full_path.unlink()
                        else:
                            full_path.parent.mkdir(parents=True, exist_ok=True)
                            full_path.write_text(content, encoding='utf-8')
                        logger.info(f"Applied mutation: {action} on {file_path}")
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            logger.error(f"Error processing mutations: {e}")

        # Save assistant message
        ProjectMessage.objects.create(
            project=project,
            role='assistant',
            content=full_response
        )

    return StreamingHttpResponse(stream_generator(), content_type='text/plain')


@csrf_exempt
def set_model_preference(request):
    """Store the user's model preference in session and reload the model."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    data = json.loads(request.body)
    model_type = data.get('model_type')
    if model_type not in ['1.5B', '7B']:
        return JsonResponse({'error': 'Invalid model type'}, status=400)

    request.session['model_preference'] = model_type
    request.session.modified = True

    # Reload the model
    llm = LLMWrapper()
    llm.load_model(model_type)

    return JsonResponse({'success': True, 'model_type': model_type})

def get_model_preference(request):
    """Return the current model preference from session."""
    model_type = request.session.get('model_preference', settings.DEFAULT_LLM_MODEL)
    return JsonResponse({'model_type': model_type})