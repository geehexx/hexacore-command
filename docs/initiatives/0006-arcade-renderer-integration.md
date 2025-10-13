---
description: complete arcade renderer integration and gameplay ui
---

# Initiative 0006: Arcade Renderer Integration & Gameplay UI Delivery

* **Objective:** Deliver a playable Arcade front-end that coordinates menu, mission briefing, and gameplay scenes with the engine event bus.
* **Status:** Proposed

## Deliverables

### Renderer Runtime and Window Management

* Implement the Arcade `Window` launcher that hosts `HexaRenderer` views.
* Add an executable entry point (Taskfile target along with `python -m hexa_core.renderer.app`) to
  start the renderer inside the Dev Container.
* Ensure deterministic initialization compatible with `uv` workflows and spec-kit driven
  development.

### Mission Briefing Presentation

* Render objective text blocks and interaction cues using Arcade GUI elements.
* Display map preview imagery sourced from `MapPreviewInfo`.
* Wire `MissionBriefingView` interactions to dispatch engine events.

### Gameplay Scene Transition and Layout

* Transition into `RendererState.GAMEPLAY` with placeholder panels (grid, script editor, status
  widgets).
* Integrate an event pipeline for gameplay start/exit notifications.
* Maintain renderer/engine separation per `docs/decisions/0002-implement-ecs-pattern.md`.

## Implementation Roadmap

* [ ] **Task 1:** Create Arcade window launcher (`src/hexa_core/renderer/app.py`) and wire
  `HexaRenderer.run()`.
* [ ] **Task 2:** Implement GUI widgets for mission briefing objectives, map preview, and
  interaction prompts.
* [ ] **Task 3:** Define gameplay scene view models and render placeholder layout.
* [ ] **Task 4:** Connect renderer-engine events for mission briefing acceptance and gameplay
  activation.
* [ ] **Task 5:** Add spec-kit coverage for renderer launcher and gameplay transition states.
* [ ] **Task 6:** Document gameplay renderer architecture in `docs/renderer_gameplay.md`.

## References

* Arcade Views Tutorial: [Arcade Views][arcade-views]
* Arcade GUI/Menu Tutorial: [Arcade GUI/Menu][arcade-menu]
* Existing Renderer Docs: `docs/renderer.md`
* Architecture Rules: `.windsurf/rules/01_architecture.md`

[arcade-views]: https://api.arcade.academy/en/latest/tutorials/views/index.html
[arcade-menu]: https://api.arcade.academy/en/latest/tutorials/menu/index.html
