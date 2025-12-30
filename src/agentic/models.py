import os
from typing import Dict, List
from .types import ModelSpec, ChatMessage, CostClass
from .local import call_local_model

# MODELS: Dict[str, ModelSpec] = {
#     "small": ModelSpec(
#         key="small",
#         id="Qwen/Qwen2.5-Coder-7B-Instruct",
#         provider="local",
#         cost_class=CostClass.FREE,
#     ),
#     "large": ModelSpec(
#         key="large",
#         id="Qwen/Qwen2.5-Coder-32B-Instruct",
#         provider="local",
#         cost_class=CostClass.FREE,
#     ),
# }


MODELS: Dict[str, ModelSpec] = {
    # Ultra-fast routing / control / tool glue
    "nano": ModelSpec(
        key="nano",
        id="llama3.2:1b",
        provider="local",
        cost_class=CostClass.FREE,
    ),

    # Small, instruction-following, good generalist
    "small": ModelSpec(
        key="small",
        id="qwen2.5:1.5b-instruct",
        provider="local",
        cost_class=CostClass.FREE,
    ),

    # Strong reasoning-per-token, good “thinking” model
    "medium": ModelSpec(
        key="medium",
        id="phi3:mini",
        provider="local",
        cost_class=CostClass.FREE,
    ),

    # Language-polish / summarization / user-facing text
    "writer": ModelSpec(
        key="writer",
        id="gemma2:2b",
        provider="local",
        cost_class=CostClass.FREE,
    ),
         "smallcode": ModelSpec(
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
