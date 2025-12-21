import sys
import uuid
import asyncio
from agentic.types import DecisionTask
from agentic.frameworks.council import run_council
from agentic.frameworks.dxo import run_dxo
from agentic.frameworks.ensemble import run_ensemble


async def main():
    framework = sys.argv[1]
    question = " ".join(sys.argv[2:])

    task = DecisionTask(
        id=str(uuid.uuid4()),
        question=question,
        framework=framework,
        framework_config={},
    )

    if framework == "council":
        task.framework_config = {
            "members": [
                {"id": "alpha", "model": "small"},
                {"id": "beta", "model": "large"},
            ],
            "chair": "large",
        }
        result = await run_council(task)

    elif framework == "dxo":
        task.framework_config = {
            "researcher": "small",
            "reviewer": "small",
            "synthesizer": "large",
        }
        result = await run_dxo(task)

    elif framework == "ensemble":
        task.framework_config = {
            "models": ["small", "large"],
            "aggregator": "large",
        }
        result = await run_ensemble(task)

    else:
        raise ValueError("Unknown framework")

    print("\nFINAL ANSWER\n============")
    print(result.final_answer)


if __name__ == "__main__":
    asyncio.run(main())
