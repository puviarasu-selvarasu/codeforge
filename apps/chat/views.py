# apps/chat/views.py
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from .llm_wrapper import LLMWrapper
from .router import SmartRouter
from .intent import is_script_request

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

    # Router for quick replies
    handled, response = SmartRouter.handle(message)
    if handled:
        def quick_stream():
            yield response
        return StreamingHttpResponse(quick_stream(), content_type='text/plain')

    # Script detection
    if is_script_request(message):
        def script_stream():
            yield "📝 **Generating script...**\n\n"
            # We'll use the LLM with a system prompt that forces code-only output
            script_prompt = (
                "You are CodeForge. Provide only the code, without any extra text or explanation. "
                "If the user asks for a specific language, use that language. Otherwise use Python."
            )
            # Use context from knowledge base if available
            try:
                from apps.knowledge.query import query_knowledge
                context_chunks = query_knowledge(message, top_k=3)
            except ImportError:
                context_chunks = []
            # Stream the code
            for chunk in llm.generate_stream(message, context_chunks=context_chunks, system_override=script_prompt):
                yield chunk
            yield "\n\n💡 **Script generated.** You can copy it or ask to save it as a file."
        return StreamingHttpResponse(script_stream(), content_type='text/plain')

    # Normal chat flow (with RAG if available)
    def stream_generator():
        try:
            from apps.knowledge.query import query_knowledge
            context_chunks = query_knowledge(message, top_k=5)
        except ImportError:
            context_chunks = []
        for chunk in llm.generate_stream(message, context_chunks=context_chunks):
            yield chunk

    return StreamingHttpResponse(stream_generator(), content_type='text/plain')