---
description: Archive Initiative Workflow
auto_execution_mode: 3
---

# Archive Initiative Workflow

## Phase 1: Verification

1. **Confirm Completion**
   Ensure the initiative's success criteria are met and living documentation has been updated.
2. **Inventory References**
   Search the repository for references to the initiative ID (e.g., `0004`) across documentation and rules to identify links that must be redirected.

## Phase 2: Archival Actions

1. **Move Brief**
   Relocate the initiative markdown file to `docs/initiatives/archive/`.
2. **Migrate Artifacts**
   If artifacts exist under `docs/initiatives/artifacts/<slug>/`, move them to an `archive/` subfolder.
3. **Update Cross-References**
   Adjust any documentation (playbooks, READMEs, rules) to point at the archived location.
4. **Document Procedure**
   Note the archive in `docs/initiatives/README.md` or other tracking documents as needed.

## Phase 3: Validation

1. **Lint Documentation**
   Run `task lint:markdown` to ensure formatting remains valid.
2. **Run Additional Checks**
   Execute any suite impacted by the changes (e.g., `task lint:all`) if cross-references touched other tooling docs.

## Phase 4: Version Control

1. **Stage Removals via Terminal**
   Use terminal-based `git add <path>` to stage deleted/moved initiative files per repository policy.
2. **Review Diff**
   Inspect staged changes with `mcp2_git_diff_staged` to confirm accuracy.
3. **Commit**
   Commit the archival work with a descriptive message (for example, `chore/docs: archive initiative 0004`).
4. **Follow-up Tasks**
   If future work is required (e.g., new initiatives spawning from TODOs), capture them in appropriate trackers.
