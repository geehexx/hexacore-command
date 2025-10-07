# Hexa-Core Command

*A turn-based tactical bot-programming game.*

## Project Overview

This project is an exploration of AI-assisted game development. The game itself involves programming a bot with a simple, BASIC-like scripting language (`Hexa-Script`) to compete against other scripted bots on a hexagonal grid.

## Getting Started (for Developers)

This project is designed to be developed within a VS Code Dev Container.

1. Ensure you have Docker and the VS Code "Dev Containers" extension installed.
2. Open this project folder in VS Code.
3. When prompted, click "Reopen in Container".
4. The container will build, install all dependencies, and set up pre-commit hooks automatically.

## Running the Game

To launch the game, run the following command from the integrated terminal:

```bash
python -m hexa_core.main
```

## **Running Tests**

To run the full test suite:

```bash
pytest
```

To run the benchmark tests:

```bash
pytest --benchmark-only
```

## **Architectural Overview**

This project follows a strict set of architectural principles, enforced by Windsurf rules. Key decisions are documented in `docs/decisions`.

* **Entity-Component-System (ECS):** Game logic is built around the `esper` ECS library.
* **Logic-Renderer Separation:** The game engine (`src/hexa_core/engine`) is a pure, deterministic Python module, completely decoupled from the Arcade-based renderer (`src/hexa_core/renderer`).
* **Event Bus:** Communication from the engine to the renderer is handled via a simple publish/subscribe event bus.
