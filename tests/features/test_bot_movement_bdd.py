from __future__ import annotations

from dataclasses import dataclass, field

import pytest
from hexa_core.engine.components import MovementIntentComponent, PositionComponent
from hexa_core.engine.datatypes import HexCoord
from hexa_core.engine.event_bus import Subscriber
from hexa_core.engine.systems.movement_system import MovementSystem
from hexa_core.engine.world import GameWorld
from pytest_bdd import given, parsers, scenarios, then, when


@dataclass
class MovementContext:
    world: GameWorld
    captured: list[tuple[str, dict[str, object]]] = field(default_factory=list)
    entities: dict[str, int] = field(default_factory=dict)
    target: HexCoord | None = None
    movement_system: MovementSystem | None = None
    origins: dict[str, HexCoord] = field(default_factory=dict)
    active_alias: str | None = None


scenarios("bot_movement.feature")


@given("a movement system is registered", target_fixture="movement_context")
def movement_context() -> MovementContext:
    world = GameWorld()
    context = MovementContext(world=world)

    def capture(event: str, payload: dict[str, object]) -> None:
        context.captured.append((event, payload))

    subscriber: Subscriber = capture
    world.subscribe_event("engine.movement.completed", subscriber)

    movement_system = MovementSystem(event_bus=world.event_bus)
    world.add_processor(movement_system)
    context.movement_system = movement_system

    return context


@given(parsers.parse('a bot with id "{alias}" at axial coordinate ({q:d}, {r:d})'))
def register_bot(movement_context: MovementContext, alias: str, q: int, r: int) -> None:
    world = movement_context.world
    entity = world.create_entity()
    world.add_component(entity, PositionComponent(q=q, r=r))
    movement_context.entities[alias] = entity
    movement_context.origins[alias] = HexCoord(q, r)
    movement_context.active_alias = alias


@when(parsers.parse("the bot queues a move intent toward axial coordinate ({q:d}, {r:d})"))
def queue_move_intent(movement_context: MovementContext, q: int, r: int) -> None:
    entity_alias = movement_context.active_alias
    if entity_alias is None:
        pytest.fail("No bot alias registered before queuing movement")

    entity_id = movement_context.entities[entity_alias]

    target = HexCoord(q, r)
    movement_context.target = target

    movement_context.world.add_component(
        entity_id,
        MovementIntentComponent(target=target),
    )

    movement_context.captured.clear()
    movement_context.world.process()


@then("the movement system publishes a completed move event")
def verify_move_event(movement_context: MovementContext) -> None:
    if not movement_context.captured:
        pytest.fail("Expected engine.movement.completed event to be published")

    event_type, payload = movement_context.captured[-1]
    if event_type != "engine.movement.completed":
        pytest.fail(f"Unexpected event type: {event_type!r}")

    alias = movement_context.active_alias
    if alias is None:
        pytest.fail("No active bot alias recorded for verification")

    entity_id = movement_context.entities[alias]
    expected_target = movement_context.target
    if expected_target is None:
        pytest.fail("Movement target was not recorded")

    origin = movement_context.origins[alias]

    if payload.get("entity_id") != entity_id:
        pytest.fail("Event payload 'entity_id' did not match created entity")
    if payload.get("from") != origin:
        pytest.fail("Event payload 'from' did not match origin coordinate")
    if payload.get("to") != expected_target:
        pytest.fail("Event payload 'to' did not match queued target")

    if len(movement_context.captured) != 1:
        pytest.fail("Movement system published an unexpected number of events")


@then(parsers.parse("the bot position is updated to axial coordinate ({q:d}, {r:d})"))
def verify_position(movement_context: MovementContext, q: int, r: int) -> None:
    alias = movement_context.active_alias
    if alias is None:
        pytest.fail("No active bot alias recorded for verification")

    entity_id = movement_context.entities[alias]

    position = movement_context.world.component_for_entity(entity_id, PositionComponent)
    if (position.q, position.r) != (q, r):
        pytest.fail("Entity position did not match expected destination")

    if movement_context.world.try_component(entity_id, MovementIntentComponent) is not None:
        pytest.fail("Movement intent component remained after processing")

    movement_context.origins[alias] = HexCoord(q, r)
