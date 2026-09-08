# Condor boot-check + Hummingbot API bring-up (Aug 19, 2026)

## Boot-check must run under `uv run`, not bare python3
Condor uses `uv` (Rust package manager) with a project venv. Bare
`python3 -c "import condor, telegram, fastapi, solana"` fails with
`ModuleNotFoundError: No module named 'telegram'` because the deps live in the
`uv`-managed venv, not system python. **Run every boot-check as `uv run python3 -c "..."`**
from `/root/condor`.

Also `unset VIRTUAL_ENV` first — a stray `VIRTUAL_ENV` pointing at an unrelated venv
(e.g. `/root/ClawWork/.venv-livebench`) makes `uv` warn and can resolve to the wrong
interpreter.

The strategy loader needs a `pathlib.Path`, not a string:
`_load_strategy_from_file(Path('agents/.../strategy.md'), slug)` — passing a str raises
`AttributeError: 'str' object has no attribute 'read_text'`.

## Hummingbot API container can be DOWN even when the stack looks up
`docker ps --filter name=hummingbot` may show only `hummingbot-postgres`,
`hummingbot-broker`, `hummingbot-tailscale` running — the **`hummingbot-api` container
itself can be absent/stopped**, so port 8002 returns 502 and Condor can't execute.
Check for the API container specifically:
```bash
docker ps --filter name=hummingbot-api   # empty = API is down
# Bring it up (pulls the image if needed):
cd /root/hummingbot-api && docker compose up -d hummingbot-api
# Verify: host 8002 -> container 8000 (the compose maps 8002:8000)
curl -s -u "$USER:$PASS" -o /dev/null -w "%{http_code}" http://localhost:8002/   # expect 200
```
The API is on **host 8002 → container 8000** (remapped). `localhost:8000` returns 502 — that's
expected; always test 8002.

## Wire the API into Condor's config.yml
After the API is up, wire it via `ConfigManager`:
```python
from config_manager import ConfigManager
cm = ConfigManager('config.yml')
cm.add_server('hummingbot-api', '127.0.0.1', 8002, USER, PASS, owner_id=ADMIN_ID)
cm.set_default_server('hummingbot-api')
```
Resulting shape: `servers: {name: {host, port, username, password}}` + `default_server: name`.
