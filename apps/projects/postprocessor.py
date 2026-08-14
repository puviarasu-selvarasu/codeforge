import os
import re
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def normalize_project(project_path, project_name, framework):
    """
    Apply framework‑specific fixes after copying the scaffold.
    """
    # Ensure project_path is a Path object and absolute
    project_path = Path(project_path).resolve()
    
    # --- SAFETY CHECK: Ensure we are inside the generated_projects/ folder ---
    if not str(project_path).startswith(str(Path('generated_projects').resolve())):
        logger.error(f"Safety check failed: {project_path} is not inside generated_projects/")
        raise ValueError(f"Project path {project_path} is not inside generated_projects/")

    if framework == 'django':
        normalize_django(project_path, project_name)
    elif framework == 'laravel':
        normalize_laravel(project_path, project_name)
    elif framework == 'springboot':
        normalize_springboot(project_path, project_name)
    elif framework == 'node_express':
        normalize_node(project_path, project_name)
    # Add others as needed

def normalize_django(project_path, project_name):
    """
    Fix Django namespace: rename config dir, replace __PROJECT_NAME__, fix settings references.
    """
    # 1. Rename __PROJECT_NAME__ directory
    old_dir = project_path / '__PROJECT_NAME__'
    new_dir = project_path / project_name
    if old_dir.exists():
        old_dir.rename(new_dir)

    # 2. Replace __PROJECT_NAME__ in all .py files INSIDE the project folder ONLY
    for file_path in project_path.rglob('*.py'):
        # Safety: ensure the file is actually inside the project_path
        if not str(file_path).startswith(str(project_path)):
            continue
        try:
            content = file_path.read_text(encoding='utf-8')
            new_content = content.replace('__PROJECT_NAME__', project_name)
            new_content = new_content.replace("'config.settings'", f"'{project_name}.settings'")
            new_content = new_content.replace('"config.settings"', f'"{project_name}.settings"')
            new_content = new_content.replace("'config.wsgi'", f"'{project_name}.wsgi'")
            new_content = new_content.replace("'config.urls'", f"'{project_name}.urls'")
            new_content = new_content.replace(
                "os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')",
                f"os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{project_name}.settings')"
            )
            if new_content != content:
                file_path.write_text(new_content, encoding='utf-8')
                logger.info(f"Updated: {file_path}")
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")

def normalize_laravel(project_path, project_name):
    env_path = project_path / '.env'
    if env_path.exists():
        content = env_path.read_text(encoding='utf-8')
        content = re.sub(r'APP_NAME=.*', f'APP_NAME={project_name}', content)
        env_path.write_text(content, encoding='utf-8')

def normalize_springboot(project_path, project_name):
    pom_path = project_path / 'pom.xml'
    if pom_path.exists():
        content = pom_path.read_text(encoding='utf-8')
        content = content.replace('<artifactId>demo</artifactId>', f'<artifactId>{project_name}</artifactId>')
        pom_path.write_text(content, encoding='utf-8')

def normalize_node(project_path, project_name):
    package_path = project_path / 'package.json'
    if package_path.exists():
        content = package_path.read_text(encoding='utf-8')
        content = re.sub(r'"name":\s*".*?"', f'"name": "{project_name}"', content)
        package_path.write_text(content, encoding='utf-8')