from __future__ import annotations

from pytest_bdd import given, scenarios, then, when

from hexa_core.engine.datatypes import HexCoord
from hexa_core.engine.event_bus import Subscriber
from hexa_core.engine.world import GameWorld

scenarios("bot_movement.feature")


@given("a bot is at axial coordinate (0, 0)", target_fixture="bot_context")
def bot_context() -> dict[str, object]:
    world = GameWorld()
    captured: list[tuple[str, dict[str, object]]] = []

    def capture(event: str, payload: dict[str, object]) -> None:
        captured.append((event, payload))

    subscriber: Subscriber = capture
    world.subscribe_event("engine.schedule_move", subscriber)

    return {"world": world, "origin": HexCoord(0, 0), "captured": captured}


@when("the bot attempts to move north")
def attempt_move(bot_context: dict[str, object]) -> None:
    world = bot_context["world"]
    origin = bot_context["origin"]
    target = HexCoord(origin.q, origin.r + 1)

    world.publish_event(
        "engine.schedule_move",
        {
            "bot_id": "bot-1",
            "from": origin,
            "to": target,
            "direction": "north",
        },
    )

    bot_context["target"] = target


@then("the engine schedules a move event")
def verify_move(bot_context: dict[str, object]) -> None:
    captured = bot_context["captured"]
    origin = bot_context["origin"]
    target = bot_context["target"]

    assert captured, "Expected engine.schedule_move event to be published"

    event_type, payload = captured[-1]
    assert event_type == "engine.schedule_move"
    assert payload["from"] == origin
    assert payload["to"] == target
    assert payload["direction"] == "north"
