from ..types import (
    DecisionTask,
    DecisionResult,
    ChatMessage,
    AgentMessage,
)
from ..models import invoke_model


async def run_dxo(task: DecisionTask) -> DecisionResult:
    cfg = task.framework_config

    messages = []

    researcher = cfg["researcher"]
    reviewer = cfg["reviewer"]
    synthesizer = cfg["synthesizer"]

    research = await invoke_model(
        researcher,
        [ChatMessage(role="user", content=f"Research:\n{task.question}")],
    )
    messages.append(AgentMessage("researcher", researcher, "initial", research))

    critique = await invoke_model(
        reviewer,
        [ChatMessage(role="user", content=f"Critique this research:\n{research}")],
    )
    messages.append(AgentMessage("reviewer", reviewer, "critique", critique))

    synthesis = await invoke_model(
        synthesizer,
        [
            ChatMessage(
                role="user",
                content=(
                    f"Question:\n{task.question}\n\n"
                    f"Research:\n{research}\n\n"
                    f"Critique:\n{critique}\n\n"
                    "Produce a final decision with caveats."
                ),
            )
        ],
    )

    messages.append(AgentMessage("synthesizer", synthesizer, "synthesis", synthesis))

    return DecisionResult(
        task_id=task.id,
        final_answer=synthesis,
        messages=messages,
        metadata={"framework": "dxo"},
    )
