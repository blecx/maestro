<skill>
<name>cross-repo-coordination-checklist</name>
<description>Neutral guidance for coordinating changes between a host repository and any documented companion repositories.</description>
<file>
# Cross-Repo Coordination Checklist

## Objective
Use this guidance when a host project adopting `softwareFactoryVscode` has one or more companion repositories that must stay in sync.

## Instructions
1. Identify whether the current change affects only the factory package, only the host repository, or both.
2. Search the impacted companion repository for matching API, schema, or workflow assumptions before shipping a breaking change.
3. Prefer backward-compatible changes first; document follow-up work for companion repos explicitly.
4. In PRs or issues, use repository-qualified references such as `Requires <owner>/<repo>#<number>`.
5. Validate each affected repository using its own documented commands rather than assuming a shared tech stack.
</file>
</skill>
