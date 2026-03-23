# AeroFTP Plugins

Official plugin registry for [AeroFTP](https://github.com/axpnet/aeroftp) AeroAgent.

## Available Plugins

| Plugin | Description | Category |
|--------|-------------|----------|
| **File Hasher** | Calculate MD5, SHA-1, SHA-256, SHA-512 hashes | File Management |
| **CSV Stats** | Analyze CSV files with row/column stats | AI Tools |
| **Image Info** | Extract image dimensions, format, metadata | File Management |

## Installation

1. Open AeroFTP > AeroTools > AI Settings > Plugins tab
2. Click "Browse Plugins"
3. Find a plugin and click "Install"

Plugins are downloaded, SHA-256 verified, and installed to `~/.config/aeroftp/plugins/`.

## Creating a Plugin

A plugin is a directory with a `plugin.json` manifest and one or more scripts.

### Directory Structure

```
my-plugin/
  plugin.json    # Manifest (required)
  run.sh         # Script (bash, python, etc.)
```

### Manifest Format

```json
{
  "id": "my-plugin",
  "name": "My Plugin",
  "version": "1.0.0",
  "author": "Your Name",
  "enabled": true,
  "tools": [
    {
      "name": "my_tool",
      "description": "What the tool does",
      "parameters": [
        {
          "name": "input",
          "type": "string",
          "description": "Input value",
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

### How Tools Work

1. AeroAgent calls the tool with JSON arguments on **stdin**
2. Your script reads stdin, processes the request
3. Output JSON result to **stdout**

### Example Script (Bash)

```bash
#!/bin/bash
INPUT=$(cat)
VALUE=$(echo "$INPUT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('input',''))")
echo "{\"result\": \"processed: $VALUE\"}"
```

### Example Script (Python)

```python
#!/usr/bin/env python3
import json, sys
args = json.load(sys.stdin)
result = {"output": args.get("input", "")}
print(json.dumps(result))
```

### Hooks

Plugins can react to events:

| Event | When |
|-------|------|
| `file:created` | Local file created |
| `file:deleted` | Local file deleted |
| `transfer:complete` | File transfer finished |
| `sync:complete` | AeroSync completed |

### Security

- All plugin tools require user approval before execution
- Scripts run in an isolated environment (env cleared)
- SHA-256 integrity verification at install and execution
- 30-second timeout, 1 MB output limit
- No shell metacharacters allowed in commands

## Contributing a Plugin

1. Fork this repository
2. Create a directory under `plugins/` with your plugin
3. Add your plugin to `registry.json`
4. Submit a pull request

## License

Plugins in this repository are licensed under GPL-3.0 unless otherwise specified.
