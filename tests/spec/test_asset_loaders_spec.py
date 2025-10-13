"""Asset loader specification tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from hexa_core.engine.assets import AssetManifest
from hexa_core.engine.maps import MapLoader


def describe_asset_manifest() -> None:
    def it_loads_manifest_entries_by_logical_name(tmp_path: Path) -> None:
        manifest_path = tmp_path / "manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "sprites": {"hero": "assets/sprites/hero.png"},
                    "sounds": {"laser": "assets/sfx/laser.wav"},
                }
            ),
            encoding="utf-8",
        )

        manifest = AssetManifest.from_file(manifest_path)

        assert manifest.get_asset_path("sprites", "hero") == Path("assets/sprites/hero.png")
        assert manifest.get_asset_path("sounds", "laser") == Path("assets/sfx/laser.wav")

    def it_raises_for_missing_asset() -> None:
        manifest = AssetManifest({"sprites": {"hero": Path("hero.png")}})

        with pytest.raises(KeyError):
            manifest.get_asset_path("sprites", "villain")


def describe_map_loader() -> None:
    def it_loads_entities_and_tiles_from_json(tmp_path: Path) -> None:
        assets_dir = tmp_path / "assets"
        assets_dir.mkdir()
        manifest_path = assets_dir / "manifest.json"
        manifest_path.write_text(json.dumps({}), encoding="utf-8")

        map_path = tmp_path / "map.json"
        map_path.write_text(
            json.dumps(
                {
                    "name": "Test Map",
                    "grid_size": {"width": 2, "height": 2},
                    "tiles": [{"type": "floor", "q": 0, "r": 0}],
                    "entities": [{"name": "Player", "components": {"Position": {"q": 0, "r": 0}, "Stats": {"health": 100, "speed": 50, "processor": 100}}}],
                }
            ),
            encoding="utf-8",
        )

        loader = MapLoader()
        level_data = loader.load(map_path)

        assert level_data.name == "Test Map"
        assert level_data.grid_size.width == 2
        assert level_data.tiles == [("floor", 0, 0)]
        assert len(level_data.entities) == 1
        player = level_data.entities[0]
        assert player.name == "Player"
        assert player.components["Position"] == {"q": 0, "r": 0}

    def it_validates_required_fields() -> None:
        loader = MapLoader()
        invalid_map = Path("missing.json")

        with pytest.raises(FileNotFoundError):
            loader.load(invalid_map)
