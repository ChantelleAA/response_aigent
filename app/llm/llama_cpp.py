"""Thin wrapper around llama-cpp-python that streams tokens."""

from llama_cpp import Llama
from app.config import MODEL_PATH

class LlamaCppEngine:
    def __init__(self, model_path, n_ctx, n_threads):
        self.llm = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_batch=512,
            n_threads=n_threads,
            n_gpu_layers=0,
        )

    # generator that yields partial tokens
    def stream(self, prompt, **kw):
        for chunk in self.llm(prompt, stream=True, **kw):
            yield chunk["choices"][0]["text"]
