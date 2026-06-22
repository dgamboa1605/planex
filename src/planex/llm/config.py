from __future__ import annotations

import os
from dataclasses import dataclass

import litellm
from dotenv import load_dotenv

load_dotenv()

OLLAMA_API_BASE = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")

# One env var per agent role — swapping Ollama for Claude/GPT is a one-liner.
CODER_MODEL = os.getenv("CODER_MODEL", "ollama/qwen2.5-coder:14b")
REASONER_MODEL = os.getenv("REASONER_MODEL", "ollama/qwen3:14b")
FAST_MODEL = os.getenv("FAST_MODEL", "ollama/llama3.1:8b")

_ROLE_MODEL_MAP: dict[str, str] = {
    "coder": CODER_MODEL,
    "reasoner": REASONER_MODEL,
    "fast": FAST_MODEL,
}

litellm.suppress_debug_info = True


@dataclass(frozen=True)
class LLMConfig:
    model: str
    api_base: str | None
    temperature: float = 0.1
    max_tokens: int = 8192


def get_llm_config(role: str = "coder") -> LLMConfig:
    """Return LiteLLM config for the given agent role."""
    model = _ROLE_MODEL_MAP.get(role, CODER_MODEL)
    api_base = OLLAMA_API_BASE if model.startswith("ollama/") else None
    return LLMConfig(model=model, api_base=api_base)


def complete(prompt: str, role: str = "coder", **kwargs) -> str:
    """Single-turn completion via LiteLLM. Returns the response text."""
    cfg = get_llm_config(role)
    response = litellm.completion(
        model=cfg.model,
        messages=[{"role": "user", "content": prompt}],
        api_base=cfg.api_base,
        temperature=cfg.temperature,
        max_tokens=cfg.max_tokens,
        **kwargs,
    )
    return response.choices[0].message.content
