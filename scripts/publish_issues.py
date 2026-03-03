#!/usr/bin/env python3
"""Deterministic issue publisher for planning/issues/*.yml specs."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.tooling.gh_throttle import run_gh_throttled

DEFAULT_GLOB = "planning/issues/*.yml"
DEFAULT_MAP_PATH = ROOT / "planning/issues/.published-map.json"
DEFAULT_SLEEP_SECONDS = 1.0

_GH_SLEEP_SECONDS = DEFAULT_SLEEP_SECONDS
_last_gh_call_monotonic: float | None = None

REPO_MAP = {
    "AI-Agent-Framework": "blecx/AI-Agent-Framework",
    "AI-Agent-Framework-Client": "blecx/AI-Agent-Framework-Client",
}


def _set_gh_sleep_seconds(seconds: float) -> None:
    global _GH_SLEEP_SECONDS
    _GH_SLEEP_SECONDS = max(0.0, float(seconds))


def _throttle_gh() -> None:
    global _last_gh_call_monotonic
    if _GH_SLEEP_SECONDS <= 0:
        return

    now = time.monotonic()
    if _last_gh_call_monotonic is not None:
        elapsed = now - _last_gh_call_monotonic
        if elapsed < _GH_SLEEP_SECONDS:
            time.sleep(_GH_SLEEP_SECONDS - elapsed)
    _last_gh_call_monotonic = time.monotonic()


@dataclass(frozen=True)
class IssueSpec:
    source_file: Path
    source_id: str
    repo_alias: str
    repo: str
    title: str
    body: str
    labels: list[str]

    @property
    def key(self) -> str:
        return f"{self.repo}|{self.source_id}"

    @property
    def title_hash(self) -> str:
        return hashlib.sha256(self.title.encode("utf-8")).hexdigest()[:12]


def _run_gh_json(args: list[str]) -> Any:
    _throttle_gh()
    proc = run_gh_throttled(["gh", *args], capture_output=True, text=True, min_interval_seconds=0)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or f"gh {' '.join(args)} failed")
    return json.loads(proc.stdout)


def _run_gh_text(args: list[str]) -> str:
    _throttle_gh()
    proc = run_gh_throttled(["gh", *args], capture_output=True, text=True, min_interval_seconds=0)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or f"gh {' '.join(args)} failed")
    return proc.stdout.strip()


def _collect_files(patterns: list[str]) -> list[Path]:
    files: list[Path] = []
    for pattern in patterns:
        files.extend(sorted(ROOT.glob(pattern)))
    return sorted(set(files))


def _source_id(entry: dict[str, Any], index: int) -> str:
    value = entry.get("id") or entry.get("number")
    if isinstance(value, str) and value.strip():
        return value.strip()
    return f"AUTO-{index:03d}"


def _render_legacy_body(entry: dict[str, Any]) -> str:
    plan = entry.get("plan", {})
    template = entry.get("issue_template", {})

    in_scope = "\n".join(f"- {item}" for item in plan.get("in_scope", [])) or "- (to be completed)"
    out_of_scope = "\n".join(f"- {item}" for item in plan.get("out_of_scope", [])) or "- (to be completed)"
    deps = entry.get("dependencies", [])
    deps_text = "\n".join(f"- {d}" for d in deps) if deps else "- None"

    tasks = entry.get("tasks", [])
    task_lines = "\n".join(f"- {t}" for t in tasks) if tasks else "- (to be completed)"

    acceptance = template.get("acceptance_criteria", [])
    acceptance_lines = "\n".join(f"- [ ] {a}" for a in acceptance) if acceptance else "- [ ] (to be completed)"

    validations = template.get("validation", [])
    validation_lines = "\n".join(f"- `{cmd}`" for cmd in validations) if validations else "- `pytest -q`"

    cross_repo = "Yes - see dependencies" if entry.get("repo") == "AI-Agent-Framework-Client" else "No"

    return "\n".join(
        [
            "## Goal / Problem Statement",
            str(plan.get("goal") or "(to be completed)"),
            "",
            "## Scope",
            "### In Scope",
            in_scope,
            "",
            "### Out of Scope",
            out_of_scope,
            "",
            "### Dependencies",
            deps_text,
            "",
            "## Acceptance Criteria",
            acceptance_lines,
            "",
            "## Technical Approach",
            task_lines,
            "",
            "## Testing Requirements",
            validation_lines,
            "",
            "## Documentation Updates",
            "- [ ] Update relevant docs and add validation evidence.",
            "",
            "## Cross-Repository Coordination",
            cross_repo,
        ]
    )


def _load_specs(files: list[Path]) -> list[IssueSpec]:
    specs: list[IssueSpec] = []

    for file in files:
        data = yaml.safe_load(file.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            continue

        for repo_alias in sorted(REPO_MAP):
            entries = data.get(repo_alias)
            if not isinstance(entries, list):
                continue

            for index, entry in enumerate(entries, start=1):
                if not isinstance(entry, dict):
                    continue
                title = str(entry.get("title", "")).strip()
                if not title:
                    continue

                source_id = _source_id(entry, index)
                labels = [str(x).strip() for x in entry.get("labels", []) if str(x).strip()]
                body = entry.get("body")
                if not isinstance(body, str) or not body.strip():
                    body = _render_legacy_body(entry)

                specs.append(
                    IssueSpec(
                        source_file=file,
                        source_id=source_id,
                        repo_alias=repo_alias,
                        repo=REPO_MAP[repo_alias],
                        title=title,
                        body=body,
                        labels=labels,
                    )
                )

    specs.sort(key=lambda s: (s.repo_alias != "AI-Agent-Framework", s.source_file.name, s.source_id, s.title))
    return specs


def _load_map(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": 1, "entries": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"version": 1, "entries": {}}
    if not isinstance(data, dict):
        return {"version": 1, "entries": {}}
    data.setdefault("version", 1)
    data.setdefault("entries", {})
    if not isinstance(data["entries"], dict):
        data["entries"] = {}
    return data


def _save_map(path: Path, mapping: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(mapping, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _safe_relpath(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _find_existing_by_title(repo: str, title: str) -> dict[str, Any] | None:
    result = _run_gh_json(
        [
            "issue",
            "list",
            "--repo",
            repo,
            "--state",
            "all",
            "--search",
            f'"{title}" in:title',
            "--limit",
            "20",
            "--json",
            "number,title,url",
        ]
    )
    if not isinstance(result, list):
        return None
    for item in result:
        if isinstance(item, dict) and item.get("title") == title:
            return item
    return None


def _create_issue(spec: IssueSpec) -> tuple[int, str]:
    args = [
        "issue",
        "create",
        "--repo",
        spec.repo,
        "--title",
        spec.title,
        "--body",
        spec.body,
    ]
    for label in spec.labels:
        args.extend(["--label", label])

    url = _run_gh_text(args)
    number_text = url.rstrip("/").split("/")[-1]
    return int(number_text), url


def publish(
    specs: list[IssueSpec],
    mapping: dict[str, Any],
    apply: bool,
    repo_filter: str | None,
) -> tuple[list[str], dict[str, Any]]:
    entries = mapping["entries"]
    logs: list[str] = []

    for spec in specs:
        if repo_filter and spec.repo != repo_filter:
            continue

        current = entries.get(spec.key)
        if current:
            logs.append(f"SKIP mapped    {spec.key} -> #{current['issue_number']} ({spec.repo})")
            continue

        existing = None
        try:
            existing = _find_existing_by_title(spec.repo, spec.title)
        except Exception as exc:
            logs.append(f"WARN duplicate-check failed for {spec.title!r}: {exc}")

        if existing:
            issue_number = int(existing["number"])
            issue_url = str(existing["url"])
            entries[spec.key] = {
                "repo": spec.repo,
                "repo_alias": spec.repo_alias,
                "source_id": spec.source_id,
                "source_file": _safe_relpath(spec.source_file),
                "title": spec.title,
                "title_hash": spec.title_hash,
                "issue_number": issue_number,
                "issue_url": issue_url,
                "status": "existing",
            }
            logs.append(f"MAP existing   {spec.key} -> #{issue_number} ({issue_url})")
            continue

        if not apply:
            logs.append(f"DRY would-create {spec.key} in {spec.repo}: {spec.title}")
            continue

        try:
            issue_number, issue_url = _create_issue(spec)
        except Exception as exc:
            logs.append(f"ERROR create failed {spec.key}: {exc}")
            continue

        entries[spec.key] = {
            "repo": spec.repo,
            "repo_alias": spec.repo_alias,
            "source_id": spec.source_id,
            "source_file": _safe_relpath(spec.source_file),
            "title": spec.title,
            "title_hash": spec.title_hash,
            "issue_number": issue_number,
            "issue_url": issue_url,
            "status": "created",
        }
        logs.append(f"CREATED       {spec.key} -> #{issue_number} ({issue_url})")

    return logs, mapping


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Publish planning issue specs to GitHub issues")
    parser.add_argument("--paths", nargs="+", default=[DEFAULT_GLOB], help="Glob(s) for issue spec files")
    parser.add_argument("--map", default=str(DEFAULT_MAP_PATH), help="Path to published issue map JSON")
    parser.add_argument("--apply", action="store_true", help="Create missing issues (default is dry-run)")
    parser.add_argument(
        "--repo",
        dest="repo_filter",
        choices=sorted(REPO_MAP.values()),
        help="Optional single target repo filter",
    )
    parser.add_argument(
        "--sleep-seconds",
        type=float,
        default=DEFAULT_SLEEP_SECONDS,
        help="Minimum delay between GitHub CLI requests (default: 1.0)",
    )
    args = parser.parse_args(argv)

    _set_gh_sleep_seconds(args.sleep_seconds)

    files = _collect_files(args.paths)
    if not files:
        print("❌ No issue spec files matched")
        return 1

    specs = _load_specs(files)
    if not specs:
        print("❌ No publishable issue entries found")
        return 1

    map_path = Path(args.map)
    mapping = _load_map(map_path)
    logs, mapping = publish(specs, mapping, apply=args.apply, repo_filter=args.repo_filter)

    print(f"ℹ️  GitHub request throttle: {_GH_SLEEP_SECONDS:.2f}s between requests")
    for line in logs:
        print(line)

    if args.apply:
        _save_map(map_path, mapping)
        print(f"✅ Mapping updated: {map_path.relative_to(ROOT)}")
    else:
        print("✅ Dry-run complete (no issues created, mapping unchanged)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
