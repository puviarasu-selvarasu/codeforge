# apps/chat/views.py
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import logging
from pathlib import Path

from .llm_wrapper import LLMWrapper
from .router import SmartRouter
from .intent import is_script_request
from apps.knowledge.query import query_knowledge
from apps.projects.generator import generate_script

logger = logging.getLogger(__name__)
llm = LLMWrapper()

@csrf_exempt
def chat_stream(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    data = json.loads(request.body)
    message = data.get('message', '').strip()
    if not message:
        return JsonResponse({'error': 'Empty message'}, status=400)

    # --- Router for greetings ---
    handled, response = SmartRouter.handle(message)
    if handled:
        def quick_stream():
            yield response
        return StreamingHttpResponse(quick_stream(), content_type='text/plain')

    # --- Script detection (snippet generation) ---
    if is_script_request(message):
        def script_stream():
            yield "📝 **Generating script...**\n\n"
            # We'll use the LLM to generate a script
            context_chunks = query_knowledge(message, top_k=3)
            script_code = generate_script(message, context_chunks)
            # Detect language (simple)
            lang = detect_language(message)
            yield f"```{lang}\n{script_code}\n```\n\n"
            yield "💡 **Script generated.** You can copy it or ask to save it as a file."
        return StreamingHttpResponse(script_stream(), content_type='text/plain')

    # --- Normal Chat Flow (with RAG) ---
    def stream_generator():
        context_chunks = query_knowledge(message, top_k=5)
        for chunk in llm.generate_stream(message, context_chunks=context_chunks):
            yield chunk

    return StreamingHttpResponse(stream_generator(), content_type='text/plain')

def detect_language(message):
    """Simple language detection based on keywords."""
    lower = message.lower()
    if 'python' in lower:
        return 'python'
    elif 'java' in lower:
        return 'java'
    elif 'javascript' in lower or 'node' in lower:
        return 'javascript'
    elif 'php' in lower:
        return 'php'
    elif 'c++' in lower or 'cpp' in lower:
        return 'cpp'
    elif 'c#' in lower or 'csharp' in lower:
        return 'csharp'
    elif 'ruby' in lower:
        return 'ruby'
    elif 'go' in lower or 'golang' in lower:
        return 'go'
    elif 'rust' in lower:
        return 'rust'
    else:
        return 'python'