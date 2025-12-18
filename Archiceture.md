# Architecture

## Overview
The agentic system is a modular framework for orchestrating AI agents with pluggable providers and frameworks. Core components are organized by responsibility: models/types, HTTP providers, framework orchestration, and CLI integration.

## Directory Structure
```
src/agentic/
├── models.py          # Agent and response models
├── types.py           # Shared data types and configurations
├── providers/
│   └── local.py       # HTTP-based LLM provider (vLLM integration)
├── frameworks/
│   └── ...            # Orchestration logic (council, etc.)
└── cli/
    └── main.py        # Command-line entry point

tests/
├── test_models.py     # Model and invocation tests
└── test_*.py          # Framework/provider tests
```

## Core Components

### Models & Types (`models.py`, `types.py`)
- Dataclass-based agent and response definitions
- Type hints for configuration and runtime state
- Shared interfaces for provider implementations

### Providers (`providers/local.py`)
- HTTP client for remote LLM endpoints (vLLM)
- Async request/response handling with error propagation
- Configurable base URL via environment variables

### Frameworks (`frameworks/`)
- Orchestration engines (e.g., council runner)
- Agent coordination and result aggregation
- Placeholder stubs for future expansions

### CLI (`cli/main.py`)
- Experimental command-line interface
- Requires running LLM endpoint (e.g., `VLLM_BASE_URL=http://localhost:8000`)

## Data Flow
1. **Input**: CLI or API receives user query
2. **Provider Call**: Framework routes to provider (local HTTP endpoint)
3. **LLM Processing**: Remote service processes and returns response
4. **Output**: Formatted result returned to user

## Testing Strategy
- Async tests via `pytest-asyncio`
- Fixtures isolate network dependencies
- Coverage on model invocation, config loading, and framework control flow

```mermaid
flowchart TB
  CLI["CLI (agentic.cli.main)"]
  FW["Frameworks (council / dxo / ensemble)"]
  INV["Model Dispatcher (invoke_model)"]
  PROV["Local Provider"]
  VLLM["vLLM Server"]

  CLI --> FW
  FW --> INV
  INV --> PROV
  PROV --> VLLM
```

```mermaid
classDiagram
  class DecisionTask {
    +str id
    +str question
    +str framework
    +dict framework_config
  }

  class DecisionResult {
    +str task_id
    +str final_answer
    +list~AgentMessage~ messages
    +dict metadata
  }

  class AgentMessage {
    +str role_id
    +str model_key
    +str stage
    +str content
  }

  class ChatMessage {
    +str role
    +str content
  }

  DecisionTask --> DecisionResult : produces
  DecisionResult --> AgentMessage : contains

```

```mermaid
sequenceDiagram
  autonumber
  participant User
  participant CLI
  participant Council as frameworks/council.py
  participant Invoke as models.invoke_model
  participant VLLM as vLLM (local)

  User->>CLI: council "question..."
  CLI->>Council: DecisionTask(members, chair)

  par Member alpha
    Council->>Invoke: invoke_model(alpha.model, [user question])
    Invoke->>VLLM: /v1/chat/completions
    VLLM-->>Invoke: alpha answer
    Invoke-->>Council: alpha answer
  and Member beta
    Council->>Invoke: invoke_model(beta.model, [user question])
    Invoke->>VLLM: /v1/chat/completions
    VLLM-->>Invoke: beta answer
    Invoke-->>Council: beta answer
  end

  Council->>Council: build_chair_prompt(question, member_answers)
  Council->>Invoke: invoke_model(chair, [chair_prompt])
  Invoke->>VLLM: /v1/chat/completions
  VLLM-->>Invoke: chair synthesis
  Invoke-->>Council: chair synthesis
  Council-->>CLI: DecisionResult(final_answer + trace)
  CLI-->>User: prints final_answer

```

```mermaid

sequenceDiagram
  autonumber
  participant CLI
  participant DXO as frameworks/dxo.py
  participant Invoke as models.invoke_model
  participant VLLM as vLLM (local)

  CLI->>DXO: DecisionTask(researcher, reviewer, synthesizer)

  DXO->>Invoke: invoke_model(researcher, ["Research: question"])
  Invoke->>VLLM: /v1/chat/completions
  VLLM-->>Invoke: research
  Invoke-->>DXO: research

  DXO->>Invoke: invoke_model(reviewer, ["Critique this research: ..."])
  Invoke->>VLLM: /v1/chat/completions
  VLLM-->>Invoke: critique
  Invoke-->>DXO: critique

  DXO->>Invoke: invoke_model(synthesizer, ["Question + research + critique + instructions"])
  Invoke->>VLLM: /v1/chat/completions
  VLLM-->>Invoke: synthesis
  Invoke-->>DXO: synthesis

  DXO-->>CLI: DecisionResult(final_answer + trace)


```

ensemble flow diagram

```mermaid
sequenceDiagram
  autonumber
  participant CLI
  participant Ens as frameworks/ensemble.py
  participant Invoke as models.invoke_model
  participant VLLM as vLLM (local)

  CLI->>Ens: DecisionTask(models[], aggregator)

  par agent_0
    Ens->>Invoke: invoke_model(models[0], [question])
    Invoke->>VLLM: /v1/chat/completions
    VLLM-->>Invoke: ans_0
    Invoke-->>Ens: ans_0
  and agent_1
    Ens->>Invoke: invoke_model(models[1], [question])
    Invoke->>VLLM: /v1/chat/completions
    VLLM-->>Invoke: ans_1
    Invoke-->>Ens: ans_1
  end

  Ens->>Ens: build agg_prompt with agent_i answers
  Ens->>Invoke: invoke_model(aggregator, [agg_prompt])
  Invoke->>VLLM: /v1/chat/completions
  VLLM-->>Invoke: final
  Invoke-->>Ens: final
  Ens-->>CLI: DecisionResult(final_answer + trace)

```