# apps/chat/llm_wrapper.py
import logging
from pathlib import Path
from django.conf import settings
from llama_cpp import Llama

logger = logging.getLogger(__name__)

class LLMWrapper:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # Set default system prompt even if loading fails
        self.system_prompt = (
            "You are CodeForge, a senior software architect and developer. "
            "You help users build software, write code, and solve engineering problems. "
            "You provide clear, concise, and professional responses."
        )
        self.llm = None
        try:
            model_path = getattr(settings, 'LLM_MODEL_PATH', None)
            if not model_path or not Path(model_path).exists():
                logger.error(f"Model not found at {model_path}")
                return
            self.llm = Llama(
                model_path=str(model_path),
                n_ctx=settings.LLM_N_CTX,
                n_batch=settings.LLM_N_BATCH,
                n_threads=getattr(settings, 'LLM_N_THREADS', 4),
                verbose=False,
                use_mlock=False,
            )
            logger.info(f"LLM loaded from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load LLM: {e}")
            self.llm = None

    def generate_stream(self, user_message, context_chunks=None, system_override=None):
        if self.llm is None:
            yield "⚠️ LLM model not loaded. Please check that the model file exists and is correct."
            return
        
        system = system_override or self.system_prompt
        messages = [
            {"role": "system", "content": system},
        ]
        if context_chunks:
            context_text = "\n\n".join(context_chunks)
            messages.append({"role": "system", "content": f"Relevant context:\n{context_text}"})
        messages.append({"role": "user", "content": user_message})

        prompt = ""
        for msg in messages:
            prompt += f"<|im_start|>{msg['role']}\n{msg['content']}<|im_end|>\n"
        prompt += "<|im_start|>assistant\n"

        stream = self.llm.create_completion(
            prompt,
            max_tokens=2048,
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