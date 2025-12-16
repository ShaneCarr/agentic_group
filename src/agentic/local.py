# Standard library import.
# Used here to read environment variables.
import os

# Third-party HTTP client library.
# httpx is roughly "requests + asyncio + sane defaults".
import httpx

# Typing helper: List[T] means "a list containing elements of type T".
# (In Python 3.9+ you can also write list[T].)
from typing import List

# Relative import from your own package.
# "..types" means "go up one package level, then import types.py".
# We're importing the dataclasses you defined earlier.
from ..types import ModelSpec, ChatMessage


# Read an environment variable if it exists.
# If not set, default to "http://localhost:8000".
#
# This is how you avoid hard-coding deployment details.
# Think: process-level config, not code-level config.
VLLM_BASE_URL = os.environ.get("VLLM_BASE_URL", "http://localhost:8000")


# Define an *async* function.
# Calling this returns a coroutine; you must 'await' it.
#
# Signature:
# - spec: a ModelSpec object (contains model id, cost class, provider)
# - messages: a list of ChatMessage objects
# - returns: a string (the model's text output)
async def call_local_model(spec: ModelSpec, messages: List[ChatMessage]) -> str:

    # Build the JSON payload expected by the OpenAI-compatible API.
    #
    # This is a normal Python dictionary.
    payload = {
        # spec.id is a string like "llama-3.1-8b"
        "model": spec.id,

        # Convert each ChatMessage object into a plain dict.
        #
        # IMPORTANT:
        # This is NOT a dict comprehension.
        # This is a LIST comprehension:
        #
        #   [expression for item in iterable]
        #
        # For each ChatMessage 'm', m.__dict__ is:
        #   {"role": "...", "content": "..."}
        #
        # Equivalent expanded form:
        #
        # messages_as_dicts = []
        # for m in messages:
        #     messages_as_dicts.append(m.__dict__)
        #
        # __dict__ works because ChatMessage is a dataclass
        # and stores its fields as attributes.
        "messages": [m.__dict__ for m in messages],

        # Hard limit on generated tokens.
        "max_tokens": 1024,

        # Controls randomness.
        # 0.0 = deterministic
        # higher = more variation
        "temperature": 0.7,
    }

    # Create an asynchronous HTTP client.
    #
    # 'async with' means:
    # - open the client
    # - guarantee cleanup (connection close) when block exits
    #
    # timeout=60.0 applies to the full request lifecycle.
    async with httpx.AsyncClient(timeout=60.0) as client:

        # Send an HTTP POST request.
        #
        # await = suspend this coroutine until the network call finishes.
        resp = await client.post(
            # Build the full URL by concatenating base + path
            f"{VLLM_BASE_URL}/v1/chat/completions",

            # Automatically JSON-encode the payload dict
            # and set Content-Type: application/json
            json=payload,
        )

        # Raise an exception for HTTP errors (4xx / 5xx).
        # This is fail-fast, not silent failure.
        resp.raise_for_status()

        # Parse response body as JSON.
        # Result is a Python dict (nested lists/dicts).
        data = resp.json()

    # Extract the model's text output.
    #
    # data["choices"] is a list
    # data["choices"][0] is the first completion
    # ["message"]["content"] is the generated text
    #
    # This matches the OpenAI chat completion schema.
    return data["choices"][0]["message"]["content"]
