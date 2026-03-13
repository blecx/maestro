<skill>
<name>workflow-runtime</name>
<description>Canonical runtime workflow module for scripted autonomous issue and PR lifecycle orchestration.</description>
<file>
# Workflow Runtime (Module)

Use this skill as the canonical implementation source for `workflow`.

## Use When

- A scripted workflow-agent run is explicitly requested.
- The task should execute through the repository's workflow runtime entrypoints rather than interactive chat implementation.
- Deterministic autonomous orchestration is needed for issue or PR lifecycle automation.

## Runtime Entry Points

- `scripts/agents/workflow`
- `agents/workflow_agent.py`

## Responsibilities

- Run autonomous workflow automation when explicitly requested.
- Preserve deterministic execution and established repo guardrails.
- Defer repo-specific implementation planning or coding back to `resolve-issue` and related canonical workflows when needed.

## Guardrails

- Treat this as a runtime execution path, not the source of truth for workflow policy.
- Keep `.copilot/skills/*` as the authority for planning, issue resolution, merge, and close rules.
- Use `.tmp/`, never `/tmp`, for transient artifacts.
- Do not rewrite Python runtime sources under `agents/` unless the user explicitly asks for runtime debugging or implementation work there.

## Completion Contract

Return a concise execution summary including:

- invoked runtime entrypoint,
- requested target or scope,
- execution result or blocker,
- any follow-up handoff to canonical workflows.

</file>
</skill>