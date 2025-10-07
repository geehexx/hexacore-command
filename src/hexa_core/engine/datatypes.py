"""Core datatypes for Hexa-Core Command."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HexCoord:
    """Axial coordinate on a hex grid."""

    q: int
    r: int

    def neighbors(self) -> tuple["HexCoord", ...]:
        """Return neighboring coordinates in axial directions."""
        directions = (
            (1, 0),
            (1, -1),
            (0, -1),
            (-1, 0),
            (-1, 1),
            (0, 1),
        )
        return tuple(HexCoord(self.q + dq, self.r + dr) for dq, dr in directions)
