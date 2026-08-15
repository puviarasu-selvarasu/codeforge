# apps/chat/views.py
import json
import logging
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .llm_wrapper import LLMWrapper
from .router import SmartRouter
from .intent import is_script_request

logger = logging.getLogger(__name__)
llm = LLMWrapper()

# Helper to get max_tokens for long commands
def get_long_command_max_tokens():
    """Return a higher token limit for @plan, @code, etc."""
    model_type = llm._current_model_type or getattr(settings, 'DEFAULT_LLM_MODEL', '1.5B')
    if model_type == '7B':
        return getattr(settings, 'LLM_7B_MAX_TOKENS', 2048) * 2  # e.g., 4096
    else:
        return getattr(settings, 'LLM_15B_MAX_TOKENS', 1024) * 2  # e.g., 2048

@csrf_exempt
def chat_stream(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    data = json.loads(request.body)
    message = data.get('message', '').strip()
    if not message:
        return JsonResponse({'error': 'Empty message'}, status=400)

    # ---------- Router for quick replies ----------
    handled, response = SmartRouter.handle(message)
    if handled:
        def quick_stream():
            yield response
        return StreamingHttpResponse(quick_stream(), content_type='text/plain')

    # ---------- Command Detection ----------
    if message.startswith('@'):
        command_parts = message.split(maxsplit=1)
        command = command_parts[0].lower()
        command_args = command_parts[1] if len(command_parts) > 1 else ''

        # ---------- @continue ----------
        if command == '@continue':
            # Retrieve last incomplete response from session
            last_response = request.session.get('last_incomplete_response')
            last_prompt = request.session.get('last_incomplete_prompt')
            if not last_response:
                def no_continue_stream():
                    yield "❌ No incomplete response to continue. Please start a new request."
                return StreamingHttpResponse(no_continue_stream(), content_type='text/plain')
            # Build continuation prompt
            continuation_prompt = (
                f"The previous response was cut off. Please continue exactly from where it stopped.\n\n"
                f"The last response ended with:\n{last_response[-300:]}\n\n"
                f"Continue the response naturally. Do not repeat the previous content."
            )
            # Clear session after retrieving
            del request.session['last_incomplete_response']
            del request.session['last_incomplete_prompt']
            request.session.modified = True

            def cont_stream():
                # Use a higher token limit for continuation
                for chunk in llm.generate_stream(continuation_prompt, max_tokens=get_long_command_max_tokens()):
                    yield chunk
            return StreamingHttpResponse(cont_stream(), content_type='text/plain')

        def command_stream():
            if command == '@help':
                yield """**📋 Available Commands**

| Command | Description |
|---------|-------------|
| `@plan <idea>` | Generate a high‑level architecture plan |
| `@code <request>` | Generate code for a specific file |
| `@explain <topic>` | Explain a design decision or concept |
| `@add <feature>` | Add a new feature to the current project |
| `@test <request>` | Generate unit tests |
| `@docs <request>` | Generate OpenAPI/Swagger docs |
| `@refactor <request>` | Suggest refactoring |
| `@audit <request>` | Perform a security audit |
| `@infra <request>` | Recommend deployment strategy |
| `@continue` | Continue a cut‑off response |
| `@help` | Show this help menu

**Example:** `@plan a task management system using Django`"""
                return

            elif command == '@plan':
                yield f"📐 **Architecture Plan for:** {command_args}\n\n"
                plan_prompt = (
                    f"You are a senior architect. Create a detailed architecture plan for: {command_args}.\n"
                    "Include: tech stack, data models, relationships, API structure, folder structure, and key design decisions."
                )
                # Use higher token limit for @plan
                for chunk in llm.generate_stream(plan_prompt, max_tokens=get_long_command_max_tokens()):
                    yield chunk

            elif command == '@code':
                yield f"💻 **Generating code for:** {command_args}\n\n```\n"
                code_prompt = (
                    f"Write production‑ready code for: {command_args}. "
                    "Only output the code. No explanations. Use the appropriate language."
                )
                for chunk in llm.generate_stream(code_prompt, max_tokens=get_long_command_max_tokens()):
                    yield chunk
                yield "\n```"

            elif command == '@explain':
                yield f"🧠 **Explanation:** {command_args}\n\n"
                explain_prompt = f"Explain the following concept clearly and concisely: {command_args}"
                for chunk in llm.generate_stream(explain_prompt):
                    yield chunk

            elif command == '@add':
                yield f"➕ **Adding feature:** {command_args}\n\n"
                add_prompt = (
                    f"Add a new feature to an existing project: {command_args}. "
                    "Provide only the new files or changes, with full code."
                )
                for chunk in llm.generate_stream(add_prompt, max_tokens=get_long_command_max_tokens()):
                    yield chunk

            elif command == '@test':
                yield f"🧪 **Generating unit tests for:** {command_args}\n\n"
                test_prompt = (
                    f"Generate unit tests for the following code or feature: {command_args}. "
                    "Provide the tests in the appropriate testing framework (pytest for Python, PHPUnit for PHP, JUnit for Java). "
                    "Include setup, test cases, and assertions."
                )
                for chunk in llm.generate_stream(test_prompt, max_tokens=get_long_command_max_tokens()):
                    yield chunk

            elif command == '@docs':
                yield f"📚 **Generating documentation for:** {command_args}\n\n"
                docs_prompt = (
                    f"Generate OpenAPI/Swagger documentation for the API described: {command_args}. "
                    "Output YAML or JSON format. Include endpoints, parameters, responses, and schemas."
                )
                for chunk in llm.generate_stream(docs_prompt, max_tokens=get_long_command_max_tokens()):
                    yield chunk

            elif command == '@refactor':
                yield f"🔧 **Refactoring suggestion for:** {command_args}\n\n"
                refactor_prompt = (
                    f"Suggest a refactoring for the following code or component: {command_args}. "
                    "Provide the refactored code and explain the improvements."
                )
                for chunk in llm.generate_stream(refactor_prompt, max_tokens=get_long_command_max_tokens()):
                    yield chunk

            elif command == '@audit':
                yield f"🔒 **Security audit for:** {command_args}\n\n"
                audit_prompt = (
                    f"Perform a security audit on the following code or system: {command_args}. "
                    "Identify vulnerabilities (SQL injection, XSS, CSRF, etc.) and provide fixes."
                )
                for chunk in llm.generate_stream(audit_prompt, max_tokens=get_long_command_max_tokens()):
                    yield chunk

            elif command == '@infra':
                yield f"☁️ **Deployment strategy for:** {command_args}\n\n"
                infra_prompt = (
                    f"Recommend a deployment strategy for the project: {command_args}. "
                    "Include Docker, CI/CD pipeline, hosting provider options, scaling, and monitoring."
                )
                for chunk in llm.generate_stream(infra_prompt, max_tokens=get_long_command_max_tokens()):
                    yield chunk

            else:
                yield f"❌ Unknown command: `{command}`. Type `@help` for available commands."

        return StreamingHttpResponse(command_stream(), content_type='text/plain')

    # ---------- Script Detection ----------
    if is_script_request(message):
        def script_stream():
            yield "📝 **Generating script...**\n\n"
            script_prompt = (
                "You are CodeForge. Provide only the code, without any extra text or explanation. "
                "If the user asks for a specific language, use that language. Otherwise use Python."
            )
            try:
                from apps.knowledge.query import query_knowledge
                context_chunks = query_knowledge(message, top_k=3)
            except ImportError:
                context_chunks = []
            for chunk in llm.generate_stream(message, context_chunks=context_chunks, system_override=script_prompt):
                yield chunk
            yield "\n\n💡 **Script generated.** You can copy it or ask to save it as a file."
        return StreamingHttpResponse(script_stream(), content_type='text/plain')

    # ---------- Normal Chat (with RAG) ----------
    def stream_generator():
        try:
            from apps.knowledge.query import query_knowledge
            context_chunks = query_knowledge(message, top_k=5)
        except ImportError:
            context_chunks = []
        full_response = ""
        for chunk in llm.generate_stream(message, context_chunks=context_chunks):
            full_response += chunk
            yield chunk
        # After streaming, store the full response and prompt in session for potential continuation
        # Only store if the response is substantial (more than 100 chars) and not a quick reply
        if len(full_response) > 100:
            request.session['last_incomplete_response'] = full_response
            request.session['last_incomplete_prompt'] = message
            request.session.modified = True

    return StreamingHttpResponse(stream_generator(), content_type='text/plain')