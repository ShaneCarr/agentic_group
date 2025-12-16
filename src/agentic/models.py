from typing import Dict, List
from .types import ModelSpec, ChatMessage, CostClass
from .providers.local import call_local_model


MODELS: Dict[str, ModelSpec] = {
    "small": ModelSpec(
        key="small",
        id="Qwen/Qwen2.5-Coder-7B-Instruct",
        provider="local",
        cost_class=CostClass.FREE,
    ),
    "large": ModelSpec(
        key="large",
        id="Qwen/Qwen2.5-Coder-32B-Instruct",
        provider="local",
        cost_class=CostClass.FREE,
    ),
}


async def invoke_model(model_key: str, messages: List[ChatMessage]) -> str:
    spec = MODELS.get(model_key)
    if not spec:
        raise ValueError(f"Unknown model: {model_key}")

    return await call_local_model(spec, messages)
