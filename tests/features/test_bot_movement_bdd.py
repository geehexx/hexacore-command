from __future__ import annotations

from dataclasses import dataclass, field

import pytest
from hexa_core.engine.datatypes import HexCoord
from hexa_core.engine.event_bus import Subscriber
from hexa_core.engine.world import GameWorld
from pytest_bdd import given, scenarios, then, when


@dataclass
class BotContext:
    world: GameWorld
    origin: HexCoord
    captured: list[tuple[str, dict[str, object]]] = field(default_factory=list)
    target: HexCoord | None = None


scenarios("bot_movement.feature")


@given("a bot is at axial coordinate (0, 0)", target_fixture="bot_context")
def bot_context() -> BotContext:
    world = GameWorld()
    context = BotContext(world=world, origin=HexCoord(0, 0))

    def capture(event: str, payload: dict[str, object]) -> None:
        context.captured.append((event, payload))

    subscriber: Subscriber = capture
    world.subscribe_event("engine.schedule_move", subscriber)

    return context


@when("the bot attempts to move north")
def attempt_move(bot_context: BotContext) -> None:
    origin = bot_context.origin
    target = HexCoord(origin.q, origin.r + 1)

    bot_context.world.publish_event(
        "engine.schedule_move",
        {
            "bot_id": "bot-1",
            "from": origin,
            "to": target,
            "direction": "north",
        },
    )

    bot_context.target = target


@then("the engine schedules a move event")
def verify_move(bot_context: BotContext) -> None:
    if not bot_context.captured:
        pytest.fail("Expected engine.schedule_move event to be published")

    origin = bot_context.origin
    target = bot_context.target
    if target is None:
        pytest.fail("Target location was not recorded")

    event_type, payload = bot_context.captured[-1]
    if event_type != "engine.schedule_move":
        pytest.fail(f"Unexpected event type: {event_type!r}")
    if payload.get("from") != origin:
        pytest.fail("Event payload 'from' did not match origin")
    if payload.get("to") != target:
        pytest.fail("Event payload 'to' did not match target")
    if payload.get("direction") != "north":
        pytest.fail("Event payload 'direction' did not match 'north'")
