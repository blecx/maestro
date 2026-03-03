#!/usr/bin/env python3
"""Generate planning/issues/step-4.yml deterministically.

Why this exists:
- The backend roadmap loop expects roadmap YAML specs to exist.
- When a new step starts, we want the tooling to be able to bootstrap the
  next roadmap without requiring manual authoring.

Behavior:
- If the target file exists, this script is a no-op unless --force is provided.
- Output is deterministic (static template).
"""

from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "planning/issues/step-4.yml"

TEMPLATE = """# Step 4 — LLM UI mockups + clickable prototype + designer skills.
# Constraint: keep issue bodies compact to fit strict token budgets.

AI-Agent-Framework:
  - number: "S4-BE-01"
    size_estimate: "M"
    title: "Step 4 — OpenAI Images client + mockup artifact writer"
    labels:
      - step:4
      - backend/ux-mockups
      - size:M
    body: |
      ## Goal / Problem Statement
      Add a minimal OpenAI Images integration that can generate UI mock images and write them to a deterministic local artifact folder.

      ## Scope
      ### In Scope
      - Add a small image client wrapper (env-keyed, no secrets on disk).
      - Write artifacts under `.tmp/mockups/issue-<n>/` (images + `index.html`).
      - Provide a single callable entry-point used by the workflow agent.
      ### Out of Scope
      - Pixel-perfect brand design.
      - Complex multi-page prototypes.
      ### Dependencies
      - OpenAI Images API (model: `gpt-image-1`) via `OPENAI_API_KEY`.

      ## Acceptance Criteria
      - [ ] A module exists that can generate at least one mock image when `OPENAI_API_KEY` is set.
      - [ ] Outputs are written under `.tmp/mockups/issue-<n>/` with an `index.html` prototype.
      - [ ] When the key is missing, the feature exits gracefully with an actionable message.

      ## Technical Approach
      - Add a small service (pure Python) that:
        - builds a prompt from the issue context
        - calls OpenAI Images
        - writes files to `.tmp/mockups/...`

      ## Testing Requirements
      - `pytest tests/unit -q`
      - `pytest tests/unit -k mockup -q`

      ## Documentation Updates
      - [ ] Document `OPENAI_API_KEY` setup and artifact output location.

      ## Cross-Repository Coordination
      None.

  - number: "S4-BE-02"
    size_estimate: "S"
    title: "Step 4 — Add designer skills: design guidelines + coder change plan"
    labels:
      - step:4
      - backend/skills
      - size:S
    body: |
      ## Goal / Problem Statement
      Implement two explicit "designer" skills so the agent can produce (1) design guidelines when mockups are approved and (2) a coder-facing change plan that can be turned into issue specs.

      ## Scope
      ### In Scope
      - Add a `design_guidelines` skill returning concise markdown.
      - Add a `coder_change_plan` skill returning markdown + machine-parsable YAML stubs.
      - Register skills in the backend skill registry.
      ### Out of Scope
      - Full UI implementation.
      - Non-deterministic, tool-heavy skills.
      ### Dependencies
      - Existing skills framework under `apps/api/skills/`.

      ## Acceptance Criteria
      - [ ] `GET /api/v1/agents/<id>/skills` lists both new skills.
      - [ ] Each skill returns a `SkillResult` envelope with deterministic structure.
      - [ ] `coder_change_plan` output includes a clearly delimited YAML block.

      ## Technical Approach
      - Add two skill classes + registry entries.
      - Keep each skill under ~100 lines; pure transformation, no side effects beyond optional `.tmp/` evidence.

      ## Testing Requirements
      - `pytest tests/unit -k "skills" -q`

      ## Documentation Updates
      - [ ] Add short usage docs for both skills.

      ## Cross-Repository Coordination
      None.

  - number: "S4-BE-03"
    size_estimate: "M"
    title: "Step 4 — Workflow Phase 2.6: generate mockups + prototype before coding"
    labels:
      - step:4
      - backend/agents
      - size:M
    body: |
      ## Goal / Problem Statement
      Insert a new workflow phase (2.6) after the UX gate to produce UI mock images and a clickable prototype before implementation begins.

      ## Scope
      ### In Scope
      - Add Phase 2.6 in `agents/autonomous_workflow_agent.py`.
      - Persist evidence under `.tmp/mockups/issue-<n>/` and link it in logs.
      - Call designer skills after mockup approval (PASS).
      ### Out of Scope
      - Client-side UI work.
      - Fancy navigation/animation beyond static clickable hotspots.
      ### Dependencies
      - Step 4 mockup generator (S4-BE-01).
      - Designer skills (S4-BE-02).

      ## Acceptance Criteria
      - [ ] Phase order is: UX gate (2.5) → mockups (2.6) → coding.
      - [ ] If image generation is unavailable, workflow continues but records a clear skip reason.
      - [ ] Evidence is persisted to `.tmp/` for later review.

      ## Technical Approach
      - Add a small phase method that:
        - builds a mockup request
        - invokes generator
        - invokes skills on PASS

      ## Testing Requirements
      - `pytest tests/unit -k "workflow" -q`

      ## Documentation Updates
      - [ ] Update workflow docs to mention Phase 2.6 artifacts.

      ## Cross-Repository Coordination
      None.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate planning/issues/step-4.yml")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output path (default: planning/issues/step-4.yml)")
    parser.add_argument("--force", action="store_true", help="Overwrite if the file already exists")
    args = parser.parse_args()

    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = ROOT / out_path

    out_path.parent.mkdir(parents=True, exist_ok=True)

    if out_path.exists() and not args.force:
        return 0

    out_path.write_text(TEMPLATE.rstrip() + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
