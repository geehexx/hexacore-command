---
trigger: glob
description: "Specifies data-driven design for assets and maps."
globs: src/hexa_core/renderer/**/*.py, assets/**/*
---

# Rule: Data-Driven Design

## 4.1 Asset Manifest

* All asset paths MUST be resolved through `assets/manifest.json`. The code must request assets by logical name (e.g., "player_sprite").

## 4.2 Map Format

* Maps are defined as JSON files in `assets/maps/`. They must specify grid dimensions, tile layouts, and initial entity placements with their components.
