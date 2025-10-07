"""ECS world wrapper for Hexa-Core Command."""

from __future__ import annotations

from typing import TYPE_CHECKING

import esper

if TYPE_CHECKING:
    from esper import World as EsperWorld  # type: ignore[attr-defined]
else:
    EsperWorld = esper.World


class GameWorld(EsperWorld):
    """Thin wrapper around `esper.World` for future customization."""

    def __init__(self) -> None:
        super().__init__()
        # TODO: Register systems and set up initial state once implemented.
