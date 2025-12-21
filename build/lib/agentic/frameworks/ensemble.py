import asyncio
from typing import List
from ..types import (
    DecisionTask,
    DecisionResult,
    ChatMessage,
    AgentMessage,
)
from ..models import invoke_model


async def run_ensemble(task: DecisionTask) -> DecisionResult:
    cfg = task.framework_config
    models: List[str] = cfg["models"]
    aggregator: str = cfg["aggregator"]

    async def call_model(idx: int, model: str) -> AgentMessage:
        content = await invoke_model(
            model,
            [ChatMessage(role="user", content=task.question)],
        )
        return AgentMessage(
            role_id=f"agent_{idx}",
            model_key=model,
            stage="initial",
            content=content,
        )

    agent_msgs = await asyncio.gather(
        *[call_model(i, m) for i, m in enumerate(models)]
    )

    agg_prompt = "Aggregate the following anonymous answers:\n\n"
    for m in agent_msgs:
        agg_prompt += f"{m.role_id}:\n{m.content}\n\n"

    final = await invoke_model(
        aggregator,
        [ChatMessage(role="user", content=agg_prompt)],
    )

    messages = agent_msgs + [
        AgentMessage("aggregator", aggregator, "synthesis", final)
    ]

    return DecisionResult(
        task_id=task.id,
        final_answer=final,
        messages=messages,
        metadata={"framework": "ensemble"},
    )
