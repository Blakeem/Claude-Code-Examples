# Claude Code Extensibility Demo

Demonstration examples for the UCSD AI Use Case presentation showing Claude Code's three extension mechanisms: **Commands**, **Skills**, and **MCP Servers**.

All examples implement the same weather functionality to compare how each mechanism works.

## Quick Start

```bash
# Install MCP SDK (required for MCP server)
pip install "mcp[cli]"

# Open this folder in Claude Code
claude

# Try the different extensions
/weather 91941
/weather-skill 91941
/weather-mcp:weather 91941
```

## Project Structure

```
Examples/
├── .claude/
│   ├── commands/
│   │   └── weather.md          # Slash command
│   └── skills/
│       └── weather-skill/
│           └── SKILL.md        # Skill definition
├── .mcp.json                   # MCP server configuration
├── mcp-server/
│   └── weather_server.py       # MCP server (tool + prompt + resource)
├── weather/
│   └── weather.py              # Shared weather utility
└── README.md
```

## Extension Comparison

| Feature | Command | Skill | MCP Server |
|---------|---------|-------|------------|
| **Location** | `.claude/commands/` | `.claude/skills/` | External process |
| **Format** | Single `.md` file | Folder with `SKILL.md` | Python/TypeScript code |
| **Invocation** | User only (`/command`) | User or model-triggered | User (prompts) or model (tools) |
| **Arguments** | `$ARGUMENTS`, `$1`, `$2` | `$ARGUMENTS`, `$1`, `$2` | Positional params (space-split) |
| **Multi-word args** | Yes | Yes | No (use zip codes or quotes*) |
| **Capabilities** | Prompt injection | Prompt injection + files | Tools, Prompts, Resources |

*Quote support for MCP prompt arguments is a known limitation with a pending fix.

## The Three Extension Types

### 1. Commands (`.claude/commands/weather.md`)

Simple markdown files that inject prompts when invoked via `/command`.

```bash
/weather San Diego, CA
```

- Arguments available as `$ARGUMENTS` (full string) or `$1`, `$2`, etc.
- Best for: Simple prompt templates, quick shortcuts

### 2. Skills (`.claude/skills/weather-skill/SKILL.md`)

Folders containing `SKILL.md` with YAML frontmatter. Can be auto-triggered by Claude based on the description, or manually invoked.

```bash
/weather-skill La Mesa, CA
```

- Can include additional files (scripts, references)
- Can restrict available tools via `allowed-tools` in frontmatter
- Best for: Complex workflows, bundled resources, model-initiated actions

### 3. MCP Servers (`mcp-server/weather_server.py`)

External processes that expose tools, prompts, and resources via the Model Context Protocol.

```bash
# Prompt (slash command)
/weather-mcp:weather 91941

# Tool (called by Claude automatically)
# Claude will use weather_tool when asked about weather

# Resource (readable data)
# Available at weather://help
```

**MCP Primitives:**
- **Tools**: Functions Claude can call (returns JSON)
- **Prompts**: Templates that appear as slash commands
- **Resources**: Data that can be read by Claude

Best for: External integrations, complex logic, shared services

## Testing the MCP Server

Use the MCP Inspector to test the server directly:

```bash
npx @modelcontextprotocol/inspector python mcp-server/weather_server.py
```

Opens a web UI at `http://localhost:6274` with tabs for:
- **Tools**: Test `weather_tool` with inputs
- **Prompts**: Test the `weather` prompt
- **Resources**: View `weather://help`

## Weather Data

All examples use [wttr.in](https://wttr.in), a free weather service that requires no API key. Supports:
- City names: `Tokyo`, `London`, `Paris`
- City + State: `San Diego, CA` (commands/skills only)
- Zip codes: `91941`, `92093`, `90210`
- Countries: `France`, `Japan`

## Key Learnings

1. **Commands & Skills** handle multi-word arguments naturally via `$ARGUMENTS`
2. **MCP Prompts** split arguments by spaces - use zip codes or single words
3. **MCP Tools** receive proper JSON from Claude, so multi-word values work fine
4. **Skills** can be triggered automatically by Claude based on their description
5. **MCP Resources** expose readable data (configs, help docs, etc.)

## Files Overview

| File | Purpose |
|------|---------|
| `weather/weather.py` | Shared utility that fetches weather from wttr.in |
| `.claude/commands/weather.md` | Command definition for `/weather` |
| `.claude/skills/weather-skill/SKILL.md` | Skill definition for `/weather-skill` |
| `mcp-server/weather_server.py` | MCP server with tool, prompt, and resource |
| `.mcp.json` | Configures the MCP server for Claude Code |
| `CLAUDE.md` | Project context for Claude |
