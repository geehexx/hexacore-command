"""Simple publish/subscribe event bus."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from typing import Any, Self

Subscriber = Callable[[str, dict[str, Any]], None]


class EventBus:
    """Minimal event bus for engine-to-renderer communication."""

    def __init__(self: Self) -> None:
        self._subscribers: dict[str, list[Subscriber]] = defaultdict(list)

    def subscribe(self: Self, event_type: str, subscriber: Subscriber) -> None:
        """Register a subscriber for a specific event type."""
        self._subscribers[event_type].append(subscriber)

    def publish(self: Self, event_type: str, payload: dict[str, Any]) -> None:
        """Notify all subscribers of an event."""
        for subscriber in self._subscribers[event_type]:
            subscriber(event_type, payload)

    def subscribers(self: Self, event_type: str) -> tuple[Subscriber, ...]:
        """Return subscribers for inspection/testing."""
        return tuple(self._subscribers[event_type])
