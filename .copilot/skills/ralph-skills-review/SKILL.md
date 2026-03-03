<skill>
<name>ralph-skills-review</name>
<description>Workflow or rule module extracted from .copilot/skills/ralph-skills-review/SKILL.md</description>
<file>
# Ralph Skills & Review Matrix

Use this matrix as hard acceptance criteria for Ralph executions.

## Skill Matrix

| Skill | Requirement | Evidence |
|---|---|---|
| Impact & Dependency Analysis | DAG-based ordering and impact rationale are explicit | Selection notes, dependency graph summary |
| Dedupe Skill | Duplicate issues closed with reference to kept issue | Issue links and close message |
| DDD Boundary Skill | Domain/service/router or feature boundaries remain clean | Diff summary with boundary checks |
| Multi-Repo Skill | Correctly identifies backend/client/both scope | Scope declaration in plan |
| Environment Parity Skill | Uses correct runtime/tooling per repo | Command logs with correct cwd |
| Validation Skill | Runs required repo-native checks for changed scope | Test/lint/build outputs |
| Documentation Skill | Updates required technical docs for behavior changes | Changed doc file list |
| Safety Skill | No secrets, no protected-path writes, no unsafe shortcuts | Security review checklist |

## Specialist Reviewer Gates

Run these gates after implementation and validation:

1. **Architecture Reviewer**
   - Scope discipline
   - File ownership and boundaries
   - No unrelated refactors

2. **Quality Reviewer**
   - Validation completeness
   - Test quality and determinism
   - CI-readiness confidence

3. **Security Reviewer**
   - Secret handling and redaction
   - Dependency and command safety
   - Sensitive path protections

4. **UX Reviewer** (conditional)
   - Required when UI/UX scope exists
   - Navigation, responsiveness, a11y, consistency

## Decision Contract

- `REVIEW_DECISION: PASS` only when all required skills and reviewer gates pass.
- Otherwise output `REVIEW_DECISION: CHANGES` with a minimal, ordered fix list.
- Stop after iteration budget is exhausted and return escalation packet.

</file>
</skill>