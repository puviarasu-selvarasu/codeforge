SCRIPT_KEYWORDS = [
    'script', 'snippet', 'function', 'program', 'code for', 'write a',
    'simple', 'quick', 'just', 'single file'
]

def is_script_request(message):
    """Return True if the user wants a single-file script/snippet."""
    lower = message.lower()
    # If it's a framework request, it's not a script
    framework_keywords = ['django', 'laravel', 'spring', 'flask', 'react', 'vue', 'node']
    if any(kw in lower for kw in framework_keywords):
        return False
    return any(kw in lower for kw in SCRIPT_KEYWORDS)