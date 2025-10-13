# Initiatives Directory Guide

Initiative briefs live directly under `docs/initiatives/` as Markdown files (e.g., `0002-mvp-ui-implementation.md`).

Store supporting artifacts for an initiative under `docs/initiatives/artifacts/<initiative-slug>/`. For example,
assets for Initiative 0002 reside in `docs/initiatives/artifacts/0002-mvp-ui-implementation/`.

Once an initiative is implemented and its living documentation is updated, archive both the initiative brief and its
artifacts according to the documentation lifecycle.

## Archiving Procedure

Follow these steps whenever closing an initiative:

1. Confirm the initiative is complete and all success criteria are met.
2. Move the initiative brief into `docs/initiatives/archive/` and migrate any artifacts into `docs/initiatives/archive/<slug>/` if applicable.
3. Update living documentation, playbooks, and cross-references (for example, testing guides) to point at the archived brief.
4. Run `task lint:markdown` (and other relevant pipelines) to ensure documentation quality gates still pass.
5. Stage file removals using terminal-based `git add` commands as required by repository rules, then commit the archive changes.

Use the `/archive-initiative` workflow (`.windsurf/workflows/archive-initiative.md`) for a detailed checklist.
