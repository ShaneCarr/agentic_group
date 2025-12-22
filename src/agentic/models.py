from typing import Dict, List
from .types import ModelSpec, ChatMessage, CostClass
from .local import call_local_model


# Logical model keys → concrete backend model IDs.
# For Ollama, these IDs MUST match tags returned by:
#   curl http://localhost:11434/api/tags
MODELS: Dict[str, ModelSpec] = {
    "small": ModelSpec(
        key="small",
        id="qwen2.5-coder:7b",     # Ollama tag
        provider="local",
        cost_class=CostClass.FREE,
    ),
    "large": ModelSpec(
        key="large",
        id="qwen2.5-coder:32b",    # Ollama tag
        provider="local",
        cost_class=CostClass.FREE,
    ),
}


async def invoke_model(model_key: str, messages: List[ChatMessage]) -> str:
    """
    Resolve a logical model key (e.g. 'small', 'large') to a concrete model
    and invoke it via the local backend adapter.
    """
    spec = MODELS.get(model_key)
    if not spec:
        raise ValueError(f"Unknown model: {model_key}")

    return await call_local_model(spec, messages)
