"""
Factory that returns the right LLM back-end.

Env vars
--------
LLM_ENGINE   llama_cpp (default) | vllm | openai
MODEL_PATH   overrides app.config.MODEL_PATH
LLM_THREADS  logical cores (default 4)
"""
import os, pathlib
from .llama_cpp import LlamaCppEngine
from app.config import MODEL_PATH as CONFIG_PATH          # "models/mistral.gguf"

# project root = two levels above this file (…/response_aigent)
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]

def _abs(p: str | os.PathLike) -> str:
    """Return absolute path, interpreting *p* relative to project root."""
    p = pathlib.Path(p)
    return str(p if p.is_absolute() else PROJECT_ROOT / p)

def get_engine():
    choice = os.getenv("LLM_ENGINE", "llama_cpp").lower()

    if choice == "llama_cpp":
        model_path = _abs(os.getenv("MODEL_PATH", CONFIG_PATH))
        return LlamaCppEngine(
            model_path=model_path,
            n_ctx=2048,
            n_threads=int(os.getenv("LLM_THREADS", 4)),
        )

    raise ValueError(f"Unsupported LLM_ENGINE='{choice}'")
