# MVP Implementation Roadmap

This document tracks the initial project setup. Once all items are checked, this document will be archived per the Documentation Lifecycle rule.

## Phase 1: Core Engine Foundations

* [x] **Task 1:** Set up initial benchmarking infrastructure with `pytest-benchmark`.
* [x] **Task 2:** Implement Core Datatypes (`HexCoord`, `Component` base classes).
  * Implemented `HexCoord.distance_to()` for axial metric and introduced a reusable `Component` mixin powering dataclass utilities (`to_dict`, `replace`).
* [x] **Task 3:** Implement Game World (`World`) and `EventBus`.
  * Added `GameWorld` wrapper that provisions dedicated `esper` contexts and exposes event bus helpers, plus `EventBus` publish/subscribe tests.
* [ ] **Task 4:** Implement Turn & Token Systems (`TurnManager`, `StatsComponent`, `TurnComponent`).
* [ ] **Task 5:** Implement Hexa-Script Lexer, Parser, and `ScriptRunner` system.
* [ ] **Task 6:** Implement Core Actions (`MovementSystem`, `CombatSystem`).
* [ ] **Task 7:** Implement Data Loaders for `manifest.json` and map files.
