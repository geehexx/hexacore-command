---
description: Git commit workflow
auto_execution_mode: 3
---

# Git Commit Workflow

> Prefer running `/develop-feature` for end-to-end feature delivery. Use this commit workflow at the finalization steps or for maintenance work that falls outside `/develop-feature`.

1. Run `mcp2_git_status` for the repo to capture the baseline working tree.
2. Perform the required edits, validations, and automated tests, consulting `docs/tooling/editing-tools.md` to choose the correct editor and to create missing directories if necessary.
3. Re-run `mcp2_git_status` to surface new changes and confirm no unexpected files.
4. Inspect unstaged modifications via `mcp2_git_diff_unstaged`, adjusting context as needed to understand every edit.
5. Verify ownership: ensure each diff belongs to the current task. If unrelated work is present, resolve before continuing.
6. Stage the intended changes through `mcp2_git_add`, supplying the repo path and explicit file list.
7. Confirm the staged snapshot with `mcp2_git_diff_staged` to ensure only desired updates are staged.
8. Commit the staged work with `mcp2_git_commit`, providing the repo path and a descriptive message.
9. Optionally review recent history with `mcp2_git_log` when preparing checkpoints or summaries.
