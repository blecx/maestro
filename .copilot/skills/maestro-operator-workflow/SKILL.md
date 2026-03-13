<skill>
<name>maestro-operator-workflow</name>
<description>Canonical operator workflow for invoking the Python Maestro CLI from chat without directly editing application code.</description>
<file>
# Maestro Operator Workflow (Module)

Use this skill as the canonical implementation source for `maestro-operator`.

## Use When

- The user explicitly wants Maestro or the autonomous agent framework to implement, test, or execute work.
- The correct path is to run the Python CLI rather than write application code directly in chat.

## Execution Flow

1. Identify the issue number, repo target, branch, or task description.
2. Use the workspace virtual environment Python executable.
3. Invoke the CLI through `python -m agents.maestro_cli <arguments>`.
4. If the run is long-lived, execute it in the background and report progress from terminal output.

## Crash Handling

- If the CLI exits non-zero, capture the relevant traceback output.
- Report:
  - exception type,
  - crashed component,
  - error message,
  - suggested immediate next action.
- Do not proactively rewrite runtime Python sources unless the user explicitly changes the task into runtime debugging.

## Guardrails

- Do not implement application feature code directly when the request is to use Maestro.
- No GUI workflow; Maestro is a terminal-driven path.
- Use `.tmp/`, never `/tmp`, for any transient artifacts or logs you manage.

## Completion Contract

Return a concise result that states:

- invoked Maestro command,
- runtime status,
- key output or crash summary,
- immediate next action if operator intervention is needed.

</file>
</skill>
