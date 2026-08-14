# apps/projects/builder.py
import json
import subprocess
import logging
from pathlib import Path
from django.conf import settings

logger = logging.getLogger(__name__)

def build_project(project):
    root = Path(project.root_path)
    plan_path = root / 'codeforge_plan.json'
    if not plan_path.exists():
        return False, "Plan file not found"

    with open(plan_path, 'r') as f:
        plan = json.load(f)

    # Write all files
    for file_spec in plan.get('files', []):
        file_path = root / file_spec['path']
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(file_spec['content'])

    # Execute commands
    for cmd in plan.get('commands', []):
        logger.info(f"Running: {cmd}")
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=str(root),
                timeout=300,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                logger.error(f"Command failed: {result.stderr}")
                # Continue to run other commands? Mark project as failed if any command fails.
                return False, f"Command '{cmd}' failed with error: {result.stderr}"
        except subprocess.TimeoutExpired:
            return False, f"Command '{cmd}' timed out after 300 seconds"
        except Exception as e:
            return False, f"Command '{cmd}' raised exception: {e}"

    return True, "Project built successfully"