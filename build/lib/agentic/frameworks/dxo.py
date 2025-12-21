# Import the “schema” types for tasks and results.
# These are dataclasses that define what fields exist and their types.
from ..types import (
    DecisionTask,     # input: question + framework + config
    DecisionResult,   # output: final answer + trace + metadata
    ChatMessage,      # basic chat message type used to call models
    AgentMessage,     # trace record for each pipeline stage
)

# Import the model-calling function.
# invoke_model(model_key_or_spec, messages) -> str
from ..models import invoke_model


# DXO runner: takes a DecisionTask and returns a DecisionResult.
# async because it makes network calls (or local HTTP calls) to the model server.
async def run_dxo(task: DecisionTask) -> DecisionResult:

    # Grab the per-task config dict.
    # This allows DXO to be parameterized without changing code.
    # Example cfg:
    # {"researcher": "small", "reviewer": "small", "synthesizer": "large"}
    cfg = task.framework_config

    # Select which model/config to use for each stage.
    # These values are whatever invoke_model expects: often a string model_key.
    researcher = cfg["researcher"]
    reviewer = cfg["reviewer"]
    synthesizer = cfg["synthesizer"]

    # We'll record a full trace of agent outputs here.
    # This becomes DecisionResult.messages for auditing / debugging / learning.
    messages = []
    
    # ---- Stage 1: Research ----
    # Call the model configured as "researcher" with a single user message.
    # The model output is a string: "research".
    research = await invoke_model(
        researcher,
        [ChatMessage(role="user", content=f"Research:\n{task.question}")],
    )

    # Record the research output as an AgentMessage trace entry.
    # AgentMessage(role_id, model_key, stage, content)
    messages.append(AgentMessage("researcher", researcher, "initial", research))

    # ---- Stage 2: Critique ----
    # Call the reviewer model and ask it to critique the research text.
    critique = await invoke_model(
        reviewer,
        [ChatMessage(role="user", content=f"Critique this research:\n{research}")],
    )

    # Record critique output in the trace.
    messages.append(AgentMessage("reviewer", reviewer, "critique", critique))

    # ---- Stage 3: Synthesis ----
    # Call the synthesizer model with ALL context:
    # - original question
    # - research result
    # - critique result
    # Then instruct it to produce a final decision (with caveats).
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

    # Record synthesis output.
    messages.append(AgentMessage("synthesizer", synthesizer, "synthesis", synthesis))

    # Return a structured result:
    # - final_answer is the synthesis (what callers generally want)
    # - messages contains the full trace for transparency
    # - metadata tags which framework produced this result
    return DecisionResult(
        task_id=task.id,
        final_answer=synthesis,
        messages=messages,
        metadata={"framework": "dxo"},
    )
