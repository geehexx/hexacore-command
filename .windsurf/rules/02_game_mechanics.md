---
trigger: glob
description: "Defines the rules for game flow. See docs/game_mechanics.md."
globs: src/hexa_core/engine/**/*.py
---

# Rule: Game Mechanics

## 2.1 The Grid & Map

* Maps are defined by JSON files in `assets/maps/`.

## 2.2 Turn & Initiative System ("Tick-Based")

* `ACTION_THRESHOLD`: `1000`.
* A `TurnManager` system manages turn order based on `speed` and `turn_counter` components.

## 2.3 Gameplay Loop

* All bots (player and AI) are entities with a `ScriptComponent`.
* The `ScriptRunner` system executes the appropriate script for the active entity.
* **MVP Scope:** For now, focus only on the core mechanics. Do not implement complex terrain, combat stats (beyond health), or alternative victory conditions. These concepts should be noted in the "living documentation" as planned future enhancements.
