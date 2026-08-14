# apps/projects/scaffold.py
import os
import shutil
from pathlib import Path
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def copy_scaffold(project):
    """
    Copy the appropriate scaffold template to the project root.
    """
    project_root = Path(project.root_path)
    # --- SAFETY: Ensure we are inside generated_projects/ ---
    generated_root = settings.PROJECTS_ROOT.resolve()
    if not str(project_root.resolve()).startswith(str(generated_root)):
        raise ValueError(f"Project root {project_root} is not inside {generated_root}")
    """
    Copy the appropriate scaffold template to the project root.
    """
    backend = project.framework
    frontend = project.frontend
    project_root = Path(project.root_path)
    
    # Source folders
    backend_template = settings.BASE_DIR / 'templates' / 'project_templates' / 'backend' / backend
    if not backend_template.exists():
        raise FileNotFoundError(f"Backend template not found: {backend_template}")

    # Copy backend template
    shutil.copytree(backend_template, project_root, dirs_exist_ok=True)

    # If frontend is not 'none', copy frontend template
    if frontend != 'none':
        frontend_template = settings.BASE_DIR / 'templates' / 'project_templates' / 'frontend' / frontend
        if not frontend_template.exists():
            logger.warning(f"Frontend template not found: {frontend_template}")
        else:
            # Copy frontend into project_root/frontend/ (or merge)
            frontend_dest = project_root / 'frontend'
            shutil.copytree(frontend_template, frontend_dest, dirs_exist_ok=True)

    # Post-process: replace _PROJECT_NAME_ and fix namespace issues
    from .postprocessor import normalize_project
    normalize_project(project_root, project.name, backend)

    logger.info(f"Scaffold copied to {project_root}")