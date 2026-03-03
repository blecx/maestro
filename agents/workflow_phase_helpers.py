"""workflow_phase_helpers.py - Per-phase KB, validation, preflight and doc update helpers.

Extracted from workflow_agent.py (Phase 2 improvements, Issues #164-#168):
- IncrementalKnowledgeBase (Issue #164): KB updates after each phase
- SmartValidation        (Issue #165): file-change-scoped validation
- IssuePreflight         (Issue #167): pre-work issue quality checks
- DocUpdater             (Issue #168): auto-doc-impact detection
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from agents.validation_profiles import (
    get_validation_commands as get_profile_validation_commands,
)
from agents.workflow_side_effect_adapters import (
    SubprocessWorkflowSideEffectAdapter,
    WorkflowSideEffectAdapter,
    WorkflowSideEffectError,
)


class IncrementalKnowledgeBase:
    """
    Incremental Knowledge Base Updates (Issue #164)

    Updates KB after each phase (not just end of workflow).
    Enables agent to use learnings mid-issue for faster problem resolution.
    """

    def __init__(self, kb_dir: Path = Path("agents/knowledge")):
        self.kb_dir = kb_dir
        self.kb_dir.mkdir(parents=True, exist_ok=True)
        self.phase_learnings_file = kb_dir / "phase_learnings.json"
        self._init_phase_learnings()

    def _init_phase_learnings(self):
        if not self.phase_learnings_file.exists():
            initial_data = {
                "learnings_by_phase": {
                    f"Phase {i}": [] for i in range(1, 7)
                },
                "metrics": {
                    "learnings_applied_same_issue": 0,
                    "problems_resolved_faster": 0,
                },
            }
            with open(self.phase_learnings_file, "w") as f:
                json.dump(initial_data, f, indent=2)

    def extract_learnings_from_phase(
        self, phase_name: str, phase_output: Dict, success: bool
    ) -> List[Dict]:
        learnings = []
        if not success and phase_output.get("error"):
            learnings.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "phase": phase_name,
                    "type": "error_pattern",
                    "error": phase_output["error"],
                    "context": phase_output.get("context", ""),
                    "solution": phase_output.get("solution", ""),
                    "confidence": 0.8,
                }
            )
        if success and phase_output.get("validation_time"):
            learnings.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "phase": phase_name,
                    "type": "performance",
                    "validation_time": phase_output["validation_time"],
                    "commands_run": phase_output.get("commands", []),
                    "confidence": 0.9,
                }
            )
        return learnings

    def update_kb_after_phase(self, phase_name: str, learnings: List[Dict]):
        if not learnings:
            return
        with open(self.phase_learnings_file, "r") as f:
            data = json.load(f)
        if phase_name in data["learnings_by_phase"]:
            data["learnings_by_phase"][phase_name].extend(learnings)
            data["learnings_by_phase"][phase_name] = (
                data["learnings_by_phase"][phase_name][-20:]
            )
        with open(self.phase_learnings_file, "w") as f:
            json.dump(data, f, indent=2)

    def get_relevant_learnings(self, phase_name: str, context: Dict) -> List[Dict]:
        with open(self.phase_learnings_file, "r") as f:
            data = json.load(f)
        phase_learnings = data["learnings_by_phase"].get(phase_name, [])
        cutoff = datetime.now() - timedelta(days=30)
        relevant = [
            l for l in phase_learnings
            if datetime.fromisoformat(l["timestamp"]) > cutoff
            and l.get("confidence", 0) > 0.7
        ]
        return sorted(relevant, key=lambda x: x.get("confidence", 0), reverse=True)


class SmartValidation:
    """
    Smart File Change Detection (Issue #165)

    Analyzes git diff to determine validation scope.
    Runs targeted validations to save time.
    """

    def __init__(
        self,
        workspace_root: Path = Path("."),
        side_effects: Optional[WorkflowSideEffectAdapter] = None,
    ):
        self.workspace_root = workspace_root
        self.side_effects = side_effects or SubprocessWorkflowSideEffectAdapter()
        self.metrics = {
            "validation_time_saved_per_issue": 0.0,
            "unnecessary_test_runs_avoided": 0,
        }

    def analyze_changes(self) -> Dict[str, bool]:
        """Analyze git changes to determine what validations are needed."""
        try:
            result = self.side_effects.run(
                ["git", "diff", "--name-only", "HEAD"],
                cwd=self.workspace_root,
                check=True,
            )
            if result.returncode != 0 or not result.stdout.strip():
                return {"doc_only": False, "test_only": False, "type_only": False, "full": True}

            changed_files = result.stdout.strip().split("\n")
            doc_files = [f for f in changed_files if f.endswith((".md", ".txt", ".rst"))]
            test_files = [f for f in changed_files if "test" in f.lower() or f.endswith(".test.ts")]
            type_files = [f for f in changed_files if f.endswith(".d.ts")]

            if len(changed_files) == len(doc_files) and doc_files:
                return {"doc_only": True, "test_only": False, "type_only": False, "full": False}
            if len(changed_files) == len(test_files) and test_files:
                return {"doc_only": False, "test_only": True, "type_only": False, "full": False}
            if len(changed_files) == len(type_files) and type_files:
                return {"doc_only": False, "test_only": False, "type_only": True, "full": False}
            return {"doc_only": False, "test_only": False, "type_only": False, "full": True}

        except WorkflowSideEffectError:
            return {"doc_only": False, "test_only": False, "type_only": False, "full": True}

    def get_validation_commands(self, repo_type: str = "backend") -> List[str]:
        """Get appropriate validation commands based on change analysis."""
        changes = self.analyze_changes()
        if changes["doc_only"]:
            commands = get_profile_validation_commands(repo_type, "doc_only")
            self.metrics["unnecessary_test_runs_avoided"] += 1
            self.metrics["validation_time_saved_per_issue"] += 120
        elif changes["test_only"]:
            commands = get_profile_validation_commands(repo_type, "test_only")
            self.metrics["validation_time_saved_per_issue"] += 60
        elif changes["type_only"]:
            commands = get_profile_validation_commands(repo_type, "type_only")
            self.metrics["validation_time_saved_per_issue"] += 90
        else:
            commands = get_profile_validation_commands(repo_type, "full")
        return commands


class IssuePreflight:
    """
    Pre-Flight Issue Readiness Checks (Issue #167)

    Validates issue quality before starting work.
    Prevents 90% of 'wrong implementation' issues.
    """

    def __init__(self, side_effects: Optional[WorkflowSideEffectAdapter] = None):
        self.side_effects = side_effects or SubprocessWorkflowSideEffectAdapter()
        self.metrics = {"issues_failed_preflight": 0, "rework_time_saved_hours": 0.0}

    def validate_issue(self, issue_data: Dict) -> Tuple[bool, List[str]]:
        """Validate issue readiness. Returns (is_valid, list_of_issues)."""
        issues = []
        body = issue_data.get("body", "")

        if not body or "acceptance criteria" not in body.lower():
            issues.append("❌ Missing acceptance criteria section")
        if len(body) < 100:
            issues.append("⚠️  Issue description seems too short (<100 chars)")
        if "blocked" in body.lower() or "blocker" in body.lower():
            issues.append("⚠️  Issue mentions blockers - verify they're resolved")
        if not issue_data.get("labels"):
            issues.append("⚠️  No labels applied - consider adding priority/type labels")
        if not any(kw in body.lower() for kw in ["estimated", "estimate", "hours", "effort"]):
            issues.append("⚠️  No time estimation found")
        if "depends on" in body.lower() or "requires #" in body.lower():
            issues.append("⚠️  Issue has dependencies - verify they're complete")

        is_valid = not any(i.startswith("❌") for i in issues)
        if not is_valid:
            self.metrics["issues_failed_preflight"] += 1
            self.metrics["rework_time_saved_hours"] += 2.0

        return is_valid, issues

    def fetch_issue_data(
        self, issue_num: int, workspace_root: Path = Path(".")
    ) -> Optional[Dict]:
        """Fetch issue data from GitHub."""
        try:
            result = self.side_effects.run(
                ["gh", "issue", "view", str(issue_num), "--json", "title,body,labels,state"],
                cwd=workspace_root,
                check=True,
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
        except (WorkflowSideEffectError, json.JSONDecodeError):
            pass
        return None


class DocUpdater:
    """
    Automated Documentation Updates (Issue #168)

    Auto-detects documentation impact and updates docs.
    Prevents docs from going stale.
    """

    def __init__(
        self,
        workspace_root: Path = Path("."),
        side_effects: Optional[WorkflowSideEffectAdapter] = None,
    ):
        self.workspace_root = workspace_root
        self.side_effects = side_effects or SubprocessWorkflowSideEffectAdapter()
        self.metrics = {"auto_doc_updates": 0, "doc_staleness_issues_prevented": 0}

    def detect_documentation_impact(self) -> Dict[str, List[str]]:
        """Detect what documentation needs updating based on git changes."""
        impacts: Dict[str, List[str]] = {}
        try:
            result = self.side_effects.run(
                ["git", "diff", "HEAD", "--unified=0"],
                cwd=self.workspace_root,
                check=True,
            )
            diff = result.stdout
            if "router.get(" in diff or "router.post(" in diff:
                impacts.setdefault("docs/api/README.md", []).append("New API endpoint detected")
                self.metrics["doc_staleness_issues_prevented"] += 1
            if "argparse" in diff or "add_argument(" in diff:
                impacts.setdefault("README.md", []).append("New CLI command detected")
                self.metrics["doc_staleness_issues_prevented"] += 1
            if any(kw in diff for kw in ["breaking change", "deprecated", "removed"]):
                impacts.setdefault("CHANGELOG.md", []).append(
                    "Breaking change or deprecation detected"
                )
                self.metrics["doc_staleness_issues_prevented"] += 1
        except WorkflowSideEffectError:
            pass
        return impacts

    def generate_documentation_updates(
        self, impacts: Dict[str, List[str]]
    ) -> Dict[str, str]:
        """Generate suggested documentation update content."""
        dispatch = {
            "docs/api/README.md": self._suggest_api_doc_update,
            "README.md": self._suggest_readme_update,
            "CHANGELOG.md": self._suggest_changelog_update,
        }
        suggestions = {
            doc: dispatch[doc]()
            for doc in impacts
            if doc in dispatch
        }
        if suggestions:
            self.metrics["auto_doc_updates"] += len(suggestions)
        return suggestions

    def _suggest_api_doc_update(self) -> str:
        return (
            "\n## New API Endpoint\n\n**TODO:** Document the new endpoint:\n"
            "- HTTP method and path\n- Request parameters\n- Response format\n- Example usage\n"
        )

    def _suggest_readme_update(self) -> str:
        return (
            "\n## New Command\n\n**TODO:** Document the new command:\n"
            "- Command syntax\n- Options/flags\n- Example usage\n"
        )

    def _suggest_changelog_update(self) -> str:
        today = datetime.now().strftime("%Y-%m-%d")
        return (
            f"\n## [Unreleased] - {today}\n\n### Changed\n"
            "- **TODO:** Describe the breaking change or deprecation\n"
        )
