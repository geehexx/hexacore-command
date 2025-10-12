# Hexa-Core Renderer Overview

## Metadata

| Key | Value |
| --- | --- |
| Topic | Arcade Renderer State Machine |
| Keywords | renderer, state machine, mission briefing, main menu |
| Related ADRs | [ADR-0002](./decisions/0002-implement-ecs-pattern.md), [ADR-0003](./decisions/0003-implement-event-bus.md) |
| Key Libraries | [Arcade](https://api.arcade.academy/en/latest/) |

## Overview

The renderer provides Arcade-facing presentation for Hexa-Core Command while honoring the engine encapsulation rules. The current implementation focuses on pre-game flows (main menu and mission briefing) and prepares the transition into gameplay scenes.

## Core Concepts

- **RendererState**
  - Enumerates the high-level UI stages (`MAIN_MENU`, `MISSION_BRIEFING`, `GAMEPLAY`).
  - Ensures event handlers and draw routines are scoped to the active context.
- **MainMenuView** and **MenuOption**
  - Immutable data structures describing the main menu layout, option labeling, and enablement.
  - Supports deterministic testing by exposing the menu model without Arcade dependencies.
- **MissionBriefingView**
  - Captures mission metadata (title, objectives, grid dimensions) loaded from map payloads.
  - Enables future rendering of objective lists and mini-map previews without coupling to file I/O.

## Implementation Details

- The menu state machine lives in `src/hexa_core/renderer/renderer.py` within `HexaRenderer`.
  - `select_menu_option()` validates enabled actions, toggles `should_exit` for the Exit path, and transitions to `MISSION_BRIEFING` when starting a new game.
  - `load_mission_briefing()` normalizes level metadata into `MissionBriefingView`, updating state while preserving determinism for tests.
  - `proceed_to_gameplay()` clears briefing data and shifts the renderer into `GAMEPLAY`, ready for upcoming scene composition.
- The renderer remains Arcade-agnostic; UI structures are pure dataclasses, facilitating spec-kit tests (`tests/spec/test_renderer_spec.py`) that drive incremental feature delivery under TDD.

## Code Examples

```python
from hexa_core.renderer.renderer import HexaRenderer, RendererState

renderer = HexaRenderer()
renderer.select_menu_option("start_new_game")
renderer.load_mission_briefing(
    {
        "name": "Operation Dawn",
        "objectives": ["Secure landing zone", "Extract scout team"],
        "grid_size": {"width": 12, "height": 10},
    }
)
assert renderer.current_state is RendererState.MISSION_BRIEFING
```
