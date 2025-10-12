# MCP Server Configuration Guide

This project relies on multiple Model Context Protocol (MCP) servers installed locally. The active configuration lives in `~/.codeium/windsurf/mcp_config.json`, which is loaded automatically by the Windsurf IDE.

```json
{
  "mcpServers": {
    "fetch": {
      "command": "mcp-server-fetch"
    },
    "git": {
      "command": "mcp-server-git"
    },
    "filesystem": {
      "command": "mcp-server-filesystem",
      "args": ["/home/gxx/projects/hexacore-command"]
    },
    "time": {
      "command": "mcp-server-time"
    }
  }
}
```

## Local Setup Checklist

1. **Install binaries**
   - Ensure `mcp-server-fetch`, `mcp-server-git`, `mcp-server-filesystem`, and `mcp-server-time` are available on your `PATH`. Using `uv tool install` is recommended for reproducibility.
2. **Copy configuration (optional)**
   - Copy the JSON above into `%USERPROFILE%/.codeium/windsurf/mcp_config.json` (Windows) or `~/.codeium/windsurf/mcp_config.json` (Linux/macOS).
   - Adjust the `filesystem.args` path if your project root differs.
3. **Server ordering**
   - Keep the server keys ordered as shown. Some clients index servers numerically based on configuration order; changing it can alter tool selection precedence.
4. **Project-local reference**
   - This document serves as the canonical reference. If collaborators need a template, create `.windsurf/mcp_config.json` from the snippet and point Windsurf to it via settings.

## Usage Notes

- **Filesystem roots**: The configured filesystem server is scoped strictly to `/home/gxx/projects/hexacore-command`. Update the argument list if additional directories are required.
- **Fetch retries**: When web content fails to convert to markdown, retry with `raw=true` and process locally.
- **Git operations**: All status, diff, staging, and commit actions should go through the MCP git server to preserve auditability.
- **Time utilities**: `mcp-server-time` provides `get_current_time` and `convert_time` for IANA timezone handling.
