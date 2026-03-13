# Maestro Agent Roles & Boundaries

This document defines the clear operational contracts for agents interacting within the Maestro repository system. To avoid conflicting source-of-truth issues, **no agent ever sets workflow policy in its own wrapper**. All workflow rules belong exclusively in `.copilot/skills/`.

## Role Map Table

| Agent | Target Audience | Primary Function Contract | Key Boundary (What it DOES NOT do) | Reference |
|---|---|---|---|---|
| **`@workflow`** | All Developers | **Workflow Policy Advocate:** Guides users conversationally on repo standards, spec-writing, and planning using `.copilot/skills/`. | Does not run the specific PR build loop or orchestrate heavy backend scripts. | `.github/agents/workflow.md` |
| **`@maestro-operator`** | All Developers | **Maestro Orchestration Operator:** Securely operates Maestro terminal scripts, orchestrates validations, and interacts with backend Python runtimes. | Does not define issue/PR workflow policies. Defers policy questions to `@workflow`. | `.github/agents/maestro-operator.md` |
| **`@resolve-issue`** | All Developers / CI | **Issue Resolution Specialist:** Executes the highly structured, single-issue-to-PR pipeline according to canonical logic. | Not for general Q&A or planning. It is a strict builder pipeline. | `.github/agents/resolve-issue.md` |

> **Note on Legacy Docs:** All old `/agents/` Python runtime documentation has been removed or de-tainted to ensure `.copilot/` remains the undivided source of truth for workflow policies.
| **Runtime Code (`agents/`)** | Backend Framework | **Stateless Execution Engine:** The Python modules in `agents/` serve strictly as stateless, mechanical execution tools that read configuration but harbor no policy authority of their own. | Does not contain workflow logic or constraints. | `agents/*.py` |
