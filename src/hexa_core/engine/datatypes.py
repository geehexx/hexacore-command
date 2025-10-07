"""Core datatypes for Hexa-Core Command."""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from dataclasses import replace as dataclass_replace
from typing import Any, TypeVar, cast


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

    def distance_to(self, other: "HexCoord") -> int:
        """Return axial distance to another coordinate."""
        dq = self.q - other.q
        dr = self.r - other.r
        return (abs(dq) + abs(dr) + abs(dq + dr)) // 2


ComponentType = TypeVar("ComponentType", bound="Component")


class Component:
    """Base mixin for ECS components providing helper utilities."""

    __slots__ = ()

    def to_dict(self) -> dict[str, Any]:
        """Return a shallow dictionary representation of the component."""
        if not is_dataclass(self):  # pragma: no cover - defensive guard
            msg = "Component instances must be dataclasses to use to_dict()"
            raise TypeError(msg)
        return cast(dict[str, Any], asdict(cast(Any, self)))

    def replace(self: ComponentType, **changes: object) -> ComponentType:
        """Return a new component instance with the provided immutable updates."""
        if not is_dataclass(self):  # pragma: no cover - defensive guard
            msg = "Component instances must be dataclasses to use replace()"
            raise TypeError(msg)

        try:
            return cast(ComponentType, dataclass_replace(cast(Any, self), **changes))
        except TypeError as exc:  # pragma: no cover - exercised via AttributeError path
            raise AttributeError(str(exc)) from exc


# TECH_DEBT: Evaluate memoizing neighbor tuples or pooling component copies if profiling reveals
# allocation pressure during large-scale simulations.
