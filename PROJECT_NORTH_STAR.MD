Agentic Code Ensemble Project North Star
Mission

Build a local-first, production-shaped agentic system in Python that can plan, generate, review, and iterate on code changes using a role-specialized agent ensemble and a Chair synthesizer. Start simple, stay rigorous, and grow into MCP-based tooling.

Current Focus

Implement an ensemble of role-specialized agents:

PM → requirements + acceptance criteria artifact

Dev → implementation plan (and later patch) artifact

SRE/DevOps → deploy/ops constraints + runbook artifact

Security → threat review + abuse cases artifact

Reviewer → critique + minimal-diff + test strategy artifact

Chair → synthesizes all artifacts into a final plan (then later a unified diff patch)

We distinguish:

Role-collaboration (one coherent solution via perspectives)

Proposal ensemble (multiple competing candidate solutions, scored/merged)
We start roles-first, then add proposal ensembles later.

Principles

Local-first: default to local models via vLLM; avoid personal billing risk.

Good software engineering:

src/ layout (no magic imports)

typed dataclasses / clear schemas

small functions, testability, separation of concerns

unit tests that mock model calls

Artifacts > vibes: agents produce typed JSON artifacts, not just prose.

Traceability: store per-role outputs + critiques + chair synthesis in a structured DecisionResult.

Minimal drift: each milestone should produce a runnable CLI + tests.

Roadmap Stages
Stage 1 — Local agentic ensemble (now)

Provider: vLLM OpenAI-compatible local server

Framework: Roles-first (PM/Dev/SRE/Sec/Reviewer → Chair)

Outputs: structured artifacts + final plan

CLI: run a task, print final plan + optionally dump JSON

Stage 2 — Add MCP properly

Wrap model invocation behind an MCP tool (e.g., invoke_model)

Add additional MCP tools (filesystem, git diff, test runner hooks later)

Orchestrator calls tools through MCP, not direct HTTP

Stage 3 — Patch generation + review loop

Inputs: repo snapshot / file list / issue description

Agents propose:

tests-first plan

minimal diffs

Chair outputs unified diff + test commands

Add iterative loop: run tests → feed failures → refine patch

Stage 4 — Broader AI mastery integration

While staying on-task, opportunistically build understanding of:

tokens, context windows, temperature/top_p (sampling)

evals over time (regression suites for agent quality)

transformers + math foundations (as separate learning modules)

Dawnwalker concepts as inspiration, not scope creep

“Don’t get distracted” guardrails

If a topic doesn’t directly help one of these, park it:

Role artifact schemas

Orchestration flow (initial → critique → synthesis)

Model routing (small for drafts, large for chair)

Reliable testing, logging, and packaging

MCP tool boundaries

If we detour into deep theory (transformers/math), we do it in separate exercises, not by bloating the core repo.

Sampling & cost knobs to learn (apply consistently)

max_tokens: cap output size per role to avoid rambling

temperature:

low (0.1–0.3) for reviewer/security consistency

medium (0.5–0.8) for ideation / multiple options

chair often low-medium for stable synthesis

top_p: alternative to temperature; keep simple early

routing:

small model for drafts + critiques

large model for chair synthesis

Definition of Done (for Stage 1)

python -m agentic.cli.main roles "<question>" runs end-to-end locally

Produces:

per-role JSON artifacts

critiques

chair synthesis plan

Tests run without a local model server (provider calls mocked)

Repo uses src/ layout