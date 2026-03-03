# Copilot Instructions for AI-Agent-Framework

## Overview

ISO 21500 Project Management AI Agent - Full-stack app with FastAPI (Python 3.10+) + React/Vite. Docker deployment or local venv. ~190MB, 8000+ files. Git-based document storage in `projectDocs/` (separate repo, NEVER commit to code). Two containers: API + web/nginx.

## Development Workflow

### Plan → Issues → PRs

**ALWAYS follow this standard workflow for all feature work, bug fixes, and cross-repo coordination:**

1. **Start with a Plan/Spec**
   - Define clear goal, scope, acceptance criteria, and constraints
   - Consider impact on related repo: [`blecx/AI-Agent-Framework-Client`](https://github.com/blecx/AI-Agent-Framework-Client)
   - Document any cross-repo dependencies or API changes

2. **Break Work into Small Issues**
   - Each issue should be sized for a single PR
   - **Size Guidelines:**
     - **S (Small):** < 50 lines changed, < 1 day (prefer for new domains)
     - **M (Medium):** 50-200 lines changed, 1-2 days (typical feature)
     - **L (Large):** > 200 lines changed (consider splitting)
   - Issues must include acceptance criteria and validation steps
   - **Use issue templates:** Backend features use `.github/ISSUE_TEMPLATE/feature_request.yml`
   - **Comprehensive descriptions:** Include goal, scope (in/out), acceptance criteria, API contract, technical approach, testing requirements, documentation updates
   - Link related issues across repositories when coordinating changes
   - **Repository placement:**
     - **Backend issues** (API, services, domain models) → `blecx/AI-Agent-Framework`
     - **UX issues** (React components, client API clients) → `blecx/AI-Agent-Framework-Client`

3. **Implement One Issue Per PR**
   - Keep diffs small and reviewable (prefer < 200 lines changed)
   - Include validation steps in PR description
   - Reference the issue number in PR title and description
   - Use descriptive commit messages following conventional commits

4. **Validation Requirements** (see below for repo-specific steps)
   - Run linting and builds before submitting PR
   - Test locally with both Docker and venv setups
   - Verify no unintended files are committed

5. **Merge Strategy**
   - Prefer squash merges to keep history clean
   - Ensure PR title is clear (becomes squash commit message)
   - Delete branch after merge

6. **Post-Merge Cleanup (MANDATORY)**
   - **ALWAYS run after successful merge:**
     ```bash
     rm -f .tmp/pr-body-<issue-number>.md .tmp/issue-<issue-number>-*.md
     ls -la .tmp/*<issue-number>* 2>/dev/null || echo "✓ Cleanup verified"
     ```
   - Verify no temporary files remain for the closed issue
   - This step is REQUIRED before marking issue as complete

### Issue Selection Order (resolve-issue-dev)

**When selecting the next issue to work on, ALWAYS follow this priority order:**

1. **Priority 1: Backend/TUI/CLI issues**
   - Repository: `blecx/AI-Agent-Framework`
   - Includes: API services, domain models, CLI tools, backend tests
   - Example issue numbers: #69-#78 (Step 2 backend)

2. **Priority 2: Client/UX issues**
   - Repository: `blecx/AI-Agent-Framework-Client`
   - Includes: React components, UI features, client tests
   - Example issue numbers: #102-#109 (Step 2 frontend)

3. **Within each priority group:**
   - **Select the LOWEST issue number first**
   - Work sequentially: #69 → #70 → #71 → ... → #77 → #78
   - Then move to client: #102 → #103 → ... → #109

**Rationale:**

- **Dependency management:** Frontend depends on backend APIs
- **Parallel work:** Backend team completes work while frontend team prepares
- **Predictability:** Everyone knows "what's next" in implementation order
- **Quality gates:** Backend E2E tests validate before frontend development

**Example (Step 2):**

- Open issues: #69, #70, #72, #102, #104
- **Correct order:** #69 → #70 → #72 → #102 → #104
- **Why:** Work backend issues (#69, #70, #72) before client issues (#102, #104)

**Edge cases:**

- If all backend issues are complete, start client issues (lowest number first)
- If all issues in both repos are complete, check for new issues or declare milestone done
- If backend issue is blocked, skip to next backend issue (don't jump to client)

### Domain-Driven Design (DDD) Architecture (REQUIRED)

**All code changes must follow DDD architecture patterns:**

#### Core Principles

1. **Single Responsibility Principle (SRP):** Each class/module has ONE clear purpose
2. **Domain Separation:** Clear boundaries between domains (Templates, Blueprints, Proposals, Artifacts, RAID, Workflow, etc.)
3. **Type Safety:** Explicit interfaces and Pydantic models for all domain objects
4. **Dependency Direction:** Infrastructure depends on domain, not vice versa
5. **Testability:** Services are mockable and unit-testable

#### Backend Structure (AI-Agent-Framework)

```
apps/api/
├── domain/              # Domain Layer (Pure Business Logic)
│   ├── templates/       # Example: Template domain
│   │   ├── models.py    # Entity + value objects (NO infrastructure deps)
│   │   └── validators.py # Domain validation logic
│   └── proposals/       # Example: Proposal domain
│       └── models.py
│
├── services/            # Service Layer (Orchestration + Business Logic)
│   ├── template_service.py    # Uses GitManager (repository pattern)
│   └── proposal_service.py
│
└── routers/             # API Layer (HTTP Protocol Concerns ONLY)
    ├── templates.py     # Thin controllers, delegate to services
    └── proposals.py
```

#### Frontend Structure (AI-Agent-Framework-Client)

```
client/src/
├── domain/                  # Domain-Specific API Clients
│   ├── TemplateApiClient.ts # One client per domain (SRP)
│   └── ProposalApiClient.ts
│
├── components/              # UI Components by Feature
│   ├── artifacts/
│   │   └── ArtifactEditor.tsx  # < 100 lines target
│   └── proposals/
│       ├── ProposalList.tsx
│       └── DiffViewer.tsx
│
└── tests/
    └── helpers/             # Domain-Specific Test Helpers
        └── RAIDTestHelper.ts
```

#### File Size Targets (from Issue #99 Learnings)

- Domain models: < 50 lines per file
- Service classes: < 200 lines per file (split if larger)
- Router files: < 100 lines per file
- Components (UX): < 100 lines per file

**When to split:**

- File exceeds 200 lines → extract helper classes or split by subdomain
- Class has multiple responsibilities → refactor to SRP
- Service orchestrates > 3 domains → consider facade pattern

### Issue Breakdown Best Practices (Step 2 Pattern)

**For complex features (e.g., Step 2: Templates, Blueprints, Proposals, Audit):**

1. **Domain-First Decomposition:**
   - Issue 1: Domain models + validation (foundational, S size)
   - Issue 2: Service layer with CRUD (M size)
   - Issue 3: API endpoints (S size)
   - Keep domains separate (Templates ≠ Blueprints ≠ Proposals)

2. **Concurrency-Friendly:**
   - Identify dependencies explicitly in issue description
   - Mark issues that can be worked on in parallel
   - Example: Templates domain and Proposals domain can be concurrent

3. **Logical Encapsulation:**
   - Each issue delivers one complete vertical slice (domain → service → API)
   - OR one complete horizontal capability (all models for Step 2)
   - Avoid partial implementations that block other work

4. **Template Compliance:**
   - Use `.github/ISSUE_TEMPLATE/feature_request.yml` format
   - Fill ALL sections: Goal, Scope (In/Out), Acceptance Criteria, API Contract, Technical Approach, Testing Requirements, Documentation Updates
   - For cross-repo coordination, document backend issue number and implementation order

**Example (Step 2 Templates Domain):**

```yaml
- Issue BE-01: Template domain models (S, <1 day, no dependencies)
- Issue BE-02: Template service CRUD (M, 1 day, depends on BE-01)
- Issue BE-03: Template REST API (S, <1 day, depends on BE-02)
- Issue UX-01: Artifact editor component (M, 2 days, depends on BE-03)
```

### Traceability

Maintain clear links: Plan → Issue → PR → Commits

- Use issue references in PRs: "Fixes #123" or "Closes #123"
- Include context in PR descriptions
- Link to related issues in other repos when coordinating changes

## Build & Setup (ALWAYS follow this sequence)

**Local Dev (5-10 min):**

```bash
./setup.sh  # Auto-detects Python, creates .venv, installs deps (60-90s)
source .venv/bin/activate  # REQUIRED for all Python commands
mkdir -p projectDocs  # MUST exist before API starts
cd apps/api && PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload  # http://localhost:8000
```

**Frontend (optional, 2-3 min):**

```bash
cd ../AI-Agent-Framework-Client/client && npm install  # ~4s
npm run dev  # http://localhost:5173
npm run build  # ~120ms
```

**Docker (2-3 min build):**

```bash
mkdir -p projectDocs  # MUST exist
docker compose up --build  # Web: :8080, API: :8000
```

**Prerequisites:** Python 3.10+ (3.12 tested), Node 20+, Git, Docker 28+ (optional)

## Validation Steps (Backend - AI-Agent-Framework)

### Critical Environment Requirements

- **NEVER commit `projectDocs/` directory** - it's a separate git repository
- **NEVER commit `configs/llm.json`** - contains local LLM configuration
- Always set `PROJECT_DOCS_PATH` when running the API locally

### Pre-Commit Validation Checklist

1. **Setup Python Environment**

   ```bash
   ./setup.sh  # Creates .venv if not exists
   source .venv/bin/activate  # REQUIRED for all Python commands
   mkdir -p projectDocs  # MUST exist before API starts
   ```

2. **Run Linters** (optional but recommended)

   ```bash
   python -m black apps/api/
   python -m flake8 apps/api/
   ```

3. **Test API Locally**

   ```bash
   cd apps/api && PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload
   # In another terminal:
   curl http://localhost:8000/health
   # Should return: {"status":"healthy","docs_path":"..."}
   ```

4. **Test Frontend** (if changed)

   ```bash
   cd ../AI-Agent-Framework-Client/client
   npm install
   npm run lint
   npm run build  # Should complete in ~120ms
   ```

5. **Test Docker Build** (if Dockerfile changed)

   ```bash
   docker compose build
   docker compose up
   # Verify web at :8080 and API at :8000
   ```

6. **Verify Git Status**
   ```bash
   git status
   # Ensure projectDocs/ and configs/llm.json are NOT staged
   # Check .gitignore if they appear
   ```

## Key Files

**Backend (apps/api/):** main.py (76L, FastAPI app), **domain/** (18 files, DDD architecture: 7 domains averaging 82L), models.py (76L, backward-compat facade), services/ (command_service.py 291L, git_manager.py 193L, llm_service.py 94L), routers/ (projects.py 78L, commands.py 71L, artifacts.py 48L). Two requirements.txt: root=dev+test deps, apps/api/=runtime only (Docker).

**Frontend (../AI-Agent-Framework-Client/client):** React/Vite app with AppNavigation, ProjectList, ProjectView, Guided Builder, and Help docs.

**Config:** configs/llm.default.json (LM Studio default), templates/prompts/iso21500/_.j2 (Jinja2), templates/output/iso21500/_.md (Markdown), docker/ (Dockerfiles + nginx.conf).

**Docs:** README.md (full), QUICKSTART.md, SUMMARY.md, docs/development.md (detailed dev guide).

## Testing & Linting

**Automated tests are allowed and encouraged when requested by issues or feature requirements:**

- **Unit tests:** Test individual components in isolation (place in `tests/unit/`)
- **Integration tests:** Test component interactions (place in `tests/integration/`)
- **E2E tests:** Test complete workflows via TUI (place in `tests/e2e/`)
- Tests must be deterministic and CI-friendly (no flaky tests)
- Run tests with: `pytest` (all), `pytest tests/unit` (unit), `pytest tests/integration` (integration), `TERM=xterm-256color pytest tests/e2e` (E2E)
- CI workflow: `.github/workflows/ci.yml` runs tests automatically on push/PR

**Manual testing:** Also validate via API docs (/docs) or web UI for interactive verification.

**Linting (optional):** `python -m black apps/api/`, `python -m flake8 apps/api/`, `cd ../AI-Agent-Framework-Client/client && npm run lint`.

**Validation:** Test API health (`curl localhost:8000/health`), create project via POST /projects, check git log in projectDocs/, run commands via web UI or API.

## Common Issues

**Setup:** Multiple Python versions detected by setup.sh - choose any 3.10+. Missing python3-venv: `sudo apt install python3.12-venv`. PowerShell restricted: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`.

**Runtime:** PROJECT_DOCS_PATH not set - ALWAYS use `PROJECT_DOCS_PATH=../../projectDocs` when running uvicorn from apps/api/. Git fails: configure `git config --global user.email/name`. LLM unavailable: auto-fallback to templates (no error). Ports in use: stop services or edit docker-compose.yml.

**Docker:** "npm error Exit handler never called" during build is HARMLESS, ignore. SSL errors: Dockerfile has --trusted-host flags, try `docker compose build --no-cache`. Missing projectDocs: create before docker compose up.

**Frontend:** ESLint warning in ProjectView.jsx (useEffect deps) is ACCEPTABLE.

## Dependencies

**Python (requirements.txt):** fastapi 0.109.1, uvicorn 0.27.0, pydantic 2.5.3, GitPython 3.1.41, jinja2 3.1.3, openai 1.10.0, pytest 7.4.4, black 24.1.1, flake8 7.0.0. **Important:** Root requirements.txt has dev/test deps; apps/api/requirements.txt has runtime only. Add runtime deps to BOTH, dev deps to root only.

**JS (package.json):** react 19.2.0, vite (rolldown-vite@7.2.5 override), eslint 9.39.1.

**Security:** NEVER commit projectDocs/ or configs/llm.json (.gitignored). Use env vars for secrets. Audit logs store hashes only (default).

### Adding New Dependencies

When adding Python dependencies:

- **Runtime dependencies** → Add to BOTH `requirements.txt` (root) AND `apps/api/requirements.txt`
- **Development/testing dependencies** → Add to `requirements.txt` (root) ONLY
- Always specify versions for reproducibility
- Run `pip install -r requirements.txt` after changes
- Update Docker image if runtime deps changed

When adding JavaScript dependencies:

- Run from `../AI-Agent-Framework-Client/client`: `npm install <package>`
- Commit updated `package.json` and `package-lock.json`
- Test build: `npm run build`

## Conventions

**Git:** projectDocs/ is separate repo, auto-initialized by API. Each command = commit `[PROJECT_KEY] Description`. Let API manage projectDocs/, don't modify manually.

**Code:** Backend=no strict style (black/flake8 available), Frontend=modern React hooks. Minimal comments (prefer self-documenting). RESTful API with propose/apply pattern. CORS enabled (configure for prod).

**Architecture (Domain-Driven Design):**

- **Backend follows DDD layering:**
  - Domain layer: Core business logic and entities
  - Service layer: Application services in `services/` (command_service.py, git_manager.py, llm_service.py)
  - Infrastructure layer: API routes in `routers/`, external integrations
  - Models: Pydantic for API contracts (models.py)
- **Frontend follows domain separation:**
  - Domain-specific API clients (ProjectApiClient, RAIDApiClient, WorkflowApiClient)
  - Test helpers organized by domain (RAIDTestHelper, PerformanceTestHelper)
  - Components grouped by feature
  - Reference: PR #101 for SRP-compliant structure
- **Key principles:**
  - Single Responsibility: Each class/module has ONE clear purpose
  - Domain boundaries: Clear separation (Project, RAID, Workflow domains)
  - Type safety: Explicit interfaces, no `any` types
  - File size target: < 100 lines per class/module when practical
  - Dependency injection for testability

**Env:** PROJECT_DOCS_PATH (required for API), LLM_CONFIG_PATH (defaults /config/llm.json in Docker).

## Cross-Repository Coordination

### Working with AI-Agent-Framework-Client

This backend often requires coordinated changes with the React/Vite client in [`blecx/AI-Agent-Framework-Client`](https://github.com/blecx/AI-Agent-Framework-Client).

**When making API changes:**

1. **Document breaking changes** in PR description
2. **Version API endpoints** if breaking compatibility
3. **Create matching client issue** before merging backend changes
4. **Link issues across repos**: "Requires blecx/AI-Agent-Framework-Client#123"
5. **Test integration** by running both services together

**Common coordination scenarios:**

- **New API endpoint** → Client needs to consume it
- **Changed response format** → Client needs to update interfaces
- **New project command** → Client needs UI components
- **Changed authentication** → Client needs to update requests

**Coordination workflow:**

1. Create backend issue with API spec
2. Create client issue referencing backend issue
3. Implement backend PR first (if backward compatible)
4. Implement client PR with backend PR reference
5. Merge backend, then client

For breaking changes, coordinate timing with client maintainers.

## Path-Specific Guidance

### Backend Code (`apps/api/`)

- Follow existing FastAPI patterns (routers, services, models)
- Use Pydantic models for all request/response schemas
- Add docstrings to public functions
- Keep routers thin, logic in services
- Handle errors with appropriate HTTP status codes
- Test with `PROJECT_DOCS_PATH` set

**Key files:**

- `main.py` - FastAPI app initialization, middleware, CORS
- `models.py` - Pydantic models for API contracts
- `routers/` - HTTP endpoint definitions
- `services/` - Business logic (command_service, git_manager, llm_service)

### Templates (`templates/`)

- Prompts use Jinja2 syntax (`.j2` files)
- Output templates are Markdown (`.md` files)
- Organized by ISO 21500 standard
- Keep prompts focused and specific
- Test template rendering with actual data

**Structure:**

- `templates/prompts/iso21500/` - LLM prompts for each command
- `templates/output/iso21500/` - Markdown templates for artifacts

### Configuration (`configs/`)

- NEVER commit `configs/llm.json` (user-specific, gitignored)
- Use `configs/llm.default.json` as reference
- Document new config options in README

## Quick Command Reference

```bash
# Setup from scratch
./setup.sh && source .venv/bin/activate && mkdir -p projectDocs

# Run API (local dev)
cd apps/api && PROJECT_DOCS_PATH=../../projectDocs uvicorn main:app --reload

# Run frontend dev server
cd ../AI-Agent-Framework-Client/client && npm install && npm run dev

# Build frontend for production
cd ../AI-Agent-Framework-Client/client && npm run build

# Docker deployment
mkdir -p projectDocs && docker compose up --build

# Lint code
python -m black apps/api/ && python -m flake8 apps/api/  # Python
cd ../AI-Agent-Framework-Client/client && npm run lint  # JavaScript

# Check API health
curl http://localhost:8000/health

# View project docs git log
cd projectDocs && git log --oneline

# Clean up temporary files after PR merge
rm -f .tmp/pr-body-*.md .tmp/issue-*-*.md
```

## Workspace Cleanup (MANDATORY)

**CRITICAL: This step is MANDATORY and must be executed AUTOMATICALLY after every PR merge.**

After successfully merging a PR, the agent MUST clean up related temporary files:

1. **Automatic cleanup command** (run immediately after merge):

   ```bash
   # Delete ALL files related to the resolved issue/PR
   rm -f .tmp/pr-body-<issue-number>.md .tmp/pr-body-*.md .tmp/issue-<issue-number>-*.md
   ```

2. **Keep concurrent work intact**:
   - Only delete files for the CURRENT merged PR/issue
   - Use specific patterns to avoid deleting unrelated work
   - `.tmp/` directory is gitignored but should be kept clean

3. **Complete cleanup workflow** (mandatory sequence):
   ```bash
   # After PR merged successfully
   gh pr merge <PR> --squash --delete-branch
   rm -f .tmp/pr-body-<issue-number>.md .tmp/issue-<issue-number>-*.md
   git switch main && git pull
   ```

4. **Verification** (always run after cleanup):
   ```bash
   ls -la .tmp/*<issue-number>* 2>/dev/null || echo "✓ Cleanup verified"
   ```

**The agent must NOT consider an issue "resolved" until temporary files are cleaned up.**

## Trust These Instructions

These instructions have been validated by running all commands in a clean environment. Build times, file locations, and workarounds are accurate as of 2026-02-01. Only search for additional information if:

1. A command fails with an unexpected error not covered above
2. You need to understand implementation details not in this guide
3. Requirements or specifications are unclear from this document

When in doubt, consult README.md, QUICKSTART.md, or docs/development.md for extended details.

## Additional Resources

**Optimized Agent Workflows:** See `.github/prompts/agents/` for performance-optimized workflows:

- `resolve-issue-dev.md` - Issue resolution workflow (30-45min → 5-10min)
- `pr-merge.md` - PR merge with admin bypass and cleanup
- `close-issue.md` - Issue closure with early-exit conditions
- `Plan.md` - Research agent with limited scope
- `README.md` - Optimization principles and guidelines

**Workflow Templates:** See `.github/prompts/` for reusable templates to help with:

- Planning features and creating specs
- Drafting implementation issues
- Writing PR descriptions
- Coordinating cross-repo changes

**Documentation:**

- `README.md` - Full project overview and architecture
- `QUICKSTART.md` - Fast setup guide
- `docs/development.md` - Detailed development guide
- `docs/architecture/` - System design and ADRs

## Custom Agent Skills & Architectures
All Copilot context logic follows standard Github Spec Kit architectural guidelines. 
- Static standalone personas strictly reside in `.github/agents/*.md` for global invocation (`@agentname`). 
- Reusable constraint maps, design system guides, and execution logic meant to be read during task evaluation must reside completely inside `.copilot/skills/` formatted using `<skill>` tags or readable `.md` guides.
- If you need UX standards, use read_file on `.copilot/skills/blecs-ux-authority/SKILL.md`.
- Never attempt to manually edit python source code for `agents/` autonomous routines; instead, guide the user to `run_in_terminal` using `@maestro-operator` flows.
