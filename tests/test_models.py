import pytest
from agentic.models import invoke_model, MODELS
from agentic.types import ChatMessage

@pytest.mark.asyncio
async def test_invoke_model(monkeypatch):
    async def fake_call(spec, messages):
        return "ok"

    monkeypatch.setattr(
        "agentic.providers.local.call_local_model",
        fake_call,
    )

    result = await invoke_model("small", [ChatMessage("user", "hi")])
    assert result == "ok"
