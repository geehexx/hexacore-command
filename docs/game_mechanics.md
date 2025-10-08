# Game Mechanics Overview

## Metadata

| Key | Value |
| --- | --- |
| Topic | Core gameplay loop and mechanics |
| Keywords | Turn Manager, Initiative, Combat, Hexa-Script |
| Related ADRs | [ADR-0003](decisions/0003-implement-event-bus.md), [ADR-0004](decisions/0004-implement-custom-scripting-language.md) |
| Key Libraries | [`esper`](https://esper.readthedocs.io/) |

## Overview

The MVP simulates autonomous bots executing Hexa-Script programs across a hexagonal battlefield. Turns advance deterministically so that simulation outcomes remain reproducible for testing and replay.

## Core Concepts

Turn Structure
:   The `TurnManager` system increments initiative per entity until the configured `ACTION_THRESHOLD` is reached, at which point the entity resolves queued actions.

Combat & Movement
:   Movement and combat systems operate over ECS components, emitting events that the renderer consumes through the `EventBus`.

Scripts
:   Hexa-Script programs, interpreted by the `ScriptRunner`, govern bot decisions by issuing deterministic commands.

## Implementation Details

* Processor tokens throttle script execution to balance simultaneous entities.
* Combat outcomes are recorded as engine events, enabling pluggable renderers or AI spectators.
* Hex-grid math relies on shared datatypes such as `HexCoord` for distance and adjacency calculations.

## Code Examples

```python
from hexa_core.engine.datatypes import HexCoord

def within_strike_range(origin: HexCoord, target: HexCoord) -> bool:
    return origin.distance_to(target) <= 1
```

Definition lists highlight mechanics terminology while keeping references close to the concepts they describe.
