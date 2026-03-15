"""Adapter for exposing the package orchestrator via the workflow API."""

from pathlib import Path

from agents.factory_orchestrator import FactoryOrchestrator


class FactoryAdapter:
    """Provides a compatible interface for work-issue scripts."""

    def __init__(self, issue_number: int, dry_run: bool = False, **kwargs):
        self.issue_number = issue_number
        self.dry_run = dry_run
        self.plan_only = False
        self.system_instructions = ""

    async def initialize(self) -> None:
        self.system_instructions = self._build_system_instructions()

    def _build_system_instructions(self) -> str:
        return ""

    async def execute(self, issue_summary: str = "", pr_title: str = "") -> bool:
        if self.dry_run:
            print(f"Factory adapter: dry run for issue #{self.issue_number}")
            return True

        if self.plan_only:
            print("Factory adapter: plan_only is not fully supported yet.")

        full_body = issue_summary
        if self.system_instructions:
            full_body = (
                f"{issue_summary}\n\n[Agent Instructions Override]\n"
                f"{self.system_instructions}"
            )

        orchestrator = FactoryOrchestrator(workspace_root=Path.cwd())
        repo = "YOUR_ORG/YOUR_REPO"
        result = await orchestrator.run_issue(
            issue_number=self.issue_number,
            repo=repo,
            issue_title=pr_title,
            issue_body=full_body,
        )
        return result.success

    async def continue_conversation(self, user_input: str) -> str:
        return "Interactive conversation is not fully supported by the factory adapter."
