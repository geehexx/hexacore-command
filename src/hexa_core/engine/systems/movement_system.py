"""Movement system for Hexa-Core Command."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, Self, cast

import esper

from hexa_core.engine.components import PositionComponent

if TYPE_CHECKING:
    from esper import World as EsperWorld  # type: ignore[attr-defined]
else:
    EsperWorld = esper.World


class MovementSystem(esper.Processor):
    """Placeholder movement system."""

    world: EsperWorld  # Provided by esper.Processor

    def process(self: Self, *_: object, **__: object) -> None:  # pragma: no cover - placeholder
        """Process movement for entities with a path to follow."""
        for _entity, _position in self._iter_positions():
            # TODO: Implement pathfinding and movement resolution.
            continue

    def _iter_positions(self: Self) -> Iterable[tuple[int, PositionComponent]]:
        """Iterate over entities with `PositionComponent`."""
        components = self.world.get_components(PositionComponent)
        return cast(Iterable[tuple[int, PositionComponent]], components)
