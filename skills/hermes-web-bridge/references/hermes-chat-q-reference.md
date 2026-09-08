# hermes chat -q — Direct CLI Bridge Reference

## Command

```bash
hermes -p <profile> chat -q "<message>" -Q
```

**Flags:**
- `-p <profile>` — Use a specific Hermes profile (e.g., `gentech`)
- `-q "<message>"` — Single query, non-interactive mode
- `-Q` — Quiet output (no banner, just session_id + response)

## Output Format

```
session_id: YYYYMMDD_HHMMSS_XXXX
<response text>
```

First line is the session ID. Everything after the first newline is the response.

## Session Continuity

```python
# First call — new session
result = await ask_hermes("Hello")
# result["session_id"] = "20260615_125503_1441a4"
# result["response"] = "Hey! Welcome to GenTech..."

# Subsequent calls — resume session
result = await ask_hermes("What did I just say?", result["session_id"])
# Hermes has full context from previous messages
```

## Performance

| Metric | Cold Start | Warm |
|--------|-----------|------|
| First call | 5-10s | — |
| Subsequent | — | 3-5s |
| Complex queries | Up to 30s | Up to 30s |
| Timeout (recommended) | 120s | 120s |

## Environment

```bash
# Must set HERMES_PROFILE or use -p flag
export HERMES_PROFILE=gentech

# For systemd services, set in service file:
Environment=HERMES_PROFILE=gentech
```

## Usage in FastAPI

```python
import asyncio

async def ask_hermes(message: str, session_id: str = None, profile: str = "gentech") -> dict:
    cmd = ["hermes", "-p", profile, "chat", "-q", message, "-Q"]
    if session_id:
        cmd.extend(["--resume", session_id])
    
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env={**os.environ, "HERMES_YOLO_MODE": "1"},
    )
    
    stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=120)
    output = stdout.decode().strip()
    
    new_session_id = session_id
    response_text = output
    
    if output.startswith("session_id:"):
        lines = output.split("\n", 1)
        new_session_id = lines[0].replace("session_id:", "").strip()
        response_text = lines[1].strip() if len(lines) > 1 else ""
    
    return {"response": response_text or "(no response)", "session_id": new_session_id}
```

## Key Insight

`hermes chat -q` bypasses the gateway entirely. It runs Hermes in CLI mode, which means:
- No Telegram/Discord relay needed
- No long-polling conflicts
- Direct access to all Hermes tools and skills
- Session context maintained via `--resume`

This is the simplest way to build external interfaces that talk to Hermes.
