"""Movement system for Hexa-Core Command."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Self, cast

import esper

from hexa_core.engine.components import MovementIntentComponent, PositionComponent
from hexa_core.engine.datatypes import HexCoord
from hexa_core.engine.event_bus import EventBus

class MovementSystem(esper.Processor):
    """Resolves movement intents and publishes completion events."""

    def __init__(self: Self, event_bus: EventBus) -> None:
        super().__init__()
        self._event_bus = event_bus

    def process(self: Self, *_: object, **__: object) -> None:
        for entity, (position, intent) in self._iter_intents():
            origin = HexCoord(position.q, position.r)
            destination = intent.target

            position.q = destination.q
            position.r = destination.r
            esper.remove_component(entity, MovementIntentComponent)

            self._event_bus.publish(
                "engine.movement.completed",
                {
                    "entity_id": entity,
                    "from": origin,
                    "to": destination,
                },
            )

    def _iter_intents(self: Self) -> Iterable[tuple[int, tuple[PositionComponent, MovementIntentComponent]]]:
        components = esper.get_components(PositionComponent, MovementIntentComponent)
        return cast(
            Iterable[tuple[int, tuple[PositionComponent, MovementIntentComponent]]],
            components,
        )
