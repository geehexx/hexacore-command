"""Combat resolution system for Hexa-Core Command."""

from __future__ import annotations

from typing import TYPE_CHECKING

import esper

from hexa_core.engine.components import StatsComponent

if TYPE_CHECKING:
    from esper import World as EsperWorld  # type: ignore[attr-defined]
else:
    EsperWorld = esper.World


class CombatSystem(esper.Processor):
    """Placeholder combat system."""

    world: EsperWorld  # Provided by esper.Processor

    def process(self, *_: object, **__: object) -> None:  # pragma: no cover - placeholder
        """Apply combat interactions between entities."""
        for _entity, _stats in self.world.get_component(StatsComponent):
            # TODO: Implement combat resolution logic.
            continue
