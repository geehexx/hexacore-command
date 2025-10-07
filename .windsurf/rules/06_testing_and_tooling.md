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

* **Mandate:** All game logic in `src/hexa_core/engine/` MUST be developed via a strict TDD workflow using `spec-kit`. See [spec-kit documentation](https://github.com/github/spec-kit).

## 6.3 Code Quality & Automation

* **Tooling:** `Ruff`, `MyPy`, and `markdownlint` are the standard for quality, enforced by `pre-commit` hooks.
* **Automation:** Use the Taskfile targets to execute repeatable workflows:
  * `task lint:all` runs Ruff, MyPy, and PyMarkdown in sequence.
  * `task test:unit` runs the full pytest suite.
  * `task ci:check` chains linting and unit tests for CI validation.
  * `task ci:benchmarks` runs the benchmark suite when performance validation is required.

## 6.4 Performance & Benchmarking

* **Mandate:** A performance-first mindset must be maintained.
* **Strategy:** The project's performance strategy is defined in ADR-0005.
* **Requirement:** Performance-sensitive systems (e.g., pathfinding, ECS processing) MUST be benchmarked using `pytest-benchmark`.
