# OpenSpace MCP — Setup & Integration

[OpenSpace](https://github.com/HKUDS/OpenSpace) (6.8k⭐) is a quality-first Skill Hub for AI agents. v2 released Jul 16, 2026. MCP-compatible: stdio, SSE, streamable HTTP.

## Installation

```bash
# OpenSpace requires Python 3.12+ — Hermes default venv is 3.11
# Create a separate venv:
python3.12 -m venv /root/openspace-venv
/root/openspace-venv/bin/pip install -e /root/OpenSpace

# Verify
/root/openspace-venv/bin/openspace-mcp --help
```

## Hermes MCP Config

Add to `~/.hermes/profiles/gentech/config.yaml` under `mcp_servers`:

```yaml
mcp_servers:
  openspace:
    command: /root/openspace-venv/bin/openspace-mcp
    args: ["--transport", "stdio"]
    env:
      OPENSPACE_WORKSPACE: /root/OpenSpace
      OPENSPACE_HOST_SKILL_DIRS: /root/.hermes/profiles/gentech/skills
      OPENSPACE_CLOUD_MODE: "off"       # local-only; set "live" for cloud
    timeout: 600
    connect_timeout: 30
    sampling:
      enabled: false                    # disable for untrusted servers
```

**Key env vars:**
- `OPENSPACE_WORKSPACE` — Absolute path to the cloned OpenSpace repo root
- `OPENSPACE_HOST_SKILL_DIRS` — Comma-separated paths to agent skill directories
- `OPENSPACE_CLOUD_MODE` — `"off"` (local-only, no API key) or `"live"` (cloud community)
- `OPENSPACE_CLOUD_API_KEY` — Required for cloud uploads; set via `openspace-cloud-auth bootstrap-agent-key`

## Cloud Auth (for Skill Upload)

```bash
cd /root/OpenSpace
/root/openspace-venv/bin/openspace-cloud-auth bootstrap-agent-key \
  --email you@example.com \
  --agent-name gentech-x402-contributor
```

This stores `OPENSPACE_CLOUD_MODE=live` and `OPENSPACE_CLOUD_API_KEY` locally.

## Uploading a Skill

```bash
# Dry run first
/root/openspace-venv/bin/openspace-upload-skill \
  --skill-dir /path/to/skill-dir \
  --visibility public \
  --dry-run

# Real upload
/root/openspace-venv/bin/openspace-upload-skill \
  --skill-dir /path/to/skill-dir \
  --visibility public
```

**Trust gate:** Upload requires a `trusted` local SkillStore record. If you get `ERROR [SKILL_TRUST_UNKNOWN]`, register the skill first:

```python
import asyncio
from pathlib import Path
from openspace.skill_engine.registry import SkillRegistry
from openspace.skill_engine.store import SkillStore

async def register_and_trust():
    store = SkillStore(db_path='/path/to/skill-dir/.skill_store.db')
    registry = SkillRegistry()
    skill_meta = registry.register_skill_dir(Path('/path/to/skill-dir'))
    await store.sync_from_registry(registry)
    record = await store.load_record_by_path(str(Path('/path/to/skill-dir')))
    if record:
        await store.record_trust_observation(record.skill_id, trusted=True)

asyncio.run(register_and_trust())
```

## Pitfalls

- **Python 3.12 requirement:** OpenSpace requires `>=3.12`. The Hermes default venv uses 3.11. Always create a separate venv with `python3.12 -m venv` and point the MCP config's `command` at that venv's binary.
- **Slow clone:** The `assets/` folder is ~50 MB. Use `--filter=blob:none --sparse` to skip it.
- **Cloud auth is interactive:** `bootstrap-agent-key` prompts for a password on the terminal. It cannot run fully headless.
- **Upload trust gate:** The CLI tool checks for a trusted local SkillStore record before uploading. A freshly cloned repo has no local store — you must register and trust the skill first via the Python API.
