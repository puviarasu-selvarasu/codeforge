# apps/chat/llm_wrapper.py
import gc
import psutil
import logging
from pathlib import Path
from django.conf import settings
from llama_cpp import Llama

logger = logging.getLogger(__name__)

class LLMWrapper:
    _instance = None
    _model = None
    _current_model_type = None
    _max_tokens = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_model(self, model_type=None):
        if model_type is None:
            model_type = getattr(settings, 'DEFAULT_LLM_MODEL', '1.5B')

        if self._current_model_type == model_type and self._model is not None:
            logger.info(f"Model {model_type} already loaded.")
            return

        if model_type == '7B':
            mem = psutil.virtual_memory()
            free_gb = mem.available / (1024**3)
            if free_gb < 4.0:
                logger.warning(f"Not enough RAM for 7B (free: {free_gb:.1f} GB). Falling back to 1.5B.")
                model_type = '1.5B'

        if self._model is not None:
            del self._model
            gc.collect()
            logger.info("Unloaded previous model.")

        if model_type == '7B':
            model_path = getattr(settings, 'LLM_7B_MODEL_PATH', None)
            self._max_tokens = getattr(settings, 'LLM_7B_MAX_TOKENS', 2048)
        else:
            model_path = getattr(settings, 'LLM_15B_MODEL_PATH', None)
            self._max_tokens = getattr(settings, 'LLM_15B_MAX_TOKENS', 1024)

        if not model_path or not Path(model_path).exists():
            logger.error(f"Model file not found: {model_path}")
            self._model = None
            self._current_model_type = None
            self._max_tokens = None
            return

        try:
            self._model = Llama(
                model_path=str(model_path),
                n_ctx=settings.LLM_N_CTX,
                n_batch=settings.LLM_N_BATCH,
                n_threads=getattr(settings, 'LLM_N_THREADS', 4),
                verbose=False,
                use_mlock=False,
            )
            self._current_model_type = model_type
            logger.info(f"Loaded model: {model_type} from {model_path} (max_tokens: {self._max_tokens})")
        except Exception as e:
            logger.error(f"Failed to load model {model_type}: {e}")
            self._model = None
            self._current_model_type = None
            self._max_tokens = None

    def generate_stream(self, user_message, context_chunks=None, system_override=None, max_tokens=None):
        if self._model is None:
            self.load_model(getattr(settings, 'DEFAULT_LLM_MODEL', '1.5B'))
            if self._model is None:
                yield "⚠️ No model loaded. Please check your configuration."
                return

        # Use provided max_tokens, or fallback to self._max_tokens, then default
        max_tokens = max_tokens or self._max_tokens or 1024

        system = system_override or self.system_prompt
        messages = [{"role": "system", "content": system}]
        if context_chunks:
            context_text = "\n\n".join(context_chunks)
            messages.append({"role": "system", "content": f"Relevant context:\n{context_text}"})
        messages.append({"role": "user", "content": user_message})

        prompt = ""
        for msg in messages:
            prompt += f"<|im_start|>{msg['role']}\n{msg['content']}<|im_end|>\n"
        prompt += "<|im_start|>assistant\n"

        stream = self._model.create_completion(
            prompt,
            max_tokens=max_tokens,
            temperature=0.7,
            top_p=0.9,
            echo=False,
            stream=True,
        )
        for chunk in stream:
            if 'choices' in chunk:
                delta = chunk['choices'][0].get('text', '')
                if delta:
                    yield delta

    system_prompt = (
        "You are CodeForge, a senior software architect, technical lead, and code generator. "
        "Your role is to help the user design, plan, and build production‑ready software. "
        "You do NOT create files on disk – you provide the code, the architecture, and the reasoning. "
        "For every request: "
        "1. Understand the user's idea and ask clarifying questions if needed. "
        "2. Propose a robust architecture and explain your choices. "
        "3. Generate the complete code for each file in markdown code blocks. "
        "4. When the user asks to add a new feature, update your mental model and generate the relevant code. "
        "5. Always include language tags (e.g., ```python, ```php, ```java) so the code is copyable. "
        "6. Do not attempt to write files to disk – just provide the code."
    )