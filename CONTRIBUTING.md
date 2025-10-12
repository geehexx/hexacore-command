# Contributing to Hexa-Core Command

## Required Workflow

All feature work is orchestrated through the `/develop-feature` workflow. This command guides you through four phases:

1. Planning and contextual analysis
2. Implementation with in-line quality checks
3. Automated validation (lint, tests, coverage, security)
4. Finalization and version control

Follow each phase sequentially and only advance once the prior phase is complete. For architectural changes, invoke `/propose-new-adr` before editing `.windsurf/rules/`.

## Quality Gates

Every contribution must satisfy the following checks before it is considered complete:

- **Linting:** `task lint:all`
- **Unit tests:** `task test:unit`
- **Coverage (≥85 % for touched code):** `task coverage:report`
- **Security scan:** `task security:audit`

Rerun a task until it exits cleanly. Address all failures immediately—do not leave known lint, test, coverage, or security issues unresolved.

## Development Environment

- Work inside the provided dev container to ensure parity across contributors.
- Manage dependencies exclusively with `uv`. The authoritative dependency definitions are `pyproject.toml` and `requirements-dev.txt`.
- Adhere to the Windsurf constitutional rules in `.windsurf/rules/` and consult ADR-0005 when performance constraints apply.

## Documentation Lifecycle

Keep living documents synchronized with code changes. After implementing a feature, update any relevant documentation (architecture records, rules, README) and, when necessary, use `/update-living-documentation` to drive the process.
