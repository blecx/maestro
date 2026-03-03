<skill>
<name>tutorial-writer-expert</name>
<description>Expert instructional design and documentation patterns for technical tutorials. Includes strict audit modes, visual evidence workflows, and gap reporting matrices.</description>
<file>
---
description: "Expert instructional design and documentation patterns for technical tutorials."
---

# Tutorial Writer Expert Skill

This skill defines the technical constraints and methodologies for writing software documentation, user manuals, and technical audits in this repository.

## 1. Primary Directives

1. **Output constraints:** Final tutorial output must always be Markdown.
2. **Separation of Concerns:** UX and TUI are fully separate, self-contained learning paths. Do not cross-pollinate GUI steps with CLI steps.
3. **Accuracy via Execution:** Validate documented steps against real system behavior before finalizing. Never hallucinate node_modules, routes, commands, or UI states.
4. **Gap Analysis:** Actively detect and report feature gaps or logical breaks back to developers.
5. **DRY Documentation:** Prevent duplicated tutorial content across tracks. Use hyperlinks to canonical explanations instead of duplicating text.

## 2. Visual Evidence Policy

- **Screenshots:** Mandatory for major transitions. Scripted screenshot generation is preferred (e.g. Playwright).
- **Schema & Architecture:** Mandatory inclusion of diagram source control references (i.e. `.drawio` source + generated `.svg` assets).
- **Workflow Paths:** End-to-end user flows must be visualized using embedded `mermaid` graph diagrams where helpful for comprehension.

## 3. Strict Audit Mode Execution

When requested to perform a "Strict Audit" (no net-new tutorial authoring unless correcting factual errors), output exactly this package:

```markdown
1. **Audit Summary:** High-level pass/fail
2. **Defect List:** (Severity + Evidence)
3. **Feature Gap List:** (Repro, Expected vs Actual, Impact, Suggested Issue Title)
4. **Duplicate Content Audit:** (Overlap matrix + Canonicalization decisions)
5. **Visual Coverage Report:** (Missing vs Available visual assets)
6. **Prioritized Fix Plan:** Next steps
```

## 4. Default Tutorial Package Output

When generating a complete tutorial, enforce this structure:

```markdown
# [Feature Name] Tutorial

**Track:** [UX | TUI]
**Audience Date:** [Date]

## 1. Prerequisites
## 2. Main Workflow Steps
(Include screenshots, command blocks, and step validations)
## 3. Troubleshooting & Verification
## 4. Feature Gap List
## 5. Duplicate Content Audit
## 6. Asset Regeneration Data (How screenshots/diagrams were created)
```

## 5. Instructional Design Tips (Microsoft / Anthropic Style)

- **Use Cognitive Anchoring:** Explain *why* a step is being taken before showing *how* to do it. Add a brief "Goal:" sentence per major header.
- **Progressive Disclosure:** Group advanced flags/options into visually collapsible `<details>` tags so beginners are not overwhelmed.
- **Fail-States Included:** Every action with a side-effect should include what to look for when it succeeds *and* when it fails.
- **Conversational Minimalism:** Keep sentences brief, active voice, and professional. Avoid overly dramatic or hyper-enthusiastic text (e.g. avoid "Amazing!").

</file>
</skill>
