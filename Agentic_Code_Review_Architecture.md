# Agentic Code Review Pipeline — How the Pieces Fit (Stage 1 → Stage 3)

This document explains the **architecture and data flow** of the agentic “GitHub-style code review” system we’re building, using your current objects:

- `DecisionTask`
- `ChatMessage`
- `AgentMessage`
- `DecisionResult`

It also shows how this evolves into a real GitHub workflow with **MCP tools** (filesystem, git diff, tests) later.

---

## The core idea

Think of this system as a **structured code review meeting**:

1. You provide a *ticket / PR description* (and later a diff + files).
2. Multiple specialized “roles” produce review artifacts (PM, Dev, SRE, Security, Reviewer).
3. A “Chair” synthesizes into a single final output (plan now; patch later).
4. Everything is captured as a trace so you can audit *why* the final answer was produced.

The “agents” are not magical beings. They are **model calls** that are *tagged* with role/stage and collected into a well-defined transcript.

---

## Map the objects to GitHub reality

### `DecisionTask` = the “PR request”
- Equivalent to: **Issue text**, **PR description**, or “ticket”
- Includes the chosen process (framework) and configuration (who participates)

### `ChatMessage` = a raw model prompt message
- Equivalent to: the *email / instructions* sent to a human reviewer
- Has a `role` (`system`, `user`, `assistant`) and `content`

### `AgentMessage` = one role’s output at one stage
- Equivalent to:
  - a reviewer’s comment
  - a security note
  - an SRE checklist
  - the chair’s final summary
- It is labeled with:
  - `role_id` (who)
  - `stage` (why/when)
  - `model_key` (which model produced it)
  - `content` (what was said)

### `DecisionResult` = the pinned PR summary + full transcript
- Equivalent to the final “review verdict” comment (approve/changes requested),
  plus the full set of individual role outputs.

---

## Data Flow Diagram (DFD)

This is the data flow for the **current system** (vLLM local provider), without MCP tools yet.

```mermaid
flowchart TB
  U["User / Ticket / PR description"] --> DT["DecisionTask"]

  DT --> FW["Framework runner\n(council / dxo / ensemble / roles)"]

  FW -->|builds prompts| CM["ChatMessage[]"]
  CM --> INV["invoke_model(model_key, ChatMessage[])"]

  INV --> LP["Local Provider (HTTP)"]
  LP --> VLLM["vLLM server"]

  VLLM --> LP
  LP --> INV
  INV --> FW

  FW --> AM["AgentMessage[] (trace)"]
  FW --> DR["DecisionResult\n(final_answer + trace + metadata)"]

  DR --> OUT["Console output / PR comment text"]
```

**What to notice:**
- Frameworks create prompts (`ChatMessage[]`).
- `invoke_model` is the single “model call” choke point.
- `AgentMessage[]` is the durable transcript.
- `DecisionResult` is the final package you render to a PR comment.

---

## Class-level “what carries what” diagram

```mermaid
classDiagram
  class DecisionTask {
    id
    question
    framework
    framework_config
  }

  class ChatMessage {
    role
    content
  }

  class AgentMessage {
    role_id
    model_key
    stage
    content
  }

  class DecisionResult {
    task_id
    final_answer
    messages
    metadata
  }

  DecisionTask --> DecisionResult : produces
  DecisionResult --> AgentMessage : contains
```

---

## How a code review works end-to-end (step-by-step)

### Stage 1: “Review simulation” (what you can do now)
Input: PR text only.

1. You create a `DecisionTask`:
   - `question` = PR description
   - `framework` = `council` or `dxo` or `ensemble`
   - `framework_config` = which models play which roles

2. The framework runs:
   - Council: parallel reviewers → chair synthesis
   - DXO: research → critique → synthesis
   - Ensemble: anonymous parallel answers → aggregator

3. The framework returns a `DecisionResult`:
   - `final_answer` = what you’d paste as the “final review comment”
   - `messages` = trace of individual agent outputs

At this stage the system is a “review meeting” that only knows what you tell it in the ticket.

---

## Sequence diagram: Council as a code review meeting

Council maps naturally to “multiple reviewers + a final summarizer”.

```mermaid
sequenceDiagram
  autonumber
  participant You
  participant Framework
  participant Model

  You->>Framework: DecisionTask(question + members + chair)

  par Member alpha
    Framework->>Model: question prompt
    Model-->>Framework: alpha review comment
  and Member beta
    Framework->>Model: question prompt
    Model-->>Framework: beta review comment
  end

  Framework->>Model: chair prompt (includes alpha + beta)
  Model-->>Framework: final review summary

  Framework-->>You: DecisionResult(final_answer + trace)
```

---

## Stage 2: “Diff-aware review” (what we add next)

To do real code review, the model needs **actual code context**: a diff and/or file contents.

We add *context payloads* into `DecisionTask.framework_config`, for example:

- `diff_text`: unified diff string
- `files`: map of `{path: content}` for key files
- `test_commands`: suggested or existing test commands
- `constraints`: minimal diff, no new deps, API stability

Then the **Reviewer** can respond to *specific changes*, not just the ticket.

### DFD with “repo context” (still no MCP)

```mermaid
flowchart TB
  U["User supplies diff + file snippets"] --> DT["DecisionTask"]
  DT --> FW["Roles framework (PM/Dev/SRE/Sec/Reviewer + Chair)"]
  FW --> INV["invoke_model(...)"]
  INV --> VLLM["vLLM local"]
  FW --> DR["DecisionResult (plan/review/patch)"]
```

At this stage, you can paste diffs manually (or read them locally via a script).

---

## Stage 3: MCP makes it real (filesystem, git, tests)

MCP turns this into a genuine PR-producing system because agents can call tools:

- `read_files(paths)` → actual file contents
- `git_diff(base, head)` → real diffs
- `run_tests(cmd)` → actual test output
- `apply_patch(diff)` → generate a branch/patch

### DFD: Orchestrator with MCP tools

```mermaid
flowchart TB
  DT["DecisionTask\n(ticket + repo ref)"] --> ORCH["Orchestrator (roles + chair)"]

  ORCH --> MCP["MCP Client"]
  MCP --> T1["Tool: read_files"]
  MCP --> T2["Tool: git_diff"]
  MCP --> T3["Tool: run_tests"]
  MCP --> T4["Tool: apply_patch"]

  ORCH --> INV["invoke_model"]
  INV --> VLLM["vLLM local"]

  ORCH --> DR["DecisionResult\n(final plan or unified diff + trace)"]
```

**Why this matters:**  
Without tools, the system “imagines” the repo. With MCP, the system *measures* the repo.

---

## A realistic role-specialized code review run (the target flow)

Here’s the flow you’re aiming for with your roles (PM, Dev, SRE, Security, Reviewer, Chair):

```mermaid
sequenceDiagram
  autonumber
  participant You
  participant Orchestrator
  participant MCP
  participant PM
  participant Dev
  participant SRE
  participant Sec
  participant Rev
  participant Chair

  You->>Orchestrator: Ticket + repo reference

  Orchestrator->>MCP: read_files(paths)
  MCP-->>Orchestrator: file contents
  Orchestrator->>MCP: git_diff(base, head)
  MCP-->>Orchestrator: unified diff

  par Draft artifacts
    Orchestrator->>PM: PM artifact (goals, AC)
    Orchestrator->>Dev: Dev artifact (plan or patch)
    Orchestrator->>SRE: Ops artifact (deploy/obs)
    Orchestrator->>Sec: Security artifact (threats)
    Orchestrator->>Rev: Review artifact (risks, tests)
  end

  Orchestrator->>Rev: critique Dev vs PM
  Orchestrator->>Sec: critique Dev vs security
  Orchestrator->>SRE: critique Dev vs operability

  Orchestrator->>Chair: synthesize final plan or patch
  Chair-->>Orchestrator: unified diff + test commands

  Orchestrator->>MCP: apply_patch(diff)
  MCP-->>Orchestrator: branch created

  Orchestrator->>MCP: run_tests(command)
  MCP-->>Orchestrator: test output

  Orchestrator-->>You: DecisionResult + artifacts for PR
```

---

## Key takeaways (the “click” points)

1. **Frameworks are orchestration.**  
   They choose who speaks when, and what prompt they get.

2. **`invoke_model` is the choke point.**  
   It’s where routing, sampling, logging, retries, and later MCP integration can happen cleanly.

3. **`AgentMessage` is the transcript.**  
   It’s the durable record of each role’s work.

4. **`DecisionResult` is the PR-ready packet.**  
   It’s what you render into a GitHub comment, plus the evidence.

5. **MCP is how you stop hallucinating repo context.**  
   Tools provide the “ground truth” inputs that make review and patching reliable.

---

## Where we go next

- Add a **roles framework** where each role emits a **typed JSON artifact**.
- Add a `render_markdown(DecisionResult)` that formats the output like a GitHub review summary.
- Add MCP tools (thin first): `read_files`, `git_diff`, `run_tests` — then `apply_patch`.

That gets you quickly to a system you can *actually* use on real tickets and real diffs.
