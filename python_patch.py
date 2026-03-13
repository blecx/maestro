import os

def insert_after(filepath, marker, text):
    with open(filepath, 'r') as f:
        content = f.read()
    if text in content: return
    content = content.replace(marker, marker + "\n\n" + text)
    with open(filepath, 'w') as f:
        f.write(content)

# workflow
insert_after(".github/agents/workflow.md", "You are the `workflow` custom agent.", "## Role Contract\n\n**repo-level runtime orchestration** - Executes the scripted repository runtime, deferring implementation authority to `resolve-issue`.")
insert_after(".copilot/skills/workflow-runtime/SKILL.md", "# Workflow Runtime", "## Role Contract\n\n**repo-level runtime orchestration** - Executes the scripted repository runtime, deferring implementation authority to `resolve-issue`.")

# maestro-operator
insert_after(".github/agents/maestro-operator.md", "You are the `maestro-operator` custom agent.", "## Role Contract\n\n**direct Maestro CLI bridge** - Acts purely as an operator interface for Maestro, without assuming broad orchestration duties.")
insert_after(".copilot/skills/maestro-operator-workflow/SKILL.md", "# Maestro Operator Workflow", "## Role Contract\n\n**direct Maestro CLI bridge** - Acts purely as an operator interface for Maestro, without assuming broad orchestration duties.")

# resolve-issue
insert_after(".github/agents/resolve-issue.md", "You are the `resolve-issue` custom agent.", "## Role Contract\n\n**issue implementation workflow authority** - Dictates how an issue becomes a PR, independent of underlying runtime execution engines.")
insert_after(".copilot/skills/resolve-issue-workflow/SKILL.md", "# Resolve Issue Workflow", "## Role Contract\n\n**issue implementation workflow authority** - Dictates how an issue becomes a PR, independent of underlying runtime execution engines.")

