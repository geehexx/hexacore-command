"""ECS world wrapper for Hexa-Core Command."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from itertools import count
from typing import ParamSpec, Self, TypeVar, cast

import esper

from hexa_core.engine.event_bus import EventBus, Subscriber

P = ParamSpec("P")
R = TypeVar("R")


class GameWorld:
    """Encapsulates an `esper` world context with event bus integration."""

    _context_ids = count()

    def __init__(self: Self, event_bus: EventBus | None = None) -> None:
        self.context_name = f"game_world_{next(self._context_ids)}"
        self.event_bus: EventBus = event_bus or EventBus()
        self._register_context()
        # TODO: Register systems and set up initial state once implemented.

    def _register_context(self: Self) -> None:
        """Ensure the underlying esper context exists."""

        with self._activate_context():
            # No-op: switching contexts creates them lazily within esper.
            pass

    @contextmanager
    def _activate_context(self: Self) -> Iterator[None]:
        previous = esper.current_world
        if previous == self.context_name:
            yield
            return

        try:
            esper.switch_world(self.context_name)
            yield
        finally:
            esper.switch_world(previous)

    def _delegate(self: Self, func: Callable[P, R]) -> Callable[P, R]:
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            with self._activate_context():
                return func(*args, **kwargs)

        return wrapper

    def __getattr__(self: Self, name: str) -> Callable[..., object]:
        delegated: dict[str, Callable[..., object]] = {
            "create_entity": esper.create_entity,
            "delete_entity": esper.delete_entity,
            "add_component": esper.add_component,
            "remove_component": esper.remove_component,
            "component_for_entity": esper.component_for_entity,
            "components_for_entity": esper.components_for_entity,
            "get_component": esper.get_component,
            "get_components": esper.get_components,
            "try_component": esper.try_component,
            "try_components": esper.try_components,
            "add_processor": esper.add_processor,
            "remove_processor": esper.remove_processor,
            "get_processor": esper.get_processor,
            "process": esper.process,
            "timed_process": esper.timed_process,
            "clear_dead_entities": esper.clear_dead_entities,
        }

        if name in delegated:
            delegate = self._delegate(delegated[name])
            setattr(self, name, delegate)
            return delegate

        raise AttributeError(f"{type(self).__name__!s} has no attribute {name!r}")

    def subscribe_event(self: Self, event_type: str, subscriber: Subscriber) -> None:
        """Register a subscriber on the underlying `EventBus`."""

        self.event_bus.subscribe(event_type, subscriber)

    def publish_event(self: Self, event_type: str, payload: dict[str, object]) -> None:
        """Publish an event via the underlying `EventBus`."""

        self.event_bus.publish(event_type, payload)

    def consume_turn(self: Self, entity: int) -> None:
        """Delegate turn consumption to the registered `TurnManager`."""

        from hexa_core.engine.systems.turn_system import TurnManager

        with self._activate_context():
            manager = cast(TurnManager | None, esper.get_processor(TurnManager))
            if manager is None:  # pragma: no cover - defensive guard
                msg = "TurnManager processor is not registered"
                raise RuntimeError(msg)
            manager.consume_turn(entity)
