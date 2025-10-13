# Editing Tools Quick Guide

## Markdown Cleanup Workflow

To eliminate existing `pymarkdown` violations:

1. Run `uv run pre-commit run pymarkdown --all-files` to capture the latest failure list.
2. Group fixes by directory (`docs/initiatives/`, `docs/tooling/`, `.windsurf/rules/`, etc.) and preserve semantic structure while adjusting indentation, heading emphasis, fenced-block spacing, and line length wrapping.
3. After each directory pass, re-run `uv run pre-commit run --files <paths>` to confine reformatting to the touched documents.
4. When all directories are addressed, finish with a full `uv run pre-commit run --all-files` and document the cleanup in the related initiative update.

## Markdownlint Remediation Workflow

To address markdownlint violations per directory:

1. Identify the directory to remediate (e.g., `docs/initiatives/`, `docs/tooling/`, `.windsurf/rules/`, etc.).
2. Run `markdownlint` on the directory to capture the latest failure list.
3. Group fixes by file and preserve semantic structure while adjusting indentation, heading emphasis, fenced-block spacing, and line length wrapping.
4. After each file pass, re-run `markdownlint` on the directory to confine reformatting to the touched documents.
5. When all files in the directory are addressed, document the cleanup in the related initiative update.

## Editing Tools Overview

This guide explains how to choose between Windsurf's built-in editing utilities and the Model Context Protocol (MCP) filesystem tools when modifying the repository.

## Decision Overview

1. Existing file, small scoped change, stable context
   - Prefer `apply_patch`.
   - Validate the file contents first (e.g., `mcp1_read_text_file` or prior diff exposure).
   - Abort and switch tools if you receive "string to replace was not found" or similar errors.

2. Protected or sensitive paths (e.g., `.windsurf/` directories)
   - Use MCP filesystem editors (`mcp1_edit_file`, `mcp1_write_file`).
   - These paths may reject direct edits from `apply_patch` due to repository guards.

3. Creating new files or directories
   - Use `mcp1_create_directory` for missing parent directories.
   - Use `write_to_file` or `mcp1_write_file` to create the new file.
   - Avoid `apply_patch` when the target file does not exist.

4. Large or multi-section edits
   - Prefer MCP editors to avoid context drift.
   - Consider editing in stages, verifying diffs via `mcp2_git_diff_unstaged` after each logical chunk.

5. Fallback strategy
   - If a tool fails (e.g., due to context changes), re-read the file (`mcp1_read_text_file`) to confirm the latest state, then retry with the alternative editor.

## Quick Reference Table

| Scenario | Recommended Tool | Notes |
| --- | --- | --- |
| Tweak a few lines in a stable file | `apply_patch` | Verify context first; switch if failure occurs. |
| Update `.windsurf/rules/` or workflows | `mcp1_edit_file` | Protected paths favor MCP editors. |
| Add new documentation file | `mcp1_create_directory`, then `write_to_file` | Ensure parent directories exist. |
| Bulk documentation rewrite | `mcp1_edit_file` | Works well with large insertions/removals. |
| Generated file cleanup | Use standard tooling, then update `.gitignore` | Avoid deleting files you cannot recreate. |

## Additional Guidelines

- Always confirm target directories exist before writing. If not, create them with
  `mcp1_create_directory`.
- Follow the Git MCP workflow for status, diff, staging, and commits
  (`mcp2_git_status`, `mcp2_git_diff_*`, `mcp2_git_add`, `mcp2_git_commit`).
- After each edit, verify with linting or tests as required (`uv run pymarkdown --config
  .pymarkdown.json scan .`, etc.).

## Filesystem MCP Playbook

- Establish context early: Read files via `mcp1_read_text_file` before editing to avoid stale
  assumptions. Pair the read with an immediate plan of attack and keep the output handy for patch
  creation.
- Batch reads: Prefer `mcp1_read_multiple_files` whenever you need parallel snapshots (e.g.,
  reviewing related specs and implementations). It tolerates single-file failures without
  aborting the batch, so you can diff partial results quickly.
- Create-first workflow: When introducing new modules or specs, prefer `mcp1_write_file` for
  the first version. Follow with `mcp2_git_status` to confirm ownership, then iterate using
  targeted `apply_patch` or `mcp1_edit_file` for refinements.
- Directory helpers: Use `mcp1_list_directory`, `mcp1_list_directory_with_sizes`, or
  `mcp1_directory_tree` to inspect structure before writing. Pair with `mcp1_create_directory` so
  parents exist prior to file writes. For metadata (timestamps, permissions), call
  `mcp1_get_file_info`.
- Guarded directories: If a path rejects `apply_patch`, switch to `mcp1_edit_file` without
  retrying the failing command repeatedly. This keeps the history clean and prevents tool rate
  limits.
- Atomic diffs: Batch related edits (code + matching tests) before staging. Use
  `mcp2_git_diff_unstaged` to review, then stage with a single `mcp2_git_add` call.
- Checkpoint cadence: Run `mcp2_git_status` → tests → `mcp2_git_add` → `mcp2_git_commit` after
  every logical milestone (e.g., spec + implementation). This mirrors the `/commit` workflow and
  keeps long-running tasks recoverable.

## Search Strategy

- Dual-path search: Combine IDE or built-in search with MCP discovery. Run your local
  search first for rapid feedback, then call `mcp1_search_files` (glob-based) or `grep_search`
  for authoritative results. When possible, reconcile both outputs before acting.
- Directory snapshots: If searching across large trees, generate a `mcp1_directory_tree`
  snapshot to confirm coverage and note excluded directories.
- Follow-up reads: After locating files, use `mcp1_read_multiple_files` for parallel context
  or `mcp1_read_text_file` for targeted sections.

## Fetch & External Resources

- Retry on conversion failures: If `mcp0_fetch` fails to simplify HTML, re-run with
  `raw=true` to retrieve the original content. Use `start_index` pagination to stream long pages
  in chunks.
- Local conversion: When raw HTML is returned, apply local utilities (e.g., markdownifier
  scripts) before summarizing to conserve tokens.
- Security posture: Remember the fetch server can reach internal networks; verify URLs before
  calling `mcp0_fetch`.

## MCP Server Reference

- Filesystem (`mcp-server-filesystem`): Full suite of file operations scoped to allowed roots; configured with project root access.
- Git (`mcp-server-git`): Primary interface for status, diff, staging, commits, branching, and logs.
- Fetch (`mcp-server-fetch`): Web retrieval with markdown/raw modes; supports chunked reads via `start_index`.
- Time (`mcp-server-time`): Provides `get_current_time` and `convert_time` using IANA zone names. Minimal use today, but list it for completeness.
