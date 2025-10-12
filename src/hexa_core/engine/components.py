"""ECS components for Hexa-Core Command."""

from __future__ import annotations

from dataclasses import dataclass

from hexa_core.engine.datatypes import HexCoord


@dataclass(slots=True)
class PositionComponent:
    """Axial grid position."""

    q: int
    r: int


@dataclass(slots=True)
class StatsComponent:
    """Basic combat and initiative statistics."""

    health: int
    speed: int
    processor: int


@dataclass(slots=True)
class ScriptComponent:
    """Reference to the Hexa-Script used by the entity."""

    path: str


@dataclass(slots=True)
class TurnComponent:
    """Tracks initiative for the turn manager."""

    turn_counter: int = 0
    ready: bool = False


@dataclass(slots=True)
class MovementIntentComponent:
    """Target coordinate for pending movement resolution."""

    target: HexCoord


@dataclass(slots=True)
class CombatIntentComponent:
    """Pending combat action against a specified target."""

    target: int
    damage: int
