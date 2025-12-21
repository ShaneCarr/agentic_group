import os
import httpx
from typing import List
from .types import ModelSpec, ChatMessage

VLLM_BASE_URL = os.environ.get("VLLM_BASE_URL", "http://localhost:8000")


async def call_local_model(spec: ModelSpec, messages: List[ChatMessage]) -> str:
    payload = {
        "model": spec.id,
        "messages": [m.__dict__ for m in messages],
        "max_tokens": 1024,
        "temperature": 0.7,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{VLLM_BASE_URL}/v1/chat/completions",
            json=payload,
        )
        resp.raise_for_status()
        data = resp.json()

    return data["choices"][0]["message"]["content"]
