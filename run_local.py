#!/usr/bin/env python3
"""
Local runner for the agentic decision engine.

Why this exists:
- Your real CLI (agentic/cli/main.py) reads sys.argv directly.
- Local model backends (Ollama, LM Studio, vLLM, llama.cpp OpenAI mode) are
  configured via environment variables.
- This wrapper makes local runs reproducible without editing library code.

Usage examples:

  # Default (ollama):
  python run_local.py council "hello world"

  # Force ollama explicitly:
  python run_local.py --provider ollama council "hello world"
  LOCAL_LLM_PROVIDER=ollama python run_local.py council "hello world"

  # Use an OpenAI-compatible server (LM Studio / vLLM / llama.cpp OpenAI mode):
  python run_local.py --provider openai council "hello world"
  OPENAI_BASE_URL=http://localhost:1234 python run_local.py --provider openai dxo "explain gather"

Notes:
- This file only sets environment variables and then calls your existing CLI main().
- It does NOT change your package code.
"""

import os
import sys
import asyncio


# -----------------------------------------------------------------------------
# Make src/ layout importable when running this script directly (no editable install)
# -----------------------------------------------------------------------------
_REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
_SRC_DIR = os.path.join(_REPO_ROOT, "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)


# Your async CLI entrypoint lives in agentic/cli/main.py
from agentic.cli.main import main as cli_main


def _pop_flag_value(argv: list[str], flag: str) -> str | None:
    """
    Remove a flag like '--provider X' from argv and return X.
    Returns None if the flag wasn't present.

    We mutate argv in-place so agentic.cli.main sees clean args.
    """
    try:
        i = argv.index(flag)
    except ValueError:
        return None

    # If flag is last, treat as missing value (let downstream error naturally).
    if i + 1 >= len(argv):
        return None

    value = argv[i + 1]
    del argv[i : i + 2]
    return value


def configure_env(argv: list[str]) -> None:
    """
    Local run config.

    Resolution order for provider:
    1) '--provider <openai|ollama>' flag (removed from argv)
    2) LOCAL_LLM_PROVIDER env var
    3) default to 'ollama' (local-first)
    """
    # Prefer explicit CLI override, otherwise env var, otherwise default.
    provider = _pop_flag_value(argv, "--provider")
    provider = (provider or os.environ.get("LOCAL_LLM_PROVIDER") or "ollama").strip().lower()

    if provider not in ("openai", "ollama"):
        raise ValueError(f"Invalid --provider '{provider}'. Use 'openai' or 'ollama'.")

    # Pin provider so your library code doesn't "auto" flip unexpectedly.
    os.environ["LOCAL_LLM_PROVIDER"] = provider

    # Default base URLs (override from shell as needed).
    #
    # OpenAI-compatible covers:
    # - LM Studio (OpenAI mode)
    # - vLLM
    # - llama.cpp server (OpenAI mode)
    os.environ.setdefault("OPENAI_BASE_URL", "http://localhost:8000")

    # Ollama default
    os.environ.setdefault("OLLAMA_BASE_URL", "http://localhost:11434")

    # Optional backward compatibility with older naming
    # (only helpful if other parts of your code still read VLLM_BASE_URL)
    os.environ.setdefault("VLLM_BASE_URL", os.environ.get("OPENAI_BASE_URL", ""))

    # Ensure only the chosen provider's URL is "active" to reduce confusion.
    if provider == "openai":
        os.environ.pop("OLLAMA_BASE_URL", None)
    else:
        os.environ.pop("OPENAI_BASE_URL", None)
        os.environ.pop("VLLM_BASE_URL", None)


async def _run() -> None:
    # sys.argv is mutable and is exactly what your CLI reads.
    argv = sys.argv
    configure_env(argv)

    # Your cli_main reads sys.argv[1:] for framework/question.
    # We don't pass args directly; we just ensure argv is clean.
    await cli_main()


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
