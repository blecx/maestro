# MAESTRO — Multi-Agent Execution System for Task Resolution and Orchestration

**Status:** Active Design → Implementation in Progress  
**Last Updated:** 2026-03-02  
**Supersedes:** Single-chain autonomous agent (v1) described in `AUTONOMOUS-AGENT-GUIDE.md`  
**Implementation tracking:** GitHub issues #708–#715

---

## Why MAESTRO Exists

The v1 autonomous agent (`autonomous_workflow_agent.py`) was analysed and found to fail in three fundamental ways:

| Root Cause | Symptom | Impact |
|-----------|---------|--------|
| 3200-char context cap | Project instructions truncated to 200 chars | Agent ignores conventions, makes known mistakes |
| 3 stateless LLM threads | Planning→Coding→Review via text string handoffs | Each phase loses what previous phase learned |
| No human gate | Bad plan goes straight to implementation | Compounding errors, wasted API quota |

MAESTRO fixes all three with: a **shared context bus** (SQLite, exposed as MCP), a **single coder thread** with full context, and a **human approval gate** after planning.

---

## Design Principles

1. **One agent, one job** — no agent does two things
2. **Shared state, not text handoffs** — every agent reads and writes structured data to the context bus
3. **Models matched to complexity** — `gpt-4o-mini` for simple tasks, `gpt-4o` only when needed
4. **MCP as the tool protocol** — all tools are MCP endpoints, same protocol for agents, VS Code, and future clients
5. **Memory that compounds** — every resolved issue writes learnings to the knowledge graph; future issues query it first
6. **Human stays in the loop** — plan approval gate before any code is written

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│  Human Interface                                                      │
│  VS Code + Copilot  ←→  CLI ./work-issue 123  ←→  Approval Gate :8001│
└─────────────────┬───────────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────────┐
│  Maestro Orchestrator (maestro.py)                                    │
│  Reads queue → spawns workers → monitors → reports                   │
└──┬──────────────────────────────────────────────────────────────────┘
   │
   │  Per-issue worker (Docker container or host process)
   │
   ├─ Router Agent        gpt-4o-mini   Score complexity, select model tier
   ├─ Decomposer Agent    gpt-4o-mini   Epic → N atomic sub-issues (if needed)
   ├─ Planner Agent       mini / full   Goal, files, AC, validation commands
   │    ↓ [Human Approval Gate]
   ├─ Coder Agent         mini / full   Single persistent thread, full context
   ├─ Validator Agent     gpt-4o-mini   Run tests, parse results, pass/block
   └─ Reviewer Agent      gpt-4o        Diff review, DDD compliance, PR body
```

---

## MCP Server Layer

All agents communicate exclusively via MCP (Model Context Protocol, Streamable HTTP).  
MCP servers run as Docker containers and are shared across all worker agents.

### Existing servers (unchanged)

| Server | Port | Purpose |
|--------|------|---------|
| `mcp-bash-gateway` | 3011 | Policy-gated shell execution |
| `mcp-github-ops` | 3018 | Issues, PRs, branches |
| `mcp-repo-fundamentals` | 3021 | Filesystem + Git + Search |
| `mcp-offline-docs` | 3014 | Library documentation |

### New servers (MAESTRO-specific)

| Server | Port | Purpose |
|--------|------|---------|
| `mcp-memory` | 3030 | Knowledge graph — entities, observations, relations |
| `mcp-agent-bus` | 3031 | Context bus — task state, file snapshots, plan, checkpoints |

---

## Memory System — Three Layers

```
Short-term     Agent thread (in-process)
               Lost when agent exits — not persisted

Working        mcp-agent-bus (SQLite: .maestro/bus.db)
               Lives for duration of one task run
               Holds: issue JSON, plan, file snapshots, test results

Long-term      mcp-memory (SQLite: .maestro/memory.db)
               Persists forever across all runs
               Holds: knowledge graph of files, patterns, past issues
```

### What the knowledge graph stores

```
Entity: "src/services/withApiFallback.ts"  type=file
  Observation: "Import path must be ../../../, not ../../  (learned 2026-03-01)"
  Observation: "Requires matching test in test/unit/services/"

Entity: "pattern:cross-repo-import"  type=pattern
  Observation: "Test files 3 levels deep from src/ need ../../../ prefix"
  Relation: caused_failure_in → withApiFallback.ts

Entity: "#269"  type=issue
  Observation: "Resolved with gpt-4o-mini, 3 files, 15 tests, complexity=3"
  Relation: triggered → pattern:cross-repo-import
```

**The Planner queries memory before writing any plan.**  
**The Reviewer writes to memory after every successful PR.**  
This is how the system gets measurably smarter with each issue.

---

## Model Routing — Complexity Scoring

The Router Agent scores each issue 0–10 and assigns a model tier:

| Signal | Score |
|--------|-------|
| 2-3 files affected | +1 |
| 4+ files affected | +3 |
| 30-100 lines estimated | +1 |
| 100+ lines estimated | +3 |
| Cross-repo change | +2 |
| New module/class | +2 |
| Test required | +1 |
| Bug fix label | -1 |
| Epic label | → forced decompose |

| Score | Tier | Planning model | Coding model |
|-------|------|---------------|-------------|
| 0–2 | MINI | gpt-4o-mini | gpt-4o-mini |
| 3–5 | MINI+REVIEW | gpt-4o-mini | gpt-4o-mini |
| 6+ | FULL | gpt-4o | gpt-4o |
| Epic | DECOMPOSE | gpt-4o-mini splits | gpt-4o implements each |

---

## Context Bus — MCP Tool Contract

The `mcp-agent-bus` server exposes these tools (all agents use them):

```python
bus_create_run(issue_number, repo) → {run_id}
bus_write_plan(run_id, goal, files, ac, validation_cmds, estimated_minutes) → ok
bus_read_context_packet(run_id) → {issue, plan, file_snapshots, test_results}
bus_write_snapshot(run_id, filepath, content_before, content_after) → ok
bus_write_validation(run_id, command, stdout, exit_code, passed) → ok
bus_write_checkpoint(run_id, label, metadata) → ok
bus_set_status(run_id, status) → ok
```

### Status lifecycle

```
created → routing → planning → awaiting_approval → approved
       → coding → validating → reviewing → pr_created → done
                                                       → failed
```

---

## Memory Server — MCP Tool Contract

The `mcp-memory` server exposes these tools:

```python
add_entity(name, entity_type) → {entity_id}
add_observation(entity_name, entity_type, content,
                confidence=1.0, source="agent") → ok
add_relation(from_entity, relation_type, to_entity, context="") → ok
search_memory(query, entity_type=None, limit=5) → [{entity, observations, score}]
get_entity(name) → {entity, observations, relations}
```

---

## Epic Decomposition

When the Router detects an Epic label or score > 8:

1. **Decomposer Agent** (gpt-4o-mini) reads the epic body and produces N sub-issue specs
2. Each spec contains: goal, scope, AC, files, validation commands, `depends_on` list
3. **Human reviews** the decomposition (approval gate shows dependency graph)
4. **Issue Creator** creates each sub-issue on GitHub with size labels
5. Queue manager picks them up in dependency order, running independent ones in parallel

---

## Docker Topology

```yaml
# docker-compose.maestro.yml (single command brings up the full system)

services:
  memory-mcp:          # :3030  NEW — knowledge graph
  agent-bus-mcp:       # :3031  NEW — context bus
  approval-gate:       # :8001  NEW — human gate web UI
  orchestrator:        # reads queue, spawns workers
  worker:              # ephemeral — 1 per issue, scalable
    scale: 3

# Existing services (referenced, not redefined here)
  bash-gateway-mcp:    # :3011  EXISTING
  github-ops-mcp:      # :3018  EXISTING
  repo-fundamentals:   # :3021  EXISTING

# Shared volume
volumes:
  maestro_data:        # .maestro/  (memory.db, bus.db, .tmp/)
```

---

## Coder Agent — The Critical Fix

The v1 agent's coding phase had three separate stateless threads that communicated via text strings. MAESTRO's Coder Agent is a **single persistent thread** that:

1. Calls `bus_read_context_packet(run_id)` at startup — gets full issue, plan, all existing snapshots
2. Calls `search_memory(relevant_keywords)` — gets pre-loaded learnings
3. Calls `file_read(path)` via mcp-bash-gateway **before every edit** — never hallucinates file state
4. Calls `bus_write_snapshot()` before and after each file touch — full rollback possible
5. Calls validation commands via mcp-bash-gateway, writes results to bus
6. If tests fail: reasons about failure in the **same thread** (full history visible), retries
7. After success: calls `bus_set_status("validating")`, hands off to Validator

No text is passed between phases. The bus is the only handoff mechanism.

---

## Implementation Order

| Issue | Size | Files | Depends on |
|-------|------|-------|-----------|
| #708 — mcp-memory server | S | `apps/mcp/memory/` | — |
| #709 — mcp-agent-bus server | S | `apps/mcp/agent_bus/` | — |
| #710 — MCPMultiClient | S | `agents/mcp_client.py` | #708, #709 |
| #711 — Router Agent | S | `agents/router_agent.py` | #710 |
| #712 — Coder Agent (new) | M | `agents/coder_agent.py` | #710, #711 |
| #713 — Maestro Orchestrator | M | `agents/maestro.py` | #711, #712 |
| #714 — Docker compose | S | `docker-compose.maestro.yml` + Dockerfiles | #713 |
| #715 — Approval Gate UI | S | `apps/approval_gate/` | #709 |

---

## File Map

```
apps/
  mcp/
    memory/              ← NEW (issue #708)
      __init__.py
      store.py           ← SQLite knowledge graph
      mcp_server.py      ← FastMCP server
    agent_bus/           ← NEW (issue #709)
      __init__.py
      bus.py             ← SQLite context bus
      mcp_server.py      ← FastMCP server
  approval_gate/         ← NEW (issue #715)
    main.py              ← FastAPI + WebSocket

agents/
  mcp_client.py          ← NEW (issue #710) — MCPMultiClient
  router_agent.py        ← NEW (issue #711)
  coder_agent.py         ← NEW (issue #712) — replaces 3-agent chain
  maestro.py             ← NEW (issue #713)

docker/
  mcp-memory/            ← NEW
    Dockerfile
  mcp-agent-bus/         ← NEW
    Dockerfile
  approval-gate/         ← NEW
    Dockerfile
  agent-worker/          ← NEW (issue #714)
    Dockerfile

docker-compose.maestro.yml  ← NEW (issue #714)

.maestro/                ← runtime dir (gitignored)
  memory.db
  bus.db
```

---

## Resuming Work

To pick up where implementation left off:

```bash
# Check issue status
gh issue list --repo blecx/AI-Agent-Framework --label maestro

# Check what's implemented
ls apps/mcp/memory/ apps/mcp/agent_bus/ 2>/dev/null
ls agents/mcp_client.py agents/router_agent.py agents/coder_agent.py agents/maestro.py 2>/dev/null

# Check context bus for any in-progress run
ls .maestro/ 2>/dev/null

# Run the full stack once available
docker compose -f docker-compose.maestro.yml up
```

---

## Design Decisions Log

| Decision | Rationale |
|---------|-----------|
| SQLite for bus + memory | Zero dependencies, ACID, same pattern as existing test fixtures |
| FastMCP for new MCP servers | Identical pattern to existing 4 servers — no new concepts |
| Single coder thread | Eliminates the #1 failure mode: context loss between phases |
| gpt-4o-mini default | Free-tier compatible; gpt-4o reserved for genuinely complex tasks |
| Human approval gate | Prevents wasted API quota on bad plans; stays optional via `--no-gate` |
| Keep existing MCP servers | 5 servers already running, tested, policy-gated — reuse completely |
| Agent SDK: `agent_framework` (existing) | No SDK mixing; ChatAgent/OpenAIChatClient already proven |

---

## Comparison: v1 vs MAESTRO

| | v1 Autonomous Agent | MAESTRO |
|--|---------------------|---------|
| Context budget | 3200 chars | 128k (gpt-4o) / 20k (mini) |
| Phase handoffs | Text strings (lossy) | mcp-agent-bus (lossless JSON) |
| Memory | JSON file (overwrites) | Knowledge graph (accumulates) |
| Human gate | None | After planning, before coding |
| Model selection | Fixed per role | Dynamic by complexity score |
| Epic handling | Fails / tries to do it all | Decomposes to atomic sub-issues |
| Tool protocol | Direct Python calls | MCP (same as VS Code Copilot) |
| Parallel issues | No | Yes (Docker workers) |
