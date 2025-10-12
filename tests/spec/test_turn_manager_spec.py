"""Turn manager specification tests."""

from __future__ import annotations

# ruff: noqa: S101
import pytest
from hexa_core.engine.components import StatsComponent, TurnComponent
from hexa_core.engine.world import GameWorld


def _setup_world(speed: int, initial_counter: int = 0) -> tuple[GameWorld, int, list[tuple[str, dict[str, object]]]]:
    from hexa_core.engine.systems.turn_system import TurnManager

    world = GameWorld()
    turn_manager = TurnManager(world.event_bus)
    world.add_processor(turn_manager)

    entity = world.create_entity()
    world.add_component(entity, StatsComponent(health=100, speed=speed, processor=100))
    world.add_component(entity, TurnComponent(turn_counter=initial_counter))

    captured: list[tuple[str, dict[str, object]]] = []

    def capture(event: str, payload: dict[str, object]) -> None:
        captured.append((event, payload))

    world.subscribe_event("engine.turn.ready", capture)

    return world, entity, captured


def describe_turn_manager() -> None:
    def it_accumulates_turn_counter_from_speed() -> None:
        world, entity, _ = _setup_world(speed=125)

        world.process()
        turn = world.component_for_entity(entity, TurnComponent)

        assert turn.turn_counter == 125
        assert turn.ready is False

    def it_marks_entity_ready_once_threshold_reached() -> None:
        world, entity, captured = _setup_world(speed=500)

        world.process()
        world.process()
        turn = world.component_for_entity(entity, TurnComponent)

        from hexa_core.engine.systems.turn_system import ACTION_THRESHOLD

        assert turn.ready is True
        assert turn.turn_counter >= ACTION_THRESHOLD
        assert captured == [
            (
                "engine.turn.ready",
                {
                    "entity_id": entity,
                    "turn_counter": turn.turn_counter,
                },
            )
        ]

    def it_allows_consuming_ready_turn_and_retains_overflow() -> None:
        world, entity, _ = _setup_world(speed=600, initial_counter=800)

        world.process()

        from hexa_core.engine.systems.turn_system import ACTION_THRESHOLD

        turn = world.component_for_entity(entity, TurnComponent)
        assert turn.ready is True

        world.consume_turn(entity)

        turn = world.component_for_entity(entity, TurnComponent)

        assert turn.ready is False
        assert 0 <= turn.turn_counter < ACTION_THRESHOLD

    def it_raises_when_consuming_non_ready_entity() -> None:
        world, entity, _ = _setup_world(speed=100)

        with pytest.raises(RuntimeError):
            world.consume_turn(entity)
