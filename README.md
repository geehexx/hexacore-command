# Hexa-Core Command

*A turn-based tactical bot-programming game.*

## Project Overview

This project is an exploration of AI-assisted game development. The game itself involves programming a bot with a simple, BASIC-like scripting language (`Hexa-Script`) to compete against other scripted bots on a hexagonal grid.

## Getting Started (for Developers)

This project is designed to be developed within a VS Code Dev Container.

1. Ensure you have Docker and the VS Code "Dev Containers" extension installed. The container image ships with Python 3.11 and all required tooling (including `uv`).
2. Open this project folder in VS Code.
3. When prompted, click "Reopen in Container".
4. The container will build, install all dependencies, and set up pre-commit hooks automatically.

If you prefer running locally, install Python 3.11+, [uv](https://docs.astral.sh/uv/), and execute `uv pip install .[dev]` to reproduce the development environment.

## Development Workflow

Run `/develop-feature` inside Windsurf for any end-to-end feature effort. The workflow enforces planning, implementation, validation, and finalization steps aligned with `.windsurf/rules/`.

Architectural changes must go through `/propose-new-adr` before editing constitutional documents. For documentation-only updates, `/update-living-documentation` remains available.

## Task Automation

This project standardizes developer workflows with [Task](https://taskfile.dev/). List all available targets via `task --list` or run the high-value tasks below:

- `task game:run` launches the renderer entrypoint (`python -m hexa_core.main`).
- `task test:unit` executes the full `pytest` suite.
- `task test:spec` focuses on the `spec-kit` driven scenarios in `tests/spec/`.
- `task test:benchmarks` runs the CodSpeed-backed performance suite (`pytest --codspeed`).
- `task coverage:report` enforces the ≥85 % coverage threshold with `pytest --cov`.
- `task lint:all` runs Ruff, MyPy, and PyMarkdown in sequence.
- `task security:audit` runs `pip-audit` against project dependencies.
- `task ci:check` chains `task lint:all` and `task test:unit` to mirror CI expectations.
- `task ci:benchmarks` executes the benchmark-only validation path.

These targets wrap the canonical `uv` commands to ensure consistency across agents and contributors. If a new workflow emerges, prefer adding a Taskfile entry before documenting a raw command.

Within VS Code, invoke `Terminal → Run Task… → pymarkdown: scan active file` to lint the current document.
The task surfaces findings through the Problems panel and reads the same `.pymarkdown.json` configuration used in CI.
This keeps IDE feedback aligned with automated checks.

## **Architectural Overview**

This project follows a strict set of architectural principles, enforced by Windsurf rules. Key decisions are documented in `docs/decisions`.

- **Entity-Component-System (ECS):** Game logic is built around the `esper` ECS library.
- **Logic-Renderer Separation:** The game engine (`src/hexa_core/engine`) is a pure, deterministic Python module, completely decoupled from the Arcade-based renderer (`src/hexa_core/renderer`).
- **Event Bus:** Communication from the engine to the renderer is handled via a simple publish/subscribe event bus.
