---
trigger: glob
description: "Defines core architectural patterns. See docs/architecture.md and relevant ADRs."
globs: src/hexa_core/**/*.py
---

# Rule: Architectural Principles

## 1.1 Entity-Component-System (ECS)

The project MUST use `esper` ([https://github.com/benmoran56/esper](https://github.com/benmoran56/esper)) for game state management.

* **Components:** Are pure data classes in `engine/components.py`.
* **Systems:** Contain all logic and operate on entities. Located in `engine/systems/`.

## 1.2 Event Bus

A simple pub/sub `EventBus` in `engine/event_bus.py` is the ONLY mechanism for the engine to communicate outwards. Engine systems publish events; the renderer subscribes.

## 1.3 Strict Decoupling

* The **Engine (`src/hexa_core/engine`)** MUST NOT contain any code related to graphics, sound, or user input (`import arcade` is forbidden).
* The **Renderer (`src/hexa_core/renderer`)** MUST NOT directly modify the ECS `World` state.
