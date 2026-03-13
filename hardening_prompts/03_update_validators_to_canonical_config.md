# Hardening Prompt 3 — Update validators to canonical config

## Objective

Refactor validators so they inspect canonical configuration in `.copilot/config/` instead of relying on outdated hard-coded assumptions.

## Why this prompt comes third

After approval tiers are designed, validators must enforce the new canonical model rather than a stale one.

## Scope

In scope:

- validation scripts under `scripts/`
- any docs that describe validator expectations
- consistency checks for projected settings

Out of scope:

- unrelated workflow behavior changes

## Instructions

1. Review validators related to:
   - subagent auto-approval
   - custom agent defaults
   - settings drift
2. Replace hard-coded expectations with canonical reads from `.copilot/config/` where appropriate.
3. Separate:
   - registry checks
   - policy checks
   - profile-specific checks
4. Ensure optional or manual-only agents are not treated as required defaults by mistake.
5. Add or update verification guidance.
6. Summarize the new validation model.

## Questions for the operator

1. Should validators enforce exact profile equality or only compliance with allowed values?
2. Do you want separate validator modes per approval tier?
3. Should the validator warn on optional agent omissions, or only fail on invalid policy?

## Success criteria

- Validators read canonical config.
- Validation logic no longer lags the migrated architecture.
- Policy compliance is explainable and deterministic.
