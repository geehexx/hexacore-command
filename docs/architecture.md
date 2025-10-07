# Hexa-Core Command Architecture

The architecture centers on a deterministic game engine and a decoupled renderer.

## Engine Layer (`src/hexa_core/engine`)

* Implements the Entity-Component-System (ECS) pattern using `esper`.
* Maintains all deterministic game state and logic.
* Communicates outward exclusively through the `EventBus`.
* Exposes core datatypes such as `HexCoord` for hex-grid math and a reusable `Component` base mixin for ECS data classes.

## Renderer Layer (`src/hexa_core/renderer`)

* Subscribes to engine events and renders via the Arcade library.
* Holds no authority over engine state.

## Supporting Systems

* **Scripting:** Custom Hexa-Script language executed by the `ScriptRunner`.
* **Assets:** Data-driven manifests describe maps, sprites, and sounds.
* **Tooling:** TDD with `spec-kit`, code quality gates via `ruff`, `mypy`, and `markdownlint`.
