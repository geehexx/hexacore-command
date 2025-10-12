"""Map loading utilities for Hexa-Core Command."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(slots=True)
class LevelGridSize:
    width: int
    height: int


@dataclass(slots=True)
class LevelEntity:
    name: str
    components: dict[str, Any]


@dataclass(slots=True)
class LevelData:
    name: str
    grid_size: LevelGridSize
    tiles: list[tuple[str, int, int]]
    entities: list[LevelEntity]


class MapLoader:
    """Load map definitions from JSON files."""

    def load(self, path: Path | str) -> LevelData:
        map_path = Path(path)
        if not map_path.exists():
            raise FileNotFoundError(f"Map file not found: {map_path}")

        data = json.loads(map_path.read_text(encoding="utf-8"))
        return LevelData(
            name=data["name"],
            grid_size=self._parse_grid(data["grid_size"]),
            tiles=self._parse_tiles(data.get("tiles", [])),
            entities=self._parse_entities(data.get("entities", [])),
        )

    def _parse_grid(self, grid: dict[str, int]) -> LevelGridSize:
        return LevelGridSize(width=grid["width"], height=grid["height"])

    def _parse_tiles(self, tiles: Iterable[dict[str, Any]]) -> list[tuple[str, int, int]]:
        return [
            (
                tile["type"],
                tile["q"],
                tile["r"],
            )
            for tile in tiles
        ]

    def _parse_entities(self, entities: Iterable[dict[str, Any]]) -> list[LevelEntity]:
        parsed: list[LevelEntity] = []
        for entity in entities:
            name = entity["name"]
            components = entity.get("components", {})
            parsed.append(LevelEntity(name=name, components=components))
        return parsed
