# Repository Guidelines

## Project Structure & Module Organization
- Core package lives in `src/agentic`: models and types in `models.py` and `types.py`; HTTP-facing provider in `providers/local.py`; placeholder frameworks in `frameworks/`; CLI entry in `cli/main .py`.
- Tests sit in `tests/` (e.g., `tests/test_models.py`); add new tests alongside related modules.
- `pyproject.toml` defines dependencies and pytest defaults; keep it as the single source of tooling config.

## Build, Test, and Development Commands
- Install (editable) with dev tools: `python -m venv .venv && source .venv/bin/activate && pip install -e .[dev]`.
- Run tests: `pytest` (asyncio mode is preconfigured). Use `pytest tests/test_file.py::test_case` for focused runs.
- Local CLI (experimental): `python -m agentic.cli.main council "your question"`; requires a running vLLM endpoint.

## Coding Style & Naming Conventions
- Target Python 3.11; use type hints and `dataclass` where fitting (see `types.py` for patterns).
- Follow PEP8 defaults (4-space indents, snake_case for functions/vars, PascalCase for classes).
- Keep modules cohesive: provider-specific logic under `providers/`, orchestration in `frameworks/`, shared models/types in `types.py`/`models.py`.
- Prefer small, async-friendly functions; handle HTTP errors with `raise_for_status()` like in `providers/local.py`.

## Testing Guidelines
- Framework: `pytest` with `pytest-asyncio` (async tests marked via `@pytest.mark.asyncio` as in `tests/test_models.py`).
- Name tests `test_<behavior>` and place them near related code. Use fixtures/monkeypatching to isolate network I/O.
- Aim for coverage on model invocation branches (unknown model errors, happy path), config loading, and any future framework control flow.

## Commit & Pull Request Guidelines
- Commit messages: use imperative mood and concise scopes (e.g., `Add council runner stub`, `Fix model lookup error`).
- Before opening a PR: ensure `pytest` passes, note required env vars (e.g., `VLLM_BASE_URL=http://localhost:8000`), and describe behavior changes plus testing performed.
- Include reproduction steps for bug fixes and usage examples for new capabilities; add screenshots only if UI output is relevant.

## Security & Configuration Tips
- Secrets/config: inject via env vars (`VLLM_BASE_URL`); avoid committing credentials.
- Network calls should time out and surface errors; log or surface context where feasible instead of silent failures.
