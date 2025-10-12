# MVP Implementation Roadmap

This document tracks the initial project setup. Once all items are checked, this document will be archived per the Documentation Lifecycle rule.

## Phase 1: Core Engine Foundations

* [x] **Task 1:** Set up initial benchmarking infrastructure with `pytest-codspeed`.
* [x] **Task 2:** Implement Core Datatypes (`HexCoord`, `Component` base classes).
  * Implemented `HexCoord.distance_to()` for axial metric and introduced a reusable `Component` mixin powering dataclass utilities (`to_dict`, `replace`).
* [x] **Task 3:** Implement Game World (`World`) and `EventBus`.
  * Added `GameWorld` wrapper that provisions dedicated `esper` contexts and exposes event bus helpers, plus `EventBus` publish/subscribe tests.
* [x] **Task 4:** Implement Turn & Token Systems (`TurnManager`, `StatsComponent`, `TurnComponent`).
  * Added `TurnManager` processor publishing `engine.turn.ready` events with spec coverage in `tests/spec/test_turn_manager_spec.py`.
* [x] **Task 5:** Implement Hexa-Script Lexer, Parser, and `ScriptRunner` system.
  * Replaced stubbed runner with a bytecode interpreter validated by `tests/spec/test_script_runner_spec.py`.
* [x] **Task 6:** Implement Core Actions (`MovementSystem`, `CombatSystem`).
  * Introduced intent-driven movement and combat processors with specs in `tests/spec/test_movement_system_spec.py` and `tests/spec/test_combat_system_spec.py`.
* [x] **Task 7:** Implement Data Loaders for `manifest.json` and map files.
  * Added `AssetManifest` and `MapLoader` modules with coverage via `tests/spec/test_asset_loaders_spec.py`.
