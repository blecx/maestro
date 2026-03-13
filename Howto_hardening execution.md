# How To Execute The Hardening Packet

## Purpose

This document explains how to execute the hardening packet in a fresh chat, in the correct order, so the repository's `.copilot` migration becomes operationally hardened rather than only structurally improved.

## Files In This Hardening Packet

- `hardening_plan.md`
- `hardening_prompts/01_fix_stale_authority_references.md`
- `hardening_prompts/02_tighten_approval_tiers.md`
- `hardening_prompts/03_update_validators_to_canonical_config.md`
- `hardening_prompts/04_reconcile_projection_scripts.md`
- `hardening_prompts/05_narrow_orchestration_boundaries.md`
- `hardening_prompts/06_clarify_runtime_roles.md`
- `hardening_prompts/07_create_agent_separation_contract_checklist.md`

## Before You Start

Open a new chat so the execution of each hardening slice remains focused and reviewable.

Recommended preparation:

1. Read `hardening_plan.md`.
2. Confirm the current repository state is clean or intentionally staged.
3. Decide whether each prompt should become its own PR or its own bounded change slice.

## Recommended Execution Order

Run the prompts in this exact order.

### Step 1 — Fix stale authority references

Use:

- `hardening_prompts/01_fix_stale_authority_references.md`

Why first:

- The authority map must be correct before anything else can be hardened reliably.

What this will achieve:

- canonical skills and wrappers stop pointing to stale authority paths
- historical references are classified correctly
- `.copilot` becomes the active authority in practice

### Step 2 — Tighten approval tiers

Use:

- `hardening_prompts/02_tighten_approval_tiers.md`

Why second:

- Once authority is clean, approval policy can be redesigned around the correct source of truth.

What this will achieve:

- safer trust boundaries
- clearer separation between subagent approval and terminal approval
- approval profiles that actually mean something

### Step 3 — Update validators to canonical config

Use:

- `hardening_prompts/03_update_validators_to_canonical_config.md`

Why third:

- Validators must enforce the new approval and authority model, not the old one.

What this will achieve:

- validator logic matches canonical config
- approval drift becomes measurable and explainable
- stale hard-coded assumptions are removed

### Step 4 — Reconcile projection scripts

Use:

- `hardening_prompts/04_reconcile_projection_scripts.md`

Why fourth:

- Once canonical policy and validation are correct, projection must converge settings to that state deterministically.

What this will achieve:

- managed settings no longer accumulate stale residue
- workspace projection becomes cleaner and more predictable
- drift checks become more trustworthy

### Step 5 — Narrow orchestration boundaries

Use:

- `hardening_prompts/05_narrow_orchestration_boundaries.md`

Why fifth:

- Core authority, validation, and projection should be stable before orchestration layers are reduced to their true responsibilities.

What this will achieve:

- continuation agents become orchestration-only
- drift risk between loop agents and core workflow skills is reduced
- reviewability of automation boundaries improves

### Step 6 — Clarify runtime roles

Use:

- `hardening_prompts/06_clarify_runtime_roles.md`

Why sixth:

- After workflow and orchestration boundaries are stable, runtime roles can be clarified without ambiguity.

What this will achieve:

- `workflow`, `maestro-operator`, and `resolve-issue` become easier to distinguish
- runtime docs stop competing with policy authority
- operators know which entrypoint matches which task

### Step 7 — Create an agent separation contract checklist

Use:

- `hardening_prompts/07_create_agent_separation_contract_checklist.md`

Why seventh:

- The checklist should codify the final hardened architecture, so it belongs after the earlier hardening work is complete.

What this will achieve:

- a durable local contract for future reviews
- explicit ownership rules for agents, skills, wrappers, and scripts
- a reusable checklist for future PR review

## How To Run Each Prompt In A New Chat

For each numbered step:

1. Start a new chat.
2. Open the corresponding file in `hardening_prompts/`.
3. Paste or summarize the prompt contents into the chat as the working brief.
4. Answer the operator questions in that prompt before implementation if the decisions are not already settled.
5. Execute the work as a bounded slice.
6. Validate the result before proceeding to the next numbered prompt.

## Recommended Delivery Style

Prefer one bounded PR or one bounded implementation slice per prompt.

Benefits:

- easier review
- easier rollback
- less cross-contamination between concerns
- clearer validation evidence

## What This Will Achieve Overall

If you execute the packet fully and in order, you should end with:

- canonical workflow authority fully consolidated under `.copilot`
- explicit and safer approval tiers
- validators aligned to canonical config
- projection scripts that reconcile managed state cleanly
- continuation/orchestration agents reduced to proper boundaries
- runtime roles that are easier to understand and approve
- a repository-local separation-of-concerns contract for future changes

## Final End State

The intended end state is:

- `.copilot` is not only documented as canonical but enforced as canonical
- approval policy reflects actual operational risk
- validator and projection behavior match the docs
- orchestration layers delegate cleanly to core workflow skills
- runtime roles are operationally distinct
- future changes can be reviewed against a stable separation contract

That is the point where the migration becomes operationally hardened and seamless in workflows.
