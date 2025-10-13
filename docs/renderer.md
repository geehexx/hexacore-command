# Hexa-Core Renderer Overview

## Metadata

| Key | Value |
| --- | --- |
| Topic | Arcade Renderer State Machine |
| Keywords | renderer, state machine, main menu, mission briefing, gameplay layout |
| Related ADRs | [ADR-0002](./decisions/0002-implement-ecs-pattern.md), [ADR-0003](./decisions/0003-implement-event-bus.md) |
| Key Libraries | [Arcade](https://api.arcade.academy/en/latest/) |

## Overview

The renderer provides Arcade-facing presentation for Hexa-Core Command while honoring the engine
encapsulation rules. The current implementation spans the pre-game flows (main menu and mission
briefing) and now exposes deterministic gameplay layout models that downstream Arcade wiring can
consume.

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

## Implementation Details

- The menu state machine lives in `src/hexa_core/renderer/renderer.py` within `HexaRenderer`.
  - `select_menu_option()` validates enabled actions, toggles `should_exit` for the Exit path, and
    transitions to `MISSION_BRIEFING` when starting a new game.
  - `load_mission_briefing()` normalizes level metadata into `MissionBriefingView`, updating state
    while preserving determinism for tests.
  - `proceed_to_gameplay()` now assembles a `GameplayView` from the active `MissionBriefingView`,
    stores it on `gameplay_view`, clears briefing state, and shifts the renderer into `GAMEPLAY`.
- The renderer remains Arcade-agnostic; UI structures are pure dataclasses, facilitating spec-kit
  tests (`tests/spec/test_renderer_spec.py`) that drive incremental feature delivery under TDD.
  - New specs assert objective wrapping, preview metadata, interaction cue formatting, gameplay
    transition behavior, and default gameplay layout construction to guard regressions across UI
    stages.

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
