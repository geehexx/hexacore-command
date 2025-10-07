"""Combat resolution system for Hexa-Core Command."""

from __future__ import annotations

import esper

from hexa_core.engine.components import StatsComponent


class CombatSystem(esper.Processor):
    """Placeholder combat system."""

    def process(self, *_: object, **__: object) -> None:  # pragma: no cover - placeholder
        """Apply combat interactions between entities."""
        for _entity, _stats in self.world.get_component(StatsComponent):
            # TODO: Implement combat resolution logic.
            continue
