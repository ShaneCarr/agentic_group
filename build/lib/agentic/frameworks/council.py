import asyncio
from typing import List, Dict, Any
from ..types import (
    DecisionTask,
    DecisionResult,
    ChatMessage,
    AgentMessage,
)
from ..models import invoke_model


async def run_council(task: DecisionTask) -> DecisionResult:
    cfg = task.framework_config
    members: List[Dict[str, str]] = cfg["members"]
    chair_model: str = cfg["chair"]

    async def call_member(member: Dict[str, str]) -> AgentMessage:
        content = await invoke_model(
            member["model"],
            [ChatMessage(role="user", content=task.question)],
        )
        return AgentMessage(
            role_id=member["id"],
            model_key=member["model"],
            stage="initial",
            content=content,
        )

    member_msgs = await asyncio.gather(*[call_member(m) for m in members])

    chair_prompt = build_chair_prompt(task.question, member_msgs)

    chair_answer = await invoke_model(
        chair_model,
        [ChatMessage(role="user", content=chair_prompt)],
    )

    messages = member_msgs + [
        AgentMessage(
            role_id="chair",
            model_key=chair_model,
            stage="synthesis",
            content=chair_answer,
        )
    ]

    return DecisionResult(
        task_id=task.id,
        final_answer=chair_answer,
        messages=messages,
        metadata={"framework": "council"},
    )

 
def build_chair_prompt(question: str, members: List[AgentMessage]) -> str:
    lines = [
        "You are the chair of an expert council.",
        "Summarize consensus, disagreements, and give a final recommendation.\n",
        f"Question:\n{question}\n",
        "Expert inputs:\n",
    ]
    for m in members:
        lines.append(f"{m.role_id}:\n{m.content}\n")
    return "\n".join(lines)
