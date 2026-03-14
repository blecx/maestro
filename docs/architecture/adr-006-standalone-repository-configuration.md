# ADR-006: Standalone Repository Configuration and Bootstrapping

**Status:** Accepted

**Context:** Historically, scripts and Docker configurations relied on legacy mappings that traversed outside the project root to integrate with external parent projects. This external dependency violates the principle of self-containment, blocking drop-in deployments and creating fragile local development environments.

**Decision:** Maestro will adopt a 100% self-referential initialization sequence. Environment variables dictating project scope will default strictly to the active git repository context (traversing `.`) rather than hardcoded parental string traversals.

**Consequences:**
- Requires writing test-fixtures and configuration files that map internally to localized mocked project directories or robust default environments, completely avoiding `../` parental lookups.
- Guarantees immediate out-of-the-box working states for any new developer cloning the repository, reinforcing modern microservice best practices for repository decoupling.
