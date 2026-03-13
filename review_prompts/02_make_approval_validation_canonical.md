# Prompt 2 — Make approval validation canonical

## Objective

Refactor approval validation so scripts validate against `.copilot/config/vscode-agent-settings.json` and related canonical config, instead of outdated hard-coded baselines.

## Why this prompt exists

Current validation logic still encodes an older worldview and does not fully reflect the migrated `.copilot` authority model.

## Instructions

1. Review validation scripts that inspect:
   - `chat.tools.subagent.autoApprove`
   - `issueagent.customAgent`
   - workspace projection state
2. Replace hard-coded expected agent sets with canonical lookups from `.copilot/config/vscode-agent-settings.json` where appropriate.
3. Distinguish clearly between:
   - **registry validation** — does the named agent exist?
   - **policy validation** — is the approved set compliant with the configured profile?
4. Ensure optional agents and manually gated agents are not accidentally treated as required baseline approvals.
5. Add or update tests or dry-run verification guidance if validation logic changes.
6. Produce a summary explaining:
   - what was hard-coded before
   - what is now canonicalized
   - what remains intentionally configurable

## Questions for the operator

1. Should the validator enforce an **exact** approved set, or only validate that configured approvals are valid and policy-compliant?
2. Do you want separate validation modes for:
   - safe profile
   - trusted workflow profile
   - low-friction profile?
3. Should continuation/runtime agents be forbidden in default auto-approve policy, or merely optional?

## Success criteria

- Approval validation reads from canonical config.
- The validator no longer encodes stale agent assumptions.
- Policy and registry validation are separated cleanly.
