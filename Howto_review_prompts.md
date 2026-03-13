# How To Execute The Review Prompts

## Purpose

This document explains how to execute the review prompt series in the correct order so the repository's `.copilot` migration becomes operationally clean, approval-safe, and separation-of-concerns compliant.

The prompts are intentionally numbered and should be run in order.

## Deliverables In This Review Packet

- `rigid_copipot_review.md` — the full rigid review and assessment
- `review_prompts/01_fix_stale_authority_references.md`
- `review_prompts/02_make_approval_validation_canonical.md`
- `review_prompts/03_split_approval_tiers_explicitly.md`
- `review_prompts/04_reconcile_managed_keys_in_projection.md`
- `review_prompts/05_narrow_continuation_agents.md`
- `review_prompts/06_clarify_runtime_roles.md`
- `review_prompts/07_split_tutorial_author_and_audit.md`

## Recommended Execution Order

Run them exactly in this order.

### 1. Fix stale authority references

Prompt file:

- `review_prompts/01_fix_stale_authority_references.md`

Why first:

- It establishes the correct canonical authority paths.
- All following cleanup depends on the source-of-truth map being correct.

Achievement after completion:

- `.copilot` becomes the unambiguous workflow authority.
- Legacy path ambiguity is reduced immediately.

### 2. Make approval validation canonical

Prompt file:

- `review_prompts/02_make_approval_validation_canonical.md`

Why second:

- Once authorities are correct, validation must be aligned to the real source of truth.
- Otherwise later approval work will still sit on stale assumptions.

Achievement after completion:

- Validation scripts stop enforcing the wrong model.
- Approval policy becomes testable against canonical config.

### 3. Split approval tiers explicitly

Prompt file:

- `review_prompts/03_split_approval_tiers_explicitly.md`

Why third:

- Only after canonical validation exists should you redesign the approval model.
- This prevents profile design on top of invalid governance logic.

Achievement after completion:

- `safe`, `trusted workflow`, and `low-friction` become meaningfully different.
- Agent approval and terminal approval become easier to reason about.

### 4. Reconcile managed keys in projection

Prompt file:

- `review_prompts/04_reconcile_managed_keys_in_projection.md`

Why fourth:

- Once approval tiers are defined, projection must converge the workspace to those definitions.
- Otherwise stale entries survive and sabotage the new model.

Achievement after completion:

- Projection becomes deterministic.
- Drift and stale managed keys are actively removable.

### 5. Narrow continuation agents

Prompt file:

- `review_prompts/05_narrow_continuation_agents.md`

Why fifth:

- Core authority and projection should be stable before orchestration layers are thinned.
- This lets continuation agents delegate into a stable core.

Achievement after completion:

- Continuation agents stop acting like parallel workflow authorities.
- Loop orchestration becomes easier to trust and approve.

### 6. Clarify runtime roles

Prompt file:

- `review_prompts/06_clarify_runtime_roles.md`

Why sixth:

- Once workflow authority is stable, runtime roles can be documented cleanly without competing with policy ownership.

Achievement after completion:

- `workflow`, `maestro-operator`, and `resolve-issue` are easier to distinguish.
- Runtime docs become less confusing for users and maintainers.

### 7. Split tutorial authoring and audit responsibilities

Prompt file:

- `review_prompts/07_split_tutorial_author_and_audit.md`

Why seventh:

- This is important, but it depends less on the core migration integrity than the previous six items.
- It should be handled after workflow authority, approval tiers, and role clarity are stable.

Achievement after completion:

- Tutorial responsibilities can be approved according to actual risk.
- Documentation workflows become clearer and safer.

## How To Use Each Prompt

For each numbered prompt:

1. Open the corresponding markdown file.
2. Use it as the working brief for the implementation or review pass.
3. Answer the operator questions in the prompt before execution where required.
4. Run the resulting implementation / review work as a separate bounded slice.
5. Verify the result before moving to the next prompt.

## Suggested Work Mode

Use one PR or one bounded implementation slice per numbered prompt where practical.

That gives you:

- clearer review boundaries
- easier rollback
- less drift between prompt intent and delivered change
- simpler validation and approval

## What You Should Have At The End

If all prompts are executed successfully, you should have:

- a truly canonical `.copilot` workflow authority
- approval validation aligned to canonical config
- explicit trust-tier approval profiles
- projection scripts that reconcile managed state cleanly
- continuation agents reduced to orchestration-only roles
- clearly differentiated runtime agents
- tutorial flows with safer and clearer approval boundaries

## Final Expected Outcome

The intended end state is not only “documentation says `.copilot` is canonical,” but rather:

- `.copilot` is operationally authoritative
- validators agree with it
- projection scripts enforce it
- workflow agents delegate cleanly
- approval policy matches real risk
- runtime roles do not interfere with workflow policy

That is the point where the migration becomes genuinely seamless in workflows rather than merely structurally improved.
