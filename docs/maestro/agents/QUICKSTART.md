# Custom AI Agents - Quick Start Guide

Complete guide to set up and use custom AI agents trained on your project's chat exports.

## Overview

This system allows you to create AI agents that learn from completed issue workflows and automate future issues with that knowledge.

**What you get:**

- ✅ Automated 6-phase workflow for issues
- ✅ Problem detection and suggested solutions
- ✅ Improved time estimates based on history
- ✅ Self-analyzing agents that request updates
- ✅ Continuous learning from every issue

## Prerequisites

- Python 3.10+ with pip
- GitHub CLI (`gh`) installed and authenticated
- Git repository
- Completed issues with exported chats

## Initial Setup (5 minutes)

### 1. Verify Directory Structure

```bash
cd /home/sw/work/AI-Agent-Framework

# Check structure was created
ls -la agents/
ls -la agents/knowledge/
ls -la scripts/agents/
```

You should see:

```
agents/
├── base_agent.py
├── workflow_agent.py
├── README.md
├── config/
├── knowledge/
│   ├── workflow_patterns.json
│   ├── problem_solutions.json
│   ├── time_estimates.json
│   ├── command_sequences.json
│   └── agent_metrics.json
└── training/
    ├── learnings/
    └── logs/
```

### 2. Train Agent from Existing Issues

If you have Issues #24 and #25 already completed:

```bash
# Step 1: Export chats (if not already exported)
# Note: You may need to export manually if chat API not available
# Save chat exports to: docs/chat/2026-01-18-issue24-complete-workflow.md
#                       docs/chat/2026-01-18-issue25-complete-workflow.md

# Step 2: Extract learnings from Issue #24
./scripts/extract_learnings.py --export docs/chat/*-issue24-*.md

# Step 3: Extract learnings from Issue #25
./scripts/extract_learnings.py --export docs/chat/*-issue25-*.md

# Step 4: Check agent status
./scripts/train_agent.py --analyze-all
```

Expected output:

```
📊 Agent Performance Analysis

Training Data:
  • Issues analyzed: 2
  • Problems cataloged: 8
  • Confidence level: low

Performance Metrics:
  • Time estimation accuracy: 87.5%
  • Problem solution coverage: 100.0%
  • Agent maturity: initial

Readiness Assessment:
  ⚠️  Agent not yet ready for production
     • Need 3 more issues for minimum confidence

💡 Recommendations:
  • Complete 3 more issues to reach minimum confidence
```

## Using the Workflow Agent

### Ralph Agent (recommended strict profile)

Run Ralph directly from CLI:

```bash
./scripts/work-issue.py --issue 26 --agent ralph
```

Run Ralph from VS Code chat:

```text
@ralph /run
```

Ralph enforces skill-based acceptance criteria and specialist review gates before PR handoff.

### First Issue (Supervised Mode)

For your first issue with the agent, monitor each phase:

```bash
# Issue #26 - Run with full interaction
./scripts/agents/workflow --issue 26
```

**What happens:**

1. **Phase 1:** Agent fetches issue, you review
2. **Phase 2:** Agent creates planning doc, you fill it in
3. **Phase 3:** You implement following test-first approach
4. **Phase 4:** Agent runs tests, detects problems
5. **Phase 5:** You perform reviews (self + Copilot)
6. **Phase 6:** Agent creates PR and validates merge

**Time:** ~2-3 hours for typical issue

### After Completing an Issue

```bash
# Export the chat (manual for now)
# Save to: docs/chat/2026-01-19-issue26-complete-workflow.md

# Extract learnings
./scripts/extract_learnings.py --export docs/chat/*-issue26-*.md

# Analyze and get recommendations
./scripts/train_agent.py --issue 26
```

Example output:

```
🔍 Analyzing agent after Issue #26

📊 Analysis Complete - 2 recommendations

🟠 HIGH Priority:

  1. Update workflow_agent
     Action: Add 2 new problem detection patterns
     Type: problem_detection
     Effort: ~30 minutes
     Details:
       • Timeout errors in chat export
       • Missing planning doc template

🟡 MEDIUM Priority:

  2. Update workflow_agent
     Action: Adjust time multiplier: 0.875 → 0.820
     Type: time_estimation
     Effort: ~10 minutes
     Details: Variance: 12.5%

📈 Total improvement effort: ~40 minutes (0.7 hours)
💡 Expected benefits: Prevent 2 known issue types in future runs
```

### Test with Dry Run

Before running on a new issue type:

```bash
./scripts/agents/workflow --issue 27 --dry-run
```

Shows what would happen without executing:

```
ℹ️  [10:30:00] Starting workflow_agent v1.0.0 (DRY RUN)
🔄 [10:30:01] Fetching issue from GitHub
ℹ️  [10:30:01] Command: gh issue view 27
ℹ️  [10:30:01] (Dry run - command not executed)
...
```

## Complete Workflow Example

Here's a complete cycle from issue to trained agent:

### Step 1: Work on Issue (with Agent)

```bash
# Start workflow
./scripts/agents/workflow --issue 26

# Agent guides you through all 6 phases
# You fill in planning, implement, test, review
# Agent handles automation and validation
```

### Step 2: Export Chat

Currently manual - you'll need to export the chat conversation to:
`docs/chat/2026-01-19-issue26-complete-workflow.md`

_Note: The `export_chat.py` script is prepared for when chat export API becomes available_

### Step 3: Extract Learnings

```bash
./scripts/extract_learnings.py --export docs/chat/2026-01-19-issue26-complete-workflow.md
```

Output:

```
📖 Extracting learnings from 2026-01-19-issue26-complete-workflow.md
   Issue: #26
   ✅ Extracted 2 problems
   ✅ Extracted 15 command sequences
   ✅ Extracted 6 workflow phases

📚 Merging learnings into knowledge base...
   ✅ Updated workflow_patterns.json (3 issues)
   ✅ Updated problem_solutions.json (+2 new problems, 10 total)
   ✅ Updated time_estimates.json (avg multiplier: 0.820)
   ✅ Updated command_sequences.json
   ✅ Updated agent_metrics.json (confidence: low)

✅ Learnings extraction complete

Next step:
  ./scripts/train_agent.py --issue 26
```

### Step 4: Analyze & Update Agent

```bash
./scripts/train_agent.py --issue 26
```

Reviews learnings and recommends updates. If high-priority updates exist, implement them:

1. Edit `agents/workflow_agent.py`
2. Add new problem detection in `_phase4_testing()`:
   ```python
   # Check for timeout errors
   if 'timeout' in error_message.lower():
       self.log("Timeout detected - try reducing chunk size", "warning")
   ```
3. Update version: `version="1.0.1"`
4. Test with dry run on next issue

### Step 5: Repeat & Improve

With each issue:

- Agent learns new patterns
- Time estimates improve
- Problem database grows
- Automation increases

## Maturity Progression

### Issues 1-2 (Current - Initial)

- Agent provides structure and reminders
- You do most of the work manually
- Learning basic patterns
- **Confidence: Low**

### Issues 3-5 (Learning)

- Agent detects some common problems
- Time estimates become useful
- Command automation helps
- **Confidence: Medium-Low**

### Issues 6-10 (Developing)

- Agent prevents known issues proactively
- Accurate time predictions
- Smooth automation flow
- **Confidence: Medium-High**

### Issues 11-20 (Mature)

- Agent handles common cases autonomously
- Rare manual intervention needed
- High-quality predictions
- **Confidence: High**

### Issues 20+ (Production-Ready)

- Fully autonomous for standard issues
- Extensive problem database
- Reliable for production use
- **Confidence: Very High**

## Monitoring Agent Performance

### Check Current Status

```bash
./scripts/train_agent.py --analyze-all
```

Shows:

- Issues trained on
- Problems cataloged
- Time accuracy
- Maturity level
- Production readiness

### View Recommendations

```bash
./scripts/train_agent.py --recommend
```

Lists all pending agent updates grouped by priority.

### Review Logs

```bash
# Latest run log
ls -lt agents/training/logs/ | head -5

# View specific log
cat agents/training/logs/issue-26-workflow_agent-20260119-103045.json | jq '.log'
```

### Inspect Knowledge Base

```bash
# See all problems cataloged
cat agents/knowledge/problem_solutions.json | jq '.problems'

# Check time statistics
cat agents/knowledge/time_estimates.json | jq '.statistics'

# View workflow patterns
cat agents/knowledge/workflow_patterns.json | jq '.issues[-1]'
```

## Troubleshooting

### Error: "Not in a git repository"

```bash
cd /home/sw/work/AI-Agent-Framework
./scripts/agents/workflow --issue 26
```

### Error: "GitHub CLI (gh) not installed"

```bash
# Install GitHub CLI
# Ubuntu/Debian:
sudo apt install gh

# macOS:
brew install gh

# Then authenticate:
gh auth login
```

### Error: "Export file not found"

You need to manually export the chat first. Save it to:
`docs/chat/2026-01-19-issue{N}-complete-workflow.md`

### Agent doesn't detect problems

The agent only knows about problems it has seen before. Add new problems:

1. Document in `agents/knowledge/problem_solutions.json`:

   ```json
   {
     "problem": "Build fails with 'Module not found'",
     "solution": "Run npm install to update dependencies",
     "category": "dependencies"
   }
   ```

2. Or wait for agent to learn it from next chat export

## Best Practices

### Do's ✅

1. **Always start with planning** - Phase 2 saves time later
2. **Follow test-first approach** - Catches issues early
3. **Complete all 6 phases** - No shortcuts
4. **Export chat after each issue** - Trains the agent
5. **Update agent every 5 issues** - Keep it current
6. **Run dry-run on unusual issues** - Verify workflow fits

### Don'ts ❌

1. **Don't skip phases** - Each builds on previous
2. **Don't ignore agent warnings** - They're based on past failures
3. **Don't modify knowledge base manually** - Use extraction scripts
4. **Don't remove functionality without approval** - Key principle
5. **Don't trust time estimates < 5 issues** - Not enough data yet

## Next Steps

1. **Complete 3 more issues** to reach minimum confidence
2. **Review agent recommendations** after each issue
3. **Update agent code** when high-priority updates accumulate
4. **Consider specialized agents** after 20+ issues if patterns diverge

## Resources

- **Agent README:** [agents/README.md](../agents/README.md)
- **Workflow Agent Guide:** [docs/agents/workflow-agent.md](workflow-agent.md)
- **Development Guide:** [docs/howto/restore-chat-and-create-custom-agent.md](../howto/restore-chat-and-create-custom-agent.md)
- **Knowledge Base:** [agents/knowledge/](../agents/knowledge/)

## Getting Help

Issues or questions:

1. Check agent logs: `agents/training/logs/`
2. Review knowledge base: `agents/knowledge/*.json`
3. Read completed chat exports: `docs/chat/`
4. See this guide and linked docs above

---

**Ready to start?** Run your first issue:

```bash
./scripts/agents/workflow --issue 26 --dry-run  # Preview first
./scripts/agents/workflow --issue 26             # Then run for real
```
