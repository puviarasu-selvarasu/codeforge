# apps/chat/views.py
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .llm_wrapper import LLMWrapper
from .router import SmartRouter
from .intent import detect_build_intent
# We'll use the singleton instance
llm = LLMWrapper()

@csrf_exempt  # for simplicity; if you have CSRF, add token
def chat_stream(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)
    
    data = json.loads(request.body)
    message = data.get('message', '').strip()
    if not message:
        return JsonResponse({'error': 'Empty message'}, status=400)
    
    # 1. Check router for quick reply
    handled, response = SmartRouter.handle(message)
    if handled:
        # Return a simulated streaming response
        def quick_stream():
            yield response
        return StreamingHttpResponse(quick_stream(), content_type='text/plain')
    
    # 2. For complex queries, use LLM with optional RAG (we'll add RAG later)
    # For now, no RAG context
    def stream_generator():
        # We can also detect intent and store for later
        is_build = detect_build_intent(message)
        # If build intent, we might store a flag; later we'll trigger project generation.
        # For now, just reply with the LLM.
        for chunk in llm.generate_stream(message):
            yield chunk
    
    return StreamingHttpResponse(stream_generator(), content_type='text/plain')