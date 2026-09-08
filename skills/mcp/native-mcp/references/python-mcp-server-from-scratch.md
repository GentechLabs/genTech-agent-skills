# Python MCP Server From Scratch (Zero Dependencies)

Build a working MCP server using only Python stdlib. No `mcp` package, no `fastapi`, no external deps.

## Minimal Server Template

```python
import json, sys
from typing import Any

TOOLS = [
    {
        "name": "my_tool",
        "description": "What this tool does",
        "inputSchema": {
            "type": "object",
            "properties": {
                "param1": {"type": "string", "description": "A parameter"}
            }
        }
    }
]

def handle_request(msg: dict) -> dict | None:
    req_id = msg.get("id")
    method = msg.get("method")
    params = msg.get("params", {})

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}

    elif method == "tools/call":
        tool = params.get("name")
        args = params.get("arguments", {})
        if tool == "my_tool":
            result_text = f"You called my_tool with {args}"
            return {"jsonrpc": "2.0", "id": req_id, "result": {
                "content": [{"type": "text", "text": result_text}]
            }}
        return {"jsonrpc": "2.0", "id": req_id,
                "error": {"code": -32601, "message": f"Unknown tool: {tool}"}}

    elif method == "resources/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"resources": []}}

    return None

def main():
    # MCP stdio transport: read JSON-RPC from stdin, write to stdout
    for line in sys.stdin:
        line = line.strip()
        if not line: continue
        try:
            msg = json.loads(line)
            resp = handle_request(msg)
            if resp:
                sys.stdout.write(json.dumps(resp) + "\n")
                sys.stdout.flush()
        except json.JSONDecodeError:
            continue
        except Exception as e:
            err = {"jsonrpc": "2.0", "id": msg.get("id"),
                   "error": {"code": -32000, "message": str(e)}}
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
```

## Required MCP Endpoints

The MCP protocol on stdio transport requires at minimum:

| Method | Purpose |
|--------|---------|
| `tools/list` | Return available tool definitions with schemas |
| `tools/call` | Execute a tool and return results |
| `resources/list` | (Optional) Return available resources — return empty list if not used |

## Tool Response Format

Always return content as an array of `{type, text}` objects:

```python
{"content": [{"type": "text", "text": "Result here"}]}
```

Errors use standard JSON-RPC error codes:
- `-32601` = Method/tool not found
- `-32000` = Generic server error

## Input/Output Protocol

- **Input**: One JSON-RPC 2.0 request object per line from `stdin`
- **Output**: One JSON-RPC 2.0 response object per line to `stdout`
- Each request has an `id` that must match in the response
- Always flush stdout after each response: `sys.stdout.flush()`

## Registration in Hermes

```bash
hermes config set mcp_servers.my-server '{
  "command": "python3",
  "args": ["/path/to/server.py"],
  "enabled": true,
  "timeout": 30,
  "connect_timeout": 10
}'
```

Or add to `~/.hermes/profiles/<agent>/config.yaml` under `mcp_servers`.

## Testing

```bash
# Test tools/list
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python3 server.py

# Test tools/call
echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"my_tool","arguments":{}}}' | python3 server.py
```

## Production Reference

See the GTA Arb MCP server at `/root/repos/gta-arb-mcp/server.py` for a complete production example with:
- Multi-tool support
- External API calls (Hyperliquid + Coinbase)
- Error handling with fallback
- Structured text responses
- Filter parameters in tool schemas
