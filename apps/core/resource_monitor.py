import psutil
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def check_free_ram():
    """
    Returns the amount of free RAM in bytes.
    """
    mem = psutil.virtual_memory()
    return mem.available

def is_safe_to_operate():
    """
    Returns True if free RAM is above the threshold (1.5 GB by default).
    """
    free = check_free_ram()
    threshold = getattr(settings, 'MIN_FREE_RAM_BYTES', 1.5 * 1024 ** 3)
    is_safe = free > threshold
    if not is_safe:
        logger.warning(f"Low RAM: {free / 1024**3:.2f} GB free. Threshold: {threshold / 1024**3:.2f} GB")
    return is_safe

def get_ram_status():
    """
    Returns a dict with free RAM and threshold.
    """
    free = check_free_ram()
    threshold = getattr(settings, 'MIN_FREE_RAM_BYTES', 1.5 * 1024 ** 3)
    return {
        'free_gb': free / 1024**3,
        'threshold_gb': threshold / 1024**3,
        'is_safe': free > threshold
    }