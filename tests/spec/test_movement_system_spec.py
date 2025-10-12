"""Movement system specification tests."""

# ruff: noqa: S101
from __future__ import annotations

from collections import deque

from hexa_core.engine.components import MovementIntentComponent, PositionComponent
from hexa_core.engine.datatypes import HexCoord
from hexa_core.engine.event_bus import EventBus
from hexa_core.engine.world import GameWorld


def describe_movement_system() -> None:
    def it_moves_entity_and_publishes_event() -> None:
        bus = EventBus()
        world = GameWorld(event_bus=bus)

        from hexa_core.engine.systems.movement_system import MovementSystem

        movement_system = MovementSystem(event_bus=bus)
        world.add_processor(movement_system)

        entity = world.create_entity()
        world.add_component(entity, PositionComponent(q=0, r=0))
        world.add_component(entity, MovementIntentComponent(target=HexCoord(1, 0)))

        captured: deque[tuple[str, dict[str, object]]] = deque()
        world.subscribe_event("engine.movement.completed", lambda event, payload: captured.append((event, payload)))

        world.process()

        position = world.component_for_entity(entity, PositionComponent)
        assert (position.q, position.r) == (1, 0)
        assert world.try_component(entity, MovementIntentComponent) is None

        assert list(captured) == [
            (
                "engine.movement.completed",
                {
                    "entity_id": entity,
                    "from": HexCoord(0, 0),
                    "to": HexCoord(1, 0),
                },
            )
        ]

    def it_handles_multiple_movement_intents() -> None:
        bus = EventBus()
        world = GameWorld(event_bus=bus)

        from hexa_core.engine.systems.movement_system import MovementSystem

        movement_system = MovementSystem(event_bus=bus)
        world.add_processor(movement_system)

        entity = world.create_entity()
        world.add_component(entity, PositionComponent(q=2, r=-1))
        world.add_component(entity, MovementIntentComponent(target=HexCoord(3, -1)))

        world.process()

        world.add_component(entity, MovementIntentComponent(target=HexCoord(3, 0)))

        world.process()

        position = world.component_for_entity(entity, PositionComponent)
        assert (position.q, position.r) == (3, 0)
