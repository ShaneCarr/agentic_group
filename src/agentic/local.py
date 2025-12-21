import os
import httpx
from typing import List
from .types import ModelSpec, ChatMessage


def _get_provider() -> str:
    """
    Resolve which local provider to use.

    LOCAL_LLM_PROVIDER:
      - 'ollama'  -> Ollama REST API
      - 'openai'  -> OpenAI-compatible API (vLLM / LM Studio / llama.cpp)
    """
    return (os.environ.get("LOCAL_LLM_PROVIDER") or "openai").strip().lower()


def _get_openai_base_url() -> str:
    """
    Base URL for OpenAI-compatible servers.
    Prefer OPENAI_BASE_URL, fall back to legacy VLLM_BASE_URL.
    """
    return (
        os.environ.get("OPENAI_BASE_URL")
        or os.environ.get("VLLM_BASE_URL")
        or "http://localhost:8000"
    )


def _get_ollama_base_url() -> str:
    """
    Base URL for Ollama server.
    """
    return os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")


async def call_local_model(spec: ModelSpec, messages: List[ChatMessage]) -> str:
    """
    Call a local LLM backend based on LOCAL_LLM_PROVIDER.

    Supported providers:
      - ollama  -> POST /api/chat
      - openai  -> POST /v1/chat/completions (vLLM / LM Studio)

    Returns assistant message content as a string.
    """
    provider = _get_provider()

    async with httpx.AsyncClient(timeout=60.0) as client:
        if provider == "ollama":
            # -------------------------
            # Ollama Chat API
            # -------------------------
            payload = {
                "model": spec.id,
                "messages": [m.__dict__ for m in messages],
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 1024,
                },
            }

            resp = await client.post(
                f"{_get_ollama_base_url()}/api/chat",
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

            return data["message"]["content"]

        # -------------------------
        # OpenAI-compatible API
        # -------------------------
        payload = {
            "model": spec.id,
            "messages": [m.__dict__ for m in messages],
            "max_tokens": 1024,
            "temperature": 0.7,
        }

        resp = await client.post(
            f"{_get_openai_base_url()}/v1/chat/completions",
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()

        return data["choices"][0]["message"]["content"]
