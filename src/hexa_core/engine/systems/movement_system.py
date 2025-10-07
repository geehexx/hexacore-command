"""Movement system for Hexa-Core Command."""

from __future__ import annotations

from typing import Iterable

import esper

from hexa_core.engine.components import PositionComponent


class MovementSystem(esper.Processor):
    """Placeholder movement system."""

    def process(self, *_: object, **__: object) -> None:  # pragma: no cover - placeholder
        """Process movement for entities with a path to follow."""
        for _entity, _position in self._iter_positions():
            # TODO: Implement pathfinding and movement resolution.
            continue

    def _iter_positions(self) -> Iterable[tuple[int, PositionComponent]]:
        """Iterate over entities with `PositionComponent`."""
        return self.world.get_components(PositionComponent)
