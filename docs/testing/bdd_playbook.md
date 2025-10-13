# BDD Playbook

## Purpose

Behavior-Driven Development (BDD) scenarios capture player-visible behaviors and orchestration across engine systems. This playbook defines conventions for writing Gherkin features and `pytest-bdd` step definitions that integrate with Hexa-Core Command's ECS and event bus.

## Authoring Principles

- **Stay declarative:** Keep Gherkin steps in user language. Push implementation details into step definitions and fixtures.
- **Use Backgrounds for shared setup:** Register processors, bootstrap worlds, and preload entities via `Background` blocks so scenarios focus on behavior.
- **Reuse pytest fixtures:** Extract world builders or entity factories into fixtures when multiple features require the same wiring.
- **Assert on events:** Subscribe to engine events (`engine.movement.completed`, etc.) inside step definitions to validate payloads rather than inspecting internals directly.
- **Prefer production services:** Step definitions must interact with real systems (`MovementSystem`, `EventBus`, `GameWorld`) to ensure coverage stays representative.

## File Layout

- **Features:** Place `.feature` files under `tests/features/`. Each file should own a single `Feature` definition.
- **Steps:** Place step modules next to their feature (`tests/features/test_<feature>_bdd.py`). Import shared fixtures from `tests/features/conftest.py` when reuse emerges.
- **Data Builders:** Keep helper utilities in `tests/features/_support/` if scenario composition grows complex.

## Step Definition Patterns

- **Context dataclasses:** Store world references, entity identifiers, and captured events in a typed dataclass injected via `target_fixture`.
- **Parser helpers:** Prefer `pytest_bdd.parsers.parse` to extract structured data (coordinates, ids) from steps.
- **World processing:** After mutating ECS state, call `GameWorld.process()` so registered processors apply changes.
- **Event capture:** Clear captured events before triggering actions to guarantee expectations remain specific.

## Example Flow

```gherkin
Feature: Bot movement
  Background:
    Given a movement system is registered

  Scenario: Bot moves north and completes the action
    Given a bot with id "bot-1" at axial coordinate (0, 0)
    When the bot queues a move intent toward axial coordinate (0, 1)
    Then the movement system publishes a completed move event
    And the bot position is updated to axial coordinate (0, 1)
```

Corresponding steps live in `tests/features/test_bot_movement_bdd.py` and demonstrate event capture plus position validation.

## Automation Targets

- Run `task test:bdd` for dedicated BDD verification.
- Run `task test:unit` to execute BDD scenarios alongside specs and other test suites.

## Next Steps

- Extend features as new systems become stable (combat resolution, script errors).
- Expand shared fixtures for multi-turn or multi-entity setups to keep scenarios readable.
