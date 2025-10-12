"""Combat resolution system for Hexa-Core Command."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Self, cast

import esper

from hexa_core.engine.components import CombatIntentComponent, StatsComponent
from hexa_core.engine.event_bus import EventBus


class CombatSystem(esper.Processor):
    """Processes combat intents and applies damage."""

    def __init__(self: Self, event_bus: EventBus) -> None:
        super().__init__()
        self._event_bus = event_bus

    def process(self: Self, *_: object, **__: object) -> None:
        for entity, components in self._intent_components():
            _stats, intent = components
            target_stats = esper.component_for_entity(intent.target, StatsComponent)

            target_stats.health = max(0, target_stats.health - intent.damage)
            defeated = target_stats.health == 0

            esper.remove_component(entity, CombatIntentComponent)

            self._event_bus.publish(
                "engine.combat.resolved",
                {
                    "attacker_id": entity,
                    "target_id": intent.target,
                    "damage": intent.damage,
                    "remaining_health": target_stats.health,
                    "defeated": defeated,
                },
            )

    def _intent_components(
        self: Self,
    ) -> Iterable[tuple[int, tuple[StatsComponent, CombatIntentComponent]]]:
        for entity, pair in esper.get_components(StatsComponent, CombatIntentComponent):
            typed_pair = cast(tuple[StatsComponent, CombatIntentComponent], pair)
            yield entity, typed_pair
