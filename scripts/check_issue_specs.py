#!/usr/bin/env python3
"""Validate planning issue spec YAML files.

This checker supports:
1) Canonical issue entries with a markdown `body`.
2) Legacy structured entries (`plan` + `issue_template`) during migration.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GLOB = "planning/issues/*.yml"

REQUIRED_BODY_SECTIONS = [
    "## Goal / Problem Statement",
    "## Scope",
    "## Acceptance Criteria",
    "## Technical Approach",
    "## Testing Requirements",
    "## Documentation Updates",
    "## Cross-Repository Coordination",
]

SECTION_ALIASES = {
    "goal": ["## Goal / Problem Statement", "## Goal"],
    "scope": ["## Scope"],
    "acceptance": ["## Acceptance Criteria", "## Acceptance criteria"],
    "technical": ["## Technical Approach", "## Requirements"],
    "testing": ["## Testing Requirements", "## Mandatory tests"],
    "documentation": ["## Documentation Updates", "Update `tests/README.md`", "Update `README.md`"],
    "cross_repo": ["## Cross-Repository Coordination"],
}

KNOWN_REPO_KEYS = {"AI-Agent-Framework", "AI-Agent-Framework-Client"}

COMMAND_HINT_RE = re.compile(
    r"(pytest|python\s+-m|npm\s+run|npm\s+--prefix\s+\S+\s+run|uvicorn|curl|gh\s+issue)",
    re.IGNORECASE,
)
CHECKBOX_RE = re.compile(r"^- \[[ xX]\]\s+", re.MULTILINE)


@dataclass
class Finding:
    file: Path
    message: str

    def __str__(self) -> str:
        try:
            rel = self.file.relative_to(ROOT)
        except ValueError:
            rel = self.file
        return f"{rel}: {self.message}"


def _issue_id(issue: dict[str, Any]) -> str | None:
    value = issue.get("id") or issue.get("number")
    if value is None:
        return None
    return str(value).strip() or None


def _is_issue_list_candidate(key: str, value: Any) -> bool:
    return isinstance(key, str) and isinstance(value, list) and key in KNOWN_REPO_KEYS


def _validate_body(
    issue: dict[str, Any],
    findings: list[Finding],
    file: Path,
    idx: int,
    strict_sections: bool,
    max_body_chars: int | None,
) -> None:
    body = issue.get("body")
    if not isinstance(body, str) or not body.strip():
        findings.append(Finding(file, f"entry #{idx}: missing non-empty body"))
        return

    if isinstance(max_body_chars, int) and max_body_chars > 0 and len(body) > max_body_chars:
        findings.append(
            Finding(
                file,
                f"entry #{idx}: body too large ({len(body)} chars > max {max_body_chars})",
            )
        )

    if strict_sections:
        for section in REQUIRED_BODY_SECTIONS:
            if section not in body:
                findings.append(Finding(file, f"entry #{idx}: body missing section '{section}'"))
    else:
        if not any(alias in body for alias in SECTION_ALIASES["goal"]):
            findings.append(Finding(file, f"entry #{idx}: body missing goal section"))
        if not any(alias in body for alias in SECTION_ALIASES["scope"]):
            findings.append(Finding(file, f"entry #{idx}: body missing scope section"))
        if not any(alias in body for alias in SECTION_ALIASES["acceptance"]):
            findings.append(Finding(file, f"entry #{idx}: body missing acceptance criteria section"))
        if not any(alias in body for alias in SECTION_ALIASES["testing"]):
            findings.append(Finding(file, f"entry #{idx}: body missing testing requirements section"))

    if "## Acceptance Criteria" in body and not CHECKBOX_RE.search(body):
        findings.append(Finding(file, f"entry #{idx}: acceptance criteria should include checkbox items"))

    if strict_sections and "## Testing Requirements" in body and not COMMAND_HINT_RE.search(body):
        findings.append(Finding(file, f"entry #{idx}: testing requirements should include runnable validation commands"))


def _validate_legacy(issue: dict[str, Any], findings: list[Finding], file: Path, idx: int) -> None:
    plan = issue.get("plan")
    template = issue.get("issue_template")
    if not isinstance(plan, dict) or not isinstance(template, dict):
        findings.append(
            Finding(
                file,
                f"entry #{idx}: missing body and not a recognized legacy shape (requires plan + issue_template)",
            )
        )
        return

    for field in ("goal", "in_scope", "out_of_scope"):
        if field not in plan:
            findings.append(Finding(file, f"entry #{idx}: legacy plan missing '{field}'"))

    if not isinstance(template.get("acceptance_criteria"), list) or not template.get("acceptance_criteria"):
        findings.append(Finding(file, f"entry #{idx}: legacy issue_template missing acceptance_criteria list"))

    validation = template.get("validation")
    if not isinstance(validation, list) or not validation:
        findings.append(Finding(file, f"entry #{idx}: legacy issue_template missing validation command list"))


def validate_file(
    file: Path,
    allow_legacy: bool,
    strict_sections: bool = False,
    max_body_chars: int | None = None,
) -> list[Finding]:
    findings: list[Finding] = []

    try:
        data = yaml.safe_load(file.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - parser error path
        return [Finding(file, f"YAML parse error: {exc}")]

    if not isinstance(data, dict):
        return [Finding(file, "root must be a mapping")]

    issue_count = 0
    for repo_key, entries in data.items():
        if not _is_issue_list_candidate(repo_key, entries):
            continue

        for idx, entry in enumerate(entries, start=1):
            issue_count += 1
            if not isinstance(entry, dict):
                findings.append(Finding(file, f"entry #{idx}: must be a mapping"))
                continue

            if not isinstance(entry.get("title"), str) or not entry["title"].strip():
                findings.append(Finding(file, f"entry #{idx}: missing non-empty title"))

            labels = entry.get("labels")
            if not isinstance(labels, list) or not labels or not all(isinstance(x, str) and x for x in labels):
                findings.append(Finding(file, f"entry #{idx}: labels must be a non-empty string list"))

            if not _issue_id(entry):
                findings.append(Finding(file, f"entry #{idx}: missing stable source ID (id or number)"))

            has_size_label = any(isinstance(lbl, str) and lbl.startswith("size:") for lbl in labels or [])
            if not (has_size_label or entry.get("size") or entry.get("size_estimate")):
                findings.append(
                    Finding(file, f"entry #{idx}: include size as 'size:*' label or size/size_estimate field")
                )

            if "body" in entry:
                _validate_body(
                    entry,
                    findings,
                    file,
                    idx,
                    strict_sections=strict_sections,
                    max_body_chars=max_body_chars,
                )
            elif allow_legacy:
                _validate_legacy(entry, findings, file, idx)
            else:
                findings.append(Finding(file, f"entry #{idx}: canonical body is required (legacy format disabled)"))

    if issue_count == 0:
        findings.append(Finding(file, "no issue entries found"))

    return findings


def collect_files(patterns: list[str]) -> list[Path]:
    files: list[Path] = []
    for pattern in patterns:
        files.extend(sorted(ROOT.glob(pattern)))
    # de-dup, deterministic order
    return sorted(set(files))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate planning issue spec files")
    parser.add_argument(
        "--paths",
        nargs="+",
        default=[DEFAULT_GLOB],
        help="Glob(s) relative to repository root (default: planning/issues/*.yml)",
    )
    parser.add_argument(
        "--no-legacy",
        action="store_true",
        help="Disable legacy format support (requires canonical body-only entries)",
    )
    parser.add_argument(
        "--strict-sections",
        action="store_true",
        help="Require exact canonical markdown section headers in body entries",
    )
    parser.add_argument(
        "--max-body-chars",
        type=int,
        default=0,
        help="Optional max allowed markdown body size per issue (0 disables check)",
    )
    args = parser.parse_args(argv)

    files = collect_files(args.paths)
    if not files:
        print("❌ No issue spec files matched the provided glob(s)")
        return 1

    findings: list[Finding] = []
    for file in files:
        findings.extend(
            validate_file(
                file,
                allow_legacy=not args.no_legacy,
                strict_sections=args.strict_sections,
                max_body_chars=(args.max_body_chars or None),
            )
        )

    if findings:
        print("❌ Issue spec validation failed:")
        for finding in findings:
            print(f"- {finding}")
        print("\nRemediation: Update the listed entries to match planning/issues/README.md schema.")
        return 1

    legacy_mode = "enabled" if not args.no_legacy else "disabled"
    print(f"✅ Issue spec validation passed ({len(files)} file(s), legacy compatibility {legacy_mode})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
