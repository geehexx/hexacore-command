# Game Mechanics Overview

The MVP simulates bots executing Hexa-Script programs on a hexagonal grid.

## Turn Structure

* A `TurnManager` system advances entities based on accumulated initiative until `ACTION_THRESHOLD` is met.
* Entities spend processor tokens when executing script commands.

## Combat & Movement

* Movement and combat systems operate on ECS components.
* Damage and movement outcomes emit events consumed by the renderer.

## Scripts

* Hexa-Script powers bot behavior, interpreted by the `ScriptRunner` system.
