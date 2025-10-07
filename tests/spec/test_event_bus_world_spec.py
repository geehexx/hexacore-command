from __future__ import annotations

from collections import deque

import esper
from hexa_core.engine.event_bus import EventBus
from hexa_core.engine.world import GameWorld


def describe_event_bus():
    def it_notifies_all_subscribers() -> None:
        bus = EventBus()
        received = deque()

        def subscriber_one(event_type: str, payload: dict[str, int]) -> None:
            received.append((event_type, payload["value"]))

        def subscriber_two(event_type: str, payload: dict[str, int]) -> None:
            received.append((event_type, payload["value"] * 2))

        bus.subscribe("test.event", subscriber_one)
        bus.subscribe("test.event", subscriber_two)

        bus.publish("test.event", {"value": 7})

        assert list(received) == [
            ("test.event", 7),
            ("test.event", 14),
        ]

    def it_allows_publishing_without_subscribers() -> None:
        bus = EventBus()

        bus.publish("unhandled", {"value": 1})


def describe_game_world():
    def it_creates_an_event_bus_if_none_is_provided() -> None:
        world = GameWorld()

        assert isinstance(world.event_bus, EventBus)

    def it_can_accept_an_existing_event_bus() -> None:
        existing_bus = EventBus()

        world = GameWorld(event_bus=existing_bus)

        assert world.event_bus is existing_bus

    def it_exposes_subscribe_and_publish_helpers() -> None:
        world = GameWorld()
        received = deque()

        world.subscribe_event("engine.tick", lambda _event, payload: received.append(payload["tick"]))

        world.publish_event("engine.tick", {"tick": 1})

        assert list(received) == [1]

    def it_registers_an_esper_context() -> None:
        world = GameWorld()

        entity = world.create_entity()
        world.delete_entity(entity)

        assert world.context_name in esper.list_worlds()
