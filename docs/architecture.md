# Hexa-Core Command Architecture

## Metadata

| Key | Value |
| --- | --- |
| Topic | Hexa-Core Command engine and renderer architecture |
| Keywords | ECS, EventBus, Renderer, Deterministic Engine |
| Related ADRs | [ADR-0002](decisions/0002-implement-ecs-pattern.md), [ADR-0003](decisions/0003-implement-event-bus.md) |
| Key Libraries | [`esper`](https://esper.readthedocs.io/), [`Arcade`](https://api.arcade.academy) |

## Overview

Hexa-Core Command separates deterministic simulation from presentation. The engine layer owns all game state and exposes events, while the renderer subscribes and visualizes without mutating core logic.

## Core Concepts

Engine Layer
:   Implements the Entity-Component-System (ECS) pattern using [`esper`](https://esper.readthedocs.io/). Systems advance game state, and components store immutable data.

Renderer Layer
:   Listens to engine events through the `EventBus` abstraction and renders via the [`Arcade`](https://api.arcade.academy) library while remaining stateless.

EventBus
:   Provides publish/subscribe isolation so engine logic never references renderer code directly, enabling pure simulation and testability.

## Implementation Details

* The engine communicates outward exclusively through the `EventBus`, emitting notifications for renderer consumption.
* Core datatypes such as `HexCoord` and the shared `Component` base live in `src/hexa_core/engine` for reuse across systems.
* Asset manifests, scripting, and system orchestration remain deterministic to keep the engine CI-friendly.

## Code Examples

```python
from hexa_core.engine.datatypes import HexCoord

origin = HexCoord(0, 0)
neighbors = origin.neighbors()
```

Use definition lists to introduce new terminology, ensuring the first mention of any external tool links to authoritative documentation.
