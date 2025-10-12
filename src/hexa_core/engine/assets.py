"""Asset manifest utilities for Hexa-Core Command."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


@dataclass(slots=True)
class AssetManifest:
    """Data container for categorized asset paths."""

    entries: dict[str, dict[str, Path]]

    @classmethod
    def from_file(cls, path: Path | str) -> "AssetManifest":
        manifest_path = Path(path)
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        return cls(cls._normalize_entries(data))

    @staticmethod
    def _normalize_entries(raw: Mapping[str, Mapping[str, str]]) -> dict[str, dict[str, Path]]:
        normalized: dict[str, dict[str, Path]] = {}
        for category, items in raw.items():
            normalized[category] = {name: Path(location) for name, location in items.items()}
        return normalized

    def get_asset_path(self, category: str, name: str) -> Path:
        try:
            category_entries = self.entries[category]
        except KeyError as exc:  # pragma: no cover - defensive guard
            raise KeyError(f"Unknown asset category '{category}'") from exc
        try:
            return category_entries[name]
        except KeyError as exc:
            raise KeyError(f"Unknown asset '{name}' in category '{category}'") from exc
