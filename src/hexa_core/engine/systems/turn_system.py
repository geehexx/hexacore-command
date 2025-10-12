"""Turn and initiative management system."""

from __future__ import annotations

from typing import Self

import esper

from hexa_core.engine.components import StatsComponent, TurnComponent
from hexa_core.engine.event_bus import EventBus

ACTION_THRESHOLD = 1000


class TurnManager(esper.Processor):
    """Processor that advances initiative and publishes ready events."""

    def __init__(self: Self, event_bus: EventBus, action_threshold: int = ACTION_THRESHOLD) -> None:
        super().__init__()
        self._event_bus = event_bus
        self._threshold = action_threshold

    def process(self: Self, *_: object, **__: object) -> None:
        for entity, (stats, turn) in esper.get_components(StatsComponent, TurnComponent):
            if turn.ready:
                # Preserve ready entities for external consumption until explicitly cleared.
                continue

            turn.turn_counter += stats.speed
            if turn.turn_counter >= self._threshold:
                turn.ready = True
                self._event_bus.publish(
                    "engine.turn.ready",
                    {
                        "entity_id": entity,
                        "turn_counter": turn.turn_counter,
                    },
                )

    def consume_turn(self: Self, entity: int) -> None:
        turn = esper.component_for_entity(entity, TurnComponent)
        if not turn.ready:
            msg = f"Entity {entity} is not ready to act"
            raise RuntimeError(msg)

        turn.turn_counter -= self._threshold
        if turn.turn_counter < 0:
            turn.turn_counter = 0
        turn.ready = False
