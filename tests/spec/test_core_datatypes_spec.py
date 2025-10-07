from __future__ import annotations

from dataclasses import dataclass

import pytest
from hexa_core.engine.datatypes import Component, HexCoord


def describe_hex_coord():
    def it_lists_all_six_neighbors() -> None:
        origin = HexCoord(0, 0)

        neighbors = origin.neighbors()

        assert neighbors == (
            HexCoord(1, 0),
            HexCoord(1, -1),
            HexCoord(0, -1),
            HexCoord(-1, 0),
            HexCoord(-1, 1),
            HexCoord(0, 1),
        )

    def it_computes_axial_distance() -> None:
        assert HexCoord(0, 0).distance_to(HexCoord(2, -1)) == 2
        assert HexCoord(-2, 3).distance_to(HexCoord(1, -1)) == 4


@dataclass(slots=True)
class ExampleComponent(Component):
    health: int
    speed: int = 0


def describe_component_base_class():
    def it_converts_to_dict_representation() -> None:
        component = ExampleComponent(health=10, speed=3)

        assert component.to_dict() == {"health": 10, "speed": 3}

    def it_provides_replace_for_immutable_updates() -> None:
        component = ExampleComponent(health=10, speed=3)

        updated = component.replace(speed=5)

        assert isinstance(updated, ExampleComponent)
        assert updated is not component
        assert updated.health == 10
        assert updated.speed == 5
        assert component.speed == 3

    def it_validates_replace_fields() -> None:
        component = ExampleComponent(health=10, speed=3)

        with pytest.raises(AttributeError):
            component.replace(unknown=1)
