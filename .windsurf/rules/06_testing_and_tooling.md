---
trigger: glob
description: "Enforces TDD, code quality, and a standardized development environment."
globs: tests/**/*.py, src/**/*.py, *.md, *.toml, *.yaml, *.json
---

# Rule: Testing, Tooling, and Development Environment

## 6.1 Development Environment

* **Standardization:** All development MUST occur within the provided Dev Container. This ensures a consistent environment for all contributors.
* **Dependency Management:** `uv` is the mandatory package manager. The `pyproject.toml` and `requirements-dev.txt` files are the sources of truth.

## 6.2 Test-Driven Development (TDD)

* **Mandate:** All game logic in `src/hexa_core/engine/` MUST be developed via a strict TDD workflow using [`spec-kit`](https://github.com/github/spec-kit). See [spec-kit documentation](https://github.com/github/spec-kit).

## 6.3 Code Quality & Automation

* **Tooling:** `Ruff`, `MyPy`, and `markdownlint` are the standard for quality, enforced by `pre-commit` hooks.
* **Automation:** Use the Taskfile targets to execute repeatable workflows:
  * `task lint:all` runs Ruff, MyPy, and PyMarkdown in sequence.
  * `task test:unit` runs the full pytest suite.
  * `task ci:check` chains linting and unit tests for CI validation.
  * `task ci:benchmarks` runs the benchmark suite when performance validation is required.
* **Self-Validation:** Contributors MUST execute the relevant Taskfile targets locally (tests, benchmarks, or linting) before delivering checkpoints or status summaries.

## 6.4 Performance & Benchmarking

* **Mandate:** A performance-first mindset must be maintained.
* **Strategy:** The project's performance strategy is defined in ADR-0005.
* **Requirement:** Performance-sensitive systems (e.g., pathfinding, ECS processing) MUST be benchmarked using `pytest-codspeed`.

## 6.5 Network Intelligence & Source Validation

* **Authoritative Sources:** Agents MUST proactively invoke `functions.*_fetch` when authoritative vendor documentation, standards, or specifications are required.
* **Validation:** When relying on non-authoritative material retrieved via `functions.*_fetch`, agents MUST cross-reference or run internal experiments to confirm accuracy and report verification status in checkpoints or summaries.
* **Traceability:** Each fetch call MUST include its rationale in checkpoints and summaries so reviewers can track decision inputs.
* **Tool Prefixes:** MCP server prefixes may change; always select tooling by capability suffix (e.g., `*_fetch`) and confirm parameters against the active environment.

## 6.6 Methodical Editing Workflow

* **Preflight Checks:** Before applying diffs, confirm the target file and directory exist via directory listings or file reads. Create missing parents with `mcp1_create_directory` to avoid repeated failures.
* **Create When Missing:** If a file or directory is absent, create it explicitly with the appropriate tool (e.g., `mcp1_write_file`, `mcp1_create_directory`) before diffing.
* **Diff Discipline:** Limit `apply_patch` to verified paths and avoid replacing entire files when scoped edits suffice.
* **Tool Selection:** Follow `docs/tooling/editing-tools.md` when choosing between Windsurf editing commands and MCP filesystem tools. Switch to MCP editors whenever context diverges or path protections block direct diffs.
* **Post-Edit Validation:** Immediately rerun the relevant lint or test command after modifications to ensure no regressions were introduced.

## 6.7 Git Operations via MCP

* **Primary Interfaces:** All status, diff, staging, and commit actions MUST be executed through MCP Git tools (`mcp2_git_status`, `mcp2_git_diff_unstaged`, `mcp2_git_diff_staged`, `mcp2_git_add`, `mcp2_git_commit`). Direct CLI commands are reserved for exceptional cases when the MCP interface is unavailable, and the reason MUST be documented.
* **Status Discipline:** Run `mcp2_git_status` before and after significant edits to maintain awareness of the working tree and to capture checkpoints for status summaries.
* **Diff Review:** Inspect changes with `mcp2_git_diff_unstaged` and `mcp2_git_diff_staged`, adjusting context as needed to understand every modification.

## 6.8 Ownership Verification & Generated Artifacts

* **Ownership Check:** Before staging, confirm via MCP diffs that every change was introduced by the current task. If unrelated work is detected, resolve it (split commits, revert, or document blockers) before proceeding.
* **Generated Outputs:** When deleting or cleaning generated artifacts (e.g., `.hypothesis/`), add the path to `.gitignore` or document why it must remain tracked. Avoid removing files you cannot confidently recreate.
* **Commit Readiness:** Only stage files once ownership and ignore rules are validated, then confirm the staged snapshot with `mcp2_git_diff_staged` prior to committing.
