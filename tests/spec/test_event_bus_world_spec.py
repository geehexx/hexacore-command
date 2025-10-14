"""Event bus and world integration specs."""

# ruff: noqa: S101
from __future__ import annotations

from collections import deque
from typing import cast

import esper
import pytest
from hexa_core.engine.event_bus import EventBus
from hexa_core.engine.world import GameWorld


def describe_event_bus() -> None:
    def it_notifies_all_subscribers() -> None:
        bus = EventBus()
        received: deque[tuple[str, int]] = deque()

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

    def it_exposes_current_subscribers_as_tuple() -> None:
        bus = EventBus()

        def subscriber(_: str, __: dict[str, int]) -> None:
            return None

        bus.subscribe("example", subscriber)

        assert bus.subscribers("example") == (subscriber,)


def describe_game_world() -> None:
    def it_creates_an_event_bus_if_none_is_provided() -> None:
        world = GameWorld()

        assert isinstance(world.event_bus, EventBus)

    def it_can_accept_an_existing_event_bus() -> None:
        existing_bus = EventBus()

        world = GameWorld(event_bus=existing_bus)

        assert world.event_bus is existing_bus

    def it_exposes_subscribe_and_publish_helpers() -> None:
        world = GameWorld()
        received: deque[int] = deque()

        world.subscribe_event("engine.tick", lambda _event, payload: received.append(payload["tick"]))

        world.publish_event("engine.tick", {"tick": 1})

        assert list(received) == [1]

    def it_registers_an_esper_context() -> None:
        world = GameWorld()

        entity = cast(int, world.create_entity())
        world.delete_entity(entity)

        assert world.context_name in esper.list_worlds()

    def it_reenters_existing_context_without_switching() -> None:
        world = GameWorld()

        with world._activate_context(), world._activate_context():
            world.create_entity()

    def it_raises_attribute_error_for_unknown_delegates() -> None:
        world = GameWorld()

        with pytest.raises(AttributeError):
            _ = world.non_existent_method  # type: ignore[attr-defined]
