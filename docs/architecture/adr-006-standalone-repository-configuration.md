# ADR-006: Standalone Repository Configuration and Bootstrapping

**Status:** Accepted

**Context:** Scripts and Docker configurations carry legacy mappings indicating they still belong to the broader `AI-Agent-Framework` ecosystem, blocking drop-in deployments.

**Decision:** Maestro will adopt a 100% self-referential initialization sequence. Environment variables dictating project scope will default strictly to the active git repository context traversing `.` rather than hardcoded parent strings. 

**Consequences:**
- Requires rewriting test-fixtures that point to `../AI-Agent-Framework` to instead point to localized mocked project directories. 
- Guarantees immediate out-of-the-box working states for any new developer cloning the `maestro` repo.
