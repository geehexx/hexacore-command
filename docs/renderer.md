# Hexa-Core Renderer Overview

## Metadata

| Key | Value |
| --- | --- |
| Topic | Arcade Renderer State Machine |
| Keywords | renderer, state machine, mission briefing, gameplay layout, arcade views |
| Related ADRs | [ADR-0002](./decisions/0002-implement-ecs-pattern.md), [ADR-0003](./decisions/0003-implement-event-bus.md) |
| Key Libraries | [Arcade](https://api.arcade.academy/en/latest/) |

## Overview

The renderer provides Arcade-facing presentation for Hexa-Core Command while honoring the engine
encapsulation rules. The current implementation includes the Arcade launcher, state-driven view
adapters, pre-game flows (main menu and mission briefing), and deterministic gameplay layout models
that downstream Arcade wiring can consume.

## Core Concepts

- RendererState
  - Enumerates the high-level UI stages (`MAIN_MENU`, `MISSION_BRIEFING`, `GAMEPLAY`).
  - Ensures event handlers and draw routines are scoped to the active context.
- MainMenuView and MenuOption
  - Immutable data structures describing the main menu layout, option labeling, and enablement.
  - Supports deterministic testing by exposing the menu model without Arcade dependencies.
- MissionBriefingView and companion dataclasses
  - Capture mission metadata: objectives, grid dimensions, optional map preview imagery, and
    interaction cues loaded from map payloads.
  - Provide deterministic helpers:
    - `objective_lines` for numbered bullet output.
    - `objective_blocks(max_width)` for line-wrapped text blocks (`ObjectiveBlock`).
    - `grid_summary` for concise layout data.
    - `map_preview` (`MapPreviewInfo`) and `interaction_cues` (`InteractionCues`) surface
      renderer-agnostic metadata for UI widgets.
- GameplayView and layout dataclasses (`GridPanelView`, `ScriptEditorView`, `BotStatusPanel`,
  `ControlButton`)
  - Model the baseline gameplay UI surface: grid preview metadata, Hexa-Script editor
    configuration, bot status entries, and core control buttons.
  - Remain pure data with no Arcade dependencies, enabling spec-kit coverage while UI rendering is
    still forthcoming.
- RendererApp and Arcade view adapters
  - `create_renderer_app()` constructs a windowed Arcade runtime that hosts the `HexaRenderer`
    state machine and event bus wiring.
  - View adapters in `src/hexa_core/renderer/arcade_views.py` convert pure dataclasses into
    `arcade.View` subclasses for menu, briefing, and gameplay scenes.
  - `src/hexa_core/renderer/events.py` centralizes renderer event channel names used by the
    engine event bus to coordinate state transitions.

## Implementation Details

- The menu state machine lives in `src/hexa_core/renderer/renderer.py` within `HexaRenderer`.
  - `select_menu_option()` validates enabled actions, toggles `should_exit` for the Exit path, and
    transitions to `MISSION_BRIEFING` when starting a new game.
  - `load_mission_briefing()` normalizes level metadata into `MissionBriefingView`, updating state
    while preserving determinism for tests.
  - `proceed_to_gameplay()` now assembles a `GameplayView` from the active `MissionBriefingView`,
    stores it on `gameplay_view`, clears briefing state, and shifts the renderer into `GAMEPLAY`.
- `src/hexa_core/renderer/app.py` wraps the renderer state machine with the Arcade runtime,
  registers event bus handlers, and exposes a `main()` entrypoint for Taskfile and `python -m`
  execution.
- Renderer views remain Arcade-agnostic in tests thanks to the adapter pattern. Specs cover
  both the pure state machine (`tests/spec/test_renderer_spec.py`) and the launcher/event wiring
  (`tests/spec/test_renderer_app_spec.py`).

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
