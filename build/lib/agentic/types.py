# Enables postponed evaluation of type annotations.
# In practice: it lets you refer to types that are defined later in the file
# without quoting them. Useful for self-referential types and forward references.
# Think: "compiler option that relaxes ordering constraints for type names".
from __future__ import annotations

# dataclass = generates boilerplate: __init__, __repr__, __eq__, etc.
# Roughly like a C# record or a Java/Kotlin data class.
from dataclasses import dataclass

# Enum = like C#/Java enum, but can also inherit from str for string-like behavior.
from enum import Enum

# typing tools: these are mostly for static type checkers (mypy/pyright) and IDE help.
from typing import Literal, List, Dict, Any


# Provider is a TYPE ALIAS.
# Literal["local"] means: "the only allowed value is exactly the string 'local'"
# (for static type checkers).
#
# C# analogy: a string that is constrained to a specific constant isn't a built-in feature,
# but you'd approximate with an enum or a union type in TypeScript.
Provider = Literal["local"]


# Enum with string values.
# Inheriting from (str, Enum) means: each enum member behaves like a string too.
# e.g. str(CostClass.FREE) -> "CostClass.FREE" normally, but CostClass.FREE.value -> "free"
class CostClass(str, Enum):
    FREE = "free"
    CHEAP = "cheap"
    PREMIUM = "premium"


# frozen=True makes instances immutable (like a C# record with init-only properties).
# After creation, you can't modify fields.
@dataclass(frozen=True)
class ModelSpec:
    # Field annotations: key is a string.
    # This is a type hint + also used by dataclass to build the constructor signature.
    key: str           # logical name, e.g. "small", "large"

    id: str            # actual model id in vLLM (naming is a bit confusing: id shadows builtin name "id")
    provider: Provider # must be the literal string "local" (per type checker)
    cost_class: CostClass  # must be one of the CostClass enum values


# Represents a normal chat message (OpenAI-style roles).
@dataclass
class ChatMessage:
    # Literal union: role must be exactly one of these strings.
    role: Literal["system", "user", "assistant"]
    content: str


# Represents a message produced by a specific agent role (alpha/reviewer/etc).
@dataclass
class AgentMessage:
    role_id: str        # e.g. "alpha", "reviewer", "chair", etc.
    model_key: str      # references ModelSpec.key (like a foreign key)
    stage: str          # e.g. "initial", "critique", "synthesis" (could also be a Literal/Enum later)
    content: str


# Represents a decision "job" the system should run.
@dataclass
class DecisionTask:
    id: str
    question: str

    # framework must be one of these exact strings.
    framework: Literal["council", "dxo", "ensemble"]

    # Arbitrary config blob per framework.
    # Dict[str, Any] means: keys are strings, values can be anything.
    framework_config: Dict[str, Any]


# Represents the final output of running the task.
@dataclass
class DecisionResult:
    task_id: str
    final_answer: str

    # List[AgentMessage] = a list of AgentMessage objects.
    messages: List[AgentMessage]

    # Metadata is another arbitrary blob: timings, token counts, model ids, etc.
    metadata: Dict[str, Any]
