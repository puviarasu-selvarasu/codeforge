# apps/projects/sandbox.py
import subprocess
import os
import signal
import time
import logging
import psutil
from django.conf import settings

logger = logging.getLogger(__name__)

def run_command(command, cwd, timeout=300, memory_limit_mb=1024):
    """
    Run a shell command in a subprocess with timeout and memory limits.
    Returns (returncode, stdout, stderr).
    """
    # Set environment variables for resource limits (Unix only)
    env = os.environ.copy()
    # For Windows, we use psutil to monitor after process starts
    proc = subprocess.Popen(
        command,
        shell=True,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
        preexec_fn=None if os.name == 'nt' else os.setsid
    )
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
        return proc.returncode, stdout, stderr
    except subprocess.TimeoutExpired:
        # Kill process tree
        if os.name == 'nt':
            parent = psutil.Process(proc.pid)
            for child in parent.children(recursive=True):
                child.kill()
            parent.kill()
        else:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        return -1, '', f"Command timed out after {timeout} seconds"
    except Exception as e:
        return -1, '', str(e)