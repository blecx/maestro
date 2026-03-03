#!/bin/bash
# Create all 15 agent improvement issues from the improvement plan

set -e

REPO="blecx/AI-Agent-Framework"
GH_API_SLEEP_SECONDS="${GH_API_SLEEP_SECONDS:-1}"

gh_t() {
  gh "$@"
  if [[ "${GH_API_SLEEP_SECONDS}" != "0" ]]; then
    sleep "${GH_API_SLEEP_SECONDS}"
  fi
}

echo "Creating 15 agent improvement issues..."
echo "GitHub API throttle: ${GH_API_SLEEP_SECONDS}s between requests"
echo ""

# Phase 1 Issues (Priority 1)

echo "Phase 1.1: PR Template Validation"
gh_t issue create --repo "$REPO" \
  --title "[Agent] Proactive PR Template Validation" \
  --label "enhancement" \
  --body "## Goal / Context
Add pre-PR validation phase to catch template errors before PR creation, reducing CI iterations from 2.3 to 1.1 per PR (52% reduction).

## Acceptance Criteria
- New script \`scripts/validate-pr-template.sh\` created
- Validates required sections, evidence format, checkboxes
- Integrated into Phase 5 of WORK-ISSUE-WORKFLOW.md
- Metrics: pr_template_validation_failures, ci_iterations_saved

## Impact
- Save 10-15 min per PR
- Prevent 60% of CI failures
- Reduce CI iterations by 52%

## Estimated Effort
4 hours"

echo "Phase 1.2: Cross-Repo Context Loader"
gh_t issue create --repo "$REPO" \
  --title "[Agent] Cross-Repo Context Loader" \
  --label "enhancement" \
  --body "## Goal / Context
Add automatic context detection when working across backend and client repos. Eliminate wrong Fixes: format and validation command errors.

## Acceptance Criteria
- New CrossRepoContext class in agents/workflow_agent.py
- Detects current repo, target issue repo, PR repo
- Returns correct validation commands per repo
- Returns correct Fixes: format for cross-repo PRs
- Metrics: cross_repo_errors, validation_command_retries

## Impact
- Reduce cross-repo errors from 40% to 5% (88% reduction)
- Eliminate wrong validation command retries

## Estimated Effort
6 hours"

echo "Phase 1.3: CI Workflow Behavior Training"
gh_t issue create --repo "$REPO" \
  --title "[Agent] CI Workflow Behavior Training Module" \
  --label "enhancement" \
  --body "## Goal / Context
Add explicit CI behavior knowledge to prevent PR #128-type confusion where agent doesn't understand workflow payload caching.

## Acceptance Criteria
- New file agents/knowledge/ci_workflows_behavior.json
- Documents GitHub Actions workflow rerun payload caching
- Solutions: push new commit, close/reopen PR
- Anti-patterns documented
- Agent consults before using 'gh run rerun'

## Impact
- Eliminate PR #128-type confusion
- Save 10-20 minutes of debugging per incident
- Zero ci_rerun_after_pr_update_errors

## Estimated Effort
2 hours"

echo "Phase 1.4: Smart Retry with Exponential Backoff"
gh_t issue create --repo "$REPO" \
  --title "[Agent] Smart Retry with Exponential Backoff" \
  --label "enhancement" \
  --body "## Goal / Context
Implement exponential backoff for CI status checking. Agent currently polls every 5s → wastes time.

## Acceptance Criteria
- New SmartRetry class in agents/workflow_agent.py
- Exponential backoff: 5s, 10s, 20s, 40s, 60s
- Estimates remaining CI time based on past runs
- Adaptive waiting
- Max wait: 10 minutes
- Metrics: ci_polling_time_saved_seconds

## Impact
- Reduce wasted polling time by 60%
- More responsive to early completion

## Estimated Effort
3 hours"

echo "Phase 1.5: Parallel Validation Execution"
gh_t issue create --repo "$REPO" \
  --title "[Agent] Parallel Validation Execution" \
  --label "enhancement" \
  --body "## Goal / Context
Run independent validations in parallel instead of sequentially. Current: lint (10s) → test (30s) → build (5s) = 45s. Target: 30s wall clock.

## Acceptance Criteria
- Async validation execution in workflow_agent.py
- Runs lint, test, build in parallel
- Aggregates results
- Metrics: phase4_execution_time_seconds

## Impact
- Save 15-20 seconds per issue (Phase 4)
- Faster feedback on multiple errors

## Estimated Effort
3 hours"

# Phase 2 Issues (Priority 2)

echo ""
echo "Phase 2.6: Incremental Knowledge Base Updates"
gh_t issue create --repo "$REPO" \
  --title "[Agent] Incremental Knowledge Base Updates" \
  --label "enhancement" \
  --body "## Goal / Context
Update knowledge base after each phase (not just end of workflow). Enable agent to use learnings mid-issue.

## Acceptance Criteria
- Modify _execute_phase() to extract learnings
- Update KB after each phase
- New metrics: learnings_applied_same_issue, problems_resolved_faster

## Impact
- Agent can use learnings within same issue
- Faster problem resolution

## Estimated Effort
4 hours"

echo "Phase 2.7: Smart File Change Detection"
gh_t issue create --repo "$REPO" \
  --title "[Agent] Smart File Change Detection" \
  --label "enhancement" \
  --body "## Goal / Context
Detect change scope and run targeted validation. Don't run full test suite for doc-only changes.

## Acceptance Criteria
- New SmartValidation class
- Detects doc-only changes → markdown lint only
- Detects test-only changes → lint + test only
- Detects type-only changes → type check + lint only
- Metrics: validation_time_saved_per_issue, unnecessary_test_runs_avoided

## Impact
- Save 2-3 minutes for doc-only PRs
- Faster iteration on tests

## Estimated Effort
4 hours"

echo "Phase 2.8: Auto-Recovery from Common Errors"
gh_t issue create --repo "$REPO" \
  --title "[Agent] Auto-Recovery from Common Errors" \
  --label "enhancement" \
  --body "## Goal / Context
Implement auto-recovery for known error patterns. Stop asking user for TypeScript/lint/test errors with known solutions.

## Acceptance Criteria
- New ErrorRecovery class with recovery patterns
- Auto-fix: 'Cannot find module X' → npm install
- Auto-fix: 'Unused import Y' → remove import
- Auto-fix: 'Type null not assignable' → add | null
- Auto-fix: 'Evidence must be filled' → convert to inline
- Metrics: auto_recoveries_successful, user_interventions_avoided

## Impact
- Reduce user interventions by 40%
- Faster issue resolution

## Estimated Effort
6 hours"

echo "Phase 2.9: Pre-Flight Issue Readiness Checks"
gh_t issue create --repo "$REPO" \
  --title "[Agent] Pre-Flight Issue Readiness Checks" \
  --label "enhancement" \
  --body "## Goal / Context
Validate issue quality before starting work. Prevent starting issues missing acceptance criteria or with unresolved blockers.

## Acceptance Criteria
- New IssuePreflight class
- Validates: acceptance criteria, blockers resolved, clear requirements, labels, estimation
- Fails gracefully with specific feedback
- Metrics: issues_failed_preflight, rework_time_saved_hours

## Impact
- Prevent 90% of 'wrong implementation' issues
- Save hours of rework

## Estimated Effort
3 hours"

echo "Phase 2.10: Automated Documentation Updates"
gh_t issue create --repo "$REPO" \
  --title "[Agent] Automated Documentation Updates" \
  --label "enhancement" \
  --body "## Goal / Context
Auto-detect documentation impact and update docs. Agent forgets to update README when adding API endpoints/commands.

## Acceptance Criteria
- New DocUpdater class
- Detects: new API endpoints → update docs/api/README.md
- Detects: new commands → update README.md
- Detects: behavior changes → update CHANGELOG.md
- Metrics: auto_doc_updates, doc_staleness_issues_prevented

## Impact
- Always up-to-date docs
- Fewer doc-only PRs

## Estimated Effort
3 hours"

# Phase 3 Issues (Priority 3)

echo ""
echo "Phase 3.11: Cached Command Results"
gh_t issue create --repo "$REPO" \
  --title "[Agent] Cached Command Results" \
  --label "enhancement" \
  --body "## Goal / Context
Cache command results within issue scope. Agent runs 'npm install' 3 times (Phase 3, 4, 5) = 12s waste.

## Acceptance Criteria
- New CommandCache class
- 1-hour TTL cache
- Cache key per command
- Metrics: cache_hits, time_saved_from_cache_seconds

## Impact
- Save 8-12 seconds per issue
- Reduce network/disk I/O

## Estimated Effort
2 hours"

echo "Phase 3.12: Predictive Time Estimation (ML)"
gh_t issue create --repo "$REPO" \
  --title "[Agent] Predictive Time Estimation with ML" \
  --label "enhancement" \
  --body "## Goal / Context
Train simple ML model on historical data for better time estimates. Current: simple average * 0.875. Target: account for complexity, domain, dependencies, multi-repo.

## Acceptance Criteria
- New TimeEstimator class with RandomForestRegressor
- Features: files_to_change, lines_estimate, domain, is_multi_repo, has_dependencies, complexity_score
- Returns prediction + confidence + reasoning
- Metrics: estimation_accuracy (MAE), estimation_confidence

## Impact
- More accurate estimates
- Better planning
- Identify high-risk issues early

## Estimated Effort
8 hours"

echo "Phase 3.13: Comprehensive Test Coverage Analyzer"
gh_t issue create --repo "$REPO" \
  --title "[Agent] Comprehensive Test Coverage Analyzer" \
  --label "enhancement" \
  --body "## Goal / Context
Analyze coverage diff and enforce minimum coverage. Agent doesn't verify coverage adequately.

## Acceptance Criteria
- New CoverageAnalyzer class
- Analyzes before/after coverage
- Fails if coverage decreases
- Warns if file coverage < 80%
- Metrics: coverage_regressions_prevented, average_coverage_delta

## Impact
- Maintain/improve coverage
- Catch untested code early

## Estimated Effort
5 hours"

echo "Phase 3.14: Multi-Stage Commit Strategy"
gh_t issue create --repo "$REPO" \
  --title "[Agent] Multi-Stage Commit Strategy" \
  --label "enhancement" \
  --body "## Goal / Context
Create logical commit sequence instead of single large commit. Hard to review/revert single commits.

## Acceptance Criteria
- New CommitStrategy class
- Stage 1: Tests (red)
- Stage 2: Implementation (green)
- Stage 3: Documentation
- Stage 4: Refactoring
- Metrics: commits_per_pr (target 2-4), pr_review_time_minutes

## Impact
- Better Git history
- Easier code review
- Safer rollbacks

## Estimated Effort
4 hours"

echo "Phase 3.15: Learning Confidence Scoring"
gh_t issue create --repo "$REPO" \
  --title "[Agent] Learning Confidence Scoring" \
  --label "enhancement" \
  --body "## Goal / Context
Score learning relevance and confidence. Agent applies all learnings equally → some are outdated/wrong for current context.

## Acceptance Criteria
- New LearningScorer class
- Scoring factors: recency (90-day half-life), domain match, repo match, success rate, application frequency
- get_relevant_learnings() returns sorted by score (threshold > 0.3)
- Metrics: learning_relevance_score_avg, irrelevant_learnings_filtered

## Impact
- Apply only relevant learnings
- Reduce false positives
- Faster problem solving

## Estimated Effort
6 hours"

echo ""
echo "✅ All 15 issues created successfully!"
echo ""
echo "Issue Summary:"
echo "  Phase 1 (Quick Wins): 5 issues, 18 hours total"
echo "  Phase 2 (Medium-Term): 5 issues, 20 hours total"
echo "  Phase 3 (Advanced): 5 issues, 30 hours total"
echo ""
echo "Next: Run ./next-issue to start implementation"
