from __future__ import annotations

from hypothesis import given, strategies as st

from hexa_core.engine.datatypes import HexCoord


def hex_coord_strategy() -> st.SearchStrategy[HexCoord]:
    return st.builds(HexCoord, st.integers(min_value=-500, max_value=500), st.integers(min_value=-500, max_value=500))


@given(hex_coord_strategy())
def test_hex_coord_distance_to_self_is_zero(coord: HexCoord) -> None:
    assert coord.distance_to(coord) == 0


@given(hex_coord_strategy(), hex_coord_strategy())
def test_hex_coord_distance_is_symmetric(a: HexCoord, b: HexCoord) -> None:
    assert a.distance_to(b) == b.distance_to(a)


@given(hex_coord_strategy())
def test_hex_coord_neighbors_are_one_step_away(coord: HexCoord) -> None:
    for neighbor in coord.neighbors():
        assert coord.distance_to(neighbor) == 1
