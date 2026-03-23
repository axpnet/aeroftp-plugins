# Contributing Plugins to AeroFTP

Thank you for your interest in extending AeroFTP with custom plugins. This guide covers everything you need to create, test, and submit a plugin.

## How It Works

AeroFTP plugins are simple scripts (Bash, Python, Node.js, or any language) that AeroAgent can call as tools. When a user asks AeroAgent to perform a task, the AI decides which tool to use, including your plugin tools.

**Data flow:**
```
User prompt → AeroAgent → calls your script with JSON on stdin → your script outputs JSON on stdout → result shown in chat
```

## Quick Start

### 1. Create the Plugin Directory

```
my-plugin/
  plugin.json    # Manifest (required)
  run.sh         # Your script (any language)
```

### 2. Write the Manifest

```json
{
  "id": "my_plugin",
  "name": "My Plugin",
  "version": "1.0.0",
  "author": "your-github-username",
  "enabled": true,
  "tools": [
    {
      "name": "my_tool_name",
      "description": "Clear description of what this tool does. AeroAgent reads this to decide when to use it.",
      "parameters": [
        {
          "name": "input",
          "type": "string",
          "description": "What this parameter is for",
          "required": true
        }
      ],
      "dangerLevel": "medium",
      "command": "bash run.sh"
    }
  ],
  "hooks": []
}
```

### 3. Write the Script

Your script receives JSON arguments on **stdin** and must output JSON on **stdout**.

**Bash example:**
```bash
#!/bin/bash
set -euo pipefail
INPUT=$(cat)
VALUE=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('input',''))")
echo "{\"result\": \"processed: $VALUE\"}"
```

**Python example:**
```python
#!/usr/bin/env python3
import json, sys

args = json.load(sys.stdin)
input_value = args.get("input", "")

result = {"output": f"processed: {input_value}"}
print(json.dumps(result))
```

**Node.js example:**
```javascript
#!/usr/bin/env node
let data = '';
process.stdin.on('data', chunk => data += chunk);
process.stdin.on('end', () => {
  const args = JSON.parse(data);
  const result = { output: `processed: ${args.input}` };
  console.log(JSON.stringify(result));
});
```

### 4. Test Locally

Copy your plugin directory to `~/.config/aeroftp/plugins/`:

```bash
cp -r my-plugin/ ~/.config/aeroftp/plugins/my_plugin/
```

Open AeroFTP, go to AI Settings > Plugins tab. Your plugin should appear. Try asking AeroAgent to use it.

### 5. Submit to the Registry

Once your plugin works, submit it here so other users can install it from the Plugin Browser.

## Submission Process

### Step 1: Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/aeroftp-plugins.git
cd aeroftp-plugins
```

### Step 2: Add Your Plugin

```bash
mkdir plugins/my-plugin
# Add your plugin.json and scripts
```

### Step 3: Add to Registry

Edit `registry.json` and add your plugin entry. Use empty `sha256` values; the maintainer will compute them before merging.

```json
{
  "id": "my-plugin",
  "name": "My Plugin",
  "version": "1.0.0",
  "author": "your-github-username",
  "description": "One-line description shown in the Plugin Browser",
  "category": "file-management",
  "downloads": 0,
  "stars": 0,
  "repo_url": "https://github.com/YOUR_USERNAME/aeroftp-plugins",
  "manifest_url": "https://raw.githubusercontent.com/axpnet/aeroftp-plugins/main/plugins/my-plugin/plugin.json",
  "files": [
    {
      "path": "plugin.json",
      "url": "https://raw.githubusercontent.com/axpnet/aeroftp-plugins/main/plugins/my-plugin/plugin.json",
      "sha256": ""
    },
    {
      "path": "run.sh",
      "url": "https://raw.githubusercontent.com/axpnet/aeroftp-plugins/main/plugins/my-plugin/run.sh",
      "sha256": ""
    }
  ]
}
```

**Categories:** `file-management`, `ai-tools`, `automation`, `integration`

### Step 4: Submit a Pull Request

```bash
git add plugins/my-plugin/ registry.json
git commit -m "feat: add my-plugin"
git push origin main
```

Open a PR against `axpnet/aeroftp-plugins`. The maintainer will:
1. Review your code for security and quality
2. Compute SHA-256 hashes for all files
3. Merge and publish

## Manifest Reference

### Plugin Manifest (`plugin.json`)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique ID (alphanumeric + underscore, no spaces) |
| `name` | string | Yes | Display name |
| `version` | string | Yes | Semver (e.g. "1.0.0") |
| `author` | string | Yes | Your GitHub username |
| `enabled` | bool | No | Default: true |
| `tools` | array | Yes | List of tool definitions |
| `hooks` | array | No | Event hooks (see below) |

### Tool Definition

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Tool name (used by AeroAgent, must be unique) |
| `description` | string | Yes | What the tool does (AeroAgent reads this) |
| `parameters` | array | Yes | Input parameters |
| `dangerLevel` | string | No | `"medium"` (default) or `"high"` |
| `command` | string | Yes | Command to execute (relative to plugin dir) |

**Note:** `dangerLevel: "safe"` is not allowed for plugins. All plugin tools require user approval.

### Parameter Definition

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Parameter name |
| `type` | string | Yes | `"string"`, `"number"`, `"boolean"`, `"array"` |
| `description` | string | Yes | What the parameter is for |
| `required` | bool | No | Default: false |

### Event Hooks

Hooks let your plugin react to events automatically.

```json
{
  "hooks": [
    {
      "event": "transfer:complete",
      "command": "on_transfer.sh",
      "filter": "*.csv"
    }
  ]
}
```

| Event | When | Context |
|-------|------|---------|
| `file:created` | Local file created | `{ "path": "...", "size": ... }` |
| `file:deleted` | Local file deleted | `{ "path": "..." }` |
| `transfer:complete` | Transfer finished | `{ "type": "download", "remote_path": "...", "local_path": "...", "size": ... }` |
| `sync:complete` | AeroSync completed | `{ "direction": "...", "files_processed": ... }` |

The `filter` field is optional and accepts glob patterns (e.g. `"*.csv"`, `"*.log"`).

## Security Rules

Plugins run in a sandboxed environment:

- **Environment isolation**: All env vars cleared except PATH, HOME, LANG, TERM
- **Timeout**: 30 seconds per execution
- **Output limit**: 1 MB stdout
- **Integrity**: SHA-256 verified at install and before every execution
- **No shell metacharacters**: Commands cannot contain `| & ; $ ( ) > < { }`
- **No path traversal**: No `..` or absolute paths in commands
- **User approval**: Every plugin tool call requires user confirmation

## Tips for Good Plugins

- **Clear description**: AeroAgent uses the description to decide when to call your tool. Be specific.
- **Minimal dependencies**: Prefer scripts that use standard tools (Python stdlib, coreutils). Users should not need to install extra packages.
- **JSON in, JSON out**: Always read JSON from stdin and write JSON to stdout.
- **Handle errors gracefully**: Output `{"error": "message"}` instead of crashing.
- **One tool, one job**: Keep tools focused. Multiple small tools are better than one complex tool.

## Questions?

Open an issue on [aeroftp-plugins](https://github.com/axpnet/aeroftp-plugins/issues) or on the main [AeroFTP repo](https://github.com/axpnet/aeroftp/issues).
