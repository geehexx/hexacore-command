"""ECS world wrapper for Hexa-Core Command."""

from __future__ import annotations

import esper


class GameWorld(esper.World):
    """Thin wrapper around `esper.World` for future customization."""

    def __init__(self) -> None:
        super().__init__()
        # TODO: Register systems and set up initial state once implemented.
