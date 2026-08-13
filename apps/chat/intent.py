# apps/chat/intent.py
import re

def detect_build_intent(message):
    """
    Returns True if the user wants to build/create/generate a project.
    """
    build_keywords = ['build', 'create', 'generate', 'make', 'develop', 'code', 'write']
    # Simple keyword matching
    words = message.lower().split()
    for kw in build_keywords:
        if kw in words:
            return True
    # Also catch phrases like "I need a..."
    if re.search(r'i (need|want|would like) (a|an)?\s*\w+', message.lower()):
        return True
    return False