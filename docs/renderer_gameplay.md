# Gameplay Renderer Architecture

## Overview

The gameplay renderer binds the deterministic layout models in `src/hexa_core/renderer/renderer.py`
with Arcade runtime primitives. The architecture preserves a strict separation between pure data
models (used by spec-kit) and the imperative Arcade event loop required for interactive scenes.

## Components

- `HexaRenderer`
  - Pure state machine that produces `MainMenuView`, `MissionBriefingView`, and `GameplayView`
    dataclasses.
  - Consumes map payloads supplied through the event bus to populate mission metadata and gameplay
    scaffolding.
- `RendererApp`
  - Arcade bootstrap located at `src/hexa_core/renderer/app.py`.
  - Creates the window, registers event bus subscriptions, and reconciles the active `RendererState`
    into an Arcade `View` implementation.
  - Exposes `create_renderer_app()` and `main()` for Taskfile/CLI integration.
- `arcade_views`
  - Adapter layer in `src/hexa_core/renderer/arcade_views.py` that translates pure dataclasses into
    Arcade-compatible `View` subclasses (`MainMenuScreen`, `MissionBriefingScreen`, `GameplayScreen`).
  - Provides callbacks that publish renderer events (`MISSION_ACCEPTED`, `GAMEPLAY_EXITED`, etc.) via
    the shared `EventBus`.
- `events`
  - Centralizes renderer event channel identifiers in `src/hexa_core/renderer/events.py` to keep the
    bus contract explicit and discoverable.

## Event Flow

```mermaid
direction LR
engine((Engine)) -->|publishes| missionRequested[renderer.mission_briefing.requested]
missionRequested --> rendererApp[RendererApp]
rendererApp --> HexaRenderer
HexaRenderer --> briefingView[MissionBriefingView]
briefingView --> missionScreen[MissionBriefingScreen]
missionScreen -->|accept| missionAccepted[renderer.mission_briefing.accepted]
missionAccepted --> engine
missionScreen -->|decline| missionDeclined[renderer.mission_briefing.declined]
missionDeclined --> engine
gameplayActivated[renderer.gameplay.activated] --> rendererApp
rendererApp --> gameplayScreen[GameplayScreen]
gameplayScreen -->|exit| gameplayExited[renderer.gameplay.exited]
gameplayExited --> engine
```

## Testing Strategy

- Spec-kit coverage keeps `HexaRenderer` pure and deterministic (`tests/spec/test_renderer_spec.py`).
- Launcher behavior, event wiring, and view reconciliation are validated in
  `tests/spec/test_renderer_app_spec.py` using stubbed Arcade primitives.
- Additional runtime validation can be layered via integration or BDD tests once engine-driven
  missions are available.

## Usage

Run the renderer inside the dev container with:

```bash
uv run python -m hexa_core.renderer.app
```

or leverage the Taskfile shortcut:

```bash
task game:run
```

Both commands create the Arcade window, subscribe to renderer events, and transition through the
main menu, mission briefing, and gameplay layout scaffolding.
