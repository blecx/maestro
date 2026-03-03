# Workflow Agent - User Guide

## Overview

The Workflow Agent automates the standard 6-phase issue resolution workflow, learning from past successes to improve over time.

## Quick Start

```bash
# Process Issue #26
./scripts/agents/workflow --issue 26

# Preview without executing (recommended for first use)
./scripts/agents/workflow --issue 26 --dry-run
```

## The 6-Phase Workflow

### Phase 1: Context Gathering

**Goal:** Understand the issue and gather relevant context

**Agent Actions:**

- Fetches issue from GitHub using `gh issue view`
- Displays issue title, description, acceptance criteria
- Identifies related files in codebase

**Your Actions:**

- Review the issue details displayed
- Ensure you understand requirements
- Press Enter when ready to proceed

**Time:** ~5-10 minutes

---

### Phase 2: Planning

**Goal:** Create structured implementation plan

**Agent Actions:**

- Creates `docs/issues/issue-{N}-plan.md`
- Estimates time based on historical data
- Lists key principles to follow
- Provides implementation checklist

**Your Actions:**

- Fill in planning document sections:
  - Objective (what needs to be done)
  - Approach (how you'll do it)
  - Acceptance criteria (from issue)
  - Risks & mitigation
- Press Enter when planning is complete

**Time:** ~15-30 minutes

**Key Principle:** Creating a plan saves 1-2 hours of implementation time

---

### Phase 3: Implementation

**Goal:** Implement changes using test-first approach

**Agent Actions:**

- Displays implementation checklist
- Reminds about test-first principle
- Warns about functionality removal approval

**Your Actions:**

1. Write or update tests first
2. Run tests (should fail for new features)
3. Implement changes
4. Run tests (should pass)
5. Commit with descriptive message
6. Press Enter when implementation complete

**Time:** Variable (bulk of work)

**Key Principle:** Test-first approach catches issues early

---

### Phase 4: Testing

**Goal:** Verify changes work correctly

**Agent Actions:**

- Detects project type (frontend/backend)
- Runs build: `npm run build` or similar
- Runs tests: `npx vitest run` or `pytest`
- Checks for known problems in output
- Suggests solutions for recognized issues

**Your Actions:**

- Watch for test failures
- Fix any failing tests
- Agent will detect and suggest solutions for known problems

**Time:** ~10-20 minutes

**Key Principle:** All tests must pass before proceeding

---

### Phase 5: Review

**Goal:** Comprehensive code review

**Agent Actions:**

- Lists changed files
- Provides review checklist (Steps 7 & 8)
- Reminds about approval requirements

**Your Actions:**

**Step 7 - Self Review:**

- No functionality removed without approval
- Code follows project conventions
- All acceptance criteria met
- No debug code or console.logs

**Step 8 - Copilot Review:**

- Ask: `@workspace review these changes for Issue #{N}`
- Address any issues Copilot finds
- Confirm all concerns resolved

**Time:** ~15-30 minutes

**Key Principle:** Review catches issues before PR

---

### Phase 6: PR & Merge

**Goal:** Create PR and merge with validation

**Agent Actions:**

- Creates PR: `gh pr create --fill`
- Extracts PR number
- Runs `prmerge` script if available
- Validates PR template
- Verifies merge and issue closure

**Your Actions:**

- Review PR template autofill
- Wait for CI checks
- Agent handles validation and merge
- Or manual merge if prmerge not available

**Time:** ~10-15 minutes

**Key Principle:** Use prmerge for consistent, validated merges

---

## Agent Intelligence Features

### Problem Detection & Solutions

The agent recognizes common problems and suggests solutions:

**Example:**

```
❌ Build failed
💡 Known problem detected: Evidence must be filled
💡 Solution: Keep evidence summary on same line in PR template
```

### Time Estimation

Agent learns from historical data:

```
📊 Estimated time for this issue: 2.3 hours
   (Based on 25 similar issues, avg multiplier: 0.875)
```

### Command Library

Agent knows proven command sequences:

- Git operations
- GitHub CLI commands
- Build and test commands
- Validation scripts

## Example Run

```bash
$ ./scripts/agents/workflow --issue 26

✅ [10:30:00] Starting workflow_agent v1.0.0
ℹ️  [10:30:01] Loaded 4 guiding principles

============================================================
📖 Phase 1: Context - Read issue and gather context
============================================================
🔄 [10:30:02] Fetching issue from GitHub
ℹ️  [10:30:02] Command: gh issue view 26
ℹ️  [10:30:03] Issue: #26 Add export timeout handling
[Issue details displayed]
⏸️  Review the issue context above.
Press Enter when ready to continue to Planning phase...

============================================================
📝 Phase 2: Planning - Create planning document
============================================================
🔄 [10:32:15] Creating planning document
ℹ️  [10:32:15] Estimated time for this issue: 2.3 hours
✅ [10:32:16] Created planning document: docs/issues/issue-26-plan.md
⏸️  Fill in the planning document with details from the issue.
Press Enter when planning is complete...

[... continues through all 6 phases ...]

============================================================
WORKFLOW SUMMARY
============================================================
✅ Phase 1: Context (2.2 min)
✅ Phase 2: Planning (18.5 min)
✅ Phase 3: Implementation (65.3 min)
✅ Phase 4: Testing (12.1 min)
✅ Phase 5: Review (22.4 min)
✅ Phase 6: PR & Merge (8.7 min)

📊 Total time: 129.2 minutes (2.2 hours)
```

## Dry Run Mode

Test the workflow without executing commands:

```bash
./scripts/agents/workflow --issue 26 --dry-run
```

**Dry run shows:**

- What commands would be run
- What files would be created
- Estimated times
- Checklist items

**Use dry run when:**

- First time using the agent
- Testing on a new project
- Verifying workflow for unusual issue type

## Troubleshooting

### Agent fails to fetch issue

**Problem:** `gh issue view` fails

**Solutions:**

1. Install GitHub CLI: `brew install gh` or `apt install gh`
2. Authenticate: `gh auth login`
3. Verify issue number exists: `gh issue list`

### Build/Test failures

**Problem:** Phase 4 tests fail

**Solutions:**

1. Check agent output for known problem detection
2. Apply suggested solution if available
3. Fix manually and restart from Phase 4
4. Document new problem for knowledge base

### Planning document not created

**Problem:** Permission error creating `docs/issues/`

**Solutions:**

1. Create directory manually: `mkdir -p docs/issues`
2. Check write permissions
3. Run with proper user privileges

### PR creation fails

**Problem:** `gh pr create` fails

**Solutions:**

1. Ensure changes are committed
2. Check you're on a feature branch (not main)
3. Verify GitHub authentication: `gh auth status`
4. Create PR manually if needed

## Best Practices

### Before Starting

1. **Read the issue completely**
2. **Check for dependencies** on other issues/PRs
3. **Run dry-run** first if unfamiliar workflow
4. **Ensure clean working directory**: `git status`

### During Execution

1. **Don't skip phases** - each builds on previous
2. **Take time in planning** - saves implementation time
3. **Follow test-first approach** - catches bugs early
4. **Get approval** before removing functionality
5. **Document problems** encountered for knowledge base

### After Completion

1. **Export chat**: `./scripts/export_chat.py --issue 26`
2. **Extract learnings**: `./scripts/extract_learnings.py --export [file]`
3. **Update agent**: `./scripts/train_agent.py --issue 26`
4. **Track actual time** vs estimate for improvements

## Advanced Usage

### Custom Knowledge Base Location

```bash
./scripts/agents/workflow --issue 26 --kb-dir /custom/path/knowledge
```

### Integration with CI/CD

```yaml
# .github/workflows/agent-workflow.yml
name: Agent Workflow

on:
  workflow_dispatch:
    inputs:
      issue_number:
        description: 'Issue number'
        required: true

jobs:
  workflow:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run workflow agent
        run: ./scripts/agents/workflow --issue ${{ github.event.inputs.issue_number }}
```

### Scripted Execution

```bash
#!/bin/bash
# Run workflow for multiple issues

for issue in 26 27 28; do
  echo "Processing Issue #$issue"
  ./scripts/agents/workflow --issue $issue

  if [ $? -eq 0 ]; then
    echo "✅ Issue #$issue completed"
    ./scripts/export_chat.py --issue $issue
    ./scripts/extract_learnings.py --export docs/chat/*-issue$issue-*.md
    ./scripts/train_agent.py --issue $issue
  else
    echo "❌ Issue #$issue failed"
    break
  fi
done
```

## Agent Improvement

The agent learns and improves automatically. Check status:

```bash
# See agent performance metrics
./scripts/train_agent.py --analyze-all

# Check pending recommendations
./scripts/train_agent.py --recommend
```

**Agent maturity progression:**

- **Issues 1-5:** Learning phase, requires manual verification
- **Issues 5-10:** Recognizing patterns, semi-autonomous
- **Issues 10-20:** High confidence, mostly autonomous
- **Issues 20+:** Mature, production-ready

## Getting Help

1. **Check agent logs**: `cat agents/training/logs/issue-*-workflow_agent-*.json`
2. **Review knowledge base**: `cat agents/knowledge/*.json`
3. **Read chat exports**: `docs/chat/`
4. **See main guide**: [restore-chat-and-create-custom-agent.md](../../docs/howto/restore-chat-and-create-custom-agent.md)

## See Also

- [Agent README](../README.md) - Overview of all agents
- [Creating Custom Agents](../../docs/howto/restore-chat-and-create-custom-agent.md) - Development guide
- [Knowledge Base Structure](../knowledge/) - Understanding agent training data
