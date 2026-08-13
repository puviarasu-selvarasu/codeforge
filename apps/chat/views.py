# apps/chat/views.py
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .llm_wrapper import LLMWrapper
from .router import SmartRouter
from .intent import detect_build_intent
# We'll use the singleton instance
llm = LLMWrapper()
from apps.knowledge.query import query_knowledge

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
        is_build = detect_build_intent(message)
        # Retrieve relevant context from the knowledge base
        context_chunks = query_knowledge(message, top_k=5)
        # Pass the context to the LLM
        for chunk in llm.generate_stream(message, context_chunks=context_chunks):
            yield chunk
    
    return StreamingHttpResponse(stream_generator(), content_type='text/plain')