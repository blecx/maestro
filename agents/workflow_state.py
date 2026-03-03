"""workflow_state.py - Cross-repo context and state detection.

Extracted from workflow_agent.py (Phase 1 improvement, Issue #160).
Handles detecting the current repository context and generating
correct cross-repo references, validation commands, and Fixes: formats.
"""

from pathlib import Path
from typing import List, Optional

from agents.validation_profiles import (
    get_validation_commands as get_profile_validation_commands,
)
from agents.workflow_side_effect_adapters import (
    SubprocessWorkflowSideEffectAdapter,
    WorkflowSideEffectAdapter,
    WorkflowSideEffectError,
)


class CrossRepoContext:
    """
    Cross-Repo Context Loader (Issue #160)

    Automatically detects repository context when working across backend and client repos.
    Eliminates confusion about Fixes: format and validation commands.
    """

    def __init__(
        self,
        workspace_root: Path = Path("."),
        side_effects: Optional[WorkflowSideEffectAdapter] = None,
    ):
        self.workspace_root = workspace_root
        self.side_effects = side_effects or SubprocessWorkflowSideEffectAdapter()
        self.current_repo = None
        self.target_issue_repo = None
        self.pr_repo = None
        self._cache = {}
        self.detect_repos()

    def detect_repos(self):
        """Detect current repo and related repos."""
        try:
            result = self.side_effects.run(
                ["git", "remote", "get-url", "origin"],
                cwd=self.workspace_root,
                check=True,
            )
            remote_url = result.stdout.strip()

            if "AI-Agent-Framework-Client" in remote_url:
                self.current_repo = "client"
                self.pr_repo = "blecx/AI-Agent-Framework-Client"
            elif "AI-Agent-Framework" in remote_url:
                self.current_repo = "backend"
                self.pr_repo = "blecx/AI-Agent-Framework"
            else:
                self.current_repo = "unknown"
                self.pr_repo = "unknown"
        except WorkflowSideEffectError:
            self.current_repo = "unknown"
            self.pr_repo = "unknown"

    def get_validation_commands(self) -> List[str]:
        """Return correct validation commands for current repo."""
        if self.current_repo in {"client", "backend"}:
            return get_profile_validation_commands(self.current_repo, "full")
        return []

    def get_fixes_format(
        self, issue_number: int, target_repo: Optional[str] = None
    ) -> str:
        """Return correct Fixes: format for cross-repo or same-repo PRs."""
        if target_repo and target_repo != self.pr_repo:
            return f"Fixes: {target_repo}#{issue_number}"
        return f"Fixes: #{issue_number}"

    def is_cross_repo_scenario(
        self, issue_number: int, target_repo: Optional[str] = None
    ) -> bool:
        """Check if this is a cross-repo scenario."""
        return bool(target_repo and target_repo != self.pr_repo)
