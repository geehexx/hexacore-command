# Editing Tools Quick Guide

This guide explains how to choose between Windsurf's built-in editing utilities and the Model Context Protocol (MCP) filesystem tools when modifying the repository.

## Decision Overview

1. **Existing file, small scoped change, stable context**
   - Prefer `apply_patch`.
   - Validate the file contents first (e.g., `mcp1_read_text_file` or prior diff exposure).
   - Abort and switch tools if you receive "string to replace was not found" or similar errors.

2. **Protected or sensitive paths (e.g., `.windsurf/` directories)**
   - Use MCP filesystem editors (`mcp1_edit_file`, `mcp1_write_file`).
   - These paths may reject direct edits from `apply_patch` due to repository guards.

3. **Creating new files or directories**
   - Use `mcp1_create_directory` for missing parent directories.
   - Use `write_to_file` or `mcp1_write_file` to create the new file.
   - Avoid `apply_patch` when the target file does not exist.

4. **Large or multi-section edits**
   - Prefer MCP editors to avoid context drift.
   - Consider editing in stages, verifying diffs via `mcp2_git_diff_unstaged` after each logical chunk.

5. **Fallback strategy**
   - If a tool fails (e.g., due to context changes), re-read the file (`mcp1_read_text_file`) to confirm the latest state, then retry with the alternative editor.

## Quick Reference Table

| Scenario | Recommended Tool | Notes |
| --- | --- | --- |
| Tweak a few lines in a stable file | `apply_patch` | Verify context first; switch if failure occurs. |
| Update `.windsurf/rules/` or workflows | `mcp1_edit_file` | Protected paths favor MCP editors. |
| Add new documentation file | `mcp1_create_directory` (if needed), then `write_to_file` | Ensure parent directories exist. |
| Bulk documentation rewrite | `mcp1_edit_file` | Works well with large insertions/removals. |
| Generated file cleanup | Remove via standard tooling, then update `.gitignore` | Avoid deleting files you cannot recreate. |

## Additional Guidelines

- Always confirm target directories exist before writing. If not, create them with `mcp1_create_directory`.
- Follow the Git MCP workflow for status, diff, staging, and commits (`mcp2_git_status`, `mcp2_git_diff_*`, `mcp2_git_add`, `mcp2_git_commit`).
- After each edit, verify with linting or tests as required (`uv run pymarkdown --config .pymarkdown.json scan .`, etc.).
