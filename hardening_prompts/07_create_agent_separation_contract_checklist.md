# Hardening Prompt 7 — Create an agent separation contract checklist

## Objective

Create a repository-local checklist that defines what each agent and skill class may and may not own, so future changes preserve separation of concerns.

## Why this prompt comes last

A separation contract should codify the hardened architecture after the previous six steps have clarified authority, approval, validation, projection, orchestration, and runtime boundaries.

## Scope

In scope:

- a new repository-local checklist document
- references from docs or governance docs where helpful
- classification of agent and skill responsibilities

Out of scope:

- major workflow rewrites beyond what the checklist documents

## Instructions

1. Define ownership classes such as:
   - canonical workflow skills
   - policy / authority skills
   - VS Code discovery wrappers
   - runtime / operator agents
   - orchestration / continuation agents
   - projection / validation scripts
2. For each class, define:
   - what it may own
   - what it must delegate
   - what it must not redefine
3. Add a review checklist for future PRs touching agent or skill architecture.
4. Link the checklist from appropriate docs if useful.
5. Produce a concise summary of how the checklist should be used in future reviews.

## Questions for the operator

1. Do you want this checklist placed in `docs/maestro/`, `.copilot/`, or another governance location?
2. Should it be written as a human review checklist, a policy doc, or both?
3. Do you want future PRs touching agent architecture to be required to reference it explicitly?

## Success criteria

- The repository has a durable local separation-of-concerns contract.
- Future agent and skill changes can be reviewed against explicit ownership rules.
- The hardened architecture becomes easier to preserve over time.
