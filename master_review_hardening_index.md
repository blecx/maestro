# Master Review And Hardening Index

## Purpose

This document is the single launcher and navigation index for the repository's AI-agent review and hardening packets.

Use this file as the starting point in future chats when you want to:

- review the current `.copilot` migration state
- execute the rigid review packet
- execute the hardening packet
- understand the correct order of work
- avoid mixing review and remediation steps accidentally

## Packet Overview

There are two related but different document series in this repository.

### 1. Review Packet

Use the review packet when you want to understand the current state, risks, separation-of-concerns issues, and approval/governance weaknesses.

Main files:

- `rigid_copipot_review.md`
- `Howto_review_prompts.md`
- `review_prompts/01_fix_stale_authority_references.md`
- `review_prompts/02_make_approval_validation_canonical.md`
- `review_prompts/03_split_approval_tiers_explicitly.md`
- `review_prompts/04_reconcile_managed_keys_in_projection.md`
- `review_prompts/05_narrow_continuation_agents.md`
- `review_prompts/06_clarify_runtime_roles.md`
- `review_prompts/07_split_tutorial_author_and_audit.md`

Use this packet when the main need is:

- analysis
- assessment
- architecture review
- approval review
- separation-of-concerns review
- planning future cleanup

### 2. Hardening Packet

Use the hardening packet when you want to actually execute the remediation program and harden the repository step by step.

Main files:

- `hardening_plan.md`
- `Howto_hardening execution.md`
- `hardening_prompts/01_fix_stale_authority_references.md`
- `hardening_prompts/02_tighten_approval_tiers.md`
- `hardening_prompts/03_update_validators_to_canonical_config.md`
- `hardening_prompts/04_reconcile_projection_scripts.md`
- `hardening_prompts/05_narrow_orchestration_boundaries.md`
- `hardening_prompts/06_clarify_runtime_roles.md`
- `hardening_prompts/07_create_agent_separation_contract_checklist.md`

Use this packet when the main need is:

- implementation
- remediation
- governance hardening
- validator alignment
- projection cleanup
- role-boundary tightening

## How To Choose The Right Packet

### Start with the Review Packet if

- you want a diagnosis before changing anything
- you want to understand the risks first
- you want to discuss tradeoffs before implementation
- you want a reusable review narrative for future decisions

### Start with the Hardening Packet if

- you already accept the review findings
- you want to remediate the issues now
- you want ordered implementation prompts
- you want a concrete hardening sequence for new chats

## Recommended Master Workflow

For the cleanest process, use the packets in this order.

### Phase A — Review

1. Read `rigid_copipot_review.md`
2. Read `Howto_review_prompts.md`
3. Use the review prompts if you want to revisit or refine the analysis

### Phase B — Hardening

1. Read `hardening_plan.md`
2. Read `Howto_hardening execution.md`
3. Execute the hardening prompts in numeric order

This keeps diagnosis and remediation separated.

## Fast Start For Future Chats

If you open a new chat and want the fastest clean start, use one of these paths.

### Option 1 — Review-first path

Tell the new chat to start from:

- `master_review_hardening_index.md`
- `rigid_copipot_review.md`
- `Howto_review_prompts.md`

Then continue into the specific review prompt you want.

### Option 2 — Hardening-first path

Tell the new chat to start from:

- `master_review_hardening_index.md`
- `hardening_plan.md`
- `Howto_hardening execution.md`
- the next numbered file in `hardening_prompts/`

This is the preferred path once the review findings are accepted.

## What This Master Index Achieves

This file gives you one stable entrypoint that:

- links both document series together
- keeps review and hardening logically separate
- tells future chats where to begin
- reduces prompt-order confusion
- makes the repository easier to navigate during multi-chat work

## Suggested Use In Future Chats

In a new chat, say something like:

> Start from `master_review_hardening_index.md` and continue with the hardening packet from the next unfinished numbered prompt.

Or:

> Start from `master_review_hardening_index.md` and use the review packet to reassess separation-of-concerns and approval policy before making changes.

## End State

With this master index in place, the repository now has:

- a full rigid review packet
- a full hardening packet
- a single launcher document that ties both together

That gives future chats one canonical starting point for either analysis or remediation.
